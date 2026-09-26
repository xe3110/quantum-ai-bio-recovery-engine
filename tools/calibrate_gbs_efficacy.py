"""Test whether the screen's score separates Guillain-Barre agents that worked from those that did not.

Guillain-Barre has few randomised trials but several clear outcomes, which makes
it a useful place to ask the question the MS calibration asked: does
``signed_reversal`` track efficacy? The comparison is deliberately coarse, two
groups, because the sourced data supports nothing finer.

Outcomes read from sources (searched 2026-09-27; the trial summaries were taken
from the search results, not from the primary papers):

* Tanruprubart (ANX005): positive pivotal phase 3, 2.4-fold improvement on the GBS
  disability scale at week 8 (p = 0.0058).
  https://ir.annexonbio.com/news-releases/news-release-details/annexon-announces-positive-topline-results-pivotal-phase-3-trial/
* Methylprednisolone: 242 patients randomised, no significant difference from
  placebo on any outcome. https://pubmed.ncbi.nlm.nih.gov/8094828/
* Interferon beta-1a as an add-on to IVIG: no significant improvement.
  https://pubmed.ncbi.nlm.nih.gov/14610140/
* Fingolimod: not better than placebo in CIDP (a related chronic neuropathy, not
  GBS itself). https://www.thelancet.com/journals/laneur/article/PIIS1474-4422(18)30202-3/abstract
* A second IVIG course: no benefit and more serious adverse events (SID-GBS).
  https://pubmed.ncbi.nlm.nih.gov/33743237/

Intravenous immunoglobulin and plasma exchange are the established standard of
care and are counted as effective, but that status was not separately sourced
here. The second IVIG course is excluded from the comparison because the panel
records it with the same target effects as IVIG (it is the same drug), so it would
only add a tied duplicate.

Eculizumab (inconclusive, underpowered) and the pain and conduction agents (which
have no disease-modifying trial) are not classified.

Run: python -m tools.calibrate_gbs_efficacy   (needs the GBS screen results)
"""

from __future__ import annotations

import csv
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "experiments/guillain_barre/results/gbs_combinations_full.csv"

EFFECTIVE = ["Tanruprubart (ANX005)", "Plasma exchange", "Intravenous immunoglobulin"]
NOT_EFFECTIVE = ["Methylprednisolone", "Interferon beta-1a", "Fingolimod"]


def monotherapy_scores() -> dict[str, dict[str, float]]:
    with SCREEN.open(newline="") as handle:
        return {
            row["combination"]: {k: float(row[k]) for k in
                                 ("signed_reversal", "reversal_efficiency", "priority_score")}
            for row in csv.DictReader(handle) if row["order"] == "1"
        }


def auc(good: list[float], bad: list[float]) -> float:
    wins = sum(1.0 if g > b else 0.5 if g == b else 0.0 for g in good for b in bad)
    return wins / (len(good) * len(bad))


def exact_p(scores: dict[str, float]) -> float:
    """One-sided exact permutation p: chance a random split scores at least this well."""
    names = EFFECTIVE + NOT_EFFECTIVE
    observed = auc([scores[n] for n in EFFECTIVE], [scores[n] for n in NOT_EFFECTIVE])
    hits = total = 0
    for chosen in combinations(names, len(EFFECTIVE)):
        rest = [n for n in names if n not in chosen]
        total += 1
        hits += auc([scores[n] for n in chosen], [scores[n] for n in rest]) >= observed - 1e-12
    return hits / total


def main() -> None:
    scores = monotherapy_scores()
    print("Effective (3) versus not effective (3), monotherapy scores from the GBS screen")
    print(f"{'score':22s} {'AUC':>5s} {'exact p (one-sided)':>20s}")
    for column in ("signed_reversal", "reversal_efficiency", "priority_score"):
        s = {n: scores[n][column] for n in EFFECTIVE + NOT_EFFECTIVE}
        good = [s[n] for n in EFFECTIVE]
        bad = [s[n] for n in NOT_EFFECTIVE]
        print(f"{column:22s} {auc(good, bad):5.2f} {exact_p(s):20.3f}")
    print("\nsigned_reversal, ordered:")
    for name in sorted(EFFECTIVE + NOT_EFFECTIVE, key=lambda n: -scores[n]["signed_reversal"]):
        tag = "effective" if name in EFFECTIVE else "no benefit"
        print(f"  {scores[name]['signed_reversal']:.4f}  {name}  ({tag})")


if __name__ == "__main__":
    main()
