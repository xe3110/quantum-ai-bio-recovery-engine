"""Choose the best k-drug regimen (k = 4, 5, 6) as a QUBO, and judge every solver against the truth.

The exhaustive combination screen stops at k = 3. This experiment applies the project's
quantum machinery to the question that lies beyond it: which k agents from a pool. It
runs, on one Hamiltonian per (disease, k):

* exhaustive enumeration of the pairwise surrogate (the surrogate's exact optimum),
* the exact eigensolver (classical diagonalisation via Qiskit),
* QAOA on a classical simulator, swept across circuit depths,
* three classical baselines: greedy, simulated annealing, and best-of-N random,

and then **re-scores every solver's answer with the true k-ary scorer** and ranks it
against every feasible subset in the pool. The pool is small enough (<= 20 qubits, the
limit of a simulator) that the true optimum is known by exhaustive scoring, so each
solver is judged against ground truth and not against another heuristic.

A quantum advantage cannot be shown here: at these sizes enumeration is instant.
What can be shown is (1) whether the pairwise surrogate is a faithful stand-in for the
k-ary scorer, (2) whether QAOA finds what exhaustive search finds as the problem grows,
and (3) how the classical heuristics compare, including on the full panel where a
simulator cannot go.

Usage:
    python -m experiments.quantum.run_regimen_selection --disease guillain_barre
    python -m experiments.quantum.run_regimen_selection --disease epilepsy --pool 20 --k 4 5 6
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import time
from itertools import combinations
from pathlib import Path

from core.biology.combination_scoring import CombinationConfig, combination_metrics, eligible_drugs
from core.design.quantum_assembly import (
    HAS_QISKIT, solve_eigensolver, solve_enumeration, solve_qaoa_sweep,
)
from core.models.disease import load_disease
from core.provenance import run_provenance
from core.quantum.constrained_qaoa import solve_constrained_qaoa
from core.quantum.regimen_selection import (
    RegimenSelectionProblem, build_pool, build_regimen_problem, solve_annealing,
    solve_greedy, solve_random, surrogate_fidelity, true_landscape,
)

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments/quantum/results"


def _judge(problem, selection, landscape, ranked, best_true_value, seconds):
    ids = tuple(sorted(selection.identifiers))
    true_value = landscape[ids]["true"] if ids in landscape else selection.exact_objective
    return {
        "backend": selection.backend,
        "regimen": list(ids),
        "feasible": selection.feasible,
        "surrogate_objective": selection.qubo_objective,
        "true_score": true_value,
        "true_rank_of_all": (ranked.index(ids) + 1) if ids in landscape else None,
        "true_gap_to_optimum": round(best_true_value - true_value, 6),
        "is_true_optimum": bool(ids in landscape and ranked[0] == ids),
        "seconds": round(seconds, 3),
        "detail": selection.detail,
    }


def run_one(problem: RegimenSelectionProblem, reps, seed, maxiter, shots, random_draws, restarts):
    landscape = true_landscape(problem)
    ranked = sorted(landscape, key=lambda s: -landscape[s]["true"])
    best_true_value = landscape[ranked[0]]["true"]
    fidelity = surrogate_fidelity(landscape)

    runs = []

    def timed(fn, *args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        return result, time.perf_counter() - start

    reference, seconds = timed(lambda: solve_enumeration(problem, top=1)[0])
    runs.append(_judge(problem, reference, landscape, ranked, best_true_value, seconds))
    for factory in (
        lambda: solve_greedy(problem),
        lambda: solve_annealing(problem, seed=seed),
        lambda: solve_random(problem, seed=seed, draws=random_draws),
        lambda: solve_random(problem, seed=seed, draws=shots),
    ):
        selection, seconds = timed(factory)
        run = _judge(problem, selection, landscape, ranked, best_true_value, seconds)
        if selection.backend == "random" and selection.detail.get("draws") == shots:
            run["backend"] = "random_matched"  # same number of draws as the quantum solver's shots
        runs.append(run)
    constrained, seconds = timed(
        lambda: solve_constrained_qaoa(problem, reps=reps, seed=seed, restarts=restarts,
                                       maxiter=maxiter, shots=shots))
    runs.append(_judge(problem, constrained, landscape, ranked, best_true_value, seconds))
    cvar, seconds = timed(
        lambda: solve_constrained_qaoa(problem, reps=reps, seed=seed, restarts=restarts,
                                       maxiter=maxiter, shots=shots, cvar_alpha=0.02))
    cvar = dataclasses.replace(cvar, backend="qaoa_constrained_cvar")
    runs.append(_judge(problem, cvar, landscape, ranked, best_true_value, seconds))
    if HAS_QISKIT:
        for name, factory in (
            ("eigensolver", lambda: solve_eigensolver(problem)),
            ("qaoa", lambda: solve_qaoa_sweep(problem, reps_range=reps, seed=seed,
                                              maxiter=maxiter, shots=shots)),
        ):
            try:
                selection, seconds = timed(factory)
            except Exception as error:  # pragma: no cover - backend availability
                runs.append({"backend": name, "error": f"{type(error).__name__}: {error}"})
                continue
            runs.append(_judge(problem, selection, landscape, ranked, best_true_value, seconds))
    else:
        runs.append({"backend": "eigensolver+qaoa", "skipped": "qiskit not installed"})
    surrogate_optimum = runs[0]
    for run in runs:
        if "surrogate_objective" in run:
            run["matches_surrogate_optimum"] = (
                run["surrogate_objective"] >= surrogate_optimum["surrogate_objective"] - 1e-9
                and run["feasible"]
            )
    return {
        "k": problem.k,
        "hamiltonian": problem.hamiltonian_summary(),
        "surrogate_fidelity": fidelity,
        "true_optimum": {"regimen": list(ranked[0]), "true_score": best_true_value},
        "solvers": runs,
    }


def scale_test(disease, signature, config, k, seed, random_draws=3000):
    """Annealing on the FULL panel, beyond what a simulator can hold, versus random regimens.

    There is no ground truth at this size, so the claim is only that a heuristic beats
    random by a margin, and that is what is reported.
    """
    import random as _random

    panel = eligible_drugs(disease.panel(), config)
    pool_all = build_regimen_problem(panel, signature, disease, k, config)
    start = time.perf_counter()
    annealed = solve_annealing(pool_all, seed=seed, steps=20000)
    seconds = time.perf_counter() - start
    rng = _random.Random(seed)
    names = pool_all.identifiers
    randoms = sorted(
        (pool_all.exact_objective(rng.sample(names, k)) for _ in range(random_draws)), reverse=True
    )
    return {
        "k": k, "n_agents": len(names),
        "feasible_subsets": pool_all.hamiltonian_summary()["feasible_states"],
        "annealed_regimen": list(annealed.identifiers),
        "annealed_true_score": annealed.exact_objective,
        "annealing_seconds": round(seconds, 2),
        "random_best_true_score": randoms[0],
        "random_median_true_score": randoms[len(randoms) // 2],
        "random_draws": random_draws,
        "annealed_beats_best_random": annealed.exact_objective > randoms[0],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--disease", required=True)
    parser.add_argument("--pool", type=int, default=18, help="qubits: agents in the pool")
    parser.add_argument("--k", type=int, nargs="+", default=[4, 5, 6])
    parser.add_argument("--reps", type=int, nargs="+", default=[1, 2, 3, 4])
    parser.add_argument("--restarts", type=int, default=2, help="optimiser restarts per depth")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--maxiter", type=int, default=150)
    parser.add_argument("--shots", type=int, default=2048)
    parser.add_argument("--random-draws", type=int, default=100)
    parser.add_argument("--scale-test", action="store_true",
                        help="also anneal on the full panel, beyond simulator size")
    args = parser.parse_args()

    disease = load_disease(args.disease)
    signature = disease.signature()
    config = CombinationConfig()
    pool = build_pool(disease.panel(), signature, disease, config, args.pool)
    print(f"Disease: {disease.name}; pool of {len(pool)} of "
          f"{len(eligible_drugs(disease.panel(), config))} eligible agents")
    print("Pool:", ", ".join(d["name"] for d in pool), "\n")

    results = []
    for k in args.k:
        problem = build_regimen_problem(pool, signature, disease, k, config)
        entry = run_one(problem, tuple(args.reps), args.seed, args.maxiter, args.shots,
                        args.random_draws, args.restarts)
        results.append(entry)
        fid = entry["surrogate_fidelity"]
        print(f"k = {k}: {entry['hamiltonian']['feasible_states']:,} feasible subsets; "
              f"surrogate Spearman {fid['spearman']}; surrogate optimum is true rank "
              f"{fid['surrogate_optimum_true_rank']}")
        print(f"  true optimum: {', '.join(entry['true_optimum']['regimen'])}"
              f" ({entry['true_optimum']['true_score']})")
        for run in entry["solvers"]:
            if run["backend"] in ("qaoa_constrained", "qaoa_constrained_cvar"):
                sweep = run["detail"]["depth_sweep"]
                uniform = 1.0 / entry["hamiltonian"]["feasible_states"]
                best = max(sweep, key=lambda a: a["p_top_1_percent"])
                run["enrichment"] = {
                    "p_top_1_percent_best_depth": best["p_top_1_percent"],
                    "uniform_top_1_percent": 0.01,
                    "top_1_percent_enrichment": round(best["p_top_1_percent"] / 0.01, 1),
                    "p_optimum_best": max(a["p_surrogate_optimum"] for a in sweep),
                    "uniform_p_optimum": round(uniform, 6),
                }
            if "error" in run or "skipped" in run:
                print(f"  {run['backend']:12s} {run.get('error') or run['skipped']}")
                continue
            flag = "TRUE OPT" if run["is_true_optimum"] else f"rank {run['true_rank_of_all']}"
            print(f"  {run['backend']:12s} surrogate {run['surrogate_objective']:8.3f}  "
                  f"true {run['true_score']:7.3f}  {flag:9s} gap {run['true_gap_to_optimum']:6.3f}"
                  f"  {run['seconds']:7.2f}s"
                  f"{'' if run.get('matches_surrogate_optimum') else '  (misses surrogate optimum)'}")
            if run.get("enrichment"):
                e = run["enrichment"]
                print(f"    state concentration: top-1% subsets hold {e['p_top_1_percent_best_depth']:.3f} "
                      f"of the probability ({e['top_1_percent_enrichment']}x uniform); "
                      f"P(true surrogate optimum) {e['p_optimum_best']:.1e} vs uniform "
                      f"{e['uniform_p_optimum']:.1e}")
        print()

    scale = []
    if args.scale_test:
        for k in args.k:
            entry = scale_test(disease, signature, config, k, args.seed)
            scale.append(entry)
            print(f"Full panel, k = {k}: {entry['n_agents']} agents, "
                  f"{entry['feasible_subsets']:,} subsets; annealed true score "
                  f"{entry['annealed_true_score']:.3f} against best-of-{entry['random_draws']} random "
                  f"{entry['random_best_true_score']:.3f} (median {entry['random_median_true_score']:.3f})")

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"{args.disease}_regimen_selection.json"
    out.write_text(json.dumps({
        "provenance": run_provenance(
            [disease.signature_path, disease.panel_path],
            command=["python", "-m", "experiments.quantum.run_regimen_selection",
                     "--disease", args.disease],
            extra={"seed": args.seed, "pool": args.pool, "qiskit_available": HAS_QISKIT},
        ),
        "disease": args.disease,
        "pool": [d["name"] for d in pool],
        "n_eligible": len(eligible_drugs(disease.panel(), config)),
        "results": results,
        "scale_test": scale,
    }, indent=2, default=str) + "\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
