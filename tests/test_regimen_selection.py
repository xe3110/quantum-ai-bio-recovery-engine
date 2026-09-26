"""The higher-order regimen QUBO, its solvers, and the claims made about them.

What is held to account here is deliberately modest, because a simulator cannot
show a quantum advantage: that the surrogate is built the way its docstring says, that
every solver returns something feasible, that the constraint-preserving QAOA really
stays inside the feasible subspace, and that it does better than uniform sampling on the
quantity it optimises. Whether it finds the single best regimen is *not* asserted,
because on the measured problems it does not reliably do so.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pytest

from core.biology.combination_scoring import CombinationConfig, combination_metrics
from core.models.disease import load_disease
from core.quantum.constrained_qaoa import (
    _basis, _cost_vector, _xy_mixer, solve_constrained_qaoa,
)
from core.quantum.regimen_selection import (
    build_pool, build_regimen_problem, solve_annealing, solve_greedy, solve_random,
    surrogate_fidelity, true_landscape,
)


@pytest.fixture(scope="module")
def setup():
    disease = load_disease("guillain_barre")
    config = CombinationConfig()
    signature = disease.signature()
    pool = build_pool(disease.panel(), signature, disease, config, 8)
    return disease, signature, config, pool


@pytest.fixture(scope="module")
def problem(setup):
    disease, signature, config, pool = setup
    return build_regimen_problem(pool, signature, disease, 3, config)


def test_the_surrogate_is_the_sum_of_pair_scores(problem):
    """The QUBO objective must be exactly the pairwise decomposition it claims to be."""
    subset = problem.identifiers[:3]
    expected = sum(problem.quadratic[tuple(sorted(pair))] for pair in combinations(subset, 2))
    assert problem.qubo_objective(subset) == pytest.approx(expected, abs=1e-5)


def test_the_true_objective_is_the_k_ary_scorer(setup, problem):
    disease, signature, config, _ = setup
    subset = [n for n in problem.identifiers[:6]]
    for chosen in combinations(subset, 3):
        members = [problem.drug(n) for n in chosen]
        row = combination_metrics(members, signature, disease, config)
        expected = row["priority_score"] - (
            problem.weights.redundancy_penalty if row["excluded_from_primary_ranking"] else 0.0
        )
        assert problem.exact_objective(chosen) == pytest.approx(expected, abs=1e-5)


def test_a_redundant_pair_is_penalised_in_both_objectives(setup):
    """Two agents the redundancy rule excludes must look bad to the solvers as well."""
    disease, signature, config, _ = setup
    panel = {d["name"]: d for d in disease.panel()}
    duplicated = [panel["Gabapentin"], panel["Pregabalin"], panel["Plasma exchange"]]
    problem = build_regimen_problem(duplicated, signature, disease, 2, config)
    duplicate_pair = problem.qubo_objective(["Gabapentin", "Pregabalin"])
    clean_pair = problem.qubo_objective(["Gabapentin", "Plasma exchange"])
    assert duplicate_pair < clean_pair - 1.0


@pytest.mark.parametrize("solver", [solve_greedy, solve_annealing, solve_random])
def test_every_classical_solver_returns_a_feasible_selection(problem, solver):
    selection = solver(problem)
    assert selection.feasible and len(selection.identifiers) == problem.k


def test_the_surrogate_tracks_the_true_scorer_better_than_chance(problem):
    """A sanity floor, not a claim of accuracy: the measured value is about 0.9."""
    fidelity = surrogate_fidelity(true_landscape(problem))
    assert fidelity["spearman"] > 0.5


def test_the_xy_mixer_preserves_the_number_of_selected_agents():
    """Constraint preservation is the point of the ansatz, so check it directly."""
    n, k = 7, 3
    states, lookup = _basis(n, k)
    mixer = _xy_mixer(n, k, states, lookup).toarray()
    assert mixer.shape == (len(states), len(states))
    assert np.allclose(mixer, mixer.T)  # a Hamiltonian must be Hermitian
    for row, subset in enumerate(states):
        for col in np.nonzero(mixer[row])[0]:
            assert len(states[col]) == k
            assert len(set(subset) ^ set(states[col])) == 2  # exactly one swap


def test_the_cost_vector_matches_the_qubo_objective(problem):
    states, _ = _basis(len(problem.identifiers), problem.k)
    values = _cost_vector(problem, states)
    for index in (0, len(states) // 2, len(states) - 1):
        chosen = [problem.identifiers[i] for i in states[index]]
        assert values[index] == pytest.approx(problem.qubo_objective(chosen), abs=1e-4)


def test_constrained_qaoa_always_returns_a_feasible_selection(problem):
    selection = solve_constrained_qaoa(problem, reps=(1, 2), restarts=1, maxiter=40, shots=256)
    assert selection.feasible and len(selection.identifiers) == problem.k
    assert selection.detail["subspace_dimension"] < selection.detail["full_space_dimension"]


def test_constrained_qaoa_beats_uniform_sampling_on_what_it_optimises(problem):
    """The optimised state must have a lower expected cost than the uniform starting state.

    This is the claim the algorithm can actually support. Finding the single best
    subset is not asserted, and on the measured problems it is not reliable.
    """
    selection = solve_constrained_qaoa(problem, reps=(2,), restarts=2, maxiter=80, shots=256)
    states, _ = _basis(len(problem.identifiers), problem.k)
    value = _cost_vector(problem, states)
    lo, hi = value.min(), value.max()
    uniform_cost = float(np.mean(-(value - lo) / ((hi - lo) or 1.0)))
    optimised_cost = selection.detail["depth_sweep"][0]["expected_cost"]
    assert optimised_cost < uniform_cost
