# Running on IBM quantum hardware

A pipeline exists for sending the higher-order regimen-selection circuit to IBM's real
quantum processors. **No hardware run has been made**: there are no IBM credentials on this
machine, and nothing has been sent anywhere. What has been done is everything short of that,
including a free local model of a real IBM device, which already says a good deal about what a
hardware run would show.

## 1. What it is, and why it is built this way

| Stage | Where it runs | What it does |
|---|---|---|
| `ibm_prepare prepare` | the project's normal environment | Optimises the QAOA angles on a classical simulator and writes an **anonymous circuit spec** and a local-only private file |
| `ibm_run noisy-sim` | `qbio-ibm-env` | **Free, no account**: runs the spec on a noise model of a real 127-qubit IBM device (Sherbrooke), locally |
| `ibm_run check` / `submit` | `qbio-ibm-env` | Authenticates and lists devices; submits the spec to a real device |
| `ibm_prepare analyze` | the project's normal environment | Reads counts back and judges them against the ideal distribution and against chance |

**The angles are optimised on a simulator, and only the fixed circuit goes to hardware.** The
variational loop needs hundreds of evaluations, which is exactly what scarce quantum time should
not be spent on, so the device is asked one question. The consequence is a hard limit: simulation
is exact only up to about 20 qubits, so angles for a larger problem cannot be optimised this way.

**A separate environment.** IBM's runtime library needs Qiskit 2.x, while the rest of the project is
pinned to 1.4.5. A dry-run install into the working environment showed pip would **upgrade Qiskit to
2.5.2**, risking every result so far, so it lives in its own environment and the two are decoupled:

```bash
qbio-quantum-env/bin/python -m venv qbio-ibm-env          # once
qbio-ibm-env/bin/python -m pip install qiskit qiskit-aer qiskit-ibm-runtime numpy scipy
```

**What is and is not sent.** The spec holds numbers only: the qubit count, the number of selected
qubits `k`, cost coefficients, mixer edge groups, the initial bitstring and the angles. It contains
**no drug names, no gene names and no disease**; qubit `i` is only an index. The mapping from index to
agent lives in the private file, which the run script never reads. A test asserts that no pool member
name and no disease name appears in a spec, and the run script refuses a spec that is not marked
anonymous.

## 2. The circuit is checked against the simulator

The gate-level circuit must implement exactly the unitary the simulator optimised, or hardware would
be compared against the wrong ideal. `tests/test_gate_qaoa.py` builds the circuit, evolves a noiseless
statevector, and compares every bitstring's probability with the subspace simulation to within 1e-8
(sign conventions of `RZZ`, `RXX` and `RYY` included). It also checks that the XY mixer never leaves the
subspace with exactly `k` ones, that the edge groups are disjoint, and that the spec is anonymous.

The ansatz starts in a basis state with `k` ones, applies the cost as `RZZ` and `RZ` phases, and mixes
with an XY ring (`RXX` then `RYY`). On a noiseless machine every measured bitstring has exactly `k`
ones. **On a real device noise breaks that, so the fraction of shots with weight `k` is a direct,
model-free gauge of how much noise the circuit picked up.** It needs no simulation and no assumption.

## 3. What a noise model of a real device predicts

Guillain-Barré's regimen problem at k = 4 (pool sizes from the disease's 16 agents), two layers,
transpiled for the 127-qubit Sherbrooke device and run locally with its noise model. **This is a
simulation of noise, not a hardware run.**

| qubits | two-qubit gates after transpiling | shots with exactly k ones | random bits would give | distance from ideal (uniform: about 1.0) | verdict |
|---|---|---|---|---|---|
| 6 | 130 | 0.564 | 0.234 | 0.19 | **clear signal** |
| 8 | 259 | 0.391 | 0.273 | 0.42 | **partial signal** |
| 10 | 410 | 0.250 | 0.205 | 0.83 | no reliable signal |
| 12 | 496 | 0.178 | 0.121 | 0.93 | no reliable signal |
| 14 | 850 | 0.108 | 0.061 | 0.98 | no reliable signal |
| 16 | 907 | 0.063 | 0.028 | 0.98 | no reliable signal |

