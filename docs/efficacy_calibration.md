# Does the screen's score track real efficacy? — calibration against published results

The screens produce a `signed_reversal` for every agent and combination, and the
docs say repeatedly that it is a ranking score, not an efficacy rate. This
document tests the strongest thing that can honestly be said about it: **do
agents that published meta-analyses rate as more effective score higher?**

The answer is a qualified yes for one disease, at the coarsest level, and no
numeric mapping from score to effect is supported. Nothing here turns a
combination's score, or a designed molecule's, into a predicted efficacy rate.

```bash
python -m tools.calibrate_ms_efficacy      # needs the MS k-ary screen results
```

## 1. What was and was not possible

Effect sizes were read from **fetched sources**, not recalled. The published
efficacy of a multiple sclerosis drug is reported as an annualized relapse rate
(ARR) reduction, and two open-access network meta-analyses give it on a common
placebo scale:

| Source | What it gives | Drugs |
|---|---|---|
| [Samjoo et al., *J Comp Eff Res* 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10508312/) | ARR rate ratio vs placebo | alemtuzumab, natalizumab, ocrelizumab, ofatumumab, ublituximab: **0.28–0.34**; ozanimod **0.43**; ponesimod **0.47** |
| [Front Immunol 2026 (oral DMT network meta-analysis)](https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2026.1733948/full) | ARR mean difference vs placebo | siponimod −0.38 (95% CI −0.76 to 0.00), fingolimod −0.21, cladribine −0.19, dimethyl fumarate −0.19 |

That is **11 drugs**, and the per-drug values inside the 0.28–0.34 antibody band
were not recoverable from the article text, so those five are one tier. The two
sources use different scales (a ratio and an absolute difference) and cannot be
merged into one number.

**Not used:** interferons, glatiramer acetate and teriflunomide, because no
figure for them was read from a fetched source (a search-engine summary offered
some, but its numbers were not reliable enough to use); and methylprednisolone,
which treats acute relapses and has no relapse-prevention figure.

**Alzheimer's and Parkinson's were not calibrated.** I did not gather sourced
effect sizes for them. Approved Alzheimer's agents report cognitive scales
(ADAS-Cog, CDR-SB) that are not comparable across the cholinesterase inhibitors,
memantine and the antibodies without a common-scale meta-analysis, and Parkinson's
has no approved disease-modifying agent. This is work not done, not a finding.

## 2. Result — a two-tier separation in MS

Antibody tier (5 drugs) against the other six disease-modifying drugs, scores
from the MS k = 1 screen:

| Score | Antibody mean | Other mean | AUC | *p* (exact-ish, one-sided) |
|---|---|---|---|---|
| **`signed_reversal`** | 0.0410 | 0.0289 | **1.00** | **0.002** |
| `reversal_efficiency` | 0.519 | 0.365 | 0.87 | 0.026 |
| `gene_coverage` | 0.083 | 0.081 | 0.53 | 0.47 |
| **`priority_score`** (the composite) | 0.729 | 0.837 | **0.30** | 0.88 |

Every one of the five antibodies scores above every one of the six others on
`signed_reversal`. That is the direction real efficacy runs, and with 5 against 6
it is unlikely to be chance (1 in 462 arrangements).

Three things it does **not** say:

- **The composite gets it backwards.** `priority_score` ranks the lower-efficacy
  drugs *higher* (AUC 0.30), because it rewards low risk, low uncertainty and
  regimen convenience as well as efficacy. That is the composite doing its job as
  a prioritisation score. It also means the composite is not an efficacy
  predictor, and the leaderboards built on it should not be read as one.
- **It is not independent of how the inputs were made.** `gene_coverage` does not
  separate the two groups (0.083 against 0.081), so the difference comes from the
  *magnitudes* of the curated `target_effects`. Those magnitudes were written by
  someone who knew which of these drugs are potent. The most likely explanation
  for the separation is that curation encoded potency, and the screen recovered
  it. The test cannot distinguish that from the model capturing real biology.
- **Within a tier it says almost nothing.** Among four oral agents the rank
  correlation is 0.63, at n = 4 and with siponimod's interval reaching zero.
  Ozanimod scores slightly above ponesimod (0.0218 against 0.0201), the same order
  as their ratios (0.43 against 0.47), by a margin too small to mean anything.

Also worth knowing: on this score the panel's top monotherapy is
**methylprednisolone**, an acute-relapse steroid with no disease-modifying claim,
and interferon beta-1a ranks above fingolimod. I did not verify either against a
source, so treat those as prompts to check, not findings.

## 2b. Guillain-Barré: a second, smaller check, with a negative result

Guillain-Barré has few randomised trials but several clear outcomes, so the same
question was put to it with a coarse two-group split (`python -m tools.calibrate_gbs_efficacy`,
which lists the sources). Three agents worked (tanruprubart in a positive phase 3, and
plasma exchange and IVIG as the established standard of care) and three did not
(methylprednisolone in a 242-patient trial, interferon beta-1a as an add-on, and
fingolimod in CIDP, a related disease).

On `signed_reversal` the effective group scores higher (AUC **0.89**) but the exact
permutation *p* is **0.100**, so with three against three it is not evidence of
separation. The cause is specific: **methylprednisolone scores 5.06%, between plasma
exchange (5.10%) and IVIG (4.98%)**, so the score cannot tell a steroid that a trial
found ineffective from the two established therapies. Its cytokine effects were
curated broadly, knowing what a steroid does to cytokine transcripts, which is the same
circularity as in MS.

There is also an external *combination* check, and the screen fails it. The top
approved-only pair is IVIG + plasma exchange (8.80% against 5.10% and 4.98%), and a
383-patient randomised trial of exactly that pairing found the two therapies equally
effective with **no significant advantage from combining them**
([Lancet 1997](https://pubmed.ncbi.nlm.nih.gov/9014908/)). A higher reversal for a pair
did not translate into a better outcome.

Taken with the MS result, the supportable statement is narrow: the score can rank a
clearly stronger tier of agents above a weaker one where curation did not decide the
outcome, cannot separate a null agent from an effective one when both move many
transcripts, and does not predict combination benefit.

## 3. Why no numeric mapping

With two tiers there is no honest curve. Approximate the antibody tier at a 66–72%
ARR reduction and the S1P modulators at 53–57%: a difference of about 15
percentage points corresponds to about 2 points of `signed_reversal`. Extrapolate
that line to a triple at 15% reversal and it predicts a reduction well over 100%.
Efficacy saturates and the score does not, so a linear calibration breaks at
exactly the values the combinations reach.

## 4. What would make a real efficacy estimate possible

1. **Verified effects for at least 15–20 agents on one scale**, per disease — a
   common-scale meta-analysis with per-drug values, not tiers.
2. **Independence from curation.** Re-derive `target_effects` blind to efficacy
   (from measured binding or perturbation data), or the score can only ever echo
   what was put in.
3. **Held-out validation.** Fit on some agents, predict others, and report the
   error. A fit assessed on the drugs it was fitted to means nothing at these
   sample sizes.
4. **A model of saturation.** A bounded link between reversal and effect, not a
   straight line.
5. **For combinations and designed molecules**, evidence that the mapping holds
   *outside* the approved single agents it was fitted to. Nothing here provides
   that, and combinations are precisely where the effect is being extrapolated.

Until then, the supportable statements are the ones in each screen's protocol:
the ordering carries information, the magnitude does not, and the mechanism
strata are the unit of inference.
