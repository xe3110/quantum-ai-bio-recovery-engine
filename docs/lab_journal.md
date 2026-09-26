# Quantum Bio Recovery Engine — Lab Journal

**Researcher:** Rishabh Kumar

**Project:** Quantum Bio Recovery Engine

**Focus:** Hybrid biological–probabilistic–combinatorial–quantum optimization for therapeutic combination discovery

**Start Date:** 2026-01-16 (Foundation Phase, Days 1-9)

**Last updated:** 2026-09-27 (Phase 9)

---

## Project Vision

To design a reproducible, extensible research platform that models disease biology as a networked system, simulates pharmacological perturbations, formulates therapeutic combination discovery as a Hamiltonian (QUBO) optimization problem, and benchmarks exact, heuristic, and quantum-ready solvers across combinatorial scaling regimes.

Long-term goal: enable hybrid quantum–classical approaches for exploring high-order therapeutic combination spaces where classical exact solvers become computationally impractical.

---

## Day 1 — Foundation & Architecture

### Objectives

* Define a full-stack conceptual pipeline for quantum-assisted drug discovery
* Establish research framing and reproducibility mindset
* Create a lab-style workflow and logging structure

### Conceptual Pipeline

```
Disease / Protein Set
        ↓
Protein Interaction Network (Healthy vs Diseased)
        ↓
Drug Input (SMILES / Known Compounds)
        ↓
Classical Docking & Pre-Filtering
        ↓
Quantum Optimization Layer
        ↓
Systems-Level Network Simulation
        ↓
Bayesian Probability Engine
        ↓
Therapeutic Success & Risk Scores
```

### Notes

* The system is designed to treat biological recovery as a **network perturbation problem** rather than a single-target optimization.
* Optimization layer framed as a **Hamiltonian minimization / QUBO maximization** task, allowing future deployment on quantum hardware.

### Reflection

> Established a hybrid architecture integrating biological modeling, probabilistic inference, and Hamiltonian-based optimization. The system is framed as a reproducible research platform rather than a black-box predictor, enabling benchmarking across classical, heuristic, and quantum solvers.

---

## Day 2 — Disease Network Construction

### Objectives

* Build a protein–protein interaction (PPI) network for a reference disease system (Multiple Sclerosis)
* Validate biological plausibility and pipeline integrity

### Implementation

* Used curated protein set related to immune signaling and myelin biology
* Queried interaction confidence scores from external biological knowledge base (STRING-style model)
* Constructed a weighted graph representation

### Results

**Network Summary:**

* Nodes: 10
* Edges: 35

**Sample Interactions:**

```
IFNG ↔ MBP | confidence=0.667
IFNG ↔ VCAM1 | confidence=0.748
IFNG ↔ MOG | confidence=0.823
IFNG ↔ HLA-DRB1 | confidence=0.830
IFNG ↔ STAT3 | confidence=0.907
IFNG ↔ CD40 | confidence=0.927
IFNG ↔ CXCL10 | confidence=0.959
IFNG ↔ IL2RA | confidence=0.967
IFNG ↔ TNF | confidence=0.991
MBP ↔ HLA-DRB1 | confidence=0.851
```

### Observations

* IFNG emerges as a dominant hub, consistent with immune-centric MS pathology
* Network density validates system coherence and biological relevance

### Reflection

> Successfully constructed a high-confidence MS PPI network and validated hub dominance of IFNG, aligning with known immune-mediated disease mechanisms. This reference network serves as the baseline system state for downstream perturbation and optimization experiments.

---

## Day 3 — Disease Distance Metric

### Objectives

* Define a quantitative measure of system deviation between healthy and perturbed network states

### Metric

**System Disease Distance Score**

* Measures aggregate edge-weight deviation under simulated perturbations
* Interpreted as network-level biological stress

### Sample Outputs

```
System Disease Distance Score: 0.1221
System Disease Distance Score: 1.2708
```

### Interpretation

* Low score → near-baseline state
* High score → strongly perturbed / diseased system

### Reflection

> Introduced a network-level scalar metric capturing global biological deviation, enabling consistent downstream mapping between drug perturbations and system recovery potential.

---

## Day 4 — Drug Recovery Scoring

### Objectives

* Simulate pharmacological perturbations
* Map drug effects onto network recovery space

### Example

**Drug:** Fingolimod
**Recovery Score:** 0.4451

### Interpretation

* Recovery score represents estimated normalization of network topology relative to disease state

### Reflection

> Established a functional mapping from drug perturbations to network recovery metrics, enabling formal comparison between pharmacological candidates.

---

## Day 5 — Probabilistic Modeling

### Objectives

* Convert recovery scores into interpretable success probabilities

### Bayesian Output

```
Probability of Therapeutic Success:
Mean: 0.412
95% CI: (0.255, 0.579)
```

### Notes

* Enables uncertainty-aware ranking of drugs
* Provides statistical framing rather than deterministic scoring

### Reflection

> Added probabilistic interpretation layer, enabling uncertainty quantification and confidence intervals for therapeutic success estimates.

---

## Day 6 — Drug Panel Screening

### Objectives

* Screen multiple drugs under unified probabilistic and recovery framework

### Results

```
=== MS Drug Screening Results ===
1. Fingolimod           | Recovery: 0.629 | P(Success): 0.667 [0.537, 0.785]
2. Dimethyl Fumarate  | Recovery: 0.380 | P(Success): 0.463 [0.333, 0.596]
3. Natalizumab        | Recovery: 0.237 | P(Success): 0.185 [0.094, 0.298]
4. Interferon-beta   | Recovery: 0.166 | P(Success): 0.130 [0.055, 0.230]
```

### Reflection

> Demonstrated rank consistency between network recovery and probabilistic success estimates, validating internal coherence of the modeling stack.

---

## Day 7 — Synergy Discovery

### Objectives

* Identify combinatorial effects between drug pairs

### Results

```
=== MS Combination Synergy Results ===
1. Fingolimod + Dimethyl Fumarate | Recovery: 0.881 | Synergy: 0.252 | P(Success): 0.87
2. Fingolimod + Natalizumab      | Recovery: 0.785 | Synergy: 0.156 | P(Success): 0.704
3. Dimethyl Fumarate + Natalizumab | Recovery: 0.617 | Synergy: 0.237 | P(Success): 0.537
```

### Interpretation

* Synergy metric captures non-linear improvement beyond additive recovery

### Reflection

> Identified dominant therapeutic synergies and established a formal combinatorial scoring framework for drug pair selection.

---

## Day 8 — Hamiltonian Formulation & Optimization

### Objectives

* Encode drug selection as a constrained optimization problem
* Validate Hamiltonian formulation

### Formulation

**Objective:**

Maximize:

```
Σ recovery[i] * x_i + Σ synergy[i][j] * x_i * x_j
```

Subject to:

```
Σ x_i = k
```

### Implementation

* Encoded as QUBO / QuadraticProgram
* Solved using exact minimum eigensolver (NumPy baseline)

### Result

```
Selected drugs:
- Fingolimod
- Dimethyl Fumarate
Objective value: 1.261
```

### Reflection

> Validated Hamiltonian formulation by independently rediscovering the same optimal combination identified by network and synergy layers, confirming cross-layer consistency.

---

## Day 9 — Scaling Benchmarks (k = 3)

### Objectives

* Benchmark optimization hardness
* Compare exact, greedy, and random solvers

### Results

| N  | Exact | Greedy | Random |
| -- | ----- | ------ | ------ |
| 4  | 3.158 | 3.158  | 3.158  |
| 6  | 3.180 | 3.180  | 3.180  |
| 8  | 3.118 | 3.118  | 3.118  |
| 10 | 3.634 | 3.634  | 3.634  |
| 12 | 3.842 | 3.575  | 3.842  |

### Interpretation

* Onset of heuristic failure observed at N ≥ 12
* Greedy solver trapped in local optimum

### Reflection

> Identified transition from polynomially tractable to combinatorially hard regime for k=3 selection, validating need for advanced optimization strategies.

---

## Day 9 — Scaling Benchmarks (k = 4)

### Results

| N  | Exact Time (s) | Exact Value | Greedy Value | Random Value |
| -- | -------------- | ----------- | ------------ | ------------ |
| 8  | 0.0064         | 5.188       | 5.188        | 5.188        |
| 12 | 0.0095         | 5.118       | 5.118        | 4.998        |
| 16 | 0.0260         | 5.065       | 5.065        | 5.034        |
| 20 | 0.1879         | 5.226       | 5.143        | 5.033        |
| 24 | 3.3665         | 5.520       | 5.494        | 5.124        |

### Observations

* Exact solver runtime increased by >500× from N=8 to N=24
* Greedy and random solvers remained constant-time but showed growing optimality gaps

### Reflection

> Demonstrated combinatorial scaling behavior and identified a computational regime where classical exact solvers become impractical and heuristics sacrifice solution quality, motivating hybrid quantum–classical optimization strategies.

---

## Public Release

### Repository

* Name: `quantum-bio-recovery-engine`
* Status: Public

### Research Layer Added

* README.md (scientific front door)
* MIT License
* CITATION.cff
* Curated requirements.txt
* One-command `setup.sh`
* Figures and reproducibility instructions

### Reflection

> Released the full research platform as a public, reproducible repository with experimental logs, figures, and setup automation, establishing academic-grade transparency and collaboration readiness.

---

---

# Phase 2 — Publication-Grade MS Combination Screen

*Entries below are date-stamped. The foundation phase above (Days 1–9) was
committed on **2026-01-16**; the work in this phase was carried out on
**2026-08-25**.*

---

## 2026-08-25 — Session A: Conservative re-scoping of the MS screen (v2)

### Motivation

The Day 6–8 screen ranked 4 drugs and reported "P(Success)" values to three
decimals. Those numbers were not calibrated against anything, and the synergy
metric treated a network-distance improvement as evidence of pharmacological
synergy. Both would fail review.

### Changes

* Rebuilt the MS workflow around an interpretable, multi-criteria
  **prioritisation score** rather than a success probability.
* Expanded the panel to **22 candidates** with explicit evidence tiers,
  mechanism classes, directional target hypotheses, and broad safety classes.
* Expanded the signature to **25 signed genes**.
* Excluded shared-mechanism and shared-safety-class pairs from the primary
  ranking, retaining them for audit.
* Added a seeded bootstrap interval over curated target-effect uncertainty.

### Reflection

> Replaced an uncalibrated probability with a transparent, auditable
> prioritisation score, and made the screen's own limitations explicit rather
> than implicit. Correct in kind, but still too small to support a publication:
> 22 candidates, 6 parameters, no significance testing, no controls.

---

## 2026-08-25 — Session B: Extension to a publishable screen (v3)

### Objectives

Scale the candidate space, broaden the evidence base beyond signature reversal,
and add the statistical apparatus a reviewer will require.

### 1. Inputs

| Input | v2 | v3 |
| --- | --- | --- |
| Candidates | 22 | **74** (55 mechanism classes) |
| Signature genes | 25 | **112** across 10 pathways |
| Scoring parameters | 6 | **20** |
| Interactome | none | STRING v12 — 261 nodes, 14,784 edges |

Evidence tiers: 24 approved · 12 phase 3 ·
28 phase 2 · 10 preclinical.

The panel is regenerated by `tools/curate_ms_panel_v3.py`, which **fails the
build** if any target gene is absent from the signature. That check caught two
curation errors on first run (an undeclared risk domain, a stray gene symbol).

### 2. Methodological decisions

**Directional signature.** Raw logFC is the wrong optimisation target for
compensatory transcripts. `HMOX1`, `SOD2`, `TREM2`, and `PDGFRA` rise in MS as a
*protective* response, so a naive "reverse the disease signature" objective
scores dimethyl fumarate — an approved therapy — as harmful. Genes are now
annotated `pathogenic` (73), `protective_deficit` (35), or `compensatory` (4),
and scoring targets the curated therapeutic direction. This annotation is the
assumption most open to challenge and is flagged as such in the protocol.

**Bliss independence replaces clipping.** Same-direction effects combine as
`a + b − ab`; opposing effects add, so antagonism is represented rather than
hidden by a hard clip.

**Double normalisation of reversal.** Absolute reversal over a 112-gene
signature spans only [0, 0.1], because any one agent engages a handful of genes.
Left uncorrected this let low-efficacy, low-risk agents win the composite on the
bonus terms alone — the first full run ranked **High-dose biotin**, a failed
phase 3 negative control, in first place. Adding `reversal_efficiency`
(therapeutic movement ÷ engaged signal) restored a comparable [0,1] scale and
fixed the face-validity failure.

**Target-family redundancy.** The efficacy/safety figure exposed
`Firategrast + Natalizumab-biosimilar` as a top Pareto point. Both block
α4-integrin, but their `mechanism_class` labels differ by modality, so the
string-equality exclusion missed them. Redundancy is now declared by explicit
`target_family` plus a target-overlap rule.

### 3. Statistical apparatus

Permutation null (400 draws/pair, size- and magnitude-preserving) → empirical
*p* → BH-FDR; a weight-free Pareto front; a ±50% weight-jitter sweep; bootstrap
resampling for score **and rank** intervals; and mechanism-stratum enrichment.

### 4. Results

**Headline — mechanism strata (the stable unit of inference):**

| axis pair | n | median score | bootstrap 95% CI | q |
| --- | --- | --- | --- | --- |
| cns innate + remyelination | 79 | 1.226 | [1.149, 1.307] | <1e-05 |
| immunomodulation + remyelination | 299 | 1.190 | [1.129, 1.274] | <1e-05 |
| cns innate + metabolic repair | 147 | 1.153 | [1.105, 1.236] | 1e-05 |
| metabolic repair + remyelination | 92 | 1.151 | [1.079, 1.284] | 9e-05 |
| neuroprotection + remyelination | 105 | 1.150 | [1.080, 1.264] | 9e-05 |
| cns innate + neuroprotection | 160 | 1.142 | [1.087, 1.224] | 0.0001 |
| cns innate + cns innate | 56 | 1.137 | [1.052, 1.237] | 0.11 |
| immunomodulation + neuroprotection | 619 | 1.135 | [1.099, 1.192] | <1e-05 |
| cns innate + immunomodulation | 421 | 1.126 | [1.088, 1.194] | 0.00015 |
| remyelination + remyelination | 17 | 1.115 | [0.947, 1.243] | 0.64 |
| immunomodulation + metabolic repair | 527 | 1.099 | [1.057, 1.162] | 1 |
| metabolic repair + neuroprotection | 185 | 1.077 | [1.037, 1.177] | 1 |
| neuroprotection + neuroprotection | 103 | 1.050 | [0.958, 1.156] | 1 |
| metabolic repair + metabolic repair | 81 | 1.038 | [0.942, 1.145] | 1 |
| immunomodulation + immunomodulation | 754 | 1.021 | [0.975, 1.054] | 1 |

