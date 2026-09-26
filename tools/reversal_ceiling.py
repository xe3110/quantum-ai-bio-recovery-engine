"""Express each disease's best signature reversal as a share of what its panel could reach.

``signed_reversal`` is the fraction of a signature's total weight that a regimen
moves in the therapeutic direction. It has no natural scale: it shrinks when the
signature gains genes nobody targets, and it cannot exceed what the panel's
targets cover. Read on its own, "10%" invites the question of what would have
been 100%.

Two ceilings answer it:

* **Full-reversal ceiling** -- the weight fraction of every signature gene the
  panel targets at all, as if each were reversed completely. Unattainable, since
  curated effects are fractions, but it is the bound the panel cannot exceed.
* **Pooled-panel ceiling** -- every agent given at once, keeping only
  therapeutic-direction effects and combining them gene-wise under Bliss. It
  respects the curated effect sizes and is the more realistic bound.

Both are properties of the panel, and the panel was curated from the signature's
gene set, so both are generous; a panel built independently would have a lower
ceiling. This is a normalisation, not a calibration: it makes the disease
screens comparable with one another, and it says nothing about clinical benefit.

Run: python -m tools.reversal_ceiling
"""

from __future__ import annotations

import csv
from pathlib import Path

from core.biology.signature import bliss_combine
from core.models.disease import load_disease

ROOT = Path(__file__).resolve().parents[1]

SCREENS = {
    "multiple_sclerosis": ROOT / "experiments/ms/results/ms_kary_combinations_full.csv",
    "parkinsons": ROOT / "experiments/parkinsons/results/pd_combinations_full.csv",
    "alzheimers": ROOT / "experiments/alzheimers/results/ad_combinations_full.csv",
    "epilepsy": ROOT / "experiments/epilepsy/results/ep_combinations_full.csv",
    "guillain_barre": ROOT / "experiments/guillain_barre/results/gbs_combinations_full.csv",
}


def ceilings(disease) -> dict[str, float]:
    signature, panel = disease.signature(), disease.panel()
    total = signature.total_weight
    targeted = {g for drug in panel for g in drug["target_effects"] if g in signature.logfc}
    pooled: dict[str, float] = {}
    for drug in panel:
        for gene, value in drug["target_effects"].items():
            if gene in signature.logfc and signature.desired[gene] * value > 0:
                pooled[gene] = bliss_combine(pooled.get(gene, 0.0), abs(value))
    return {
        "targeted": len(targeted),
        "signature_genes": len(signature.logfc),
        "full_reversal": sum(signature.weight[g] for g in targeted) / total,
        "pooled_panel": sum(signature.weight[g] * pooled[g] for g in pooled) / total,
    }


def best_by_order(disease, path: Path) -> dict[int, float]:
    best: dict[int, float] = {}
    if not path.exists():
        return best
    for row in csv.DictReader(path.open(newline="")):
        order = int(row.get("order", 2))
        best[order] = max(best.get(order, 0.0), float(row["signed_reversal"]))
    return best


def main() -> None:
    for identifier, path in SCREENS.items():
        disease = load_disease(identifier)
        ceiling = ceilings(disease)
        best = best_by_order(disease, path)
        print(f"\n{identifier}: {ceiling['targeted']}/{ceiling['signature_genes']} genes targeted; "
              f"full-reversal ceiling {ceiling['full_reversal']:.1%}, "
              f"pooled-panel ceiling {ceiling['pooled_panel']:.1%}")
        if not best:
            print(f"  (no screen results at {path.relative_to(ROOT)}; run the screen first)")
        for order in sorted(best):
            value = best[order]
            print(f"  k={order}: reversal {value:.2%}  = {value / ceiling['full_reversal']:.1%} of "
                  f"full ceiling, {value / ceiling['pooled_panel']:.1%} of pooled ceiling")


if __name__ == "__main__":
    main()
