"""Higher-order drug-regimen selection as a QUBO, solvable by the project's quantum backends.

The exhaustive combination screen stops at k = 3. That is a limit of cost, not of
interest: real regimens can have four or five agents, and the number of subsets grows
combinatorially while every one of them has to be scored. This module states the
question the project's Hamiltonian machinery was built for, *which k agents from a
pool*, on the combination problem itself, rather than only on pharmacophore fragments.

The surrogate
-------------
Every k-ary term in :mod:`core.biology.combination_scoring` is defined as the mean of
its pairwise form, so a k-subset's score is approximated by the mean of the scores of
the pairs inside it. That is a pairwise (quadratic) function of the selection, which
is exactly what a QUBO can express::

    maximise   sum_{i<j} q_ij x_i x_j      subject to   sum_i x_i = k

with ``q_ij`` the composite score of the pair (i, j), and a large penalty on pairs the
redundancy rule would exclude. The approximation is not exact, because some terms
(Bliss saturation on shared targets, the safety union, the regimen burden) are not
pairwise. So the problem class carries both objectives, as the fragment problem does:
``qubo_objective`` is what the solvers optimise, and ``exact_objective`` re-scores a
selection with the true k-ary scorer. **How well the surrogate tracks the truth is
the thing being measured**, not assumed.

Because the solvers in :mod:`core.design.quantum_assembly` only need ``identifiers``,
``linear``, ``quadratic``, ``k``, the two objectives and a Hamiltonian summary, this
class works with them unchanged: enumeration, the exact eigensolver, and QAOA.

Honest limits
-------------
* QAOA runs on a **classical simulator**, so it is limited to roughly 20 qubits. At
  that size exhaustive enumeration also finishes instantly, so nothing here can show a
  quantum advantage. What it can show is whether the formulation is faithful at
  higher order and whether QAOA finds what exhaustive search finds.
* Classical heuristics (greedy, simulated annealing) scale to the full panel, which a
  simulator cannot. They are the honest baselines.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable, Sequence

import numpy as np

from core.biology.combination_scoring import (
    CombinationConfig, combination_metrics, eligible_drugs,
)
from core.design.quantum_assembly import FragmentSelection


@dataclass(frozen=True)
class RegimenWeights:
    """The one tunable in the surrogate: how hard a redundant pair is penalised."""

    redundancy_penalty: float = 3.0

    def as_dict(self) -> dict[str, float]:
        return {"redundancy_penalty": self.redundancy_penalty}


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


@dataclass(frozen=True)
class RegimenSelectionProblem:
    """A QUBO over which k agents to combine, with the true scorer alongside it."""

    drugs: tuple[dict[str, Any], ...]
    linear: dict[str, float]
    quadratic: dict[tuple[str, str], float]
    k: int
    signature: Any
    disease: Any
    config: CombinationConfig
    weights: RegimenWeights

    @property
    def identifiers(self) -> list[str]:
        return [d["name"] for d in self.drugs]

    def drug(self, name: str) -> dict[str, Any]:
        for drug in self.drugs:
            if drug["name"] == name:
                return drug
        raise KeyError(name)

    def qubo_objective(self, selection: Iterable[str]) -> float:
        """The pairwise surrogate the solvers optimise."""
        chosen = list(selection)
        value = sum(self.linear[i] for i in chosen)
        for pair in combinations(sorted(chosen), 2):
            value += self.quadratic[pair]
        return round(value, 6)

    def exact_objective(self, selection: Iterable[str]) -> float:
        """The true k-ary composite score, with the redundancy exclusion priced in.

        A combination the screen would exclude from the primary ranking is charged
        the same penalty the surrogate charges, so the two objectives are on one
        footing and a selection that is redundant cannot look good on either.
        """
        members = [self.drug(n) for n in selection]
        if not members:
            return 0.0
        row = combination_metrics(members, self.signature, self.disease, self.config)
        score = float(row["priority_score"])
        if row["excluded_from_primary_ranking"]:
            score -= self.weights.redundancy_penalty
        return round(score, 6)

    def hamiltonian_summary(self) -> dict[str, Any]:
        return {
            "n_variables": len(self.drugs),
            "n_linear_terms": len(self.linear),
            "n_quadratic_terms": len(self.quadratic),
            "cardinality_constraint": self.k,
            "feasible_states": math.comb(len(self.drugs), self.k),
            "search_space": 2 ** len(self.drugs),
        }


def build_pool(drugs: Sequence[dict], signature, disease, config: CombinationConfig,
               size: int) -> list[dict]:
    """The ``size`` eligible agents with the best monotherapy composite score.

    A simulator cannot hold the whole panel, so a pool is chosen first, exactly as the
    fragment problem pre-filters its library. It is a real restriction: an agent that
    is weak alone and excellent in combination can be dropped before the optimiser
    sees it, so pool selection is reported wherever a result is.
    """
    eligible = eligible_drugs(drugs, config)
    scored = [
        (combination_metrics([d], signature, disease, config)["priority_score"], d["name"], d)
        for d in eligible
    ]
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [d for _, _, d in scored[:size]]


def build_regimen_problem(
    pool: Sequence[dict], signature, disease, k: int,
    config: CombinationConfig | None = None,
    weights: RegimenWeights | None = None,
) -> RegimenSelectionProblem:
    """The pairwise QUBO for choosing ``k`` agents from ``pool``."""
    config = config or CombinationConfig()
    weights = weights or RegimenWeights()
    names = [d["name"] for d in pool]
    quadratic: dict[tuple[str, str], float] = {}
    for a, b in combinations(pool, 2):
        row = combination_metrics([a, b], signature, disease, config)
        value = float(row["priority_score"])
        if row["excluded_from_primary_ranking"]:
            value -= weights.redundancy_penalty
        quadratic[_pair_key(a["name"], b["name"])] = round(value, 6)
    return RegimenSelectionProblem(
        drugs=tuple(pool), linear={n: 0.0 for n in names}, quadratic=quadratic, k=k,
        signature=signature, disease=disease, config=config, weights=weights,
    )


# ---------------------------------------------------------------------------
# What the truth is, and how well the surrogate tracks it
# ---------------------------------------------------------------------------

def true_landscape(problem: RegimenSelectionProblem) -> dict[tuple[str, ...], dict[str, float]]:
    """Score **every** feasible subset with both objectives.

    This is the ground truth the solvers are judged against, and it is only affordable
    because the pool is small. Beyond it there is no ground truth, which is the honest
    reason a claim about a large pool cannot be checked.
    """
    landscape: dict[tuple[str, ...], dict[str, float]] = {}
    for subset in combinations(sorted(problem.identifiers), problem.k):
        landscape[subset] = {
            "surrogate": problem.qubo_objective(subset),
            "true": problem.exact_objective(subset),
        }
    return landscape


def surrogate_fidelity(landscape: dict[tuple[str, ...], dict[str, float]]) -> dict[str, float]:
    """Rank correlation between the surrogate and the true score over all subsets."""
    from scipy.stats import spearmanr

    surrogate = [v["surrogate"] for v in landscape.values()]
    truth = [v["true"] for v in landscape.values()]
    rho = spearmanr(surrogate, truth)
    best_surrogate = max(landscape, key=lambda s: landscape[s]["surrogate"])
    best_true = max(landscape, key=lambda s: landscape[s]["true"])
    ranked = sorted(landscape, key=lambda s: -landscape[s]["true"])
    return {
        "n_subsets": len(landscape),
        "spearman": round(float(rho.statistic), 4),
        "surrogate_optimum_true_rank": ranked.index(best_surrogate) + 1,
        "surrogate_optimum_true_gap": round(
            landscape[best_true]["true"] - landscape[best_surrogate]["true"], 6
        ),
        "same_optimum": best_surrogate == best_true,
    }


# ---------------------------------------------------------------------------
# Classical baselines, which are what a simulator-bound quantum solver is measured against
# ---------------------------------------------------------------------------

def _as_selection(problem: RegimenSelectionProblem, ids: Iterable[str], backend: str,
                  detail: dict[str, Any] | None = None) -> FragmentSelection:
    ordered = tuple(sorted(ids))
    return FragmentSelection(
        identifiers=ordered,
        qubo_objective=problem.qubo_objective(ordered),
        exact_objective=problem.exact_objective(ordered),
        backend=backend,
        feasible=len(ordered) == problem.k,
        detail=detail or {},
    )


def solve_greedy(problem: RegimenSelectionProblem) -> FragmentSelection:
    """Add the agent with the best marginal surrogate gain until k are chosen."""
    chosen: list[str] = []
    remaining = list(problem.identifiers)
    while len(chosen) < problem.k:
        def gain(name: str) -> float:
            return sum(problem.quadratic[_pair_key(name, c)] for c in chosen)
        best = max(remaining, key=lambda n: (gain(n), -remaining.index(n)))
        chosen.append(best)
        remaining.remove(best)
    return _as_selection(problem, chosen, "greedy")


def solve_annealing(problem: RegimenSelectionProblem, seed: int = 7, steps: int = 4000,
                    start_temperature: float = 0.5) -> FragmentSelection:
    """Simulated annealing over fixed-size subsets, swapping one agent at a time."""
    rng = random.Random(seed)
    names = problem.identifiers
    current = rng.sample(names, problem.k)
    current_value = problem.qubo_objective(current)
    best, best_value = list(current), current_value
    for step in range(steps):
        temperature = start_temperature * (1.0 - step / steps) + 1e-9
        out = rng.choice(current)
        candidates = [n for n in names if n not in current]
        if not candidates:
            break
        incoming = rng.choice(candidates)
        proposal = [n for n in current if n != out] + [incoming]
        value = problem.qubo_objective(proposal)
        if value >= current_value or rng.random() < math.exp((value - current_value) / temperature):
            current, current_value = proposal, value
            if current_value > best_value:
                best, best_value = list(current), current_value
    return _as_selection(problem, best, "annealing", {"steps": steps, "seed": seed})


def solve_random(problem: RegimenSelectionProblem, seed: int = 7, draws: int = 200) -> FragmentSelection:
    """The best of ``draws`` random subsets: the floor any solver has to clear."""
    rng = random.Random(seed)
    best, best_value = None, -float("inf")
    for _ in range(draws):
        subset = rng.sample(problem.identifiers, problem.k)
        value = problem.qubo_objective(subset)
        if value > best_value:
            best, best_value = subset, value
    return _as_selection(problem, best or [], "random", {"draws": draws, "seed": seed})