**Top pairs (diversity-capped at 3 appearances per agent):**

| # | combination | score | q | separation |
| --- | --- | --- | --- | --- |
| 1 | Clemastine + Minocycline | 1.511 | 0.0083 | 0.28 |
| 2 | Minocycline + Opicinumab | 1.502 | 0.0083 | 0.28 |
| 3 | Minocycline + Ocrelizumab | 1.488 | 0.0083 | 0.22 |
| 4 | Clemastine + Ocrelizumab | 1.467 | 0.0083 | 1.00 |
| 5 | Clemastine + Ibudilast | 1.446 | 0.0083 | 0.22 |
| 6 | Opicinumab + Tolebrutinib | 1.427 | 0.0083 | 0.47 |
| 7 | Ibudilast + Ocrelizumab | 1.426 | 0.0083 | 0.22 |
| 8 | Methylprednisolone + Siponimod | 1.423 | 0.0083 | 0.05 |
| 9 | Methylprednisolone + Opicinumab | 1.422 | 0.0083 | 0.54 |
| 10 | Ibudilast + Ofatumumab | 1.413 | 0.0241 | 0.35 |

**Controls, declared before ranking:**

Redundant positive control (Natalizumab + Natalizumab-biosimilar):
excluded as expected — **True**.

| safety control | best primary rank | in top 30 |
| --- | --- | --- |
| Daclizumab | 299 | no |
| Cyclophosphamide | 317 | no |
| Mitoxantrone | 385 | no |

| negative-efficacy control | best primary rank | in top 30 |
| --- | --- | --- |
| Ustekinumab | 16 | yes |
| High-dose biotin | 13 | yes |
| Opicinumab | 2 | yes |
| Evobrutinib | 242 | no |

**Robustness:**

* Weight sensitivity: Spearman **0.9742** mean, 0.9174 min under ±50% jitter.
* Pairs at q < 0.05: **1,315 / 1,793**.
* Pareto-optimal pairs: 361 of 2,016.
* Top-30 bootstrap Jaccard: **0.2458**.

### 5. The negative result, stated plainly

**Individual pair ranks are not reliable.** Under the curated target-effect
uncertainty the top-30 bootstrap Jaccard is 0.2458, and rank
95% CIs span hundreds of positions. A leaderboard of named pairs is therefore
*not* a defensible output of this screen, and the runner prints an explicit
warning whenever that statistic falls below 0.5.

Stratum medians behave differently: their bootstrap intervals are narrow
relative to the spread between strata, and the ordering survived the
target-family redundancy fix unchanged. The defensible finding is therefore the
**ordering of mechanism combinations**, not any specific pair.

Three negative-efficacy controls (Opicinumab, High-dose biotin, Ustekinumab)
still rank inside the top 30.
This is reported rather than filtered: the screen scores mechanism and
transcriptional direction, not trial outcome, and this bounds what it can claim.

### 6. Interpretation

Pairing a **CNS-innate agent with a remyelination agent** is the top-ranked
stratum (1.226), while pairing **two peripheral
immunomodulators** ranks last (1.021) despite being
the largest stratum (n=754) and the one most represented in
current practice. Every stratum pairing remyelination or CNS-innate action with
a second axis outranks every immunomodulation-only combination.

This is consistent with compartmentalised inflammation behind an intact
blood-brain barrier as the reason peripheral immunosuppression plateaus in
progressive MS. It is a hypothesis the screen was built to generate, not
evidence that it is true.

### 7. Artefacts

```
core/biology/ms_scoring.py           20-parameter pair scoring
core/biology/network_proximity.py    STRING proximity / separation
core/biology/screen_statistics.py    nulls, FDR, Pareto, stability, strata
experiments/ms/run_extended_screen.py
experiments/ms/plot_screen.py
tools/curate_ms_panel_v3.py          panel curation + validation
tools/fetch_string_network.py        cached interactome fetch
tests/                               19 tests, all passing
figures/fig_mechanism_strata.png
figures/fig_rank_stability.png
figures/fig_efficacy_safety_tradeoff.png
```

Runs are deterministic under a stated seed and carry a provenance block
recording git revision, Python/NumPy versions, platform, and the exact command.

### Reflection

> Scaled the MS screen from 22 to 74 candidates and 6 to 20
> parameters, and added the significance, robustness, and control apparatus a
> manuscript requires. The most important output was not the ranking but the
> demonstration that the ranking is unstable at the pair level — which relocated
> the claim to the mechanism stratum, where it survives bootstrap resampling, a
> ±50% weight sweep, and a redundancy fix. Two curation errors and one
> face-validity failure were caught by the validation and control machinery
> rather than by inspection, which is the argument for building it.

### Next steps

1. Replace the illustrative signature with discovery + validation cohorts,
   stratified by RRMS / active SPMS / PPMS.
2. Re-derive `target_effects` from measured pharmacology — the rank instability
   is driven by `target_uncertainty`, so this is the highest-value fix.
3. Wire the Hamiltonian/QAOA layer to the v3 scores to select higher-order
   (k > 2) combinations under the same safety and redundancy constraints.
4. Validate the top stratum in glia/oligodendrocyte co-culture with full
   dose matrices (Bliss, HSA, Loewe, ZIP).
5. Preprint.

---

---

# Phase 3 — De Novo Molecular Design

*Carried out on **2026-08-26**.*

---

## 2026-08-26 — Session A: From selecting molecules to designing one

### Motivation

Phase 2 ended with a screen that ranks pairs drawn from a fixed panel of 74
agents. That question has a ceiling built into it: **the answer can only ever
be a molecule someone has already made.** In MS every approved agent is a
peripheral immunomodulator, and the screen's own headline finding was that
peripheral-only combinations rank last. The screen could identify the gap and
could not, in principle, fill it.

So the question changed from *"which two existing agents pair best?"* to *"what
should a molecule do, and what would such a molecule look like?"*

That required three things the repository did not have: a specification of what
a single molecule must do, a chemistry layer that can represent and measure a
structure, and a generator that searches chemical space against the
specification.

### Architectural decision: build it disease-agnostic

Phase 2's vocabularies — `MS_DISEASE_PATHWAYS`, `THERAPEUTIC_AXES`,
`RISK_DOMAINS` — were module constants inside the MS scoring code. Fine for one
disease and wrong for two: adding Parkinson's would have meant editing scoring
logic. Phase 3 introduces a **disease model** (`core/models/disease.py`) loaded
from a registry entry under `data/diseases/`. Everything downstream reads the
context and never names a disease.

### 1. The chemistry model

RDKit has no wheel for the interpreter this project pins, so `core/chemistry/`
was written from scratch: SMILES **parser and writer** (a generator must emit
structures, not only read them), valence model, ring perception, Ertl TPSA,
Wildman–Crippen logP, Lipinski/Veber, Wager CNS MPO, a declared
synthetic-tractability proxy, structural alerts as readable graph predicates,
and ECFP-style circular fingerprints.

Validation state, all test-enforced:

| Quantity | Status |
| --- | --- |
| SMILES round-trip | 15-molecule corpus, composition preserved exactly |
| Formula and mass | all 42 curated structures match published values |
| TPSA | matches published Ertl values exactly |
| cLogP | reduced Crippen typing; ~0.4 MAE vs experiment |
| Stereochemistry | absent — parsed and discarded |
| Aromaticity | trusted as written, not re-perceived |

Sanity check on real MS drugs behaved correctly on first run: dimethyl fumarate
and diroximel fumarate flagged as Michael acceptors (that *is* their Nrf2
mechanism), fingolimod's primary-amine pKa found, minocycline scored low on
tractability as a complex polycyclic natural product.

### 2. The Target Product Profile

`core/design/target_profile.py` ranks candidate proteins by

```
priority = leverage x tractability x (1 - 0.5 x liability) x (1 + 0.35 x axis_gap)
```

with leverage split 60/40 between weighted signature membership and
distance-decayed influence through STRING.

**The tractability term is the single most important guard in the pipeline.**
A new annotation, `data/targets/druggability.json`, assigns each of the 93
panel targets a class and a small-molecule prior: 22 at or above 0.6, 32 below
0.2. CD20 has among the highest leverage in MS and a tractability of **0.05**.
Without the floor the engine would confidently specify a small molecule to bind
the target of ocrelizumab. Sub-floor targets are reported as **readouts** —
the profile still wants their expression to move, but no arm is pointed at
them.

**Axis-gap analysis, the campaign's most defensible output:**

| therapeutic axis | unmet fraction among approved agents |
| --- | --- |
| remyelination | **1.00** |
| neuroprotection | 0.96 |
| cns_innate | 0.92 |
| metabolic_repair | 0.88 |
| immunomodulation | **0.00** |

This is Phase 2's stratum finding restated as a specification, and derived
independently.

### 3. Fragment selection as a Hamiltonian

Choosing which pharmacophores to fuse is a constrained binary optimisation —
coverage saturates under Bliss, chemotypes duplicate, and a shared mass budget
couples every pair. That is a QUBO, solved on three backends: exhaustive
enumeration (ground truth), an exact Ising eigensolver, and QAOA on Aer.

Two approximations, both documented rather than hidden:

1. **Coverage truncation** — exact at `k=2`, second-order beyond.
2. **Budget linearisation** — whole-molecule budgets cannot be written as a
   quadratic, so each fragment is charged against a `1/k` share. Subadditivity
   makes this **conservative**: the QUBO may reject a design that would have
   fitted, and never admits one that does not. Test-enforced.

### 4. Assembly

A design is a recipe — scaffold, an arm per attachment point, a linker each,
caps on the remainder — assembled into a real molecular graph, capped, and
measured. Search is exhaustive enumeration over assemblies followed by seeded
hill-climbing, then novelty assessment and MaxMin diversity selection.

---

## 2026-08-26 — Session B: What went wrong, and what it changed

Three failures are recorded here because they are the useful part of the
session.

### Failure 1 — Coverage-only optimisation designs molecules that cannot reach the brain

The first full run selected a **statin acid plus a sulfonylurea**: excellent
profile coverage, TPSA 170–250 against an 40–80 window, MW up to 554 against a
420 ceiling. **Every** top design failed the CNS gate.

The Hamiltonian was optimising coverage while blind to the delivery constraint.
Adding a polarity penalty fixed TPSA and **just moved the failure**: the
optimiser swapped to an adamantane and a chloroarene and landed at cLogP 5.8–7.2,
failing the same gate from the other side.

The fix required the envelope to enter the Hamiltonian on **polarity, donors,
and lipophilicity at once**, plus a mass budget that reserves atoms for the
scaffold and linkers assembly adds afterwards. Handing the arms the whole
molecular-weight ceiling was why 550 Da molecules kept appearing against a
420 Da envelope.

### Failure 2 — A silent bug in the Hamiltonian, caught by a test

Quadratic couplings were stored keyed on the fragments' **ranked** order and
looked up in **sorted** order. Every coupling whose ranking disagreed with the
alphabet read back as zero. The optimiser was solving a different Hamiltonian
than the one being reported, and nothing about the output looked wrong.

It surfaced only because a test asserted the truncated objective agrees with an
independently-recomputed exact objective at `k=2`. The lookup now raises on a
missing pair rather than defaulting to zero. **All results below are post-fix.**

### Failure 3 — QAOA returned an infeasible state that scored better than the optimum

At `reps=2`, QAOA selected **four** arms where three were allowed, scoring
*above* the true optimum precisely because the extra arm was never paid for.

| reps | ansatz depth | feasible | matches optimum |
| --- | --- | --- | --- |
| 1 | 55 | yes | no |
| 2 | 87 | **no** | no |
| 3 | 119 | yes | **yes** |
| 4 | 151 | yes | no |
| 6 | 215 | yes | no |

Textbook behaviour: `reps=3` finds the optimum, and deeper circuits do *worse*
at a fixed iteration budget as the variational landscape gets harder. Every
result now carries a `feasible` flag, because reading the objective without it
inverts the conclusion. Default depth set to 3.

### A blind spot in CNS MPO, found by a failing test

A test asserting memantine should out-score a statin acid on CNS MPO failed —
and the test premise was wrong, not the implementation. **Wager's score takes
the *most basic* pKa as its ionisation term**, correctly for the basic and
neutral compounds it was derived on, and is therefore blind to acids: a small
carboxylic acid scores above 5 of 6 while being anionic at pH 7.4 and
effectively barred from the brain.

The implementation stayed faithful to Wager. A separate `acidic_centres()`
check was added and the delivery gate now consults both.

---

## 2026-08-26 — Session C: Results

> **Superseded.** The numbers in this session predate the Phase 4 bug fixes
> (three chemistry errors found by RDKit cross-validation, and per-claim
> evidence weighting). They are left as the record of what was believed at the
> time; the current results are in the Phase 4 summary.

### Backend agreement

```
Hamiltonian : 10 binary variables, 45 couplings, choose 2 (45 feasible of 1024 states)
  enumeration  match  objective=+0.0901  feasible=True  0.024s
  eigensolver  match  objective=+0.0901  feasible=True  0.022s
  qaoa         match  objective=+0.0901  feasible=True  1.313s
```

### Target profile (top 8 of 14)

| gene | class | direction | priority |
| --- | --- | --- | --- |
| MMP9 | enzyme | down | 0.7883 |
| BTK | kinase | down | 0.7665 |
| NLRP3 | enzyme | down | 0.7651 |
| NOS2 | enzyme | down | 0.7442 |
| CSF1R | kinase | down | 0.7016 |
| RORC | nuclear receptor | down | 0.6994 |
| S1PR1 | GPCR | down | 0.6505 |
| MTOR | kinase | down | 0.5450 |

32 further targets classified as readouts and excluded from binding.

### Designs

7,350 recipes attempted, 225 rejected as chemically invalid, 7,125 distinct
structures.

