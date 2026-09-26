"""Run an anonymous circuit spec on IBM hardware, or on a free local model of it.

This runs in the separate ``qbio-ibm-env`` environment, because IBM's runtime library needs a
newer Qiskit than the rest of the project is pinned to. It imports only
``core.quantum.gate_circuit``, which has no project dependencies, and reads only the anonymous
``*.spec.json``. It never sees the private file, so no agent, gene or disease name can leave.

    check       authenticate and list devices. Sends nothing.
    noisy-sim   FREE: run the spec on a noise model of a real IBM device, locally. No account.
    submit      run the spec on real IBM hardware. Uses your monthly free quota.
    retrieve    fetch the counts of a previously submitted job

Credentials: set them in your own shell, never in this repository or a chat.
    export QISKIT_IBM_TOKEN=<your IBM Quantum Platform API key>
    export QISKIT_IBM_INSTANCE=<optional: your instance CRN>

Usage:
    qbio-ibm-env/bin/python -m experiments.quantum.ibm_run noisy-sim --spec results/ibm/T.spec.json
    qbio-ibm-env/bin/python -m experiments.quantum.ibm_run check
    qbio-ibm-env/bin/python -m experiments.quantum.ibm_run submit --spec results/ibm/T.spec.json --yes
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from core.quantum.gate_circuit import build_circuit

OUT = Path(__file__).resolve().parent / "results/ibm"
NO_TOKEN = (
    "No IBM credentials found. In your own terminal (not here, and not in a chat), run:\n"
    "    export QISKIT_IBM_TOKEN=<your IBM Quantum Platform API key>\n"
    "    export QISKIT_IBM_INSTANCE=<optional: your instance CRN>\n"
    "then run this command again. Create an account and key at https://quantum.cloud.ibm.com ."
)


def service():
    from qiskit_ibm_runtime import QiskitRuntimeService

    if not os.environ.get("QISKIT_IBM_TOKEN"):
        try:
            return QiskitRuntimeService()  # a locally saved account, if any
        except Exception:
            raise SystemExit(NO_TOKEN)
    return QiskitRuntimeService(token=os.environ["QISKIT_IBM_TOKEN"],
                                instance=os.environ.get("QISKIT_IBM_INSTANCE"))


def load_spec(path: str) -> dict:
    spec = json.loads(Path(path).read_text())
    if not spec.get("anonymous"):
        raise SystemExit("Refusing to use a spec that is not marked anonymous.")
    return spec


def transpile_for(circuit, backend, seed: int = 7):
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    manager = generate_preset_pass_manager(optimization_level=3, backend=backend, seed_transpiler=seed)
    isa = manager.run(circuit)
    ops = dict(isa.count_ops())
    two_qubit = sum(v for name, v in ops.items() if name in ("cz", "ecr", "cx", "rzz", "swap"))
    return isa, {"depth": isa.depth(), "two_qubit_gates": two_qubit, "gate_counts": ops}


def save(tag: str, source: str, backend_name: str, counts: dict, extra: dict) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{tag}.{source}.counts.json"
    path.write_text(json.dumps({"tag": tag, "source": source, "backend": backend_name,
                                "counts": counts, **extra}, indent=2) + "\n")
    return path


def cmd_check(args) -> None:
    svc = service()
    backends = svc.backends(simulator=False, operational=True)
    print(f"Authenticated. {len(backends)} operational real devices available to this account:\n")
    for backend in sorted(backends, key=lambda b: b.status().pending_jobs):
        status = backend.status()
        print(f"  {backend.name:22s} {backend.num_qubits:4d} qubits   queue {status.pending_jobs:4d}")
    print("\nNothing was sent. Choose a device with few pending jobs, then use `submit`.")


def cmd_noisy_sim(args) -> None:
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

    spec = load_spec(args.spec)
    fake = FakeSherbrooke()
    circuit = build_circuit(spec)
    isa, transpiled = transpile_for(circuit, fake)
    print(f"Transpiled for {fake.name} ({fake.num_qubits} qubits): "
          f"{transpiled['two_qubit_gates']} two-qubit gates, depth {transpiled['depth']}")
    simulator = AerSimulator.from_backend(fake)
    started = time.perf_counter()
    result = simulator.run(isa, shots=args.shots, seed_simulator=args.seed).result()
    counts = result.get_counts()
    print(f"Simulated {args.shots} shots with the device's noise model in "
          f"{time.perf_counter() - started:.1f}s (local, free, no account).")
    tag = Path(args.spec).name.replace(".spec.json", "")
    path = save(tag, "noisy_simulator", fake.name, counts,
                {"shots": args.shots, "transpiled": transpiled})
    print(f"Wrote {path}")


def cmd_submit(args) -> None:
    from qiskit_ibm_runtime import SamplerV2

    spec = load_spec(args.spec)
    svc = service()
    n = int(spec["n"])
    backend = (svc.backend(args.backend) if args.backend else
               svc.least_busy(operational=True, simulator=False, min_num_qubits=n))
    circuit = build_circuit(spec)
    isa, transpiled = transpile_for(circuit, backend)
    print(f"Device: {backend.name} ({backend.num_qubits} qubits, queue {backend.status().pending_jobs})")
    print(f"Circuit: {n} qubits, k = {spec['k']}, {spec['layers']} layers -> "
          f"{transpiled['two_qubit_gates']} two-qubit gates after transpiling, depth {transpiled['depth']}")
    print(f"Shots: {args.shots}. This sends ONLY the anonymous circuit (numbers, no names) and "
          "uses your monthly free quota.")
    if not args.yes:
        raise SystemExit("Dry run only. Re-run with --yes to submit.")
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = args.shots
    sampler.options.dynamical_decoupling.enable = True
    job = sampler.run([isa])
    print(f"Submitted job {job.job_id()}. Waiting for it (this is a queue; it may take a while)...")
    result = job.result()
    counts = result[0].data.c.get_counts()
    usage = None
    try:
        usage = job.usage()
    except Exception:
        pass
    tag = Path(args.spec).name.replace(".spec.json", "")
    path = save(tag, "ibm_hardware", backend.name, counts,
                {"shots": args.shots, "job_id": job.job_id(), "transpiled": transpiled,
                 "quantum_seconds_used": usage})
    print(f"Wrote {path}  (quantum seconds used: {usage})")


def cmd_retrieve(args) -> None:
    svc = service()
    job = svc.job(args.job_id)
    result = job.result()
    counts = result[0].data.c.get_counts()
    tag = args.tag or args.job_id
    path = save(tag, "ibm_hardware", job.backend().name, counts, {"job_id": args.job_id})
    print(f"Wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    n = sub.add_parser("noisy-sim")
    n.add_argument("--spec", required=True)
    n.add_argument("--shots", type=int, default=4000)
    n.add_argument("--seed", type=int, default=7)
    s = sub.add_parser("submit")
    s.add_argument("--spec", required=True)
    s.add_argument("--backend", default=None)
    s.add_argument("--shots", type=int, default=4000)
    s.add_argument("--yes", action="store_true")
    r = sub.add_parser("retrieve")
    r.add_argument("--job-id", required=True)
    r.add_argument("--tag", default=None)
    args = parser.parse_args()
    {"check": cmd_check, "noisy-sim": cmd_noisy_sim, "submit": cmd_submit,
     "retrieve": cmd_retrieve}[args.command](args)


if __name__ == "__main__":
    main()