(2,000 shots up to 12 qubits, 1,000 at 14 and 16.) Signal survives to about 8 qubits and is gone from
10, and 16 qubits is barely above what random bits would give.

**Why, and what it means for "more qubits".** The cost of this problem is dense: every pair of agents
interacts, so a circuit on `n` qubits needs about `n(n-1)/2` interaction gates per layer, and IBM's
heavy-hex connectivity adds swaps to route them. Two-qubit gates grew from 130 to 907 between 6 and 16
qubits, and each carries an error of the order of a percent, so the signal decays exponentially in the
gate count. **Submitting a 20-, 30- or 64-qubit version of this circuit is possible, and the model says it
would return noise.** More physical qubits do not help unless the problem can be made sparse or the
error rate falls by an order of magnitude. This is a claim about a noise model, and a real device can
differ; the point of running on hardware would be to check it.

## 4. How to run it on real hardware

Only you can do the first two steps: they create a credential, and it must never be pasted into this
repository or a chat.

1. **Create a free IBM Quantum Platform account and an API key** at
   [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com). The open plan is described as offering real
   processors of up to 127 qubits and about 10 minutes of quantum time a month; confirm the current
   terms on IBM's own pages, since the figures here come from search summaries, one from a third-party site.
2. **In your own terminal**, set the credential:
   ```bash
   export QISKIT_IBM_TOKEN=<your API key>
   export QISKIT_IBM_INSTANCE=<optional: your instance CRN>
   ```
3. **List devices** (sends nothing): `qbio-ibm-env/bin/python -m experiments.quantum.ibm_run check`
4. **Prepare a spec** at a size where signal is expected, for example 6 and 8 qubits:
   `python -m experiments.quantum.ibm_prepare prepare --disease guillain_barre --pool 8 --k 4 --layers 2`
5. **Dry-run the submission**, which prints the device, the transpiled gate count and the shot count and
   submits nothing: `qbio-ibm-env/bin/python -m experiments.quantum.ibm_run submit --spec <tag>.spec.json`
6. **Submit** by adding `--yes`. The job waits in IBM's queue, so it may take a while.
7. **Analyse**: `python -m experiments.quantum.ibm_prepare analyze --tag <tag> --counts <tag>.ibm_hardware.counts.json`

Each job should need seconds of quantum time, but I have not measured it on hardware and IBM reports
the usage after the run.

## 5. What a hardware run could and could not show

- **It can show** whether the noise model is right: the fraction of shots with weight `k` and the
  distance from the ideal distribution on 6 and 8 qubits, against the predictions above.
- **It cannot show a quantum advantage.** At these sizes exhaustive search is instant and simulated
  annealing already matches it, so the only claim available is that a real device runs the circuit and
  produces a distribution above chance.
- **It cannot reach the sizes that matter.** Beyond about 8 qubits the model predicts noise, and beyond
  about 20 the angles could not be optimised or checked against an ideal simulation.

A first hardware run should therefore be read as a check of the noise model and of this pipeline, not
as a route to better regimens.

## 6. Measured on hardware (ibm_fez, 2026-09-27)

Guillain-Barré, k = 4, two layers, 4,000 shots, 3 quantum seconds per job:

| qubits | 2-qubit gates | weight-k fraction (hardware) | noise model | uniform random | TV from ideal | verdict |
|---|---|---|---|---|---|---|
| 6 | 136 | 0.582 | 0.564 | 0.234 | 0.14 | clear signal |
| 8 | 262 | 0.431 | 0.391 | 0.273 | 0.36 | partial signal |