| # | formula | MW | cLogP | TPSA | CNS-MPO | Tanimoto to nearest known |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | C16H17ClN4O | 316.8 | 1.45 | 48.5 | 5.83 | 0.41 |
| 2 | C18H18ClFN4O | 360.8 | 2.07 | 59.0 | 5.99 | 0.34 |
| 3 | C20H20FN3O3 | 369.4 | 3.14 | 71.5 | 5.13 | 0.30 |

Top design: `N1(CCN(CC1)c2ccc(Cl)cc2)C(=O)Nc3cccnc3`

All above the CNS-MPO gate of 4.0, all inside the property envelope, all novel
at a 0.6 Tanimoto threshold.

### The negative result, stated plainly

**Under a CNS envelope, three arms do not fit.** With the mass budget correctly
reserving atoms for the scaffold and linkers, every `k=3` selection scores
negative, while `k=2` lands at TPSA 62, cLogP 2.5, 19 heavy atoms. A
CNS-penetrant three-mechanism single molecule is not reachable from this
fragment library. The tool reports that rather than emitting 550 Da molecules
that fail the gate.

### The two stages disagree, and that is informative

The arm set the Hamiltonian ranks first is **not** the arm set that assembles
into the best molecule:

| arm set | Hamiltonian objective | best assembled fitness |
| --- | --- | --- |
| BTK + CSF1R | **+0.0901** (rank 1) | 1.5439 |
| BTK + TLR4 | +0.0822 (rank 2) | 1.4919 |
| CSF1R + TLR4 | +0.0783 (rank 3) | **1.6027** |

The QUBO scores profile coverage under a linearised envelope; design fitness
adds developability, tractability, and structural alerts to a molecule that
actually exists. The covalent BTK arm carries a Michael-acceptor alert and more
mass, and pays for both only at the second stage — so the last-ranked arm set
produced the winning structure.

Caught only because the campaign carries several arm sets forward instead of
the optimum alone. Reporting "the Hamiltonian's optimum" as though it were "the
best design" would have been wrong, and the two are now reported separately
throughout.

### Interpretation

The Hamiltonian's optimum, **BTK + CSF1R**, is the pairing of the two leading
CNS-penetrant MS mechanisms — B-cell and microglial on one arm, microglial on
the other. That it was reached from a directional signature, an interactome,
and a druggability annotation, without ever being told, is the strongest
internal-consistency check available at this stage.

The top *assembled* molecule, `N1(CCN(CC1)c2ccc(Cl)cc2)C(=O)Nc3cccnc3`, is a
**dual CSF1R / TLR4 antagonist aimed at microglial activation in progressive
MS** — CNS-MPO 5.83 of 6, coordinated suppression of the microglial activation
programme (CSF1R −0.75, AIF1 −0.69, TLR4 −0.60, CD68 −0.50, downstream
TNF/IL-1β/IL-6/CCL2), and no counter-therapeutic movement at all.

Its efficacy is **unknown and untested even for binding.** Scored on the panel's
own scale it reaches a signature reversal of 0.0519 — second of 75, above the
approved-agent median of 0.0301 — but that comparison is close to circular,
because its arms were selected to maximise alignment with this very signature
while the panel agents were not. It is an internal-consistency check, not
evidence of effect.

It also serves **one axis only** (`cns_innate`), and not the one with the
largest gap: remyelination sits at an unmet fraction of 1.00 and this molecule
does nothing for it. The envelope forced that — two arms of budget, both spent
on the same axis. The molecule the profile argues for is exactly the one that
does not fit.

The defensible outputs therefore remain structural rather than chemical: the
axis-gap asymmetry, and the demonstration that a three-mechanism CNS molecule
does not fit the envelope. **Individual molecules are the least reliable thing
the campaign produces**, for the same reason pair ranks were in Phase 2 — they
sit downstream of the most uncertain inputs.

### Artefacts

```
core/chemistry/molecule.py           SMILES parser + writer, valence, assembly
core/chemistry/descriptors.py        Ertl TPSA, Crippen logP, shape, flexibility
core/chemistry/druglikeness.py       Lipinski, Veber, CNS MPO, alerts, acids
core/chemistry/fingerprint.py        circular fingerprints, novelty, diversity
core/models/disease.py               disease model + registry loader
core/design/target_profile.py        Target Product Profile derivation
core/design/pharmacophores.py        fragment library loader + validation
core/design/quantum_assembly.py      QUBO, enumeration / eigensolver / QAOA
core/design/denovo.py                assembly, scoring, search
experiments/design/run_denovo_design.py
data/diseases/multiple_sclerosis.json
data/targets/druggability.json       93 targets annotated
data/chemistry/pharmacophore_library.json   48 fragments
data/chemistry/ms_known_structures.json     42 verified structures
tests/                               142 tests, all passing
docs/denovo_design_protocol.md
```

### Reflection

> Extended the platform from selecting existing drugs to specifying and
> assembling new ones, and made the whole stack disease-agnostic in the
> process. The most valuable outputs were again negative or structural: that
> coverage-blind optimisation produces molecules that cannot reach the tissue,
> that penalising one property just moves the failure to another, and that a
> three-mechanism CNS molecule does not fit the envelope this library can
> reach. A silent Hamiltonian bug and a documented blind spot in a published
> CNS score were both caught by tests rather than by inspection, which is the
> same argument Phase 2 made for building the validation machinery.

### Next steps

1. **Dock every proposal, then assay it.** Fragment-inherited engagement is an
   assumption, not a prediction, and it is the first thing that will break.
2. Have a chemist assess synthesisability — the tractability score is a
   declared proxy, not a route.
3. Profile `kinase_aminopyrimidine_hinge` selectivity across the kinome. A
   designed multi-target ligand and an uncontrolled polypharmacology liability
   are the same molecule seen from two sides.
4. Expand the fragment library along the remyelination axis, where the profile
   reports the largest unmet gap and the library is thinnest.
5. Add ADMET: metabolic stability, hERG, CYP, and especially P-glycoprotein
   efflux, which decides many CNS programmes and is unmodelled here.
6. Populate a second disease registry entry end to end to exercise the
   generality claim rather than asserting it.

---

---

# Phase 4 — Hardening: Generality, Validation, and Provenance

*Carried out on **2026-08-26**, in response to a review that identified five
gaps. Each is recorded below with what was actually done about it, including
where the answer was "the claim was too strong" rather than "the code was
wrong".*

---

## 2026-08-26 — Session D: The review

Five gaps, all correct:

1. **"Disease-configurable", not proven disease-agnostic.** One registry entry,
   and the new layers still imported `core.biology.ms_scoring` directly.
2. **Hypothesis generation, not drug-design prediction.** No binding,
   selectivity, assay loop, or validated ADMET.
3. **Reimplementing chemistry instead of using RDKit is the highest technical
   risk.** 42 formula checks do not validate perception, logP, or fingerprints.
4. **Fragment engagement is manually inherited** with no per-claim evidence,
   confidence, or feedback.
5. **Result files treated as durable truth** rather than reproducible run
   artifacts.

Gap 1 was the sharpest: the import graph contradicted the README. A layer that
calls itself disease-agnostic while importing MS scoring is not one, whatever
its registry says.

---

## 2026-08-26 — Session E: Chemistry validated against RDKit (gap 3)

RDKit has no wheel for the pinned interpreter, but the project's second
environment is Python 3.11, where it installs cleanly. That turned gap 3 from
unanswerable into measurable.

### Architecture change

RDKit is now the **preferred backend**, used automatically wherever importable;
`core/chemistry/` is explicitly fallback infrastructure.
`core.chemistry.backend` resolves the choice, records it on every descriptor
vector, refuses to silently downgrade when RDKit is requested and absent, and
is pinned to `local` for the test suite so assertions do not depend on the
environment.

### What cross-validation measured

`tools/validate_chemistry.py` compares both implementations over curated drugs,
library fragments, and **300 generated structures** — the molecules the
pipeline actually emits, which exercise ring systems no curated set contains.

| quantity | agreement |
| --- | --- |
| **structural perception** | **388 / 388 canonical SMILES match** |
| HBD, HBA | exact everywhere |
| TPSA | exact on designs; worst case 3.53 A^2 on curated drugs |
| rotatable bonds | 0.91–1.00 exact |
| ring count | 0.91–0.98 exact |
| **cLogP** | **MAE 0.65–0.86, worst case 2.23** |
| fingerprints | Spearman 0.982; 4/565 pairs disagree at the novelty threshold |

The perception result is the one that matters and the one that was previously
unevidenced: parser and writer together preserve the molecule as RDKit
understands it, on every structure tested.

### Three real bugs, none visible to composition checks

* **Rotatable bonds were wrong on essentially every generated structure** —
  0% exact, bias **+2.75**. Only amide C–N bonds were excluded where the strict
  definition excludes any conjugated carbonyl–heteroatom bond, and assembly
  produces carbamates and anhydrides freely. Now 0.91–1.00.
* **Aromatic rings bearing exocyclic carbonyls were mistyped in cLogP by
  +3 log units** (caffeine, uracil): a purinone ring carbon typed as an
  aromatic ether rather than a carbonyl. Any purinone design would have had its
  CNS MPO badly distorted.
* **Ring perception invented a macrocycle in adamantane.**
  `networkx.cycle_basis` is a spanning-tree basis, not a minimum one, and
  returned an eight-membered ring where three six-membered rings exist. The
  tractability proxy penalises rings above seven atoms, so every
  adamantane-containing design was charged 0.35 for a macrocycle it does not
  have. Switched to `minimum_cycle_basis`.

One over-correction is recorded too: matching RDKit's *atom-centric* strict
rotatable-bond rule exactly swung the bias negative, so the bond-level rule was
kept and the residual disagreement documented rather than chased. Chasing exact
parity with a reference implementation is a poor use of effort once the
reference itself is available — the right answer was to prefer RDKit.

---

## 2026-08-26 — Session F: A second disease, end to end (gap 1)

### Contracts extracted

`Signature`, `load_signature`, `bliss_combine`, `combine_effects`,
`alignment_metrics`, and `EVIDENCE_RANK` moved to `core/biology/signature.py`.
`ms_scoring` re-exports them, so no caller broke. Risk weighting moved out of
`ScoringConfig` and into the registry, because how strongly infection or
dyskinesia constrains use is a property of the disease and its population, not
of a scoring function. A test now asserts no module under `core/design/`
mentions `ms_scoring`.

### Parkinson's, built from scratch

| | MS | Parkinson's |
| --- | --- | --- |
| Signature | 112 genes | **90 genes, 13 pathways** |
| Panel | 74 agents | **35 agents, 29 mechanism classes** |
| Interactome | STRING v12, 261 nodes | **STRING v12, 240 nodes** |
| Druggability | 93 targets | **90 targets** |

The panel is weighted deliberately toward failures — creatine, CoQ10,
isradipine, inosine, cinpanemab — because Parkinson's has an unusually
well-documented record of neuroprotection trials that did not work, which makes
strong negative controls easy to declare in advance.

Two things the second disease forced into the design:

* **Gene aliasing.** STRING v12 still calls glucocerebrosidase `GBA`; HGNC says
  `GBA1`. Unmapped, the most common genetic risk factor in PD had **zero
  network leverage** and dropped out of the profile silently. Aliases are now
  registry data, applied at load, so the cached interactome stays a faithful
  record of what the source returned.
* **A sharper test of the tractability floor.** Alpha-synuclein — the central
  protein in the disease — is intrinsically disordered, prior 0.25. The profile
  routes around its most important target through lysosomal and autophagic
  mechanisms, which is what the clinical field actually does.

The PD profile ranks **LRRK2 first**, then SLC6A3, NLRP3, MAOB, GBA1. Axis
gaps: `symptomatic_dopaminergic` 0.00, `synuclein_proteostasis` and
`trophic_support` both 1.00.

### The library learned what it was missing

Run against PD, `unreachable_requirements()` reported **10 of 14 targets with
no chemical matter** — the library was built for MS. Eleven PD pharmacophores
were added (LRRK2 aminopyrimidine, propargylamine, nitrocatechol, aminotetralin,
iminosugar, dihydropyridine, hydroxypyridinone, ketoamide, and others), taking
the library to 59 fragments and the gap to two, both symptomatic-dopaminergic
targets a disease-modifying design would not pursue anyway.

That diagnostic driving library growth is the intended workflow: fragments are
disease-agnostic chemical matter, and the tool names what it cannot reach
rather than quietly producing something worse.

---

## 2026-08-26 — Session G: Evidence, provenance, and honest status (gaps 2, 4, 5)

### Per-claim evidence (gap 4)

All **154 fragment–target claims** now carry provenance. Each pharmacophore
declares an `evidence_tier` for its chemotype and the `primary_targets` it
claims to *bind*; everything else in its map is a downstream transcriptional
consequence and is discounted by half. Confidence weights profile coverage
directly, so the optimiser prefers well-evidenced arms instead of treating a
speculative inference like approved-drug pharmacology.

Library composition: 10 approved-drug, 8 clinical-candidate, 9
published-chemotype, 4 speculative.

This visibly changed the MS result. The top design is now a **dual BTK / CSF1R
inhibitor serving two therapeutic axes** (`cns_innate` + `immunomodulation`),
where the previous top design served one.

### Evidence status (gap 2)

The binding, selectivity, and ADMET gaps cannot be closed without models and
data this project does not have. What *was* fixed is that the caveats now
travel with the data: every candidate carries a machine-readable
`evidence_status` block enumerating **13 unassessed axes** — target binding,
selectivity, cell activity, in-vivo efficacy, permeability, BBB transport, P-gp
efflux, metabolic stability, CYP, hERG, solubility, synthetic route, freedom to
operate — each with what would satisfy it and why its absence matters.
`readiness` reads `hypothesis_only`. A consumer that never opens the protocol
still receives the caveat.

### Run artifacts (gap 5)

`core/provenance.py` records the SHA-256 digest of every input, the git
revision **and whether the tree was dirty**, interpreter, platform, tracked
package versions, and the active chemistry backend. Results moved to
`experiments/design/results/<disease>/`, are git-ignored, and carry a README
distinguishing disposable snapshots from curated `data/`.

The digest is the part that matters: a version string in a metadata block does
not survive someone editing a CSV.

---

## 2026-08-26 — Session H: QAOA's default was luck

Re-running the quantum benchmark across two diseases after the library grew
exposed something the single-disease campaign had hidden. QAOA success is
**non-monotonic in circuit depth and specific to the problem instance**: depth
3, adopted as the default because it solved the original MS instance, then
failed on *both* campaigns, while depths 2, 4, and 5 each succeeded on some
instances and not others.

