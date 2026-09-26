# Higher-order regimen selection as a quantum optimisation problem

The k = 1, 2, 3 combination screens are classical because they are exhaustive: every
combination is scored, so there is nothing to optimise. Beyond k = 3 the question changes.
Real regimens can have four or five agents, the number of subsets grows combinatorially,
and the honest question becomes *which k agents from a pool* — the selection problem the
project's Hamiltonian machinery was built for, but which had only been pointed at
pharmacophore fragments. This document records applying it to the combination problem
itself, and what came of it.

```bash
python -m experiments.quantum.run_regimen_selection --disease guillain_barre --pool 16 --k 4 5 6 --scale-test
python -m experiments.quantum.summarize
pytest -q tests/test_regimen_selection.py
```

> **Status.** All five diseases have run (15 disease-and-k experiments). Guillain-Barré, whose
> 16-agent panel needs no pool restriction, is worked through in §5; the results across all five
> diseases are in §6, and they are less flattering to the quantum solvers than §5 alone suggests.

## 1. What is new

| | before | now |
|---|---|---|
| What the quantum solvers were pointed at | 10 pharmacophore fragments | **which k drugs to combine, k = 4 to 6** |
| How solutions were judged | agreement with enumeration of the same QUBO | **re-scored with the true k-ary scorer** and ranked against every feasible subset in the pool |
| QAOA | penalty-based (Qiskit), one variant | **penalty-based, constraint-preserving, and CVaR** variants |
| Baselines | none | greedy, simulated annealing, random, and random with matched shots |
| Whether the surrogate was checked | not applicable | **measured**: rank correlation with the true score over all subsets |

## 2. The formulation

Every k-ary term in the combination scorer is defined as the mean of its pairwise form, so a
k-subset's score is approximated by the mean of the composite scores of the pairs inside it:

    maximise   sum over pairs i<j of  q_ij * x_i * x_j      subject to   sum_i x_i = k

with `q_ij` the composite score of the pair, and a penalty on pairs the redundancy rule would
exclude from the primary ranking. This is a QUBO. It is **an approximation**: Bliss
saturation on shared targets, the safety union and the regimen burden are not pairwise. So
the problem class carries two objectives, as the fragment problem does. `qubo_objective` is
what the solvers optimise, and `exact_objective` re-scores a selection with the true scorer.
Code: [core/quantum/regimen_selection.py](../core/quantum/regimen_selection.py).

**The pool.** A simulator cannot hold a whole panel, so a pool of at most 18 agents (the
best by monotherapy composite) is chosen first. That is a real restriction, because an agent
weak alone and strong in combination can be dropped before any solver sees it. Guillain-Barré
has 16 eligible agents, so its pool is the whole panel.

## 3. The solvers

| Solver | What it is |
|---|---|
| Enumeration | Exhaustive search of the surrogate: its exact optimum |
| Exact eigensolver | Classical diagonalisation of the Ising Hamiltonian, via Qiskit |
| QAOA, penalty | The project's existing Qiskit QAOA: the constraint `sum(x) = k` folded in as a penalty over all `2^n` bitstrings |
| **QAOA, constrained** | **Dicke-state start with an XY (hopping) mixer**, which preserves the number of selected agents exactly, so every state visited is feasible and no penalty is needed |
| **QAOA, constrained + CVaR** | The same, optimising the mean of the best 2% of the probability mass rather than the overall mean |
| Greedy, annealing, random | Classical baselines; random is run with 100 draws and with 4,096 draws to match the quantum solvers' shots |

The constrained variants are an **exact statevector simulation on the feasible subspace**
([core/quantum/constrained_qaoa.py](../core/quantum/constrained_qaoa.py)), not Qiskit
circuits. They are the same algorithm a gate-model device would run, with the mixer and cost
applied exactly instead of compiled to gates. Working on the subspace (`C(18, 6)` = 18,564
amplitudes, against `2^18` for the full space) is what makes 16 to 18 qubits tractable. The
penalty variant is why they were written: on this problem it did badly (§5).

## 4. What this can and cannot show

**No quantum advantage can be shown here.** Everything runs on a classical simulator, capped
at about 20 qubits, and at that size exhaustive enumeration finishes in seconds and greedy or
annealing in milliseconds. What can be shown is:

1. whether the pairwise surrogate is a faithful stand-in for the k-ary scorer;
2. whether the quantum algorithms find what exhaustive search finds, and how that changes as
   the problem grows;