The device matched or slightly beat the FakeSherbrooke prediction, and the verdicts agree. Shots covered 100% and
99% of the feasible subsets, so the rank of the best measured regimen is uninformative at these sizes. This checks
the pipeline and the noise model; it is not evidence of quantum advantage. 10 qubits and above were not run on
hardware.

## 7. A sparse formulation (noise model only)

The dense problem lets every pair of agents interact, so gates grow quadratically. `ibm_prepare prepare --keep N`
centres the pair scores on their mean (which changes nothing at fixed k) and keeps only each agent's `N` strongest
couplings; the rest cost no gate (`core/quantum/gate_qaoa.py: sparsify`). Guillain-Barré, k = 4, two layers,
`--keep 2`, FakeSherbrooke noise model, 4,000 shots:

| qubits | ZZ terms (dense → sparse) | 2-qubit gates (transpiled) | weight-k fraction | uniform random | TV from ideal | verdict |
|---|---|---|---|---|---|---|
| 10 | 45 → 15 | 223 | 0.359 | 0.205 | 0.47 | partial |
| 12 | 66 → 18 | 230 | 0.345 | 0.121 | 0.49 | partial |
| 16 | 120 → 23 | 329 | 0.231 | 0.028 | 0.68 | partial |

Dense circuits gave no signal from 10 qubits (§3), so sparsity does extend the usable size on this gauge. **The cost
is fidelity to the problem:** the noiseless sparse circuit's most likely regimen has true rank 106 of 210, 88 of 495
and 335 of 1,820, so discarding couplings degrades what the circuit is optimising before any noise. The weight-k
fraction is a noise gauge, not a quality measure, and a device that preserves weight while optimising a poor
objective has not found good regimens. Not run on hardware.

## 8. 10-qubit dense run: the noise model was too pessimistic

Guillain-Barré, k = 4, two layers, dense, ibm_fez, 4,000 shots, 3 quantum seconds:

| qubits | 2-qubit gates | weight-k fraction (hardware) | noise model | uniform random | TV from ideal (hardware / model) | verdict (hardware / model) |
|---|---|---|---|---|---|---|
| 10 | 410 | 0.288 | 0.250 | 0.205 | 0.67 / 0.83 | partial / none |

The FakeSherbrooke model predicted no reliable signal; the device kept partial signal. Across 6, 8 and 10 qubits the
device has beaten the model each time, so the model is a conservative guide (ibm_fez is a newer processor than the
one it models, which I have not verified as the cause). The margin over random is small (0.288 against 0.205), and
this still says nothing about solution quality.

## 9. 12 qubits dense and 16 qubits sparse on hardware

ibm_fez, Guillain-Barré, k = 4, two layers, 4,000 shots, 3 quantum seconds each:

| circuit | 2-qubit gates | weight-k fraction (hardware) | noise model | uniform random | TV from ideal (hardware / model) | verdict (hardware / model) |
|---|---|---|---|---|---|---|
| 12 qubits, dense | 474 | 0.220 | 0.178 | 0.121 | 0.70 / 0.93 | partial / none |
| 16 qubits, sparse (`--keep 2`) | 355 | 0.203 | 0.231 | 0.028 | 0.72 / 0.68 | partial / partial |

Dense 12 qubits follows the earlier pattern: the device beat the model, which called it noise. The sparse 16-qubit
circuit is the first case where the device came in *below* the model (0.203 against 0.231), so the model is not
always pessimistic. The sparse circuit keeps about 7 times the weight-preserving fraction that random bits would
(0.203 against 0.028), at a gate count similar to the dense 10-qubit circuit. The caveat in §7 stands: the sparse
circuit's noiseless most-likely regimen has true rank 335 of 1,820, so this shows a circuit that survives, not one
that finds good regimens. The "best measured regimen" rank in the analysis is uninformative here, since 4,000 shots
cover a large share of the subsets and the choice is made with the dense surrogate.

## 10. Better couplings, and a correction to §7