| depth | MS | Parkinson's |
| --- | --- | --- |
| 1 | +0.0443 ✓ | +0.0732 |
| 2 | +0.0443 ✓ | +0.0830 ✓ |
| 3 | +0.0355 | +0.0830 ✓ |
| 4 | +0.0443 ✓ | +0.0830 ✓ |
| 5 | +0.0443 ✓ | +0.0830 ✓ |

The runner now sweeps depths 1–5, keeps the best *feasible* selection, and
prints what every depth returned. Reporting one lucky depth would have
presented a heuristic as though it were a solver.

### The stage inversion held for both diseases

| disease | Hamiltonian rank 1 | best molecule came from |
| --- | --- | --- |
| MS | BTK + RORgt (+0.0443) | BTK + CSF1R, **rank 3** |
| PD | GLUT + MAO-B (+0.0830) | caspase-1 + MAO-B, **rank 2** |

Confirming that carrying several arm sets forward, rather than the optimum
alone, is load-bearing rather than defensive.

---

## Phase 4 results

**Multiple sclerosis** — `N1(CCN(CC1)C(=O)Nc2cccnc2)C3CCN(CC3)C(=O)C=C`
C18H25N5O2, MW 343.4, cLogP 1.41, TPSA 68.8, CNS-MPO 5.33, Tanimoto 0.36.
Dual BTK/CSF1R, two axes, mean engagement confidence 0.40.

**Parkinson's** — `c1(ccc(cc1)CC(C)N(C)CC#C)OC(=O)C(=O)NCC2CC2`
C19H24N2O3, MW 328.4, cLogP 1.61, TPSA 58.6, CNS-MPO 4.93, Tanimoto 0.32.
MAO-B inhibitor fused to a caspase-1 warhead, mean engagement confidence 0.47.

Both rank first against their disease panels on signature reversal — a
**near-circular** comparison, since their arms were selected to maximise
alignment with the signature they are then scored against, and reported only
with that caveat attached.

Test suite: **174 passing** without RDKit, **198 with it**.

### Reflection

> Four of the five gaps were closed and the fifth was made honest. The most
> valuable work was again negative: cross-validation against RDKit found three
> chemistry bugs that a year of formula-and-mass tests would never have caught,
> and the second disease found a gene-alias failure that silently zeroed the
> most important target in Parkinson's. Both were invisible in the output.
> The pattern across all four phases is consistent — the machinery built to
> doubt the results is what produces the results worth keeping. Where a claim
> could not be supported, the claim moved rather than the evidence: RDKit
> became the preferred backend instead of the reimplementation being defended,
> and QAOA's depth became a swept parameter instead of a lucky constant.

### Next steps

1. **Dock the proposals.** Everything else is downstream of the
   fragment-transplantation assumption, and it remains untested.
2. Close the evidence loop: `core/design/evidence.py` has the hook for assay
   results to update fragment confidences, and nothing populates it.
3. Add ADMET where it can be done honestly — P-gp efflux first, since it
   decides CNS programmes on its own.
4. Replace both signatures with cohort-derived data; the PD one is weaker than
   the MS one and both are illustrative.
5. A third disease outside the CNS, to exercise the peripheral branch of the
   delivery constraint, which neither current entry does.

---

## Phase 5 — The second disease gets its own screen (2026-08-26)

### Objective

Parkinson's was registered in Phase 4 and exercised end to end by the *design*
campaign, but it had no combination screen of its own. The MS screen could not
be pointed at it: `core/biology/ms_scoring.py` holds MS's pathways, therapeutic
axes, risk domains, and risk weights as module constants, so running it against
Parkinson's would have scored PD combinations against MS's vocabulary and
reported `infection` as a worst risk domain for a disease where nothing is
constrained by infection risk.

Two things had to change, and one thing deliberately did not.

### 1. Vocabulary moved from the code to the registry

`core/biology/combination_scoring.py` reads every vocabulary from a
`DiseaseContext`. Adding a third disease now touches no scoring code. A test
asserts the property directly rather than by inspection: scoring a PD pair must
produce a `worst_risk_domain` that is one of PD's domains and **is not** one of
MS's.

### 2. The screen learned to count past two

The MS screen is pairwise. Parkinson's is treated with genuine polypharmacy —
levodopa plus a decarboxylase inhibitor plus a COMT inhibitor plus a MAO-B
inhibitor is an ordinary regimen — so a pairwise-only screen would have been
answering the wrong question.

`combination_metrics` scores a combination of any order. Every k-ary term is
defined as the **mean of its pairwise form**, which was the design constraint
worth holding: it makes k = 2 numerically identical to the pairwise
definitions, so nothing about the MS results is being quietly restated in a new
arithmetic, and it gives k ≥ 3 a definition that privileges no member. Tests
pin the reduction for target complementarity, safety union, and Bliss folding,
and assert that scoring is invariant to the order the members are listed in.

### 3. The comparison that needed a rule, not a number

The headline ask was monotherapy versus combination. The obvious
implementation — rank everything by `priority_score` and see what wins — is
wrong, and quietly so.

`priority_score` includes target complementarity, compartment complementarity,
and network separation. A single agent scores **zero on all three by
construction**. Ranking singles against pairs by composite score therefore
concludes that combinations win, when what they actually did was collect
bonuses that are structurally unavailable to a monotherapy. The number would
have looked like a finding.

So the rule is stated instead: **`priority_score` is comparable only within a
fixed order**, and across orders only the efficacy block — defined identically
at every k — may be compared. `monotherapy_comparison` reports that block and
nothing else, and a test asserts `priority_score` never enters the comparable
set. Three fields carry the actual comparison:
`reversal_gain_over_best_single`, `score_gain_over_best_subset` (negative means
a third agent does not earn its place), and `additivity_ratio`.

The last of those needed fixing after first sight. Its median is 1.0 at every
order, because most agents in the panel have disjoint target sets and Bliss is
exactly additive on disjoint genes — the median is the uninformative half of
the statistic. The tail is the finding: 17% of pairs and 36% of triples are
sub-additive, meaning their members are covering the same signal. The report
now carries `fraction_subadditive`, the 5th percentile, and the minimum.

### The bug that a smoke run would not have caught

The first full run returned `nan` for every order-3 stratum bootstrap interval
and a top-K Jaccard of exactly 0.0 — not a warning, a structural zero.

The order loop reassigns `prefilter` at the end of each iteration to seed the
next order. The robustness analyses ran *after* that reassignment, so at order 3
they re-enumerated the triple space filtered by a set of **3-tuples** rather
than the 2-faces that built it. Nothing matched, every re-ranking returned an
empty list, and the statistics dutifully reported `nan` over nothing.

It is the failure mode this project keeps producing: not a crash, an
answer-shaped absence of an answer. The Jaccard of 0.0 was the tell — a real
instability produces a small number, not a perfectly round one. The prefilter
in force for the current order is now held in its own name.

### The result that did not need the leaderboard

The pattern from the MS screen reproduced exactly, at both orders: individual
combination ranks are **not** stable under the curated target-effect
uncertainty, while **stratum medians are**. Same conclusion, different disease,
different vocabulary, different panel. The unit of inference is the mechanism
stratum.

Consistent with this, both screens agree on the shape of the disease they were
given: the strata that rank highest are the ones pairing a symptomatic or
metabolic agent with the axis that has **no approved agent at all** — trophic
support in Parkinson's, remyelination in MS. A screen bounded by its panel can
identify that gap and cannot, in principle, fill it. That is what the de novo
design campaign is for.

### What I chose not to build

Parkinson's regimens are chronic oral polypharmacy in an elderly population, so
the binding constraint on co-administration is pharmacokinetic — CYP and COMT
interactions, additive hypotension, serotonin syndrome with MAO-B inhibitors.
No such model exists here. Building one would have made the PD results
non-comparable with the MS v3 numbers until MS was re-run against it, so the
screen ships with route burden and half-life spread (`regimen_burden`) as the
only co-administration cost, and the gap declared in the caveats block of every
result file rather than only in prose.

It is the top-priority next model.

### Reflection

> The interesting work was again in refusing a number rather than producing
> one. `priority_score` across orders would have given a clean,
> publishable-looking answer to the question I was actually asked, and it would
> have been an artefact of which terms a single agent can structurally earn.
> Writing down the comparison rule, then testing that the rule cannot be
> violated, was worth more than the ranking it constrains. The `nan` bug makes
> the same point from the other direction: the analysis did not fail, it
> succeeded on an empty set, and only an implausibly round robustness figure
> gave it away.

### Next steps

1. **PK/DDI model** — the largest declared gap, and the one that binds hardest
   on the disease just screened.
2. Migrate the MS screen onto `combination_scoring` so both diseases run one
   contract, and re-run MS at k = 3.
3. Dock the design proposals; still the assumption everything else sits on.
4. Replace both signatures with cohort-derived data.
5. A non-CNS disease, to exercise the peripheral branch of the delivery
   constraint that neither current entry does.

---

## Phase 6 — Parkinson's drug discovery, and a silent novelty failure (2026-08-28)

### Objective

Bring the Parkinson's *design* campaign to the same standard as the MS one.
Phase 4 had already run it end to end and Phase 5 gave PD its own combination
screen, so on paper this was a re-run at parity. It was not.

### The bug: an optional field that degraded a result without saying so

Novelty in the design campaign is assessed against

```python
reference = [*disease.known_structures(), *library.parent_structures()]
```

`known_structures()` reads `data.structures` from the registry entry and
returns `[]` when the key is absent. **Parkinson's had no `structures` key.**

So every Parkinson's design was having its novelty measured against nothing but
the pharmacophore fragments it had just been assembled from. The consequence is
worse than a missing number would have been:

- the `nearest_known_compound` field was **populated**, with
  `Propargylamine MAO-B warhead`;
- the Tanimoto was **plausible** at 0.32;
- `is_novel` was **True**;
- and nothing anywhere in the JSON, the CSV, or the console output indicated
  that the comparison set had been cut in half.

A missing file would have been caught in a minute. A silently reduced
comparison survived two phases and got written into a protocol document.

With `data/chemistry/pd_known_structures.json` registered — 26 structures
covering the panel's small molecules — the same molecule's nearest neighbour is
**selegiline** at **Tanimoto 0.47**. It still clears the declared 0.6 threshold,
so the headline conclusion holds, but the margin is much narrower and it is now
measured against an approved Parkinson's drug rather than against the pipeline's
own parts. In hindsight the old answer was obviously wrong: the design *is* a
propargylamine, so of course selegiline is its nearest neighbour. The number
only looked defensible because selegiline was not in the comparison.

Curating the 26 structures went the way this repo's chemistry work usually
goes — three of my first 27 transcriptions were wrong (safinamide's amide was
on the wrong carbon, minocycline had three carbons too many, and my *literature*
mass for deferiprone was wrong rather than the SMILES). All three were caught by
re-deriving formula and mass from the structure and comparing against the
published values, which is exactly what that guard exists for. Every entry was
additionally cross-checked against RDKit before admission.

### The guards, because "remember to add the file" is not a guard

- `test_each_disease_declares_a_novelty_reference_set` — fails if a registered
  disease has no reference set, or one that barely overlaps its own panel.
- `test_novelty_is_measured_against_real_drugs_not_only_fragments` — fails if
  the set adds nothing the fragment library already contained, which would make
  registering it a no-op.
- `tests/test_chemistry.py` now iterates **every** registered disease's
  structure file rather than naming the MS one, so a third disease's set is
  formula- and mass-validated the moment it is added, without new test code.

The campaign protocol's "adding a disease" checklist gained the reference set as
step 5, with the reason attached rather than left as an instruction.

### A second reporting defect, found while writing it up

The design runner prints `design["candidates"]` — the diversity-selected
deliverable — and wrote `design["all_ranked"]` to the CSV. Those are different
lists drawn from different pools, and neither contains the other: **three of the
four designs in the report were absent from the CSV entirely**, which is the
file anyone would actually open.

The CSV now carries the union, deduplicated and ordered by fitness, with a
`selected_for_diversity` column distinguishing the deliverable from the raw
ranking. Both diseases were regenerated so their artifacts stay comparable.

### Results

Parkinson's, at parity with MS (`--k 2 --arms 3 --top 4 --quantum-benchmark`,
RDKit backend):

- 14-requirement target profile led by LRRK2 (0.965), SLC6A3, NLRP3, MAOB, GBA1.
- `DDC` and `SLC18A2` reported **unreachable** — no chemical matter in the
  library. Still the most useful line a run produces.
- 10-variable QUBO, 45 couplings, 45 feasible states of 1,024. Enumeration,
  exact eigensolver, and QAOA all reach +0.0830; QAOA needs depth ≥ 2, with
  d1 falling short at +0.0732.
- Axis gaps: `synuclein_proteostasis` and `trophic_support` both **1.00**
  unmet, `symptomatic_dopaminergic` 0.00.
- Leading design `C19H24N2O3`, MW 328.4, CNS-MPO 4.93/6 — a MAO-B inhibitor
  fused to a caspase-1 warhead.

The **stage inversion held again**: the Hamiltonian's rank-1 arm set
(GLUT + MAO-B, +0.0830) did not build the best molecule; rank 2
(caspase-1 + MAO-B, +0.0732) did. Third disease, same lesson — carrying several
arm sets forward is load-bearing.

The axis-gap result is also the *screen's* Phase 5 finding arrived at
independently: the combination screen's top mechanism strata all pair something
with `trophic_support`, and the design campaign — reading only the panel's
approved agents, never the combination scores — reports that axis at 1.00 unmet.

Test suite: **236 passing** without RDKit, **260 with it**.

### Reflection

> Both defects this phase were the same shape as the `nan` bug in Phase 5:
> nothing failed. An optional registry key degraded a scientific claim while
> leaving a well-formed, plausible number in place, and a CSV confidently
> presented the wrong four molecules. Neither would have been caught by reading
> the output, because the output looked right — they were caught by asking what
> the number was actually measured against, and by noticing that two views of
> the same result disagreed. The fix in both cases was to make the quiet failure
> loud: a test that fails when a reference set is missing, a column that names
> which rows are the deliverable. I am increasingly convinced that the useful
> question for this project is not "is this number right?" but "what would this
> number look like if it were wrong?" — and that where the answer is "exactly
> the same", that is the bug to go hunting.

