"""The gate-level circuit for weight-preserving QAOA, with no project dependencies.

This module builds a plain Qiskit circuit from a JSON-serialisable *spec*, and imports
nothing from the rest of the project. That is deliberate. The IBM runtime library needs a
newer Qiskit than the one the rest of the project is pinned to, so it lives in a separate
environment (``qbio-ibm-env``), and this file is the only piece of project code that
environment needs.

What a spec contains, and what it does not
------------------------------------------
Numbers only: the qubit count, the number of selected qubits ``k``, the coefficients of
the cost Hamiltonian, the mixer's edge groups, the initial bitstring, and the angles. It
carries **no drug names, no gene names and no disease**. Qubit ``i`` is just an index.
The mapping from index to agent stays on the local machine, so anonymous circuit
geometry is all that would ever be sent to an external service.

The ansatz
----------
A quantum alternating operator ansatz that preserves the number of ones:

* start in a computational basis state with ``k`` ones (a feasible selection), or, when
  the spec says ``"start": "dicke"``, in the uniform superposition of all of them;
* each layer applies the cost as diagonal phases, ``exp(-i gamma H_C)`` with
  ``H_C = sum c_ij Z_i Z_j + sum d_i Z_i``, using ``RZZ`` and ``RZ`` gates;
* then the XY mixer over a ring of adjacent qubits, one edge group at a time, using
  ``RXX`` and ``RYY`` gates, which swap an occupied and an empty position and so keep
  the number of ones fixed. Edges inside a group are disjoint, so the group's gates
  commute and the Trotter product is exact for that group.

On a noiseless machine every measured bitstring has exactly ``k`` ones. On a real device
noise breaks that, so **the fraction of measured bitstrings with weight ``k``** is a
direct, model-free gauge of how much noise the circuit has picked up.
"""

from __future__ import annotations

from typing import Any


def mixer_groups(n: int) -> list[list[tuple[int, int]]]:
    """Ring edges split into groups of disjoint edges (two groups if n is even, else three)."""
    edges = [(i, (i + 1) % n) for i in range(n)] if n > 2 else [(0, 1)]
    if n <= 2:
        return [edges]
    even = [e for e in edges if e[0] % 2 == 0 and e[0] != n - 1]
    odd = [e for e in edges if e[0] % 2 == 1 and e[0] != n - 1]
    closing = [(n - 1, 0)]
    if n % 2 == 0:
        return [even, odd + closing]
    return [even, odd, closing]


def prepare_dicke(circuit, n: int, k: int) -> None:
    """Prepare the uniform superposition of all weight-``k`` bitstrings on qubits ``0..n-1``.

    The Bärtschi-Eidenbenz construction: start from ``k`` ones at the front, then apply
    split-and-cyclic-shift blocks (a two-qubit and several three-qubit partial-swap gates)
    over shrinking windows, about ``n * k`` two-qubit gates and linear depth. The exact
    gate roles were fixed by checking the output statevector against the Dicke state,
    amplitude and phase, for every (n, k) tested, not taken from memory of the paper.
    """
    from math import acos, sqrt

    from qiskit.circuit.library import RYGate

    for qubit in range(k):
        circuit.x(qubit)

    def block(m: int, window: int) -> None:
        w = list(range(n - m, n - m + window + 1))
        a, b = w[0], w[1]
        circuit.cx(b, a)
        circuit.cry(2.0 * acos(sqrt(1.0 / m)), a, b)
        circuit.cx(b, a)
        for l in range(2, window + 1):
            p, q, r = w[0], w[l - 1], w[l]
            circuit.cx(p, r)
            circuit.append(RYGate(-2.0 * acos(sqrt(l / m))).control(2), [q, r, p])
            circuit.cx(p, r)

    for m in range(n, k, -1):
        block(m, k)
    for m in range(k, 1, -1):
        block(m, m - 1)


def build_circuit(spec: dict[str, Any], measure: bool = True):
    """The QAOA circuit for a spec, as a plain Qiskit ``QuantumCircuit``."""
    from qiskit import QuantumCircuit

    n = int(spec["n"])
    circuit = QuantumCircuit(n, n if measure else 0)
    if spec.get("start") == "dicke":
        prepare_dicke(circuit, n, int(spec["k"]))
    else:
        for qubit in spec["initial"]:
            circuit.x(qubit)
    for gamma, beta in zip(spec["gammas"], spec["betas"]):
        for i, j, coefficient in spec["zz"]:
            circuit.rzz(2.0 * gamma * coefficient, i, j)
        for i, coefficient in enumerate(spec["z"]):
            if coefficient:
                circuit.rz(2.0 * gamma * coefficient, i)
        for group in spec["mixer_groups"]:
            for a, b in group:
                circuit.rxx(beta, a, b)
                circuit.ryy(beta, a, b)
    if measure:
        circuit.measure(range(n), range(n))
    return circuit