`sparsify_fit` (`core/quantum/gate_qaoa.py`) chooses couplings by orthogonal matching pursuit and refits their
weights, instead of keeping the largest. At the same edge budget as `--keep 2`, noiseless, two layers, GBS k = 4
(Spearman of the circuit's own objective against the true score over all feasible subsets):

| qubits | edges | dense | strongest | fit |
|---|---|---|---|---|
| 10 | 15 of 45 | 0.948 | 0.878 | 0.925 |
| 12 | 18 of 66 | 0.947 | 0.866 | 0.906 |
| 16 | 23 of 120 | 0.903 | 0.845 | 0.836 |

The fitted couplings track the dense objective better at 10 and 12 qubits and slightly worse at 16, so this is not a
clear improvement. **More important, the couplings were not the bottleneck, and §7 blamed them wrongly.** The dense
circuit is just as poor: at two layers its noiseless state puts probability 1.000 on a single regimen, the same one
the sparse circuits pick, which is not the optimum (true rank 88 of 495 at 12 qubits, 335 of 1,820 at 16) and gives
the true top 1% no mass. That regimen, (1, 2, 4, 11) at 12 qubits, is two ring hops from the starting subset
(0, 1, 2, 3). The hardware circuit starts from one computational-basis subset, not the spread-out Dicke state used
in the exact simulator of `constrained_qaoa.py`, and a shallow ring mixer cannot move far from it. Deeper circuits
spread the state and raise the surrogate optimum's probability (16 qubits: 0.0000 at 2 layers, 0.0015 at 4, 0.0184
at 6, against 0.0005 uniform), but they cost more gates. The hardware results in §8 and §9 stand as noise
measurements; what changes is that a circuit with probability 1.000 on one wrong regimen is a test of hitting that
state, not of searching. Next steps that would address the cause: a Dicke-state start (about n·k gates), a warm
start from the annealing solution, or more layers.

## 11. Dicke-state start: it does not fix quality

`prepare_dicke` (`core/quantum/gate_circuit.py`) builds the uniform superposition of all weight-k bitstrings, about
n·k two-qubit gates. Its gate roles were found by checking the output statevector against the exact Dicke state,
amplitude and phase, and it is tested for several (n, k); the Dicke-start circuit also matches the subspace simulation
bitstring by bitstring. `ibm_prepare prepare --start dicke` uses it. Noiseless, GBS k = 4, optimised angles:

| qubits | circuit | start | layers | P(true top 1%) (uniform ≈ 0.01) | mean true percentile rank (0.5 = random) |
|---|---|---|---|---|---|
| 12 | dense | basis | 2 / 4 | 0.000 / 0.006 | 0.178 / 0.188 |
| 12 | dense | Dicke | 2 / 4 | 0.010 / 0.009 | 0.438 / 0.393 |
| 16 | dense | basis | 2 / 4 | 0.000 / 0.009 | 0.184 / 0.204 |
| 16 | dense | Dicke | 2 / 4 | 0.012 / 0.012 | 0.409 / 0.417 |
| 16 | sparse | Dicke | 2 / 4 | 0.015 / 0.009 | 0.417 / 0.457 |

(Ten qubits and the sparse rows at 10 and 12 are in the same script's output and show the same pattern.)

**With the Dicke start the circuit is barely better than random:** mass on the true top 1% is about the uniform
value, and the mean rank is 0.39 to 0.46 against 0.5 for random. This confirms §10's diagnosis (the basis-start
circuit could not spread out) but not its hoped-for cure. It also corrects how to read the basis-start rows: their
good mean rank (0.18) is not a search result. **The pool is ordered by monotherapy score, so the fixed start subset
(0, 1, 2, 3) is the four best single agents**, a classical prior, and two shallow layers keep the state near it.
The basis start is therefore a warm start from a classical heuristic, and the earlier "sparse circuit picks poorly"
comparison was against a strong classical baseline, not against random.