### Next steps

1. **PK/DDI model** — still the largest declared gap, unchanged from Phase 5.
2. Migrate the MS screen onto `combination_scoring` and re-run MS at k = 3.
3. **Dock the proposals.** Three phases running, still the assumption
   everything else rests on, and now the only untested claim standing between
   these structures and a reason to make one.
4. Replace both signatures with cohort-derived data; PD's remains the weaker.
5. A non-CNS disease, to exercise the peripheral branch of the delivery
   constraint — and, now, to be the first disease that gets its reference set
   right on the first pass.

---

## Phase 7 — Alzheimer's disease, the third campaign (2026-09-26)

### Objective

Run the same two research tracks that Parkinson's got — the k = 1, 2, 3
combination screen over existing agents, and the de novo design campaign — for
Alzheimer's, and do it by following
[the campaign protocol](disease_campaign_protocol.md) rather than by copying
what Parkinson's happened to contain. Alzheimer's was chosen because it is the
hardest test the abstraction has faced: the two proteins that *define* the
disease are the two a small molecule reaches worst.

| | MS | Parkinson's | **Alzheimer's** |
| --- | --- | --- | --- |
| Signature | 112 genes | 90 genes | **97 genes, 13 pathways** |
| Panel | 74 agents | 35 agents | **36 agents, 34 mechanism classes** |
| Interactome | STRING v12, 261 nodes | STRING v12, 240 nodes | **STRING v12, 247 nodes, 10,572 edges** |
| Druggability | 93 targets | 90 targets | **97 targets** |
| Known structures | 42 agents | 26 agents | **23 agents** |
| Gene aliases needed | — | `GBA` → `GBA1` | **none** (97 of 97 present) |
| Combination screen | pairs (v3); k = 1, 2, 3 added later the same day, see the addendum | k = 1, 2, 3 | **k = 1, 2, 3** |

### What the disease forced into the inputs

* **Amyloid-β has no transcript.** The signature is transcriptional, and amyloid
  burden is a protein quantity. The amyloid axis is scored through `APP`, the
  secretases, and downstream injury and glial markers (`NEFL`, `GFAP`, `C1QA`),
  so for an antibody the `APP` row is a *proxy*, and the amyloid result is the
  least reliable in the screen.
* **A modality Parkinson's did not have.** The approved disease-modifying agents
  are antibodies, dose-limited by imaging-detected brain oedema (ARIA). The risk
  vocabulary therefore has `aria` as its highest-weighted domain, alongside
  `bradycardia_syncope` and `cognitive_worsening`, and shares nothing with the
  earlier two except generic organ toxicity. The antibodies are modelled at CNS
  penetration 0.10–0.15, not zero, because they reach the brain at about one
  per cent and still work; a test pins that band.
* **Tractability direction.** The first draft of the druggability file scored
  targets from class precedent, so `AKT1`, `BCL2`, `CAMK2A`, `GPX4`, `SIRT1` and
  `HMOX1` all came out tractable, as *inhibitors*, although every one of them needs
  to go **up**. `AKT1` was fifth in the design profile as a result. Checking, for
  each of the profile's top targets, what chemistry could push it in the wanted
  direction exposed the error, and all six were rescored as activation problems. The
  rule is written into the annotation file and pinned by a test.

### Tooling problems, both silent

* **A `sed` wildcard.** The Alzheimer's runner was made by copying the Parkinson's
  one and replacing `experiments.parkinsons.`; `.` matches `/`, so
  `experiments/parkinsons/results` became `experiments.alzheimers.results`. The run
  succeeded and wrote 2 MB into a directory that did not belong anywhere. Nothing
  failed.
* **PD prose in the results file.** The runner's control report carried the
  string "Two non-ergot D2/D3 agonists are pharmacodynamically duplicate" into
  the Alzheimer's JSON. The campaign protocol said the runner needed only its
  `DISEASE` constant changed; that was wrong, and step 7 of the checklist now
  lists every place that has to change and says what the right refactor is.

Both are the same shape as Phase 6: nothing failed, and the output looked like a
result.

### Combination screen

Deterministic (`--seed 7`), 36 agents at k = 1, 2, 3: 36 + 630 + 6,360
combinations, 7,026 rows including the excluded ones, about 6 minutes.

* **Combination gain is smaller than in Parkinson's at order 2** (12.7% of pairs
  beat their best member, against 26.4%) **and much more redundant** (62.0% of
  triples sub-additive, against 36.0%).
* **But third agents earn their place more often**: 33.0% of triples have a
  negative gain over their best pair, against 60.3% in Parkinson's, with a
  median gain of **+0.0238** against −0.0192.
* Bootstrap top-25 Jaccard **0.187 / 0.085** at orders 2 / 3 — worse than
  Parkinson's — while weight sensitivity stays excellent (Spearman 0.97). Same
  conclusion: the unit of inference is the mechanism stratum.
* **Donepezil + memantine**, the one approved combination in the panel, ranks 70
  of 606 pairs (top 12%, *q* = 0.10). A sanity check rather than a control.

### The strata disagree with the design campaign, for the first time

In MS and Parkinson's, the screen's strongest strata paired something with the
axis that had the least approved cover, and the design campaign's independent
gap analysis named the same axis. I had started to treat that convergence as a
property of the method.

It did not reproduce. **Six of the top seven order-2 strata contain
`cholinergic_symptomatic`** — the axis the design campaign scores at 0.00 unmet
— while tau and metabolic rescue, both at 1.00, sit in the middle and bottom.
Amyloid-only pairs are last. The inputs explain it partly (the cholinergic
agents are approved, with the lowest target uncertainty in the panel; the
antibodies carry the heaviest-weighted risk and move the signature only through
a proxy) but I cannot separate "the composite correctly penalises a risky,
poorly-exposed class" from "the composite is mis-scoring a protein-level
mechanism with a transcript-level signature". The protocol says that, rather
than picking the reading that matches the earlier two diseases.

### A control that failed while reporting that it passed

The safety-penalty control is **tacrine**, withdrawn for hepatotoxicity. By the
runner's definition (best position in the pooled primary ranking) it sits at
rank 62 and the control passes. Read per order it does not: tacrine is **#1 of 36
monotherapies** by composite score, despite having the **highest safety union of
any single agent** (0.203), and appears three times in the top-25 pairs and
three times in the top-25 triples.

The cause is in the scorer, not the panel. `evidence_tier` records approval, not
withdrawal, so tacrine earns full evidence credit; and `safety_union` is a
weighted mean over eight risk domains, so hepatic 0.95 × weight 0.7 is one term
among many. I did **not** tune the scorer to make the control pass — that would
be fitting the method to its own check — and reported it as a failure to
represent withdrawal. Two of five negative-efficacy controls (pioglitazone,
verubecestat) also reach the top 25, against one of five in Parkinson's.

### Design campaign

Run under RDKit and qiskit (a separate interpreter from the default one, which
has neither), `--k 2 --arms 3 --top 4 --quantum-benchmark`:

* 14-requirement profile led by `BACE1` (0.697), `GSK3B`, `NOS2`, `MTOR`,
  `CASP3`. Tau and APP were routed around by the tractability floor, as a test
  now asserts.
* The library reported **six of fourteen targets unreachable** at first (`BACE1`,
  `PPARG`, `FYN`, `PTGS2`, `MAPK14`, `BCHE`). Seven pharmacophores were added
  (66 fragments), taking the gap to zero and leaving MS and Parkinson's
  unchanged.
* Enumeration, exact eigensolver and QAOA all reach +0.0724; QAOA holds at
  depths 2–4 and **falls to +0.0404 at depth 5** — more layers made it worse.
* Leading design `C17H19N3O3`, MW 313.4, CNS-MPO 5.48/6, a cholinesterase
  carbamate fused to a CSF1R amide, nearest known compound rivastigmine at
  Tanimoto 0.38. It is novel, and it is built on the axis the gap analysis calls
  fully served.
* **`BACE1`, the top-priority target, never entered the optimiser.** The
  Hamiltonian pre-filters to the ten fragments with the best solo benefit, and
  the BACE1 amidine ranks 31 of 38 at −0.51 because its polarity and mass
  overrun the CNS property envelope. That mirrors the real problem BACE1
  programmes had with brain exposure, but it is also a consequence of my choice
  of fragment; a less polar chemotype is the obvious next experiment.
* **The stage inversion held for a third disease.** The Hamiltonian's rank-1 arm
  set built the worst of the three molecules (fitness 0.93 against 1.48 for the
  best), because its carboxylic acid is what the CNS gate penalises.
* A vocabulary leak I noticed and did not fix: the design's `axes` line includes
  `cns_innate`, an MS axis, from the shared fragment `csf1r_picolinamide`.
  Per-fragment axis labels are stale for any disease other than the one that
  added the fragment.

### Chemistry

23 of the 36 panel agents have a curated structure (nine antibodies and peptides,
one antisense oligonucleotide, one chemotype-only entry, and two structures I
could not transcribe with confidence are omitted). **All 23 reproduced their
literature formula and mass on the first pass**, on both the local backend and
RDKit. That is weaker reassurance than it looks. The Parkinson's set needed three
corrections that only this check could find, and formula and mass cannot detect
a positional isomer at all. I wrote these structures from memory of the
published skeletons, and the file says so; they need confirming against a
primary structure source. The novelty reference set was registered before the
first design run, so this was the first disease not to repeat the Phase 6 hole.

### Tests

**276 passed, 24 skipped** without RDKit; **300 passed** with it (236 / 260
before). New checks: pairwise no-shared-axis and generic-overlap-only tests
across every registered disease, that tau and APP stay out of the profile, that
activation-direction targets are not scored as inhibitor-tractable, and that the
amyloid antibodies stay low-but-nonzero on CNS exposure.

### Reflection

> Phase 6 ended with the note that the useful question is "what would this
> number look like if it were wrong?". Three times this phase the answer was
> "exactly the same": a druggability file that looked fully populated while
> scoring six targets in the wrong direction; a results directory that existed
> and was full; a control report that said the control passed. In each case the
> output was well-formed. What found them was looking at a specific thing
> instead of the summary — the profile's top targets one by one, the file tree,
> one drug's rank in each order rather than in the pooled list.
>
> The result I trust least is the one most people will look for first. The screen
> cannot see amyloid, and its strata disagree with the design analysis. I would
> rather have that written down than a fourth tidy convergence.

### Next steps

1. **A max-domain term in `safety_union`**, and a `withdrawn` flag the scorer
   reads, evaluated on all three diseases at once so it is not tuned to
   tacrine.
2. **A less polar BACE1 chemotype** (amino-thiazine or amino-oxazine) and a
   larger optimiser pool, to see whether `BACE1` reaches the Hamiltonian at all.
3. **Re-annotate fragment axes per disease**, so a design's axes line never
   carries another disease's vocabulary.
4. **Read control names and descriptions from panel metadata** so a runner needs
   only a `DISEASE` constant, as the protocol originally claimed.
5. **PK/DDI model** — still the largest declared gap, and it binds hardest in a
   frail, polypharmacic dementia population.
6. **APOE-stratified safety.** ARIA risk is genotype-dependent and the model is
   not.
7. Confirm the two recent negative-trial records (semaglutide, AL002) and the
   hand-transcribed structures against primary sources.
8. A non-CNS disease, still, to exercise the peripheral branch of the delivery
   constraint.

### Addendum (2026-09-26, later the same day): what a percentage means, MS at k = 3, and calibration

Three follow-ups came from one question — "what is the efficacy rate?" — and the
honest answer to it changed how the results are stated.

