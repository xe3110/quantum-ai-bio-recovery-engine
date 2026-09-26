"""Constraint-preserving QAOA for "choose exactly k", simulated on the feasible subspace.

Why this exists
---------------
The Qiskit path in :mod:`core.design.quantum_assembly` folds the cardinality constraint
``sum(x) == k`` into the cost as a penalty and runs an ordinary QAOA over all ``2**n``
bitstrings. That works at the ten-variable fragment problem, and it degrades badly as
the problem grows: most of the state space is infeasible, the penalty landscape is
rugged, and the optimiser spends its budget avoiding illegal selections instead of
finding good ones. Measured on the regimen problem it returned selections ranked in
the thousands out of thousands, worse than picking at random.

The standard remedy is the *quantum alternating operator ansatz* (Hadfield et al.):

* start in the **Dicke state**, the uniform superposition over all weight-``k``
  bitstrings, so the constraint holds from the first step;
* mix with an **XY (hopping) mixer**, which swaps an occupied and an empty position and
  therefore preserves the number of ones exactly;
* apply the problem's cost as diagonal phases, as in standard QAOA.

Every state the algorithm visits is feasible, so the search space shrinks from ``2**n``
to ``C(n, k)`` and no penalty is needed.

What this is, and is not
------------------------
This is an **exact statevector simulation on the feasible subspace**, not a Qiskit
circuit. It is the same algorithm a gate-model device would run, with the mixer
``exp(-i beta H_XY)`` and the cost ``exp(-i gamma C)`` applied exactly rather than
compiled to gates. Working on the subspace is what makes 20 to 22 qubits tractable
(``C(20, 6)`` is 38,760 amplitudes, against ``2**20`` for the full space).

Being a classical simulation, it cannot demonstrate a quantum advantage. It can
show whether the *algorithm* finds good regimens as the problem grows, which is
the question that decides whether hardware would be worth trying, and it is honest
about the two regimes: exact (no shot noise) and sampled (finite shots).
"""

from __future__ import annotations

import time
from itertools import combinations
from typing import Any, Sequence

import numpy as np
from scipy.optimize import minimize
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import expm_multiply

from core.design.quantum_assembly import FragmentSelection


def _basis(n: int, k: int) -> tuple[list[tuple[int, ...]], dict[tuple[int, ...], int]]:
    states = list(combinations(range(n), k))
    return states, {s: i for i, s in enumerate(states)}


def _cost_vector(problem, states: list[tuple[int, ...]]) -> np.ndarray:
    """The surrogate objective of every feasible subset, as a vector (higher is better)."""
    names = problem.identifiers
    index = {name: i for i, name in enumerate(names)}
    n = len(names)
    upper = np.zeros((n, n))
    for (a, b), value in problem.quadratic.items():
        i, j = index[a], index[b]
        upper[min(i, j), max(i, j)] = value
    linear = np.array([problem.linear[name] for name in names])
    membership = np.zeros((len(states), n))
    for row, subset in enumerate(states):
        membership[row, list(subset)] = 1.0
    return membership @ linear + np.einsum("ri,ij,rj->r", membership, upper, membership)


def _xy_mixer(n: int, k: int, states, lookup) -> "coo_matrix":
    """Sparse hopping operator on the weight-k subspace, over a ring of adjacent positions."""
    rows, cols = [], []
    for row, subset in enumerate(states):
        occupied = set(subset)
        for i in range(n):
            j = (i + 1) % n
            if (i in occupied) != (j in occupied):
                swapped = tuple(sorted((occupied - {i, j}) | ({i, j} - occupied)))
                rows.append(row)
                cols.append(lookup[swapped])
    data = np.ones(len(rows))
    return coo_matrix((data, (rows, cols)), shape=(len(states), len(states))).tocsr()


def _evolve(psi0, cost, mixer, gammas, betas):
    psi = psi0.astype(complex)
    for gamma, beta in zip(gammas, betas):
        psi = np.exp(-1j * gamma * cost) * psi
        psi = expm_multiply(-1j * beta * mixer, psi)
    return psi


