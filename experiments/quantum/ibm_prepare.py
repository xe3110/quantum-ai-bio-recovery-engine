"""Prepare an anonymous circuit spec for IBM hardware, and analyse what comes back.

This runs in the project's normal environment. It never imports the IBM runtime, and
nothing it writes to ``*.spec.json`` identifies an agent, a gene or a disease.

    prepare   optimise the angles on a simulator and write two files:
                  <tag>.spec.json     anonymous: the only file that may be sent anywhere
                  <tag>.private.json  local only: which qubit is which agent, the ideal
                                      distribution, and the true landscape
    analyze   read hardware (or noisy-simulator) counts back and judge them

Usage:
    python -m experiments.quantum.ibm_prepare prepare --disease guillain_barre --pool 8 --k 4 --layers 2
    python -m experiments.quantum.ibm_prepare analyze --tag guillain_barre_n8_k4_p2 --counts results/ibm/<counts>.json
"""

from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path

from core.biology.combination_scoring import CombinationConfig
from core.models.disease import load_disease
from core.quantum.gate_qaoa import (
    counts_to_subsets, optimise, sparsify, total_variation, weight_distribution,
)
from core.quantum.regimen_selection import (
    build_pool, build_regimen_problem, true_landscape,
)

OUT = Path(__file__).resolve().parent / "results/ibm"


def build(disease_name: str, pool_size: int, k: int):
    disease = load_disease(disease_name)
    config = CombinationConfig()
    signature = disease.signature()
    pool = build_pool(disease.panel(), signature, disease, config, pool_size)
    return build_regimen_problem(pool, signature, disease, k, config)


