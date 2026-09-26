"""Optimise weight-preserving QAOA in simulation, and read hardware results back.

The angles are found on a classical simulator, on the feasible subspace, using exactly the
unitary the gate circuit in :mod:`core.quantum.gate_circuit` implements: a computational-
basis start with ``k`` ones, cost phases, and a Trotterised XY mixer applied one disjoint
edge group at a time. Only the *fixed* optimised circuit is then sent to hardware. This is
the usual way to spend scarce QPU time: the variational loop, which needs hundreds of
evaluations, runs on a simulator, and the device is asked one question.

The limit this exposes is honest and simple. Simulation is exact only up to about 20
qubits, so angles for a larger problem cannot be optimised this way. A hardware run on more
qubits than that can only use angles transferred from a smaller instance or a fixed
schedule, and it cannot be checked against an ideal simulation.
"""

from __future__ import annotations

import time
from typing import Any, Sequence

import numpy as np
from scipy.optimize import minimize
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import expm_multiply

from core.quantum.constrained_qaoa import _basis, _cost_vector
from core.quantum.gate_circuit import mixer_groups


def _group_hopping(n, states, lookup, edges):
    """Hopping operator restricted to one group of edges, on the weight-k subspace."""
    rows, cols = [], []
    for row, subset in enumerate(states):
        occupied = set(subset)
        for i, j in edges:
            if (i in occupied) != (j in occupied):
                swapped = tuple(sorted((occupied - {i, j}) | ({i, j} - occupied)))
                rows.append(row)
                cols.append(lookup[swapped])
    size = len(states)
    return coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(size, size)).tocsr()


class SubspaceSimulator:
    """Exact simulation of the circuit on the weight-k subspace."""

    def __init__(self, problem, initial: Sequence[int], start: str = "basis"):
        self.n = len(problem.identifiers)
        self.k = problem.k
        self.states, self.lookup = _basis(self.n, self.k)
        self.value = _cost_vector(problem, self.states)
        lo, hi = float(self.value.min()), float(self.value.max())
        self.lo, self.span = lo, (hi - lo) or 1.0
        self.cost = -(self.value - lo) / self.span
        self.groups = mixer_groups(self.n)
        self.hopping = [_group_hopping(self.n, self.states, self.lookup, g) for g in self.groups]
        self.initial = tuple(sorted(initial))
        self.psi0 = np.zeros(len(self.states), dtype=complex)
        if start == "dicke":
            self.psi0[:] = 1.0 / np.sqrt(len(self.states))
        else:
            self.psi0[self.lookup[self.initial]] = 1.0

    def evolve(self, gammas, betas):
        psi = self.psi0.copy()
        for gamma, beta in zip(gammas, betas):
            psi = np.exp(-1j * gamma * self.cost) * psi
            for hop in self.hopping:
                psi = expm_multiply(-1j * beta * hop, psi)
        return psi

    def probabilities(self, gammas, betas) -> np.ndarray:
        probs = np.abs(self.evolve(gammas, betas)) ** 2
        return probs / probs.sum()

    def expected_cost(self, gammas, betas) -> float:
        return float(np.dot(self.probabilities(gammas, betas), self.cost))

    def cvar_cost(self, gammas, betas, alpha: float) -> float:
        """Mean cost over the best ``alpha`` of the probability mass (lower cost is better)."""
        probs = self.probabilities(gammas, betas)
        order = np.argsort(self.cost)
        p, c = probs[order], self.cost[order]
        cumulative = np.cumsum(p)
        cut = int(np.searchsorted(cumulative, alpha)) + 1
        w = p[:cut].copy()
        w[-1] -= cumulative[cut - 1] - alpha
        w = np.clip(w, 0.0, None)
        return float(np.sum(w * c[:cut]) / max(w.sum(), 1e-12))


def cost_coefficients(problem, span: float):
    """``H_C = sum c_ij Z_i Z_j + sum d_i Z_i`` (up to a constant) for ``-(qubo - lo) / span``."""
    names = problem.identifiers
    index = {name: i for i, name in enumerate(names)}
    n = len(names)
    zz, z = [], [0.0] * n
    for (a, b), value in problem.quadratic.items():
        if value == 0.0:
            continue  # a dropped (sparsified) coupling costs no gate
        i, j = sorted((index[a], index[b]))
        zz.append((i, j, -value / (4.0 * span)))
        z[i] += value / (4.0 * span)
        z[j] += value / (4.0 * span)
    for name, value in problem.linear.items():
        z[index[name]] += value / (2.0 * span)
    return zz, z


