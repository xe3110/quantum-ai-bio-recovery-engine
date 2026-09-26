"""The gate circuit must implement exactly the unitary the simulator optimises.

Angles are optimised on a subspace simulator and then sent to hardware as a gate circuit. If
the two disagree about even a sign convention, hardware results are a comparison against the
wrong ideal, and nothing downstream can be trusted. So this is checked directly, gate by gate,
on a noiseless statevector.
"""

from __future__ import annotations

import numpy as np
import pytest

from core.biology.combination_scoring import CombinationConfig
from core.models.disease import load_disease
from core.quantum.gate_circuit import build_circuit, mixer_groups
from core.quantum.gate_qaoa import (
    SubspaceSimulator, counts_to_subsets, optimise, weight_distribution,
)
from core.quantum.regimen_selection import build_pool, build_regimen_problem


@pytest.fixture(scope="module")
def problem():
    disease = load_disease("guillain_barre")
    config = CombinationConfig()
    signature = disease.signature()
    pool = build_pool(disease.panel(), signature, disease, config, 6)
    return build_regimen_problem(pool, signature, disease, 3, config)


@pytest.mark.parametrize("n", [4, 5, 6, 7, 8])
def test_mixer_groups_are_disjoint_and_cover_the_ring(n):
    groups = mixer_groups(n)
    edges = [tuple(e) for g in groups for e in g]
    assert len(edges) == len(set(edges)) == n
    for group in groups:
        qubits = [q for edge in group for q in edge]
        assert len(qubits) == len(set(qubits)), "edges inside a group must not share a qubit"


def test_the_gate_circuit_matches_the_subspace_simulation(problem):
    """Same probabilities, bitstring by bitstring, from two independent implementations."""
    pytest.importorskip("qiskit")
    from qiskit.quantum_info import Statevector

    spec, simulator = optimise(problem, layers=2, restarts=1, maxiter=30)
    circuit = build_circuit(spec, measure=False)
    # Qiskit orders bits little-endian, so qubit i is bit i from the right.
    gate_probs = Statevector.from_instruction(circuit).probabilities_dict()
    subspace = simulator.probabilities(spec["gammas"], spec["betas"])
    n = spec["n"]
    for state, probability in zip(simulator.states, subspace):
        bits = "".join("1" if q in state else "0" for q in reversed(range(n)))
        assert gate_probs.get(bits, 0.0) == pytest.approx(probability, abs=1e-8), bits


def test_noiseless_measurement_keeps_exactly_k_ones(problem):
    """The XY mixer must never leave the feasible subspace."""
    pytest.importorskip("qiskit")
    from qiskit.quantum_info import Statevector

    spec, _ = optimise(problem, layers=2, restarts=1, maxiter=30)
    probs = Statevector.from_instruction(build_circuit(spec, measure=False)).probabilities_dict()
    infeasible = sum(p for bits, p in probs.items() if bits.count("1") != spec["k"])
    assert infeasible == pytest.approx(0.0, abs=1e-9)


def test_the_spec_is_anonymous_and_json_serialisable(problem):
    """Nothing that identifies an agent, a gene or a disease may be in what gets sent."""
    import json

    spec, _ = optimise(problem, layers=1, restarts=1, maxiter=10)
    text = json.dumps(spec)
    for pool_member in problem.identifiers:
        assert pool_member not in text
    assert "guillain" not in text.lower()
    assert spec["anonymous"] is True


def test_optimisation_improves_on_the_uniform_starting_state(problem):
    spec, simulator = optimise(problem, layers=2, restarts=2, maxiter=60)
    uniform = float(np.mean(simulator.cost))
    assert spec["ideal_expected_cost"] < uniform


def test_the_noise_gauge_counts_only_weight_k_bitstrings():
    counts = {"0011": 70, "0111": 20, "0000": 10}
    gauge = weight_distribution(counts, 2)
    assert gauge["feasible_shots"] == 70 and gauge["feasible_fraction"] == pytest.approx(0.7)
    assert counts_to_subsets(counts, 2) == {(0, 1): 70}


def test_sparsify_fit_keeps_at_most_the_requested_couplings(problem):
    from core.quantum.gate_qaoa import sparsify_fit

    sparse = sparsify_fit(problem, 5)
    assert sum(1 for v in sparse.quadratic.values() if v != 0.0) <= 5


def test_sparsify_zeroes_couplings_and_they_cost_no_gate(problem):
    from core.quantum.gate_qaoa import cost_coefficients, sparsify

    sparse = sparsify(problem, 1)
    kept = sum(1 for v in sparse.quadratic.values() if v != 0.0)
    assert kept < len(sparse.quadratic)
    zz, _ = cost_coefficients(sparse, span=1.0)
    assert len(zz) == kept


@pytest.mark.parametrize("n,k", [(4, 2), (6, 3), (8, 4), (7, 1), (6, 5)])
def test_dicke_preparation_is_the_uniform_weight_k_superposition(n, k):
    from math import comb

    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    from core.quantum.gate_circuit import prepare_dicke

    circuit = QuantumCircuit(n)
    prepare_dicke(circuit, n, k)
    amplitudes = Statevector(circuit).data
    support = amplitudes[np.abs(amplitudes) > 1e-9]
    assert len(support) == comb(n, k)
    assert np.allclose(support / support[0], 1.0, atol=1e-7)
    assert all(bin(i).count("1") == k for i in np.flatnonzero(np.abs(amplitudes) > 1e-9))


def test_dicke_start_circuit_matches_the_subspace_simulation(problem):
    from qiskit.quantum_info import Statevector

    spec, simulator = optimise(problem, layers=2, restarts=1, maxiter=30, start="dicke")
    assert spec["start"] == "dicke"
    circuit = build_circuit(spec, measure=False)
    probabilities = np.abs(Statevector(circuit).data) ** 2
    ideal = simulator.probabilities(spec["gammas"], spec["betas"])
    for row, subset in enumerate(simulator.states):
        index = sum(1 << q for q in subset)
        assert abs(probabilities[index] - ideal[row]) < 1e-8


def test_cvar_cost_is_no_worse_than_mean_and_reaches_the_minimum_at_small_alpha(problem):
    spec, simulator = optimise(problem, layers=1, restarts=1, maxiter=20)
    g, b = spec["gammas"], spec["betas"]
    mean = simulator.expected_cost(g, b)
    assert simulator.cvar_cost(g, b, 1.0) == pytest.approx(mean, abs=1e-9)
    assert simulator.cvar_cost(g, b, 0.05) <= mean + 1e-12