def prepare(args) -> None:
    problem = build(args.disease, args.pool, args.k)
    tag = f"{args.disease}_n{len(problem.identifiers)}_k{args.k}_p{args.layers}"
    dense_problem = problem
    if args.keep:
        problem = sparsify(problem, args.keep)
        tag += f"_s{args.keep}"
    if args.start == "dicke":
        tag += "_d"
    spec, simulator = optimise(problem, layers=args.layers, seed=args.seed,
                               restarts=args.restarts, maxiter=args.maxiter, start=args.start)
    probs = simulator.probabilities(spec["gammas"], spec["betas"])
    ideal = {simulator.states[i]: float(p) for i, p in enumerate(probs)}
    landscape = true_landscape(dense_problem)
    ranked = sorted(landscape, key=lambda s: -landscape[s]["true"])
    names = problem.identifiers
    index = {n: i for i, n in enumerate(names)}

    def by_index(subset_names):
        return tuple(sorted(index[n] for n in subset_names))

    surrogate_best = max(landscape, key=lambda s: landscape[s]["surrogate"])
    private = {
        "tag": tag, "disease": args.disease, "qubit_to_agent": names, "k": args.k,
        "ideal_probabilities": [[list(s), p] for s, p in ideal.items()],
        "true_rank_by_subset": [[list(by_index(s)), r + 1] for r, s in enumerate(ranked)],
        "surrogate_by_subset": [[list(by_index(s)), landscape[s]["surrogate"]] for s in landscape],
        "surrogate_optimum": list(by_index(surrogate_best)),
        "true_optimum": list(by_index(ranked[0])),
        "feasible_subsets": comb(len(names), args.k),
        "uniform_feasible_fraction": comb(len(names), args.k) / 2 ** len(names),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{tag}.spec.json").write_text(json.dumps(spec, indent=2) + "\n")
    (OUT / f"{tag}.private.json").write_text(json.dumps(private, indent=2) + "\n")
    print(f"tag: {tag}")
    print(f"  qubits {spec['n']}, k = {spec['k']}, layers {spec['layers']}, "
          f"{len(spec['zz'])} ZZ terms, optimised in {spec['optimisation_seconds']}s on a simulator")
    print(f"  ideal (noiseless) expected cost {spec['ideal_expected_cost']}; "
          f"a random feasible bitstring would be {sum(simulator.cost) / len(simulator.cost):.3f}")
    print(f"  wrote {OUT / (tag + '.spec.json')}  (anonymous; the only file to send)")
    print(f"  wrote {OUT / (tag + '.private.json')}  (local only)")


def analyze(args) -> None:
    private = json.loads((OUT / f"{args.tag}.private.json").read_text())
    counts_payload = json.loads(Path(args.counts).read_text())
    counts = counts_payload["counts"]
    k = private["k"]
    gauge = weight_distribution(counts, k)
    uniform = private["uniform_feasible_fraction"]
    feasible = counts_to_subsets(counts, k)
    total_feasible = sum(feasible.values())
    measured = {s: c / total_feasible for s, c in feasible.items()} if total_feasible else {}
    ideal = {tuple(s): p for s, p in private["ideal_probabilities"]}
    rank = {tuple(s): r for s, r in private["true_rank_by_subset"]}
    surrogate = {tuple(s): v for s, v in private["surrogate_by_subset"]}
    names = private["qubit_to_agent"]
    print(f"Source: {counts_payload.get('source', '?')}  ({counts_payload.get('backend', '?')}, "
          f"{gauge['shots']} shots)")
    print(f"  qubits {len(names)}, k = {k}, feasible subsets {private['feasible_subsets']:,}")
    print(f"  fraction of shots with exactly k ones: {gauge['feasible_fraction']:.3f}"
          f"   (noiseless ideal 1.000; uniform random bits {uniform:.4f})")
    if counts_payload.get("transpiled"):
        t = counts_payload["transpiled"]
        print(f"  transpiled: {t.get('two_qubit_gates')} two-qubit gates, depth {t.get('depth')}")
    if total_feasible == 0:
        print("  no feasible shots: the circuit's output is indistinguishable from noise.")
        return
    tv = total_variation(measured, ideal)
    top = max(feasible, key=feasible.get)
    best = max(feasible, key=lambda s: surrogate[s])
    ideal_top = max(ideal, key=ideal.get)
    uniform_tv = total_variation({s: 1.0 / len(ideal) for s in ideal}, ideal)
    print(f"  among feasible shots: total variation from the ideal distribution {tv:.3f}"
          f"  (a uniform distribution would be {uniform_tv:.3f})")
    print(f"  best measured feasible regimen (by surrogate): true rank {rank[best]} of "
          f"{private['feasible_subsets']:,}; ideal-circuit mode has true rank {rank[ideal_top]}; "
          f"surrogate optimum has true rank {rank[tuple(private['surrogate_optimum'])]}")
    print(f"  most-measured feasible regimen: {[names[i] for i in top]}  (measured {measured[top]:.3f})")
    coverage = len(feasible) / private["feasible_subsets"]
    if coverage > 0.5:
        print(f"  caution: the shots visited {coverage:.0%} of all feasible subsets, so the rank of the best "
              "measured regimen says little; sampling alone would find good ones.")
    fraction = gauge["feasible_fraction"]
    if fraction >= 0.5 and tv <= 0.5 * uniform_tv:
        verdict = "clear signal: most shots stay feasible and the distribution is far closer to ideal than uniform"
    elif fraction > 1.25 * uniform and tv < 0.9 * uniform_tv:
        verdict = "partial signal: weight is preserved above chance and the distribution is closer to ideal than uniform"
    else:
        verdict = "no reliable signal: noise has washed out the circuit's structure"
    print("  verdict: " + verdict)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--disease", required=True)
    p.add_argument("--pool", type=int, default=8)
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--layers", type=int, default=2)
    p.add_argument("--keep", type=int, default=0,
                   help="sparsify: keep each agent's N strongest couplings (0 = dense)")
    p.add_argument("--start", choices=("basis", "dicke"), default="basis",
                   help="initial state: one feasible subset, or the uniform superposition of all")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--restarts", type=int, default=4)
    p.add_argument("--maxiter", type=int, default=200)
    a = sub.add_parser("analyze")
    a.add_argument("--tag", required=True)
    a.add_argument("--counts", required=True)
    args = parser.parse_args()
    {"prepare": prepare, "analyze": analyze}[args.command](args)


if __name__ == "__main__":
    main()
