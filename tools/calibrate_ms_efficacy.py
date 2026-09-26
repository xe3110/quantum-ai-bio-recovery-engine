"""Test whether the screen's scores track published multiple sclerosis efficacy.

The screen produces a ``signed_reversal`` for every agent, but nothing ties that
number to an observed effect. This checks the one thing that can be checked
without inventing a mapping: do agents that published meta-analyses rate as more
effective score higher?

Only drugs whose effect was read from a fetched source are used. The claim is
deliberately coarse -- two tiers -- because that is all the verified data
supports.

Sources (fetched 2026-09-26; effect estimates copied from the article text):

* Samjoo IA et al. Comparative efficacy of therapies for relapsing multiple
  sclerosis: a systematic review and network meta-analysis. J Comp Eff Res 2023.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10508312/
  Annualized relapse rate (ARR) rate ratio versus placebo: alemtuzumab,
  natalizumab, ocrelizumab, ofatumumab and ublituximab 0.28 to 0.34; ozanimod
  0.43; ponesimod 0.47. Per-drug values inside the 0.28-0.34 band were not
  recoverable from the text, so those five are treated as one tier.
* Efficacy and safety of disease-modifying oral drugs in relapsing-remitting
  multiple sclerosis: systematic review and network meta-analysis. Front Immunol
  2026. https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2026.1733948/full
  ARR mean difference versus placebo: siponimod 2 mg -0.38 (95% CI -0.76 to
  0.00), fingolimod 0.5 mg -0.21, cladribine 3.5 mg/kg -0.19, dimethyl fumarate
  240 mg BID -0.19.

Not used, because no figure was read from a fetched source: interferons,
glatiramer acetate, teriflunomide, and every drug without a relapse-prevention
trial (methylprednisolone treats acute relapses; it has no ARR figure).

Run: python -m tools.reversal_ceiling  (for the screen), then
     python -m tools.calibrate_ms_efficacy
"""

from __future__ import annotations

import csv
from pathlib import Path

from scipy.stats import mannwhitneyu, spearmanr

ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "experiments/ms/results/ms_kary_combinations_full.csv"

HIGH_EFFICACY_MABS = ["Ocrelizumab", "Alemtuzumab", "Natalizumab", "Ofatumumab", "Ublituximab"]
OTHER_DMTS = ["Siponimod", "Dimethyl fumarate", "Fingolimod", "Cladribine", "Ozanimod", "Ponesimod"]
ORAL_MEAN_DIFFERENCE = {"Siponimod": -0.38, "Fingolimod": -0.21,
                        "Cladribine": -0.19, "Dimethyl fumarate": -0.19}
ARR_RATE_RATIO = {"Ozanimod": 0.43, "Ponesimod": 0.47}


def monotherapy_scores() -> dict[str, dict[str, float]]:
    with SCREEN.open(newline="") as handle:
        return {
            row["combination"]: {k: float(row[k]) for k in
                                 ("signed_reversal", "reversal_efficiency",
                                  "priority_score", "gene_coverage")}
            for row in csv.DictReader(handle) if row["order"] == "1"
        }


def main() -> None:
    scores = monotherapy_scores()
    print("Two-tier separation: 5 monoclonal antibodies (ARR RR 0.28-0.34) vs 6 other DMTs")
    print(f"{'score':22s} {'mAb mean':>9s} {'other mean':>11s} {'AUC':>5s} {'p (one-sided)':>14s}")
    for column in ("signed_reversal", "reversal_efficiency", "gene_coverage", "priority_score"):
        a = [scores[n][column] for n in HIGH_EFFICACY_MABS]
        b = [scores[n][column] for n in OTHER_DMTS]
        test = mannwhitneyu(a, b, alternative="greater")
        auc = test.statistic / (len(a) * len(b))
        print(f"{column:22s} {sum(a)/len(a):9.4f} {sum(b)/len(b):11.4f} {auc:5.2f} {test.pvalue:14.4f}")

    names = list(ORAL_MEAN_DIFFERENCE)
    rho = spearmanr([-ORAL_MEAN_DIFFERENCE[n] for n in names],
                    [scores[n]["signed_reversal"] for n in names])
    print(f"\nWithin four oral agents (ARR mean difference), Spearman rho on signed_reversal = "
          f"{rho.statistic:.2f} (n = 4; not interpretable)")
    print("Ozanimod vs ponesimod (RR 0.43 vs 0.47): signed_reversal "
          f"{scores['Ozanimod']['signed_reversal']:.4f} vs {scores['Ponesimod']['signed_reversal']:.4f}")


if __name__ == "__main__":
    main()