3. how they compare with classical heuristics judged on the same ground truth.

**The reported best regimens do not depend on the quantum solvers.** Within a pool the true
optimum is known by exhaustively scoring every subset. The quantum solvers are judged on
whether they recover it. That is the honest position for a project run on a simulator, and it
is stated in every disease's document.

**A shots caveat that nearly produced a false positive.** The quantum solvers draw 4,096 shots
from a space of 1,820 to 8,008 subsets. At those sizes even *uniform random* sampling with the
same number of draws finds the optimum some of the time, so "the best sampled regimen was the
optimum" is weak evidence. The tables therefore report a **matched-shot random baseline** and
the probability the final state places on good subsets, which sampling cannot hide.

## 5. A worked example — Guillain-Barré (16 agents, no pool restriction)

**The surrogate.** Rank correlation with the true k-ary score across every feasible subset is
about 0.9 at each k, so it is a good approximation. But the surrogate's own optimum
**drifts down the true ranking as k grows**:

| k | feasible subsets | Spearman | surrogate optimum's true rank |
|---|---|---|---|
| 4 | 1,820 | 0.90 | 2 |
| 5 | 4,368 | 0.91 | 13 |
| 6 | 8,008 | 0.91 | 54 |

A solver that finds the surrogate's optimum perfectly is therefore still 54th of 8,008 at
k = 6, because the surrogate has lost information the true scorer uses.

**Where each solver's regimen ranked among all feasible subsets** (1 = the true optimum):

| k | enumeration | greedy | annealing | random (100) | random (4,096) | QAOA, penalty | QAOA, constrained | QAOA, constrained + CVaR |
|---|---|---|---|---|---|---|---|---|
| 4 | 2 | 2 | 2 | 6 | 2 | **258** | 2 | 2 |
| 5 | 13 | 13 | 13 | 9 | 104 | **237** | **7** | 13 |
| 6 | 54 | 54 | 54 | 115 | 308 | **588** | 54 | 54 |

- **The penalty QAOA fails**, ranked in the hundreds and worse than 100 random picks at every
  k. Encoding "choose exactly k" as a penalty over all `2^n` bitstrings is the cause: most of
  the space is infeasible and the optimiser spends its budget avoiding it.
- **The constrained QAOA works**: it recovers the surrogate optimum at k = 4 and 6 and, at
  k = 5, returns a regimen ranked 7th, *better on the true score than the surrogate's own
  optimum* (13th), by sampling a neighbour. **CVaR recovers the surrogate optimum at all
  three k.**
- **Matched random sampling** finds the optimum at k = 4 only because 4,096 draws exceed the
  1,820 subsets. At k = 5 and 6 it ranks 104th and 308th, so the constrained variants beat it
  where the comparison is meaningful.
- **Greedy, annealing, enumeration and the exact eigensolver all reach the surrogate optimum
  at every k here, in milliseconds** (enumeration alone grows to about 1.5 s at k = 6, and the
  constrained QAOA takes 5 to 26 s). Greedy does *not* do this in the other diseases (§6.2), so
  Guillain-Barré flatters it.

**How the final state of the constrained QAOA is distributed**, which sampling cannot hide:

| k | objective | top-1% probability | enrichment | P(surrogate optimum) | uniform P | best depth |
|---|---|---|---|---|---|---|
| 4 | mean | 0.132 | 13.2× | 1.9e-04 | 5.5e-04 | 4 |
| 4 | CVaR | 0.076 | 7.6× | 1.8e-03 | 5.5e-04 | 4 |
| 5 | mean | 0.198 | 19.8× | 4.9e-05 | 2.3e-04 | 2 |
| 5 | CVaR | 0.104 | 10.4× | 3.6e-04 | 2.3e-04 | 4 |
| 6 | mean | 0.271 | 27.1× | 1.9e-04 | 1.3e-04 | 3 |
| 6 | CVaR | 0.111 | 11.1× | 5.2e-04 | 1.3e-04 | 4 |

The mean objective puts 13 to 27 times the uniform probability on the best 1% of regimens,
but **little on the single best one**: at k = 4 and 5 its probability of the optimum is
*below* uniform. That is the state a good average produces, not a focused one. CVaR trades
top-1% enrichment for focus, raising the optimum's probability to 1.6 to 3.3 times uniform
at k = 4 and 5 and 4.0 times at k = 6. Neither variant is strong: probabilities of order
10^-4 to 10^-3 on the optimum are why the answer came from sampling, and why matched-shot
random is the honest comparison.