**Reversal as a percentage of a ceiling.** `signed_reversal` (the share of the
signature's weight moved the right way) has no natural scale: it shrinks when the
signature gains untargeted genes and cannot exceed what the panel covers. Added
[tools/reversal_ceiling.py](../tools/reversal_ceiling.py), which divides the best
reversal at each order by a **full-reversal ceiling** (every targeted gene fully
reversed) and a **pooled-panel ceiling** (all agents at once, therapeutic effects
only, Bliss-combined). Best triples capture 16.1% / 25.7% of those ceilings in
Alzheimer's, 19.6% / 33.2% in Parkinson's, and 17.5% / 21.4% in MS. Both ceilings
are generous, because each panel was curated from its own signature's genes.

**MS at k = 3.** Closed the Phase 6 next step "re-run MS at k = 3" by adding
`experiments/ms/run_combination_screen.py`, the MS instance of the k-ary runner
(64 eligible agents at phase 2 or above; 64 singles, 2,016 pairs, 29,757 triples).
The best triple is methylprednisolone + ocrelizumab + opicinumab at **14.95%**
reversal (best pair 10.54%, best single 5.58%). The full run took about two
hours of wall-clock time, and its output was empty the whole time because Python
buffers stdout when redirected. The silence was first read as per-stage printing,
which produced a wrong time estimate; comparing CPU time with elapsed time showed
the process had been mostly idle.

Results: 45.0% of pairs and 93.4% of triples beat the best monotherapy (higher than
either other disease, partly because the best single is a broad steroid and the
panel has many weak agents), 40.4% and 77.2% sub-additive (highest of the three),
and 33.6% of triples have a negative gain over their best pair (median +0.0332).
223 of 2,016 pairs were excluded as redundant. **The strata reproduce the v3
result under the new scorer**: `cns_innate + remyelination` first,
`immunomodulation + immunomodulation` last, and at order 3 the top six strata all
contain remyelination. So MS keeps the convergence between the screen and the
design campaign's gap analysis (remyelination, 1.00 unmet) that Alzheimer's broke.
Bootstrap top-25 Jaccard is 0.229 / 0.132, again unstable, with Spearman 0.97 under
weight jitter.

Controls: natalizumab and its biosimilar are excluded as expected. The safety
controls (daclizumab, cyclophosphamide, mitoxantrone) rank 61st to 64th of 64 as
monotherapies and nowhere near the top 25 in combination, so unlike tacrine in
Alzheimer's they do not slip through; I do not know why, and only have a candidate
explanation (several heavily-weighted domains burdened at once). Two of four
negative controls reach the top 25 (high-dose biotin 6th, evobrutinib 22nd),
opicinumab is 28th, and opicinumab also appears in both the best-reversal pair and
triple. Full detail in [the MS protocol, §12](ms_publication_protocol.md).

The same class of problem recurred in the MS runner: it was copied from the
Alzheimer's runner rather than the Parkinson's one, and its prose (ARIA monitoring, "elderly patient", cholinesterase
inhibitors) from the MS caveats. The refactor named in step 7 of the campaign
protocol, reading controls from the panel metadata, would remove the copy step.

**Calibration against published efficacy.** I wanted to know whether the score
tracks real efficacy, so I gathered effect sizes from two fetched meta-analyses (11 MS drugs) and
tested it; see [the calibration write-up](efficacy_calibration.md). The five
antibodies (relapse-rate ratio 0.28 to 0.34) all outscore the six other
disease-modifying drugs on signature reversal (AUC 1.00, p ≈ 0.002), and the
composite `priority_score` ranks them the *wrong* way round (AUC 0.30). The
separation comes from the curated effect *magnitudes*, not from how many genes
each drug touches, and I wrote those magnitudes knowing which drugs are
potent, so I cannot separate the model recovering biology from the
curation echoing what was put in. Two tiers cannot support a curve, and a linear
fit would predict a relapse reduction above 100% for a triple. **No score-to-effect
mapping is supported, and no predicted efficacy percentage exists for any
combination or designed molecule.**

Also a source-quality lesson: a web-search summary gave me confident-looking
relapse-reduction figures for the interferons, glatiramer and teriflunomide that I
could not trace to a fetched page, and one of its statements muddled two trials. I
left those drugs out rather than use them. Alzheimer's and Parkinson's were not
calibrated at all (no sourced effect sizes gathered), which is work not done.

**Reflection.** The reversal percentages looked like efficacy rates and were
repeatedly read as one, by me included, when I wrote "about a quarter of what the
panel could reach". That is a normalisation for comparing diseases, and it is easy
to hear as a clinical claim. The calibration was the check that could have shown
the score was uninformative; it did not, but it also showed the composite is not an
efficacy predictor and that the one positive result may be circular.

**Next steps (additional).** Gather a common-scale effect table for at least
15–20 agents per disease. Re-derive `target_effects` blind to efficacy so the
calibration test can be independent. Add a bounded, held-out-validated link between
reversal and effect before any percentage is attached to a combination.

---

## Phase 8 — Epilepsy, the fourth campaign (2026-09-27)

### Objective

Run the same two tracks for epilepsy that the other three diseases got — the
k = 1, 2, 3 combination screen and the de novo design campaign — following the
campaign protocol as corrected during Alzheimer's. Epilepsy was chosen because it
inverts the Alzheimer's problem: its disease-defining targets are ion channels and
receptors, the most tractable class there is, so the question stops being "can a
small molecule reach the target" and becomes "what is left once the crowded
channel targets are covered".

| | MS | Parkinson's | Alzheimer's | **Epilepsy** |
| --- | --- | --- | --- | --- |
| Signature | 112 genes | 90 genes | 97 genes | **85 genes, 14 pathways** |
| Panel | 74 agents | 35 agents | 36 agents | **37 agents, 32 mechanism classes** |
| Approved share of panel | 24 of 74 | 16 of 35 | 8 of 36 | **30 of 37** |
| Interactome | 261 nodes | 240 nodes | 247 nodes | **234 nodes, 7,001 edges** |
| Genes absent from network | — | `GBA1` (aliased) | none | **`AQP4` (STRING v12 does not recognise the symbol)** |
| Known structures | 42 | 26 | 23 | **31** |

### What the disease forced

* **The redundancy rule matches clinical practice, and that costs something.**
  Eight panel agents carry the `sodium_channel_blocker` class, so 28
  sodium-channel pairs are excluded by construction, which is what rational
  polytherapy does anyway. It also means a useful dual-sodium combination would be
  invisible to the screen.
* **An approved-heavy panel breaks a test I had assumed universal.** The
  unserved-axis test asserted an axis with gap exactly 1.00. Epilepsy has none:
  everolimus (approved for TSC-associated seizures) and retigabine (approved, then
  withdrawn in 2017) give every axis some approved cover. I relaxed it to 0.8 and
  wrote the reason into the test, because relaxing a test to pass is only honest if
  the reason is stated. It also exposes the withdrawal blind spot a second time:
  a drug withdrawn from every market still counts as cover.
* **Teratogenicity is shared with MS, and I widened the test rather than rename the
  domain.** The pairwise vocabulary check failed because MS and epilepsy both weigh
  it (teriflunomide; valproate). It genuinely applies to both. Renaming it to
  `fetal_malformation` would have passed and would have been the check being gamed,
  so I added it to the generic set and said so in the docstring.
* **Tractability has a direction, applied from the start this time.** GAD1/2, KCC2,
  EAAT2, Kir4.1 and Nav1.1 all have to go *up*, and the precedent for each is
  inhibitors or nothing, so they are scored low. That is the Alzheimer's lesson
  applied on the first pass, and a test pins it.

### Verifying the controls instead of recalling them

The negative-efficacy and safety controls are the part of a panel most likely to be
written from a half-remembered headline, so I checked each against a source before
declaring it: soticlestat's phase 3 missed its primary endpoints in Dravet and
Lennox-Gastaut syndromes; the bumetanide neonatal trial missed its endpoint and was
stopped after hearing loss; retigabine was withdrawn in 2017 for pigmentation;
azetukalner's phase 3 was positive (53.2% against 10.4% seizure reduction). One
of my candidates did not survive: ganaxolone failed in adult focal seizures but is
approved for CDKL5 deficiency, so it is not a clean negative control and I left
it out. That leaves **three** negative controls, fewer than the other diseases,
which the panel metadata says plainly. Talampanel is the weakest of the three: one
source described a 300-patient trial failing to show efficacy while an earlier
crossover had suggested some, so I recorded both.

### Problems found during the build

* **Invalid JSON, silently.** A `\\n` typed in the curation script's source left the
  panel file ending in a literal backslash-n, so it was not valid JSON. The script
  printed "Wrote ..." and exited normally; parsing the file exposed it. Same shape as
  the earlier silent failures.
* **Brivaracetam ring size.** The SMILES had a four-membered lactam where the drug
  has a pyrrolidinone. The formula check rejected it (C10H18N2O2 against
  C11H20N2O2). The other 30 structures passed first time, which is weaker
  reassurance than it sounds: formula and mass cannot detect a positional isomer.
* **Unbuffered output.** The full screen was launched with `python -u` from the
  start, having learned from the MS run that redirected output is otherwise buffered
  until exit. Progress was visible throughout.
* **`AQP4` explanation was wrong.** The epilepsy network omits `AQP4`, and I first
  recorded the reason as "no interactions at the 0.4 cutoff" without checking.
  Querying STRING directly for the symbol returns "not found", so it is a
  symbol-recognition failure. Corrected in the registry entry, the epilepsy
  protocol and the table above. Found while building the Guillain-Barré network,
  where the same lookup showed `MPZ` and `IGHG1` unrecognised and `VEGFA` resolving
  to a different protein.

### Design campaign

Run under RDKit and qiskit, `--k 2 --arms 3 --top 4 --quantum-benchmark`:

* 14-requirement profile led by `SLC12A2` (0.756), `MTOR`, `GABRA1`, `PTGS2`,
  `KCNQ2`. **Ten of fourteen targets were unreachable**, the same as Parkinson's had
  at the outset; ten pharmacophores were added (76 fragments) and the gap went to
  zero, with the other three diseases' lists unchanged.
* Enumeration, exact eigensolver and QAOA all reach +0.0868. The depth sweep is
  d1 +0.0868, **d2 −0.0573**, then +0.0868 at depths 3 to 5: it dips at depth 2 and
  recovers.
* Leading design `C22H27N5O2`, MW 393.5, CNS-MPO 5.09/6: an S6 kinase arm fused to
  an SV2A ligand, on two axes that are mostly unserved (gaps 0.83). Nearest real
  drug levetiracetam at Tanimoto 0.39. **Its reversal is 2.44%, the lowest of the
  four campaigns' leading designs.**
* Every arm set carried forward contains the SV2A arm, because it has the best solo
  benefit in the library, so the campaign explored a narrow region, and the SV2A
  engagement sign is the least settled thing in the panel.
* **Only one of four designs fits the property window.** The other three, all built
  on a benzodiazepinone arm, are 445 to 472 Da against a 420 Da ceiling.
* **The stage inversion held for a fourth disease**: the Hamiltonian's rank-1 arm
  set built the worst molecule (fitness 0.87 against 1.36 for the best).

### Combination screen

37 + 666 + 6,174 combinations, `--seed 7`, about 14 minutes.

* Best reversal: the P2X7 antagonist exemplar alone (3.08%), everolimus + P2X7
  (5.27%), midazolam + everolimus + P2X7 (**7.41%**). Against the panel's ceiling
  (41 of 85 genes targeted; full-reversal 43.9%, pooled-panel 30.8%, the lowest of
  the four diseases) the best triple captures 16.9% and 24.1%.
* **Third agents almost never earn their place: 83.4% of triples have a negative
  gain over their best pair** (median −0.0706), against 60.3% in Parkinson's and
  about a third in MS and Alzheimer's. Consistent with the clinical advice to be
  slow to add a third drug, but part of it is risk arithmetic, so I do not read it
  as validation.
* Redundancy is low (14.5% of pairs and 33.4% of triples sub-additive), partly
  because the redundancy rule removes 51 pairs before scoring, 28 of them among the
  eight sodium-channel blockers.
* Bootstrap top-25 Jaccard **0.358 / 0.235** (highest of the four, still unstable);
  weight sensitivity Spearman 0.951 / 0.942, the lowest of the four, so this is the
  first disease whose ranking is somewhat sensitive to the weights as well.
* **Five of the top seven order-2 strata contain `potassium_channel_opening`**, the
  axis the gap analysis rates most unmet (0.92), so screen and gap analysis agree,
  as in MS and Parkinson's. But that axis has two agents, one of them withdrawn.

**The safety-penalty control failed, this time by the runner's own test.**
Vigabatrin is first and retigabine second in the pooled ranking, and vigabatrin is
#1 of 37 monotherapies, of 615 pairs and of 6,174 triples. The top pair is
vigabatrin + acetazolamide and the top triple is vigabatrin + retigabine +
acetazolamide. Tacrine in Alzheimer's slipped through only when read per order;
this is the whole ranking. I looked for why before writing anything, and it is
in the composite rather than the panel: `reversal_efficiency` divides movement by
the signal an agent engages, so an agent with one well-aligned target scores near
1.0 however little it moves. Vigabatrin has one target (ABAT), efficiency 0.90, and
a signature reversal of 0.0075, less than half of carbamazepine's, and still wins.
The panel has many narrow agents, so they fill the leaderboard. Its safety union
(0.229) is below carbamazepine's (0.389) because one severe domain is averaged
across nine. I did not tune the scorer to pass the controls. Bumetanide (a
negative-efficacy control) also reaches the top 25, on the same narrow-and-aligned
advantage; soticlestat and talampanel do not. The top composite pair reverses 1.17%
of the signature, the best reversal pair 5.27%, which is why `priority_score` must
not be read as an efficacy ranking.

The `reversal_efficiency` mechanism was designed to stop low-efficacy, low-risk
agents winning on bonus terms, and here it does the opposite for a different kind
of agent. I built that guard and did not anticipate the inverse.

### Tests

**322 passed, 24 skipped** without RDKit; **346 passed** with it (276 / 300 before).
New checks: tractability scored in the wanted direction, sodium-channel pairs
excluded while carbamazepine with levetiracetam is not, and teratogenicity named as
the heaviest risk. Two existing tests were changed deliberately, as described above.

### Reflection

> The result that surprised me most was in the scorer. I had a guard against
> low-efficacy agents winning on bonus terms, and it lets a one-target agent win on
> efficiency alone. I found it only because a control I had declared in advance
> failed, and I had checked its provenance carefully enough to trust the failure.
>
> The other results were procedural, not biological. Four diseases in,
> the failures that cost the most time were all the same one: a step that reports
> success while producing something subtly wrong. A script that printed "Wrote"
> and produced invalid JSON; a run whose empty log I read as progress; a test that
> assumed an axis at exactly 1.00. What has worked each time is reading the output
> as data, by parsing the file, checking CPU time against the clock, and asking
> what a test was actually written to protect before deciding whether to change it.
>
> I also want a rule for when relaxing a test is honest. Two were relaxed this
> phase. I only trust them because each change is written where the next person
> will see it, with the reason that made the old assertion wrong for this disease,
> and because neither weakens what the test is for.

### Next steps

1. **Fix the composite's narrow-agent advantage and the missing withdrawal signal
   together**: cap or reweight `reversal_efficiency`, add a max-domain safety term
   and a `withdrawn` flag the scorer and the gap analysis both read, and evaluate all
   of it on all four diseases at once, not tuned to vigabatrin and tacrine.
2. **A `withdrawn` flag the scorer and the gap analysis both read**, evaluated on
   all four diseases together (tacrine, retigabine).
3. **Syndrome-stratified signatures.** A pooled epilepsy signature averages over
   mechanisms that need opposite treatment, and sodium-channel blockers can worsen
   Dravet syndrome.
4. **Enzyme-induction and interaction model.** Carbamazepine, phenytoin and
   phenobarbital lower the levels of most co-prescribed drugs, so the regimen-level
   constraints are pharmacokinetic and entirely unmodelled here.
5. Retrofit the older runners to read control names and prose from the panel
   metadata, as the epilepsy runner does.
6. Gather verified per-drug effects to extend the efficacy calibration beyond MS;
   epilepsy has an unusually large number of approved agents with published
   seizure-reduction figures, which makes it the best candidate.

---

## Phase 9 — Guillain-Barré syndrome, the fifth campaign and the first peripheral one (2026-09-27)

### Objective

Run the same two tracks for Guillain-Barré syndrome (GBS): the k = 1, 2, 3 combination
screen, then the de novo design campaign, and report the best combination and a new
molecule. GBS was chosen because it is the non-CNS disease that has been on the next-steps
list since Phase 4. Every earlier disease sets `requires_cns_exposure`; GBS attacks
peripheral nerve and root, so switching the gate off exercises the branch of the delivery
logic that none of the other four had run.

| | MS | Parkinson's | Alzheimer's | Epilepsy | **GBS** |
| --- | --- | --- | --- | --- | --- |
| Signature | 112 genes | 90 genes | 97 genes | 85 genes | **78 genes, 12 pathways** |
| Panel | 74 agents | 35 agents | 36 agents | 37 agents | **16 agents, 14 mechanism classes** |
| Approved in panel | 24 of 74 | 16 of 35 | 8 of 36 | 30 of 37 | **7 of 16** |
| Interactome | 261 nodes | 240 nodes | 247 nodes | 234 nodes | **226 nodes, 11,062 edges** |
| Known structures | 42 | 26 | 23 | 31 | **7** |
| CNS gate | on | on | on | on | **off** |

### What the disease forced

* **The peripheral branch ran, with no code change.** With the gate off the profile uses
  a general oral property window (MW 250–500, TPSA 40–130, no CNS floor). Whether the
  compartment term, scored as *spread* (the term written for MS), means anything in a
  disease where every effective agent acts peripherally is not established, so I have
  recorded it as unvalidated.
* **The panel is short on purpose.** Few agents have a randomised trial in GBS. Padding
  the panel with agents never tested in it would have added ranked names and no
  information. I dropped subcutaneous immunoglobulin as a redundancy control for that
  reason: it is approved for CIDP, not GBS, so it would have been an extrapolation.
* **Most of what works is not chemistry.** IVIG and plasma exchange are a biologic and a
  procedure, and the newest candidates are antibodies and enzymes. Nine of the 16 agents
  have no structure, so the novelty reference set is 7 structures, the smallest of the
  five, and novelty figures here carry less weight.
* **Two agent records I had to decide about.** The second IVIG course is the same drug as
  IVIG, so it has identical target effects and is excluded from the redundancy pair by
  construction; I kept it because a randomised trial (SID-GBS) found no benefit and more
  serious adverse events (35% against 16%), which makes it a clean safety-penalty control.
  Fingolimod failed a phase 3 in CIDP, not GBS, so it is a negative control from a related
  disease and is labelled that way.
* **A new risk vocabulary.** Respiratory depression carries the highest weight, because the
  disease weakens the respiratory muscles and a sedating pain drug can tip a patient into
  failure. Thromboembolism and meningococcal infection follow. The eight domains share
  only `cardiac` and `hepatic` with the other diseases, so no test had to be widened this
  time.

### Verifying the controls

Each control was checked against a source before it was declared: the methylprednisolone
trial (242 patients, no benefit), the interferon beta-1a add-on trial (no significant
improvement), the eculizumab phase 2 (33 patients, too small to prove efficacy; inconclusive,
so not a control), the SID-GBS second-dose trial, the positive tanruprubart phase 3, the
imlifidase phase 2, and the fingolimod CIDP failure. The trial summaries came from search
results, not the primary papers, which the calibration tool records.

### Problems found during the build

* **STRING symbol resolution, and a correction to Phase 8.** Three signature genes are
  missing from the GBS network. Querying STRING directly for each showed `IGHG1` and `MPZ`
  are answered "not found" and `VEGFA` resolves to a different protein (`COL18A1`). The
  same lookup for `AQP4` (missing from the epilepsy network) also returns "not found", so
  my Phase 8 note that it had "no interactions at the 0.4 cutoff" was wrong; it is a
  symbol-recognition failure. Corrected in the epilepsy registry entry and protocol. The
  campaign protocol's network step now says to query STRING directly for each absent symbol
  before recording a reason.
* **The screen was launched unbuffered** (`python -u`), so its progress was visible.

### Combination screen

16 + 120 + 518 combinations (42 triples were not enumerated because a pair inside them was
excluded), `--seed 7`, seconds.

* Best reversal: tanruprubart alone **8.06%**, tanruprubart + methylprednisolone **13.13%**,
  IVIG + tanruprubart + methylprednisolone **16.72%**. Against the panel's ceiling (32 of 78
  genes targeted; full-reversal 46.9%, pooled-panel 29.8%) the best triple captures 35.6% and
  56.0%, the highest of the five, which reflects a tiny panel of broad-acting agents and not
  anything about GBS.