At two to four layers on these problems, no start state I tried gives a circuit that finds the top regimens, which
matches the simulator finding in `docs/quantum_regimen_selection.md`. I did not send a Dicke circuit to hardware: it
adds gates and the noiseless version is not better, so the run would cost quantum time to measure noise on a circuit
that has nothing to preserve.

## 12. Deeper circuits and a CVaR objective (noiseless)

`optimise(..., cvar_alpha=0.05)` minimises the mean cost of the best 5% of the probability mass instead of the mean
cost, which rewards concentrating on the best regimens. Dense circuit, Dicke start, Guillain-Barré k = 4, noiseless,
3 COBYLA restarts of up to 400 evaluations (so a poor optimum at depth is possible and these are not upper bounds):

| qubits | objective | layers | P(true top 1%) (uniform) | P(surrogate optimum) (uniform) | mean true percentile rank |
|---|---|---|---|---|---|
| 12 | mean | 4 / 8 / 12 | 0.013 / 0.011 / 0.007 (0.008) | 0.0059 / 0.0013 / 0.0016 (0.0020) | 0.40 / 0.30 / 0.33 |
| 12 | CVaR 0.05 | 4 / 8 / 12 | 0.031 / **0.082** / 0.058 | 0.020 / **0.050** / 0.050 | 0.46 / 0.43 / 0.35 |
| 16 | mean | 4 / 8 / 12 | 0.012 / 0.012 / 0.014 (0.010) | 0.0005 / 0.0001 / 0.0001 (0.0005) | 0.42 / 0.35 / 0.37 |
| 16 | CVaR 0.05 | 4 / 8 / 12 | 0.012 / 0.019 / **0.055** | 0.0002 / 0.0024 / 0.0062 | 0.49 / 0.49 / 0.43 |

**The objective matters more than depth.** With the mean objective, more layers never lift the top-end probability
above uniform at either size. With CVaR at 12 qubits, 8 layers put 0.082 on the true top 1% (about 10 times uniform)
and 0.050 on the surrogate's optimum (25 times), and at 16 qubits it takes 12 layers to reach 0.055 (about 5.5 times)
and 0.006 on the surrogate optimum (12 times). The mean rank does not improve with CVaR, which is what the objective
trades away.

**Read this as a simulator result, and a modest one.** It is the first setting in which the algorithm concentrates
on good regimens, but exhaustive search finds the optimum instantly at these sizes, annealing already matches it, and
the concentration grows more slowly with size (needing 12 layers at 16 qubits). The cost on hardware is prohibitive:
the dense 16-qubit circuit was 907 two-qubit gates at two layers, so twelve layers is far beyond what the device
preserves (§8 and §9 measure noise tolerance only up to a few hundred gates). Nothing here was run on hardware.

## 13. Sparse CVaR: a loss, dense stays the default

Same setting as §12 (Dicke start, CVaR 0.05, noiseless), with the sparse circuits at the same edge budget as `--keep 2`
(18 edges at 12 qubits, 23 at 16), P(true top 1%) at 8 / 12 layers:

| qubits | dense CVaR (§12) | sparse, strongest couplings | sparse, fitted couplings |
|---|---|---|---|
| 12 | 0.082 / 0.058 | 0.006 / 0.013 | 0.014 / 0.010 |
| 16 | 0.019 / 0.055 | 0.017 / 0.024 | 0.019 / 0.025 |

(uniform is 0.008 at 12 qubits and 0.010 at 16.) At 12 qubits the sparse circuits lose the effect entirely; at 16 they
give about 2 times uniform where dense at 12 layers gives 5.5 times. So discarding couplings costs the concentration
that CVaR buys, and the hardware-survivable sparse circuits from §7 and §9 are not the ones that would search well.
Nothing was changed by this: `--keep` and `--start dicke` remain opt-in, and the default is still the dense circuit.