def solve_constrained_qaoa(
    problem,
    reps: Sequence[int] = (1, 2, 3, 4, 5, 6),
    seed: int = 7,
    restarts: int = 4,
    maxiter: int = 250,
    shots: int = 4096,
    cvar_alpha: float | None = None,
) -> FragmentSelection:
    """QAOA with a Dicke start and an XY mixer, swept across depths, best feasible kept.

    The cost is normalised to [0, 1] so that the same parameter ranges suit every
    problem, and each depth starts from a linear-ramp (annealing-inspired)
    schedule plus perturbed restarts, which is a standard way to keep the optimiser
    out of poor local minima at moderate depth. The returned selection is the best
    subset among ``shots`` samples drawn from the final state, which is what a
    device would give, and the record carries the exact probability of the true
    surrogate optimum so the sampling does not hide how the state actually looks.
    """
    n, k = len(problem.identifiers), problem.k
    states, lookup = _basis(n, k)
    value = _cost_vector(problem, states)
    lo, hi = float(value.min()), float(value.max())
    span = (hi - lo) or 1.0
    cost = -(value - lo) / span  # minimise; the best subset has the lowest cost
    mixer = _xy_mixer(n, k, states, lookup)
    dimension = len(states)
    psi0 = np.full(dimension, 1.0 / np.sqrt(dimension), dtype=complex)
    best_index = int(np.argmax(value))
    rng = np.random.default_rng(seed)

    attempts: list[dict[str, Any]] = []
    best_overall: tuple[float, np.ndarray] | None = None
    for p in reps:
        started = time.perf_counter()

        order = np.argsort(cost)  # best (lowest-cost) subsets first

        def energy(theta):
            gammas, betas = theta[:p], theta[p:]
            psi = _evolve(psi0, cost, mixer, gammas, betas)
            if cvar_alpha is None:
                return float(np.real(np.vdot(psi, cost * psi)))
            # CVaR objective: the mean cost of the best ``alpha`` of the probability mass.
            # It rewards putting weight on the best subsets, not on a good average, which
            # is what finding an optimum needs.
            probs = np.abs(psi[order]) ** 2
            probs = probs / probs.sum()
            cumulative = np.cumsum(probs)
            cut = int(np.searchsorted(cumulative, cvar_alpha)) + 1
            weights = probs[:cut].copy()
            weights[-1] -= cumulative[cut - 1] - cvar_alpha
            weights = np.clip(weights, 0.0, None)
            return float(np.sum(weights * cost[order][:cut]) / max(weights.sum(), 1e-12))

        ramp = (np.arange(p) + 0.5) / p
        best_theta, best_energy = None, np.inf
        for attempt in range(restarts):
            gammas0 = 2.0 * np.pi * ramp * 0.6
            betas0 = np.pi / 3.0 * (1.0 - ramp)
            theta0 = np.concatenate([gammas0, betas0])
            if attempt:
                theta0 = theta0 + rng.normal(0.0, 0.25, size=theta0.shape)
            result = minimize(energy, theta0, method="COBYLA", options={"maxiter": maxiter})
            if result.fun < best_energy:
                best_theta, best_energy = result.x, float(result.fun)
        psi = _evolve(psi0, cost, mixer, best_theta[:p], best_theta[p:])
        probabilities = np.abs(psi) ** 2
        probabilities /= probabilities.sum()
        sampled = rng.choice(dimension, size=shots, p=probabilities)
        sampled_best = int(sampled[np.argmax(value[sampled])])
        attempts.append({
            "reps": p,
            "expected_cost": round(best_energy, 6),
            "p_surrogate_optimum": round(float(probabilities[best_index]), 6),
            "p_top_1_percent": round(float(np.sort(probabilities)[::-1][: max(1, dimension // 100)].sum()), 6),
            "sampled_best_objective": round(float(value[sampled_best]), 6),
            "found_surrogate_optimum": bool(sampled_best == best_index),
            "seconds": round(time.perf_counter() - started, 2),
        })
        if best_overall is None or value[sampled_best] > best_overall[0]:
            best_overall = (float(value[sampled_best]), sampled_best)

    assert best_overall is not None
    ids = problem.identifiers
    chosen = tuple(sorted(ids[i] for i in states[best_overall[1]]))
    detail = {
        "algorithm": "constraint-preserving QAOA (Dicke start, XY ring mixer), exact subspace simulation",
        "subspace_dimension": dimension,
        "full_space_dimension": 2 ** n,
        "restarts": restarts,
        "shots": shots,
        "objective": "expected cost" if cvar_alpha is None else f"CVaR (alpha = {cvar_alpha})",
        "depth_sweep": attempts,
    }
    return FragmentSelection(
        identifiers=chosen,
        qubo_objective=problem.qubo_objective(chosen),
        exact_objective=problem.exact_objective(chosen),
        backend="qaoa_constrained",
        feasible=len(chosen) == k,
        detail=detail,
    )