* **Methylprednisolone is in the best pair and triple**, although a 242-patient trial found it
  no better than placebo. It is the third-highest single agent (5.06%), level with plasma
  exchange (5.10%) and above IVIG (4.98%).
* Removing agents with a null trial, the best pair is **IVIG + tanruprubart** (12.02%,
  *q* = 0.018) and the lowest-burden alternative is efgartigimod + tanruprubart (10.21%). No
  triple clearly earns its place: the best gains +0.017 over its best pair.
* **79.2% of triples have a negative gain over their best pair** (median −0.0857), close to
  epilepsy's 83.4%.
* Bootstrap top-25 Jaccard is 0.598 at order 2 (the first above 0.5) and 0.360 at order 3, but
  the top 25 of 117 pairs is 21% of the space, so these are not comparable with the larger
  screens.
* Every one of the top six order-2 strata contains a symptomatic axis (pain or conduction),
  and the axis with the largest gap (`nerve_repair_promotion`, 1.00) has no agent in the panel,
  so the screen cannot rank anything on it.

**The screen fails an external combination check.** The top approved-only pair is IVIG +
plasma exchange at 8.80% reversal against 5.10% and 4.98% for the two singles. I searched
for a trial of that pairing and found one: 383 patients randomised to plasma exchange, IVIG,
or plasma exchange followed by IVIG (*Lancet* 1997), which found the two therapies equally
effective and the combination without a significant advantage. The score predicted a gain
that a randomised trial found does not exist, which is the clearest external check available
and it goes against the method. Signature reversal adds across mechanisms and clinical benefit
saturates.

Controls: gabapentin and pregabalin are excluded as expected. **The safety controls
(eculizumab, second IVIG course) do not reach the top 25** at any order, unlike tacrine in
Alzheimer's and vigabatrin and retigabine in epilepsy. I do not think the scorer prices
toxicity better here; they are not the narrowest agents (reversal efficiency 0.66 and 0.31),
so they do not get the advantage that put vigabatrin first. Two of the three negative controls
reach the top 25 (methylprednisolone 14th, fingolimod 16th).

### Calibration

Six agents have a sourced outcome (three that worked, three that did not), so I ran the coarse
check (`python -m tools.calibrate_gbs_efficacy`). The effective group scores higher on
signature reversal (AUC 0.89), but with three against three the exact *p* is 0.100, so it is
not evidence of separation. The reason is the steroid: methylprednisolone scores between plasma
exchange and IVIG, so the score cannot tell it from the established therapies. I curated its
cytokine effects broadly, knowing what a steroid does to cytokine transcripts, so this is the
same circularity as in MS.

### Design campaign

Run under RDKit and qiskit, `--k 2 --arms 3 --top 4 --quantum-benchmark`:

* 14-requirement profile led by `MMP9` (0.818), `C5AR1` (0.743), `CSF1R`. **Seven of fourteen
  targets were unreachable**; six pharmacophores were added (82 fragments) and the gap went to
  zero, with the other four diseases' lists unchanged.
* The disease's own targets (C1q, C5, IgG, FcRn) score 0.05 to 0.2 for small-molecule
  tractability and are routed around; a test asserts it.
* Enumeration, exact eigensolver and QAOA all reach +0.1113; QAOA falls short only at depth 1.
* Leading design `C12H15N5O2`, MW 261.3, cLogP 0.79, TPSA 92.1: a 4-aminopyridine arm (the
  Kv1 blocker scaffold of dalfampridine) fused to an MMP9-inhibiting hydroxamic acid. **Reversal
  is 4.04%, about half of tanruprubart's 8.06%.** It addresses conduction and barrier
  protection, not the 1.00 gap, and `C5AR1` is not on the leading designs.
* All four designs share the same two arms. The pipeline's structural-alert list returned
  nothing for the hydroxamic acid, a known liability class, and 4-aminopyridine's seizure risk
  is not in the output either.
* **The stage inversion held only just**: rank 2 built 1.585 against 1.552 for ranks 1 and 3, a
  margin of about 2%, the weakest confirmation of the five.
* The design axes line again carries MS labels (`cns_innate`, `neuroprotection`) from the shared
  `mmp_hydroxamate` fragment, the vocabulary leak I noted in Phase 7 and have not fixed.

### Tests

**346 passed, 24 skipped** without RDKit; **370 passed** with it (322 / 346 before). New
checks: GBS is the only peripheral disease and the profile has no CNS floor, the central protein
targets are routed around, the reference set is small because the treatments are not small
molecules, respiratory depression is the heaviest weight, and gabapentin and pregabalin are
excluded as duplicates. No existing test needed relaxing.

### Reflection

> The best-evidenced results in GBS are the ones the method is least able to see. IVIG, plasma
> exchange and the antibodies act on proteins, so they are scored through proxy genes, and the
> one external combination check I could find went against the screen. I would rather have that
> recorded than a ranked list of pairs that looks like an answer.
>
> The small panel changed how I read the numbers. Stability, ceilings and stratum sizes all move
> with panel size, so several figures that looked like findings (the high Jaccard, the high
> ceiling capture) are properties of having 16 agents.

### Next steps

1. **Report the screen's prediction beside any published combination trial**, as a standing
   check, starting with the IVIG and plasma exchange result.
2. **A time axis.** GBS treatment works if started within about two weeks, and a ranking without
   time cannot say when to give it.
3. Give protein-level agents a scoring path that does not run through a transcript proxy; GBS is
   the disease where that matters most.
4. Fix the max-domain safety term, the narrow-agent advantage in `reversal_efficiency`, and the
   missing `withdrawn` flag together, evaluated on all five diseases at once.
5. Re-annotate fragment axes per disease, so a design's axis line never carries another disease's
   vocabulary.
6. Test the IVIG + tanruprubart pairing directly; the one pairing already tested (IVIG + plasma
   exchange) showed no advantage.

### Addendum (2026-09-27): where quantum computing is and is not used

Recorded for all five diseases (MS, Parkinson's, Alzheimer's, epilepsy, Guillain-Barré),
because the project is described as hybrid quantum-classical and the write-ups did not say
which stage was which.

* **The k = 1, 2, 3 combination screens are classical in every disease.** They enumerate every
  combination exhaustively (from 654 rows for Guillain-Barré to 31,837 for MS), so the answer is
  exact and there is no search problem for a quantum heuristic to help with. The cost is
  classical statistics (permutation null, bootstrap, weight sensitivity), not search.
* **QAOA ran only as a benchmark of the design campaign's fragment selection**, a 10-variable
  QUBO, on a classical simulator (Qiskit Aer). Enumeration takes about 0.07 s and the QAOA depth
  sweep 5 to 6 s. The arm sets carried into assembly come from enumeration; QAOA's output is not
  used downstream. At ten variables there are 1,024 states, so no quantum advantage can be
  demonstrated or expected.
* **QAOA matched the enumeration optimum in all five diseases**, so the formulation transfers to
  a quantum algorithm. By depth: MS fell short at depth 3 (+0.0355 against +0.0443), Parkinson's
  at depth 1 (+0.0732 against +0.0830), Alzheimer's at depths 1 and 5 (+0.0404 against +0.0724),
  epilepsy dipped at depth 2 (−0.0573 against +0.0868) and recovered, and Guillain-Barré fell
  short at depth 1 (+0.1025 against +0.1113).
* **Molecule assembly is a classical stochastic search.** No real quantum hardware was used
  anywhere.
* The foundation-phase Hamiltonian (Day 8) was solved with an exact minimum eigensolver running
  classically, and the Day 9 benchmark compared exact, greedy and random classical solvers. That
  is the argument for stronger optimisers at larger scale, not a result obtained with a quantum
  one.

No finding in any of the five diseases depends on quantum computing. The regime where quantum
optimisation might matter, selections from hundreds of candidates at high order, is not one any
panel here reaches. Each disease's protocol document now has a section stating this with its own
numbers.

### Addendum (2026-09-27): applying the quantum machinery to the combination problem

The previous addendum recorded that quantum computing was used only as a benchmark of the
ten-variable fragment selection, and that no finding depended on it. The project is built around
quantum optimisation, so I pointed the same Hamiltonian machinery at the combination problem
itself: which k = 4 to 6 drugs to combine, the question that lies beyond the exhaustive k = 3
screen. Full write-up in [quantum_regimen_selection.md](quantum_regimen_selection.md).

**What was built.**

* A QUBO for regimen selection ([core/quantum/regimen_selection.py](../core/quantum/regimen_selection.py)).
  Every k-ary term in the scorer is a mean of its pairwise form, so a k-subset's score is
  approximated by the sum of its pair scores, with a penalty on pairs the redundancy rule
  excludes. The existing enumeration, exact eigensolver and QAOA solvers work on it unchanged.
* Two objectives on every problem: `qubo_objective` (what the solvers optimise) and
  `exact_objective` (the true k-ary score). Every solver's answer is re-scored with the true
  scorer and ranked against all feasible subsets in the pool, so solvers are judged against ground
  truth and not against each other.
* A constraint-preserving QAOA (Dicke-state start, XY mixer) and a CVaR variant
  ([core/quantum/constrained_qaoa.py](../core/quantum/constrained_qaoa.py)), run as exact
  statevector simulations on the feasible subspace. Classical baselines: greedy, simulated
  annealing, random, and random with as many draws as the quantum solvers' shots.
* 11 tests ([tests/test_regimen_selection.py](../tests/test_regimen_selection.py)); the suite is at 357 passing.

**Why the constrained QAOA.** The project's existing penalty-based Qiskit QAOA did badly on this
problem. At k = 6 on Guillain-Barré it returned a regimen ranked 588th of 8,008, worse than 100
random picks (115th). Folding "choose exactly k" into a penalty over all 2^n bitstrings leaves most
of the space infeasible, and the optimiser spends its budget avoiding it. Restricting to the
feasible subspace fixes that.

**Results, all five diseases** (15 runs: k = 4, 5, 6 for each; the pool is the 18 best agents for MS,
Parkinson's, Alzheimer's and epilepsy, and the whole 16-agent panel for Guillain-Barré; every solver
is judged against the true optimum from exhaustively scoring the pool).