**Beyond simulator size.** Annealing on the full panel (also 16 agents here) reaches the
surrogate optimum, and its true score (1.370 at k = 6) is *below* the best of 3,000 random
regimens (1.423), which have been scored with the true scorer. So on this problem
optimising the surrogate harder does not find the best true regimen: the surrogate is the
limit, not the solver.

## 6. Results across all five diseases

The pool is the 18 best agents by monotherapy composite for MS, Parkinson's, Alzheimer's and
epilepsy (out of 64, 35, 36 and 37 eligible), and the whole panel for Guillain-Barré. Each row is
one Hamiltonian, and every solver is judged against the true optimum found by exhaustively scoring
every feasible subset in the pool.

### 6.1 The surrogate loses fidelity as k grows, unevenly

| disease | k = 4 | k = 5 | k = 6 |
|---|---|---|---|
| Multiple sclerosis | 0.91 (surrogate optimum ranked 20 of 3,060) | 0.71 (19 of 8,568) | **0.44** (4 of 18,564) |
| Parkinson's | 0.92 (23) | 0.91 (24) | 0.90 (14) |
| Alzheimer's | 0.95 (13) | 0.94 (10) | 0.93 (**328**) |
| Epilepsy | 0.93 (11) | 0.85 (61) | **0.75** (**513**) |
| Guillain-Barré | 0.90 (2 of 1,820) | 0.91 (13 of 4,368) | 0.91 (54 of 8,008) |

Cells are Spearman correlation with the true k-ary score across all subsets, and in brackets the
true rank of the surrogate's own optimum. Fidelity is stable in Parkinson's and Guillain-Barré and
degrades sharply in MS (0.91 to 0.44) and epilepsy (0.93 to 0.75). Even where the correlation
holds, the surrogate's optimum can sit hundreds of places down the true ranking (Alzheimer's k = 6,
epilepsy k = 6). **The surrogate, not the solver, is the binding limit.**

### 6.2 Where each solver's regimen ranked among all feasible subsets (1 = the true optimum)

| disease | k | enumeration | greedy | annealing | random (100) | random (4,096) | QAOA penalty | QAOA constrained | QAOA constrained + CVaR |
|---|---|---|---|---|---|---|---|---|---|
| MS | 4 | 20 | 5 | 20 | 33 | 160 | 1411 | 8 | 20 |
| MS | 5 | 19 | 19 | 19 | 37 | 380 | 105 | 39 | 19 |
| MS | 6 | 4 | 4 | 4 | 196 | 446 | 4811 | 26 | 446 |
| Parkinson's | 4 | 23 | 84 | 23 | 23 | 23 | **failed** | 23 | 23 |
| Parkinson's | 5 | 24 | 54 | 24 | 50 | 30 | 1580 | 24 | 24 |
| Parkinson's | 6 | 14 | 86 | 14 | 292 | 30 | 4080 | 14 | 14 |
| Alzheimer's | 4 | 13 | 203 | 13 | 97 | 48 | **failed** | 13 | 13 |
| Alzheimer's | 5 | 10 | 471 | 10 | 448 | 10 | 1290 | 10 | 313 |
| Alzheimer's | 6 | 328 | 1365 | 328 | 2406 | 105 | 5520 | 741 | 218 |
| Epilepsy | 4 | 11 | 21 | 11 | 15 | 55 | 384 | 11 | 11 |
| Epilepsy | 5 | 61 | 10 | 61 | 30 | 61 | 3127 | 61 | 61 |
| Epilepsy | 6 | 513 | 174 | 513 | 942 | 942 | 277 | 713 | 513 |
| Guillain-Barré | 4 | 2 | 2 | 2 | 6 | 2 | 258 | 2 | 2 |
| Guillain-Barré | 5 | 13 | 13 | 13 | 9 | 104 | 237 | 7 | 13 |
| Guillain-Barré | 6 | 54 | 54 | 54 | 115 | 308 | 588 | 54 | 54 |

**"Failed"** means the penalty QAOA returned no feasible selection at any depth, so it produced no
answer at all, in 2 of the 15 runs. The scoreboard:

| Comparison (15 runs) | Result |
|---|---|
| Penalty QAOA (the project's original) against matched-shot random | beat it in 2 of the 13 runs where it produced an answer; median true rank 1,290 |
| Constrained QAOA against matched-shot random | wins 10, ties 4, loses 1 |
| Constrained QAOA + CVaR against matched-shot random | wins 9, ties 4, loses 2 |
| Constrained QAOA reaching the same rank as exact enumeration | 9 of 15 |
| Constrained QAOA + CVaR reaching the same rank as exact enumeration | **12 of 15** |
| Greedy reaching the same rank as exact enumeration | **5 of 15** (all Guillain-Barré and two MS runs) |
| Annealing reaching the same rank as exact enumeration | 15 of 15 |

Four things stand out.

- **The penalty QAOA is the wrong formulation for this problem.** It failed outright twice and
  otherwise ranked in the hundreds to thousands. The constraint-preserving variants fix that.
- **CVaR is the best of the quantum variants**, matching enumeration in 12 of 15 runs. It failed to
  match it in MS k = 6 (rank 446 against 4), Alzheimer's k = 5 (313 against 10) and Alzheimer's
  k = 6 (218, though that is better than the enumeration's 328).
- **Annealing is the best solver overall**, matching enumeration in all 15 runs in about 10
  milliseconds. Greedy is not reliable: it missed badly in Parkinson's and Alzheimer's (for
  example rank 1,365 against 328).
- **A worse solver can beat the surrogate optimum on the true score**, because the surrogate is
  wrong. Greedy reached rank 5 against enumeration's 20 in MS k = 4, and rank 10 against 61 in
  epilepsy k = 5. Solving the surrogate better is not the same as finding a better regimen.

**Matched random is a stronger baseline than it looks.** 4,096 draws cover 74%, 38% and 20% of the
3,060, 8,568 and 18,564 subsets of an 18-agent pool at k = 4, 5 and 6, so it finds good regimens
by coverage. It matched the surrogate optimum's rank in Parkinson's at k = 4 and Alzheimer's at
k = 5, and beat the constrained QAOA in Alzheimer's k = 6 (105 against 741). This is why "the QAOA found the optimum"
proved nothing on its own, and why the comparison needed a matched-shot baseline.

### 6.3 How the final state of the quantum solver is distributed

Sampling cannot hide this. Uniform would put 1% of the probability in the top 1% of regimens.

| Quantity | Constrained QAOA, mean objective | Constrained QAOA + CVaR |
|---|---|---|
| Probability in the top 1% of regimens | **13 to 36 times uniform**, in all 15 runs | 4.5 to 27 times uniform |
| Probability on the single best surrogate regimen against uniform | above uniform in 6 of 15, about equal in 2, **below uniform in 7** (in epilepsy k = 6 it is zero) | **above uniform in all 15**, by 1.5 to 56 times |

The mean objective concentrates probability on a broad good region and not on the best regimen.
CVaR trades some of that breadth for focus. Neither puts much probability on the optimum in
absolute terms (10^-4 to 10^-2), which is why the answers come from sampling and not from the
state itself.

### 6.4 Beyond simulator size: annealing on the whole panel

Annealing runs on the full panel (35 to 64 agents; up to 75 million subsets at k = 6 in MS),
beyond what a simulator holds and beyond where the true optimum can be verified. Scored with the
true scorer against the best of 3,000 random regimens:

| disease | k = 4 | k = 5 | k = 6 |
|---|---|---|---|
| MS (64 agents) | **1.624** vs 1.606 | **1.637** vs 1.611 | **1.650** vs 1.604 |
| Parkinson's (35) | 1.565 vs 1.585 | 1.600 vs 1.603 | 1.623 vs 1.632 |
| Alzheimer's (36) | **1.480** vs 1.467 | 1.553 vs 1.558 | 1.535 vs 1.556 |
| Epilepsy (37) | **1.483** vs 1.475 | 1.507 vs 1.554 | 1.508 vs 1.522 |
| Guillain-Barré (16) | 1.385 vs 1.389 | 1.382 vs 1.407 | 1.370 vs 1.423 |

Bold marks where annealing on the surrogate beat the best random regimen: **5 of 15**, and every
MS case, the only disease where the space is large enough (up to 75 million subsets) that 3,000
random draws cannot compete. Where the space is small enough for random draws to cover a real
fraction, optimising the surrogate does not beat them, which is the surrogate's error again.

### 6.5 The best 4-, 5- and 6-drug regimens, within each pool

Found by exhaustively scoring every subset with the true k-ary composite, so these do not depend
on any solver. They are pool-limited (the 18 best agents by monotherapy composite) and have the
same standing as any other screen result: hypotheses from a curated model.

| disease | k | best regimen (composite score) |
|---|---|---|
| MS | 4 | clemastine, diroximel fumarate, fenebrutinib, minocycline (1.668) |
| MS | 5 | + high-dose biotin (1.686) |
| MS | 6 | clemastine, diroximel fumarate, high-dose biotin, ibudilast, siponimod, tolebrutinib (1.660) |
| Parkinson's | 4 | LRRK2 inhibitor, minocycline, NLRP3 inhibitor, safinamide (1.648) |
| Parkinson's | 5 | ambroxol, entacapone, LRRK2 inhibitor, minocycline, NLRP3 inhibitor (1.647) |
| Parkinson's | 6 | those five plus safinamide (1.636) |
| Alzheimer's | 4 | blarcamesine, encenicline, NLRP3 inhibitor, xanomeline-trospium (1.504) |
| Alzheimer's | 5 | blarcamesine, memantine, NLRP3 inhibitor, pioglitazone, xanomeline-trospium (1.567) |
| Alzheimer's | 6 | buntanetap, encenicline, intranasal insulin, memantine, NLRP3 inhibitor, semaglutide (1.589) |
| Epilepsy | 4 | azetukalner, ethosuximide, everolimus, zonisamide (1.517) |
| Epilepsy | 5 | + brivaracetam (1.554) |
| Epilepsy | 6 | brivaracetam, ethosuximide, everolimus, **retigabine**, **vigabatrin**, zonisamide (1.601) |
| Guillain-Barré | 4 | amitriptyline, dalfampridine, plasma exchange, tanruprubart (1.389) |
| Guillain-Barré | 5 | C5aR antagonist exemplar, dalfampridine, imlifidase, pregabalin, tanruprubart (1.410) |
| Guillain-Barré | 6 | the k = 5 regimen plus efgartigimod (1.423) |

**Read these with the earlier caveats.** The epilepsy six-drug regimen contains retigabine
(withdrawn worldwide in 2017) and vigabatrin (permanent visual-field loss), the two agents the
composite ranked first and second and the two failed safety controls in the epilepsy screen.
Adding a sixth agent raises the composite here while the regimen becomes more dangerous, so this is
the known composite failure again, not a recommendation. Pools are chosen by monotherapy
composite, so they inherit its preference for narrow, well-aligned agents.

## 7. What would have to be true for quantum optimisation to matter here

- **A problem classical heuristics do not solve.** On the surrogate as built, simulated
  annealing reached the exact optimum in all 15 runs (in about 10 ms), so it is the bar a
  quantum solver has to clear; greedy is not (it matched in only 5 of 15). The regime that might
  differ is a pool of hundreds of agents at high order, where enumeration is impossible and
  heuristics may stall. No panel here reaches it, and a simulator cannot.
- **A better surrogate first.** The largest error is not the solver but the pairwise
  approximation, which loses fidelity as k grows (§5). Higher-order terms (a cubic or
  quartic Hamiltonian, or an added penalty on safety saturation) would help every solver and
  would need higher-order QAOA circuits.
- **Hardware.** Noise on present devices would dominate at the depths and qubit counts that
  matter. Nothing here has been run on hardware, and I would not expect a first hardware run
  to match the simulator.
- **Mixer and initial-state circuits.** The constrained variants are simulated exactly.
  Compiling the Dicke-state preparation and XY mixer into gates, and counting their depth,
  is the concrete step from here to a device.

## 8. Real hardware

A pipeline for running the same circuit on IBM devices is in [the IBM document](ibm_quantum_hardware.md). No hardware run has been made. A free local noise model of a real 127-qubit device predicts usable signal only up to about 8 qubits for this dense problem, and none by 10, so submitting a 20-qubit or larger version would return noise.

## 9. Files

| | |
|---|---|
| [core/quantum/regimen_selection.py](../core/quantum/regimen_selection.py) | The QUBO, both objectives, the true landscape, surrogate fidelity, and the classical baselines |
| [core/quantum/constrained_qaoa.py](../core/quantum/constrained_qaoa.py) | Constraint-preserving QAOA (Dicke start, XY mixer) with an optional CVaR objective |
| [experiments/quantum/run_regimen_selection.py](../experiments/quantum/run_regimen_selection.py) | Runs every solver on one disease and judges each against the true optimum |
| [experiments/quantum/summarize.py](../experiments/quantum/summarize.py) | Tabulates the per-disease results |
| [core/quantum/gate_circuit.py](../core/quantum/gate_circuit.py) | The gate-level circuit from an anonymous spec, with no project dependencies, so the IBM environment needs only this file |
| [core/quantum/gate_qaoa.py](../core/quantum/gate_qaoa.py) | Angle optimisation on the feasible subspace using the same unitary as the gate circuit, and hardware-count analysis helpers |
| [experiments/quantum/ibm_prepare.py](../experiments/quantum/ibm_prepare.py), [ibm_run.py](../experiments/quantum/ibm_run.py) | Prepare an anonymous spec, run it on a free noise model or real IBM hardware, and analyse the counts |
| [tests/test_gate_qaoa.py](../tests/test_gate_qaoa.py) | The gate circuit matches the subspace simulation to 1e-8, preserves the number of selected agents, and the spec is anonymous |
| [tests/test_regimen_selection.py](../tests/test_regimen_selection.py) | Surrogate construction, feasibility of every solver, constraint preservation of the mixer, and that the optimised state beats uniform sampling |

The tests assert only what the algorithm supports: that the surrogate is built as documented,
that every solver returns a feasible selection, that the XY mixer preserves the number of
selected agents, and that the optimised state has a lower expected cost than uniform. They do
**not** assert that the algorithm finds the best regimen, because on the measured problems it
does not reliably do so.

## 10. Does the circuit guide a classical search better? (simulation, five diseases)

`experiments/quantum/run_hybrid_guided.py`. The expensive step is the true k-ary scorer, so each method proposes 20
regimens for it to evaluate, and the score is the best **true rank** among the 20 (1 = the true optimum; pool 12,
k = 4, 495 subsets, ground truth by enumeration). Circuit: dense, Dicke start, 8 layers, noiseless, CVaR at four
values of alpha (the circuit parameter that mattered most in §12 of `docs/ibm_quantum_hardware.md`); the circuit's 20
candidates are its 20 most probable subsets (a version using 4,000 sampled shots gave the same or worse).

| disease | surrogate optimum's true rank | random 20 | classical surrogate top 20 | annealing + neighbours | circuit CVaR 0.02 / 0.05 / 0.10 / 0.25 |
|---|---|---|---|---|---|
| multiple sclerosis | 7 | 22.9 | **1** | **1** | 2 / 5 / 2 / 7 |
| Parkinson's | 2 | 24.0 | **1** | **1** | 1 / 1 / 1 / 1 |
| Alzheimer's | 8 | 22.3 | **1** | **1** | 3 / 7 / 7 / 2 |
| epilepsy | 7 | 22.7 | **1** | **1** | 7 / 7 / 15 / 1 |
| Guillain-Barré | 2 | 24.5 | 2 | **1** | 2 / 1 / 2 / 1 |
| **mean best rank** | | 23.3 | 1.2 | 1.0 | 3.0 / 4.2 / 5.4 / 2.4 |

**The circuit does not improve the classical search.** Ranking by the classical pairwise surrogate and rescoring its
top 20 finds the true optimum in four of five diseases and rank 2 in the fifth; the circuit's best is worse in most
cells (mean rank 2.4 to 5.4 against 1.2). This is expected: the circuit optimises the same surrogate, so its
candidates are at best that ranking, blurred by an imperfect optimisation. The one setting that ties or nearly ties
(CVaR alpha = 0.25, mean 2.4) is not consistent across diseases (7 in MS), and the choice of alpha changes the
result by more than the difference between the circuit and the classical ranking, which is itself a warning about
tuning on five cases. Circuit parameters do matter (alpha changes the epilepsy result from rank 1 to 15), but
tuning them did not get the circuit ahead of the method it is built from. Mean probability on the true top 1% was
0.03 to 0.05 (uniform about 0.008).

**What this leaves open.** The surrogate's own optimum is a poor answer in three diseases (true rank 7, 8, 7), yet
its top 20 always contains the true best, so what helps is scoring a *set* of good candidates with the true scorer,
not the solver that produced them. A hybrid that gets value from a circuit would need to generate candidates the
surrogate ranks poorly but the true scorer likes, which this circuit, optimising the surrogate, does not do.
