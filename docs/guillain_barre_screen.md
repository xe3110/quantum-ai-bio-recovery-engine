# Guillain-Barré syndrome combination screen — protocol and results

A deterministic, multi-parameter, discovery-stage screen over a curated panel of
**16 Guillain-Barré candidates** scored at **three orders** — 16 monotherapies,
120 pairs, 518 triples — against a **78-gene directional disease signature** and a
**cached STRING v12 interactome**.

It is **not** a clinical combination recommendation. Guillain-Barré is an acute
disease in which treatment has to start within about two weeks of onset, patients
may need ventilation, and the two established therapies are a biologic and a
procedure. No in-silico score prices timing, ventilator risk, or the cost of a
relapse after treatment. Every output is a hypothesis for experimental validation.

The standing procedure this run instantiates is in the
[disease campaign protocol](disease_campaign_protocol.md). **This document states
only what is specific to Guillain-Barré.** The companion screens are
[multiple sclerosis](ms_publication_protocol.md), [Parkinson's](parkinsons_screen.md),
[Alzheimer's](alzheimers_screen.md) and [epilepsy](epilepsy_screen.md); the campaign
that designs a molecule is [here](denovo_design_protocol.md#guillain-barré-syndrome).

```bash
python -u -m experiments.guillain_barre.run_combination_screen --top 25 --seed 7   # seconds
pytest -q tests/test_combination_scoring.py tests/test_multi_disease.py
python -m tools.calibrate_gbs_efficacy
```

---

## 1. What is different about this disease

| | earlier diseases | Guillain-Barré |
|---|---|---|
| Target tissue | central nervous system | **peripheral nerve and root** |
| CNS gate | on (`requires_cns_exposure: true`) | **off — the first disease to switch it off** |
| Established treatments | small molecules | **a biologic (IVIG) and a procedure (plasma exchange)** |
| Panel size | 35 to 74 agents | **16 agents** |
| Reference set of known structures | 23 to 42 | **7** |
| Heaviest risk | ARIA, teratogenicity, dyskinesia | **respiratory depression** |

**The peripheral branch was run for the first time.** With the CNS gate off, the
design profile uses a general oral property envelope (MW 250–500, no CNS floor) and
the combination scorer's compartment term is scored as *spread*, the term written
for MS. I have not checked that spread means anything in a disease where every
effective agent acts peripherally, so that term should be treated as unvalidated
here.

**The panel is short on purpose.** Few agents have a randomised trial in the
disease, and padding the panel with agents that were never tested in it would add
ranked names and no information. What is in it was checked against sources (§5).
That also means fewer than 600 combinations, so stability figures are not comparable
with the other diseases (§4).

**Most of what works is not chemistry.** Immunoglobulin, plasma exchange and the
antibody candidates act on proteins (C1q, C5, IgG, FcRn), not transcripts, and are
scored through downstream proxy genes. Nine of the sixteen agents have no
small-molecule structure, so the novelty reference set is only 7 structures and a
novelty figure here means less than in any other disease.

## 2. Inputs specific to Guillain-Barré

- **`data/gbs_expression.csv`** — 78 genes across 12 pathways.

  > **This signature is weaker evidence than the MS entry's.** It is curated from
  > literature knowledge rather than derived from a cohort, and it mixes the
  > demyelinating form (AIDP) with the axonal forms (AMAN, AMSAN), which a real study
  > would separate. The signature also comes from nerve and blood biology that is
  > hard to sample in an acute disease.

- **`data/drugs/guillain_barre_panel_v1.json`** — 16 records from
  `python -m tools.curate_gbs_panel`, which fails on any target gene absent from the
  signature. 7 approved, 4 phase 3, 5 phase 2; 14 mechanism classes; 32 of 78 genes
  targeted.

- **`data/networks/string_gbs_network.tsv`** — STRING v12, confidence ≥ 0.4, 226
  nodes, 11,062 edges. **Three signature genes are absent, for different reasons**:
  `IGHG1` and `MPZ` because STRING v12 does not recognise the symbols (a direct
  lookup returns "not found"), and `VEGFA` because STRING resolves that symbol to a
  different protein (`COL18A1`). No alias is declared, since aliasing `VEGFA` to
  `COL18A1` would be wrong. All three contribute to signature reversal and not to
  network proximity. Discovering this is what showed that the epilepsy network's
  missing `AQP4` had the same cause, and not the one I had first recorded.

- **Vocabulary** — seven therapeutic axes (`complement_inhibition`,
  `antibody_clearance`, `fc_receptor_modulation`, `cytokine_immune_modulation`,
  `conduction_restoration`, `neuropathic_pain_relief`, `nerve_repair_promotion`) and
  eight risk domains (`thromboembolic_events`, `renal_injury`,
  `meningococcal_infection`, `immune_haemolysis`, `treatment_related_fluctuation`,
  `respiratory_depression`, `cardiac`, `hepatic`). No axis is shared with any other
  disease, and only `cardiac` and `hepatic` overlap among risk domains.

  Respiratory depression carries the highest weight because the disease weakens the
  respiratory muscles, so a sedating pain drug can tip a patient into failure.
  Thromboembolism and meningococcal infection follow.

- **`nerve_repair_promotion` has no agent in the panel.** It is the axis with a gap
  of exactly 1.00, and because nothing in the panel sits on it the screen cannot
  rank anything there. That is the limit of a panel-bounded screen, stated as sharply
  as it has been stated for any disease.

## 3. Results — monotherapy versus combination

Compared on the efficacy block only. `priority_score` is **not** in this table and
must not be: it includes complementarity and separation terms a single agent cannot
earn by construction (see the [rule](disease_campaign_protocol.md#comparing-across-orders--the-rule)).

| order | n | median reversal | max reversal | % beating best monotherapy | max gain | % sub-additive |
|---|---|---|---|---|---|---|
| 1 | 16 | 0.0207 | 0.0806 | — | — | 0% |
| 2 | 117 | 0.0576 | 0.1313 | 17.9% | +0.0507 | 25.6% |
| 3 | 518 | 0.0785 | 0.1672 | 44.6% | +0.0866 | 56.0% |

3 of 120 pairs were excluded as redundant (gabapentin + pregabalin, carbamazepine +
amitriptyline, IVIG + its second course). Triples containing an excluded pair were
not enumerated, so 518 of a possible 560 were scored. No monotherapy has *q* < 0.05;
the best, tanruprubart, has *q* = 0.060.

### Efficacy as percentages

`signed_reversal` is the share of the signature's weight moved in the therapeutic
direction. It is **not** a clinical effect.

| | best reversal | regimen |
|---|---|---|
| Single agent | **8.06%** | tanruprubart (C1q antibody; positive phase 3) |
| Pair | **13.13%** | tanruprubart + methylprednisolone |
| Triple | **16.72%** | IVIG + tanruprubart + methylprednisolone |

The best pair and triple both contain **methylprednisolone**, which a 242-patient
randomised trial found no better than placebo. It is the third-highest single agent
by reversal (5.06%), level with plasma exchange (5.10%) and above IVIG (4.98%). The
**IVIG second course** appears in an identical triple because the panel records it
with the same target effects as IVIG, since it is the same drug. Removing agents that
have a null randomised trial (methylprednisolone, interferon beta-1a, fingolimod, and
the second IVIG course):

| | best reversal | regimen | *q* |
|---|---|---|---|
| Pair | **12.02%** | IVIG + tanruprubart | 0.018 |
| Pair | 11.77% | plasma exchange + tanruprubart | 0.021 |
| Pair | 10.21% | efgartigimod + tanruprubart (lowest safety burden, 0.075) | 0.014 |
| Triple | 14.83% | IVIG + plasma exchange + tanruprubart | 0.015 |

Restricted to **approved** agents, the best single is plasma exchange (5.10%), the best
pair is IVIG + plasma exchange (8.80%), and the best triple adds carbamazepine
(10.23%).

**As a share of what the panel could reach** ([tools/reversal_ceiling.py](../tools/reversal_ceiling.py)):
32 of 78 genes are targeted, a full-reversal ceiling of 46.9% and a pooled-panel
ceiling of 29.8%. The best single, pair and triple are 17.2%, 28.0% and 35.6% of the
full ceiling and 27.0%, 44.0% and 56.0% of the pooled-panel one, the highest capture
of any disease. That is not a finding about Guillain-Barré. It reflects a tiny panel
of broad-acting agents that engage many cytokine and complement genes, so the same
number would look lower against a larger panel. It is a normalisation for comparing
diseases, not a clinical calibration.

### Three readings that matter more than the leaderboard

**1. Third agents rarely earn their place.** Of 518 triples, **410 (79.2%)** have a
negative `score_gain_over_best_subset`, with a median gain of **−0.0857**, close to
epilepsy's 83.4% and far from Alzheimer's and MS (about a third). Guillain-Barré is
treated with one established therapy, and I have not tested whether this reflects
that or only the risk arithmetic: several heavily weighted safety domains compound
when a third agent is added.

**2. Redundancy is moderate.** 25.6% of pairs and 56.0% of triples are sub-additive.
The complement, Fc-receptor and antibody-clearance agents all move overlapping sets of
genes (`C3`, `C1QA`, `IGHG1`), so combining them adds less than their reversals sum to.

**3. The best approved-only pair is a combination a randomised trial refuted.** The
screen's top approved-only pair is **IVIG + plasma exchange**, at 8.80% reversal
against 5.10% and 4.98% for the two singles. That exact comparison was run: a
383-patient randomised trial of plasma exchange, IVIG, and plasma exchange followed
by IVIG found the two therapies **equally effective and the combination without a
significant advantage** ([Plasma Exchange/Sandoglobulin GBS Trial Group, *Lancet*
1997](https://pubmed.ncbi.nlm.nih.gov/9014908/)). The screen therefore predicts a
gain that a trial found does not materialise, which is the clearest single external
check available for this method, and it fails it. Signature reversal adds up across
mechanisms; clinical benefit saturates.

## 4. Mechanism strata

**The unit of inference is the mechanism stratum, not the named combination.**
Bootstrap top-25 Jaccard is **0.598 at order 2** and **0.360 at order 3**, and the
runner prints its instability warning only at order 3. **These are not comparable
with the other diseases.** The top 25 of 117 pairs is 21% of the space, against under
1% in the larger screens, so overlap is far easier to achieve here. Weight
sensitivity is high (Spearman 0.965 / 0.959, minimums 0.91 and 0.86).

Top and bottom strata at order 2:

| axis stratum | n | median | 95% CI | q |
|---|---|---|---|---|
| complement_inhibition + neuropathic_pain_relief | 24 | 1.208 | [1.144, 1.330] | ~0 |
| complement_inhibition + conduction_restoration | 6 | 1.190 | [1.102, 1.346] | 0.0076 |
| antibody_clearance + neuropathic_pain_relief | 20 | 1.187 | [1.085, 1.301] | 0.0001 |
| fc_receptor_modulation + neuropathic_pain_relief | 12 | 1.170 | [1.062, 1.315] | 0.0047 |
| … | | | | |
| antibody_clearance + antibody_clearance | 9 | 0.768 | [0.639, 0.935] | 1 |
| **antibody_clearance + fc_receptor_modulation** | 8 | **0.765** | [0.634, 0.922] | 1 |

**Every one of the top six strata contains a symptomatic axis** (`neuropathic_pain_relief`
or `conduction_restoration`), and pain is the axis the gap analysis scores as fully
served. The strongest strata therefore pair an immune axis with the served symptomatic
one, as the cholinergic axis did in Alzheimer's, while the axis with the largest gap
(`nerve_repair_promotion`) cannot appear because it has no agent. The two approved
disease-specific therapies' axes (`antibody_clearance`, `fc_receptor_modulation`) form
the bottom strata. I read this as a property of how the composite treats cheap,
low-risk symptomatic agents, not as evidence about disease modification.

## 5. Controls, declared before ranking

Each was checked against a source; see [the calibration tool](../tools/calibrate_gbs_efficacy.py)
for the links.

| Control | Members | Result |
|---|---|---|
| Positive redundancy | Gabapentin + Pregabalin | **Excluded as expected** |
| Safety penalty | Eculizumab (63), IVIG second course (42) | **Neither reaches the top 25** |
| Negative efficacy | Methylprednisolone (**14**), Fingolimod (**16**), Interferon beta-1a (85) | **Two of three reach the top 25** |

Ranks are the best position in the pooled primary ranking of orders 2 and 3. With only
about 635 ranked rows the top 25 is 4% of them.

Unlike epilepsy and Alzheimer's, **the safety controls hold up**, at every order:
eculizumab is 10th of 16 monotherapies, 19th of 117 pairs and 48th of 518 triples, and
the second IVIG course 9th, 20th and 29th. I do not think the scorer prices toxicity
better here than it did for tacrine or vigabatrin. The likelier reason is that these two
are not the narrowest agents: eculizumab's reversal efficiency is 0.66 and the second
IVIG course's is 0.31, so neither gets the efficiency advantage that put vigabatrin
first in epilepsy. I would not read the controls passing as evidence that the safety
term works.

**The negative-efficacy result is the known limitation, reported not filtered.**
Methylprednisolone (no benefit in a 242-patient trial) and fingolimod (which failed in
CIDP, a related disease) reach the top 25, on the same mechanistic-coherence grounds as
before. **The composite also again favours narrow agents**: the top monotherapies are
pregabalin and gabapentin (reversal 1.2% and 1.1%, efficiency 0.80 and 0.70), ahead of
tanruprubart (8.06%), and dalfampridine (reversal 0.52%) is fourth. It does not cost a
safety control this time, but it means `priority_score` is not an efficacy ranking
here either.

### Does the score separate what worked from what did not?

Six agents have a sourced trial outcome: three that worked (tanruprubart, plasma
exchange, IVIG) and three that did not (methylprednisolone, interferon beta-1a,
fingolimod in CIDP). On `signed_reversal` the effective group scores higher
(AUC **0.89**), but with three against three the exact permutation *p* is **0.100**,
so this is not evidence of separation. The reason for the shortfall is specific:
methylprednisolone scores 5.06%, between plasma exchange (5.10%) and IVIG (4.98%), so
the score cannot tell an ineffective steroid from the two established therapies. I
curated the steroid's cytokine effects broadly, knowing what it does to cytokine
transcripts, which is the circularity flagged in
[the calibration write-up](efficacy_calibration.md).

## 6. Where this screen ends and design begins

The design campaign runs over the same model. Its axis-gap analysis, from the panel's
*approved* agents:

| therapeutic axis | unmet fraction |
|---|---|
| neuropathic_pain_relief | 0.00 |
| complement_inhibition | 0.50 |
| antibody_clearance | 0.50 |
| fc_receptor_modulation | 0.75 |
| cytokine_immune_modulation | 0.75 |
| conduction_restoration | 0.75 |
| **nerve_repair_promotion** | **1.00** |

The design results are in [the design protocol](denovo_design_protocol.md#guillain-barré-syndrome).

## 7. The better combination, and the new molecule

**Combination.** After removing agents with a null trial, the model's best pair is
**IVIG + tanruprubart** (12.02% reversal, *q* = 0.018), with **efgartigimod +
tanruprubart** the lowest-burden alternative (10.21%, safety union 0.075). No triple
clearly earns its place: the best (IVIG + plasma exchange + tanruprubart, 14.83%) gains
only +0.017 over its best pair, and it contains the IVIG + plasma exchange pairing that
a randomised trial found no better than either alone. **I would not call any of these a
recommendation.** Every leading pair depends on tanruprubart, and I did not establish whether its phase 3
permitted concurrent IVIG or tested it as an add-on, so the pairing is untested as far
as I know, and the score has just failed the one external combination check available.

**New molecule.** The leading design is a **4-aminopyridine arm fused to an
MMP9-inhibiting hydroxamic acid** (`C12H15N5O2`, MW 261.3, cLogP 0.79, TPSA 92.1),
reversing **4.04%** of the signature with reversal efficiency 0.53, about half of
tanruprubart's 8.06%. It has never been made, docked or assayed. It addresses
conduction and blood-nerve-barrier protection, not the largest gap, and it is not a
substitute for a complement or IgG-targeting agent, because the disease's centre of
gravity is not a small-molecule target.

## 8. Reproduce

```bash
python -m tools.curate_gbs_panel                                  # regenerate + validate the panel
python -m tools.fetch_string_network --signature data/gbs_expression.csv \
    --out data/networks/string_gbs_network.tsv                    # optional; cached copy is committed
python -u -m experiments.guillain_barre.run_combination_screen --top 25 --seed 7
python -m tools.calibrate_gbs_efficacy
pytest -q tests/
```

Outputs land in `experiments/guillain_barre/results/`: `gbs_combination_screen.json`
and `gbs_combinations_full.csv` (654 rows).

## 9. Known limitations specific to Guillain-Barré

The [standing limitations](disease_campaign_protocol.md#7-standing-limitations-of-every-campaign)
apply. What is different here:

- **The best-evidenced agents are scored through proxies.** Immunoglobulin, plasma
  exchange and the antibodies act on proteins, so the result for them is the least
  reliable in the screen, and they are the agents that matter.
- **The score failed an external combination check** (§3, reading 3), and does not
  separate a null steroid from the established therapies (§5).
- **The panel is 16 agents**, so strata are small (5 to 27 combinations) and the
  stability figures are not comparable with the other diseases (§4).
- **The compartment term is unvalidated** for a peripheral disease (§1).
- **Timing is not modelled.** Treatment works if started within about two weeks, and a
  screen that ranks regimens without a time axis cannot say when to give them.
- **The signature mixes AIDP and axonal forms**, whose complement biology differs.
- **No pharmacokinetic or interaction model**, which matters for sedating agents in
  patients with failing respiratory muscles.
- **`nerve_repair_promotion` is invisible to the screen** (§2).
- **Novelty numbers are weak.** The reference set is 7 structures (§1).

## 10. Required validation before publication

1. Stratify by subtype (AIDP, AMAN, AMSAN, Miller Fisher) and by anti-ganglioside
   antibody status before any signature is built.
2. Replace the signature with discovery and validation cohorts.
3. Re-derive `target_effects` from measured pharmacology, and give protein-level agents
   a scoring path that does not run through a transcript proxy.
4. **Test the IVIG + tanruprubart pairing directly**, not the PE + IVIG one that has
   already been refuted.
5. Add a time axis and a max-domain safety term, and evaluate both on all five
   diseases together.
6. Test in patient-derived peripheral nerve or Schwann-cell systems, and validate in
   experimental autoimmune neuritis, an appropriate model of the disease.
7. Release code, frozen inputs, seed, full rankings including excluded combinations, and
   the control analysis.

## Where quantum computing is and is not used

**Not used: the combination screen.** The k = 1, 2, 3 screen (16 monotherapies, 120 pairs, 518 triples) is classical.

*Why.* (1) The screen enumerates every combination exhaustively, so the answer is exact
and there is no search problem for a quantum heuristic to help with; the whole screen finishes in seconds.
(2) The expensive part is statistical scoring (the permutation null, bootstrap stability,
weight sensitivity), which is classical and has no quantum counterpart here. (3) The
drug-selection problem can be written as a QUBO (the project does this, see below), but at
this size exact enumeration is faster and gives the true optimum, so there is nothing for
a quantum solver to improve on. Quantum optimisation could matter for much larger
selections (many agents, high order); none of the panels here is in that regime.

**Used, as a benchmark only: the design campaign's fragment selection.** The 10-variable arm-selection QUBO gives +0.1113 on all three solvers; the depth sweep is d1 +0.1025, then +0.1113 at depths 2 to 5.
Enumeration finishes in about 0.07 s; the QAOA depth sweep takes 5 to 6 s. The arm sets
carried into molecule assembly come from **enumeration**, not from QAOA, and QAOA's output
is not used downstream.

*Why only a benchmark.* At 10 binary variables there are 1,024 states, which exhaustive
search covers instantly, so no quantum advantage can be demonstrated or is expected. The
benchmark checks that the Hamiltonian formulation is faithful and transfers to a quantum
algorithm, and that is all it shows.

**Used for higher-order regimen selection (k = 4 to 6), as a benchmark against ground truth.**
The k = 1, 2, 3 screen above stops at k = 3 because it scores every combination. The project's
Hamiltonian machinery has since been pointed at the question beyond it, which k agents from a
pool, written as a QUBO and solved by enumeration, the exact eigensolver, QAOA (penalty and
constraint-preserving variants) and classical baselines. Every answer is re-scored with the true
scorer and ranked against all feasible subsets. It runs on a classical simulator, so no advantage
can be shown. For this disease the pool is the whole 16-agent panel. The pairwise surrogate tracks the true score well (Spearman about 0.9) but its optimum's true rank falls with k (2nd of 1,820 at k = 4, 13th of 4,368 at k = 5, 54th of 8,008 at k = 6); the penalty QAOA ranked in the hundreds, worse than random; the constraint-preserving QAOA recovered the surrogate optimum at k = 4 and 6 and CVaR at all three; and greedy and annealing reached it in milliseconds. Method, caveats and the full tables are in
[the regimen-selection document](quantum_regimen_selection.md).

**Never used: real quantum hardware, and molecule assembly.** QAOA ran on a classical
simulator (Qiskit Aer) A pipeline for running on IBM hardware now exists ([ibm_quantum_hardware.md](ibm_quantum_hardware.md)), but no hardware run has been made,, and the assembly step that builds the new structures is a classical
stochastic search. None of the findings in this document depends on the quantum solvers: the regimens it reports come from exhaustive classical scoring, and the quantum solvers are judged on whether they recover them.

## 11. Key references

- Menche J, et al. *Science* (2015), disease-module separation, PMID: 25700523.
- Cheng F, et al. *Nat Commun* (2019), network-based combination prediction, PMID: 31000720.
- Szklarczyk D, et al. *Nucleic Acids Res* (2023), STRING v12, PMID: 36370105.
- Zheng S, et al. *Nucleic Acids Res* (2021), DrugComb, PMCID: PMC8218202.
- Plasma Exchange/Sandoglobulin Guillain-Barré Syndrome Trial Group. *Lancet* (1997),
  PMID: 9014908.