* **The surrogate loses fidelity as k grows, unevenly.** Spearman with the true score stays about 0.9
  in Parkinson's and Guillain-Barré, but falls from 0.91 to 0.44 in MS and from 0.93 to 0.75 in
  epilepsy. Even where it holds, the surrogate's own optimum can sit hundreds of places down the true
  ranking (Alzheimer's k = 6: 328th of 18,564; epilepsy k = 6: 513th). The surrogate, not the solver,
  is the binding limit.
* **The project's original penalty QAOA was the wrong formulation.** It returned no feasible selection
  at any depth in 2 of the 15 runs and otherwise ranked in the hundreds to thousands (median 1,290),
  beating matched random sampling in only 2 of the 13 runs where it answered.
* **The constraint-preserving QAOA works, and CVaR is better.** It matched exact enumeration in 9 of 15
  runs and beat matched random in 10, tied 4 and lost 1. With CVaR it matched enumeration in 12 of 15
  (the misses: MS k = 6, Alzheimer's k = 5 and k = 6).
* **Simulated annealing matched enumeration in all 15 runs in about 10 ms; greedy in only 5** (all of
  Guillain-Barré, which flatters it, and two MS runs).
* **A worse solver can beat the surrogate optimum on the true score, because the surrogate is wrong**:
  greedy reached rank 5 against 20 in MS k = 4 and rank 10 against 61 in epilepsy k = 5.
* **The final quantum state concentrates probability but not on the optimum.** With the mean objective it
  puts 13 to 36 times the uniform probability on the best 1% of regimens in every run, but on the single
  best regimen it is above uniform in only 6 of 15 (and zero in epilepsy k = 6). CVaR is above uniform in
  all 15 (by 1.5 to 56 times).
* **Annealing on the full panel** (up to 75 million subsets in MS) beat the best of 3,000 random regimens on
  the true score in 5 of 15 cases, including all three in MS, the only disease large enough that random
  draws cannot compete.
* **The best 4-, 5- and 6-drug regimens** within each pool are in the regimen-selection document. The
  epilepsy six-drug regimen contains retigabine and vigabatrin, the two failed safety controls, so it is
  the composite failure again and not a recommendation.

**A near miss.** The quantum solvers draw 4,096 shots from a space of 1,820 to 8,008 subsets, so
even uniform random sampling with the same draws finds the optimum some of the time (it does at
k = 4, because 4,096 exceeds 1,820). I had started reading "the best sampled regimen was the
optimum" as evidence, and it is not. The tables use random sampling with matched shots as the
baseline and report the probability the final state places on good subsets, which sampling cannot
hide.

**What this does and does not show.** It runs on a classical simulator capped at about 20 qubits, and
at that size exhaustive search is instant, so no quantum advantage can be shown. The regimens
reported still come from exhaustive classical scoring within the pool, and the quantum solvers are
judged on whether they recover them. What it does establish is that the pipeline works end to end on
the real combination problem, that the penalty formulation is the wrong one for a cardinality
constraint, and that on the sizes a simulator can hold simulated annealing is as good as anything
quantum I tried (greedy is not). A first
hardware run would face noise at the depths that matter, and I would not expect it to match the
simulator.

**Next steps.** A better surrogate with
higher-order terms, since the pairwise approximation is the binding limit. Compile the Dicke-state
preparation and XY mixer to gates and count their depth, the concrete step towards a device. Try a
pool of hundreds of agents at high order with classical heuristics, which is the regime a simulator
cannot verify.
\n
### Addendum (2026-09-27): a pipeline for IBM quantum hardware

I wanted to know whether real hardware could take the regimen problem beyond the ~20 qubits a classical
simulator handles. I looked at what is free. IBM's open plan is described as giving real processors of up to
127 qubits with about 10 minutes of quantum time a month (from search summaries, one third-party; not confirmed
on IBM's own pages). D-Wave's free trial is about a minute of annealing time. I chose IBM. Full write-up in
[ibm_quantum_hardware.md](ibm_quantum_hardware.md).

**No hardware run has been made.** There are no IBM credentials on this machine and nothing has been sent
anywhere. I built everything short of that.

* **A separate environment.** A dry-run install of IBM's runtime library into the working environment showed pip
  would upgrade Qiskit from 1.4.5 to 2.5.2, risking every earlier result, so I did not install it there.
  `qbio-ibm-env` holds Qiskit 2.5.2 and the runtime, and the two environments are decoupled through a JSON spec.
* **An anonymous spec.** It holds numbers only (qubit count, k, cost coefficients, mixer edges, initial bitstring,
  angles): no drug names, gene names or disease. The index-to-agent mapping stays in a private local file the run
  script never reads. A test asserts it, and the run script refuses a spec not marked anonymous.
* **Angles are optimised on a simulator and only the fixed circuit goes to hardware**, so scarce quantum time is not
  spent on the variational loop. The cost is that angles cannot be optimised beyond ~20 qubits.
* **The gate circuit is checked against the simulator.** It matches the subspace simulation to 1e-8 bitstring by
  bitstring and never leaves the subspace with exactly k ones (`tests/test_gate_qaoa.py`). The fraction of shots
  with weight k is then a model-free noise gauge on a real device.

**What a free noise model of a real 127-qubit device (Sherbrooke) predicts**, run locally with no account, for
Guillain-Barré at k = 4, two layers. This is a simulation of noise, not a hardware run.

| qubits | two-qubit gates | shots with exactly k ones | random bits | distance from ideal | verdict |
|---|---|---|---|---|---|
| 6 | 130 | 0.564 | 0.234 | 0.19 | clear signal |
| 8 | 259 | 0.391 | 0.273 | 0.42 | partial signal |
| 10 | 410 | 0.250 | 0.205 | 0.83 | none |
| 12 | 496 | 0.178 | 0.121 | 0.93 | none |
| 14 | 850 | 0.108 | 0.061 | 0.98 | none |
| 16 | 907 | 0.063 | 0.028 | 0.98 | none |

Signal survives to about 8 qubits and is gone from 10. The problem is dense (every pair of agents interacts), so
two-qubit gates grow from 130 to 907 between 6 and 16 qubits and the signal decays exponentially in the gate
count. **Submitting a 20-, 30- or 64-qubit version is possible, and the model says it would return noise.** More
physical qubits do not help unless the problem is made sparse or error rates fall by an order of magnitude.

**Two things I corrected along the way.** My first verdict rule was too strict (it called 8 qubits "no signal" when
the distribution was clearly closer to ideal than uniform), and at 6 and 8 qubits the space has only 15 and 70
feasible subsets, so 2,000 shots visit most of them and "the best measured regimen ranked first" means nothing. The
analysis now warns when shots cover more than half the feasible subsets.

**What a real run could show.** Whether the noise model is right on 6 and 8 qubits, and that the pipeline works.
Not a quantum advantage (exhaustive search is instant and annealing already matches it), and not the sizes that
matter. **To run it** I need a credential that only I can create: an IBM Quantum Platform account and API key set in
my own terminal as `QISKIT_IBM_TOKEN`, never pasted into the repository or a chat. The steps are in the document.

**Next steps.** Make the IBM account and run 6 and 8 qubits, comparing the fraction of shots with weight k with the
predictions above. Try a sparse formulation of the problem, which is the only route the model suggests to more
usable qubits. Compare with D-Wave annealing, which is a natural fit for a QUBO but a different algorithm.

### First real hardware run (ibm_fez, 2026-09-27)

I ran the 6- and 8-qubit Guillain-Barré circuits on **ibm_fez** (156 qubits, free open plan), 4,000 shots each, 3
quantum seconds per job. Only the anonymous numeric circuit was sent. The noise model was close on both.

| qubits | 2-qubit gates | shots with weight k (hardware) | noise model | random bits | TV from ideal (hardware) | verdict |
|---|---|---|---|---|---|---|
| 6 | 136 | 0.582 | 0.564 | 0.234 | 0.14 | clear signal |
| 8 | 262 | 0.431 | 0.391 | 0.273 | 0.36 | partial signal |

The device did slightly better than the model predicted, at both sizes, and the verdicts match. The model is a
reasonable guide, so its prediction that signal is gone from 10 qubits is now something I trust more, though I have
not run 10 or above on hardware. The most-measured regimen was the same as in the model at both sizes.

**What this does not show.** At 6 and 8 qubits the 4,000 shots visited 100% and 99% of all feasible regimens, so
"the best measured regimen ranked first" means nothing here. The circuit is not doing a search that beats
exhaustive enumeration (15 and 70 subsets). It shows the pipeline works on a real device and the noise gauge is
sound. It is not a quantum advantage.

### Sparse circuits (noise model)

The dense problem was the reason signal died from 10 qubits, so I added `--keep N`, which keeps each agent's N
strongest couplings and drops the rest. With N = 2 the ZZ terms fall from 45, 66 and 120 to 15, 18 and 23 at 10, 12
and 16 qubits, and the noise model gives weight-k fractions of 0.36, 0.35 and 0.23 against random 0.21, 0.12 and
0.03, so 16 qubits keeps a partial signal where the dense circuit had none. **The catch is mine to own:** the
noiseless sparse circuit already picks poorly (its most likely regimen ranks 106 of 210, 88 of 495 and 335 of 1,820
by the true score), so I bought hardware survivability with problem fidelity. The gauge I use only measures noise,
so it cannot tell me this. I have not run any of it on hardware.

### 10 qubits on hardware: the model was wrong

I ran the dense 10-qubit circuit on ibm_fez (410 two-qubit gates, 4,000 shots). 28.8% of shots kept exactly four
agents against 20.5% for random bits, and the distance from the ideal distribution was 0.67 against 0.83 in the
noise model. I had written that signal was gone from 10 qubits, and the device says partial. My earlier line that I
"trust the model more" after 6 and 8 qubits was too strong: it has now been too pessimistic three times running, so
it is a conservative floor, not a forecast. The margin over random is small, and the gauge still measures noise, not
the quality of the regimens. I have not run 12 or above on hardware.

### 12 dense and 16 sparse on hardware

Dense 12 qubits (474 gates): 22.0% of shots kept exactly four agents against 12.1% for random bits, partial signal,
where the noise model said none. Sparse 16 qubits (355 gates): 20.3% against 2.8% for random bits, partial signal,
and this time the device was slightly *below* the model's 23.1%. So my "the model is a conservative floor" line from
the 10-qubit entry is also too strong: it was pessimistic on the four dense circuits and mildly optimistic on the one
sparse one. Sparsity did what I wanted, since 16 qubits survives at roughly the gate count of dense 10. What it did
not do is fix the thing I flagged before: the noiseless sparse circuit ranks its own favourite regimen 335 of 1,820,
so I have shown a circuit that survives the device, not one that finds good regimens.

### Better couplings, and I had blamed the wrong thing

I added a fitted sparsifier (orthogonal matching pursuit with refit weights) and compared it with keeping the
strongest couplings at the same edge count. It tracks the dense objective better at 10 and 12 qubits (Spearman 0.925
against 0.878, and 0.906 against 0.866) and slightly worse at 16 (0.836 against 0.845), so it is no clear win. Then I
ran the dense circuit for comparison and found it is **just as poor**: at two layers the noiseless state sits with
probability 1.000 on one regimen, the same for dense and sparse, and it is not the optimum. So my entry on sparse
circuits, where I said I had "bought survivability with problem fidelity", was wrong about the cause. The problem is
the circuit, not the sparsity: it starts from one computational-basis subset (0, 1, 2, 3) and a two-layer ring mixer
only reaches subsets a couple of hops away. The exact simulator I used earlier starts from the Dicke superposition
and does not have this problem. Deeper circuits spread the state (16 qubits: the optimum's probability goes from 0 at
two layers to 0.018 at six), at more gates. What I still have not done is the fix that targets the cause: a
Dicke-state start, a warm start from the annealing solution, or more layers on hardware.

### Dicke-state start: it did not help, and it changed how I read the last result

I built the Dicke-state preparation, found the gate layout by checking the statevector against the exact state for
several sizes (my recollection of the paper's layout did not survive that, and the first search failed until I
fixed my own window placement), and confirmed the circuit matches the exact simulation. Then I measured. With the
Dicke start, the noiseless circuit puts about the uniform amount of probability on the true top 1% of regimens
(0.010 to 0.015 against 0.008 to 0.010) and its mean rank is 0.39 to 0.46 against 0.5 for random. It is barely better
than random. The basis-start circuit's good mean rank (0.18) turns out not to be search at all: my pool is sorted by
monotherapy score, so the fixed start (0, 1, 2, 3) is the four best single agents and two layers stay near it. I had
been reading a classical prior as circuit quality. So both fixes I proposed (better couplings, a Dicke start) did
nothing for quality, and I have not sent a Dicke circuit to hardware because the noiseless version has nothing worth
preserving. The consistent picture from the simulator work and this is that shallow QAOA does not find the top
regimens here; what the hardware runs show is noise tolerance only.

### Deeper circuits and CVaR: the first thing that moved the top end

With the mean-cost objective, going from 4 to 12 layers never lifted the top-1% probability above uniform, at 12 or 16
qubits. Switching the objective to CVaR (mean cost of the best 5% of the mass) did. At 12 qubits, 8 layers put 0.082
on the true top 1% (about 10 times uniform) and 0.050 on the surrogate optimum (25 times uniform). At 16 qubits it took
12 layers to get 0.055 and 0.006. So the objective mattered more than depth, which fits the simulator work where CVaR
was the one thing that helped. My caveats: this is noiseless simulation only, the concentration weakens with size
(at 16 qubits 4 layers is still at chance), the optimiser had a small budget so these are not upper bounds, and the
gate counts are far past what ibm_fez preserved (a dense 16-qubit circuit is 907 two-qubit gates at two layers, so
twelve layers is not something I can measure on the device). Exhaustive search is instant at these sizes and
annealing already matches it, so this is still not an advantage; it is the first evidence that the algorithm itself
can concentrate on good regimens when it is given the right objective and enough depth.

### Sparse CVaR: it lost, so I kept the dense circuit

I tried CVaR on the sparse circuits, with both the strongest-coupling and the fitted rules, hoping to get the
concentration I saw on the dense circuit at a gate count the device can hold. It did not work. At 12 qubits the top-1%
probability was 0.006 to 0.014 (uniform 0.008) against 0.082 for dense at 8 layers, and at 16 qubits it reached only
0.024 to 0.025 at 12 layers against 0.055 for dense. So the couplings I dropped were carrying the signal CVaR needs,
and the circuits small enough for the hardware are the ones that cannot search. Nothing needed reverting because the
options were all opt-in, and the default stays dense. Where I am: the hardware runs measure noise tolerance, the
simulator shows CVaR can concentrate on good regimens only with dense couplings and 8 to 12 layers, and those two
things do not overlap at any size I can run on ibm_fez.