def optimise(problem, layers: int, seed: int = 7, restarts: int = 4, maxiter: int = 200,
             initial: Sequence[int] | None = None, start: str = "basis",
             cvar_alpha: float | None = None) -> tuple[dict[str, Any], SubspaceSimulator]:
    """Find angles on a simulator and return a hardware-ready, anonymous spec."""
    n, k = len(problem.identifiers), problem.k
    initial = tuple(initial) if initial is not None else tuple(range(k))
    simulator = SubspaceSimulator(problem, initial, start)
    rng = np.random.default_rng(seed)
    ramp = (np.arange(layers) + 0.5) / layers
    best_theta, best_energy = None, np.inf
    started = time.perf_counter()
    for attempt in range(restarts):
        theta0 = np.concatenate([2 * np.pi * ramp * 0.6, np.pi / 3 * (1 - ramp)])
        if attempt:
            theta0 = theta0 + rng.normal(0.0, 0.25, size=theta0.shape)
        result = minimize(
            (lambda t: simulator.expected_cost(t[:layers], t[layers:])) if cvar_alpha is None
            else (lambda t: simulator.cvar_cost(t[:layers], t[layers:], cvar_alpha)), theta0,
            method="COBYLA", options={"maxiter": maxiter},
        )
        if result.fun < best_energy:
            best_theta, best_energy = result.x, float(result.fun)
    zz, z = cost_coefficients(problem, simulator.span)
    spec = {
        "n": n, "k": k, "initial": list(initial), "layers": layers,
        "zz": [(int(i), int(j), float(c)) for i, j, c in zz], "z": [float(v) for v in z],
        "mixer_groups": [[list(e) for e in g] for g in simulator.groups],
        "gammas": [float(v) for v in best_theta[:layers]],
        "betas": [float(v) for v in best_theta[layers:]],
        "ideal_expected_cost": round(best_energy, 6),
        "optimisation_seconds": round(time.perf_counter() - started, 2),
        "anonymous": True,
    }
    if start == "dicke":
        spec["start"] = "dicke"
    return spec, simulator


def weight_distribution(counts: dict[str, int], k: int) -> dict[str, Any]:
    """The model-free noise gauge: how many measured bitstrings still have exactly k ones."""
    total = sum(counts.values())
    feasible = sum(c for bits, c in counts.items() if bits.count("1") == k)
    return {"shots": total, "feasible_shots": feasible,
            "feasible_fraction": feasible / total if total else 0.0}


def counts_to_subsets(counts: dict[str, int], k: int) -> dict[tuple[int, ...], int]:
    """Feasible measured bitstrings as index tuples (Qiskit's bit ``i`` from the right is qubit ``i``)."""
    subsets: dict[tuple[int, ...], int] = {}
    for bits, count in counts.items():
        if bits.count("1") != k:
            continue
        chosen = tuple(sorted(i for i, b in enumerate(reversed(bits)) if b == "1"))
        subsets[chosen] = subsets.get(chosen, 0) + count
    return subsets


def total_variation(p: dict[Any, float], q: dict[Any, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(x, 0.0) - q.get(x, 0.0)) for x in keys)


def sparsify(problem, keep: int):
    """A copy of ``problem`` keeping only each agent's ``keep`` strongest couplings.

    Pair scores are first centred on their mean, which changes nothing at fixed
    cardinality (a constant per pair adds a constant to every weight-k subset), then
    every coupling that is not among the ``keep`` largest in magnitude for at least one
    of its two agents is set to zero and costs no gate. Gate count then grows roughly
    linearly in the number of agents instead of quadratically. The price is fidelity to
    the surrogate, which the caller should measure rather than assume.
    """
    from dataclasses import replace

    values = list(problem.quadratic.values())
    centre = sum(values) / len(values)
    centred = {pair: v - centre for pair, v in problem.quadratic.items()}
    kept: set = set()
    for name in problem.identifiers:
        mine = sorted((p for p in centred if name in p), key=lambda p: -abs(centred[p]))
        kept.update(mine[:keep])
    sparse = {p: (v if p in kept else 0.0) for p, v in centred.items()}
    return replace(problem, quadratic=sparse)


def sparsify_fit(problem, edges: int):
    """Keep ``edges`` couplings chosen and re-weighted by orthogonal matching pursuit.

    The dense objective over weight-k subsets is a linear function of the pair
    indicators ``x_i x_j``, so the best ``edges``-term approximation of it can be built
    greedily: repeatedly add the pair whose indicator best explains what is still
    unexplained, then refit all chosen weights by least squares. Unlike keeping the
    largest couplings, this accounts for how often a pair co-occurs in a k-subset and
    for correlations between pairs. Everything else is set to zero and costs no gate.
    """
    from dataclasses import replace
    from itertools import combinations as _comb

    names = problem.identifiers
    index = {n: i for i, n in enumerate(names)}
    subsets = list(_comb(range(len(names)), problem.k))
    pairs = sorted(problem.quadratic)
    columns = []
    for a, b in pairs:
        i, j = sorted((index[a], index[b]))
        columns.append([1.0 if (i in s and j in s) else 0.0 for s in subsets])
    features = np.array(columns).T
    target = np.array([sum(problem.quadratic[tuple(sorted((names[i], names[j])))]
                           for i, j in _comb(s, 2)) for s in subsets])
    target = target - target.mean()
    features = features - features.mean(axis=0)
    chosen: list[int] = []
    residual = target.copy()
    for _ in range(min(edges, len(pairs))):
        norms = np.linalg.norm(features, axis=0)
        norms[norms == 0] = np.inf
        scores = np.abs(features.T @ residual) / norms
        scores[chosen] = -1.0
        chosen.append(int(np.argmax(scores)))
        weights, *_ = np.linalg.lstsq(features[:, chosen], target, rcond=None)
        residual = target - features[:, chosen] @ weights
    sparse = {p: 0.0 for p in pairs}
    for column, weight in zip(chosen, weights):
        sparse[pairs[column]] = float(weight)
    return replace(problem, quadratic=sparse)
