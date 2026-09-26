"""Summarise the regimen-selection runs across every disease that has results.

Usage: python -m experiments.quantum.summarize
"""

from __future__ import annotations

import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"
ORDER = ["multiple_sclerosis", "parkinsons", "alzheimers", "epilepsy", "guillain_barre"]
SOLVERS = ["enumeration", "greedy", "annealing", "random", "random_matched",
           "qaoa_constrained", "qaoa_constrained_cvar", "eigensolver", "qaoa"]
LABEL = {"enumeration": "enumeration", "greedy": "greedy", "annealing": "annealing",
         "random": "random (100)", "random_matched": "random (4096, matched shots)",
         "qaoa_constrained": "QAOA, constrained (XY mixer)",
         "qaoa_constrained_cvar": "QAOA, constrained + CVaR", "eigensolver": "exact eigensolver",
         "qaoa": "QAOA, penalty (Qiskit)"}


def load() -> dict[str, dict]:
    out = {}
    for name in ORDER:
        path = RESULTS / f"{name}_regimen_selection.json"
        if path.exists():
            out[name] = json.loads(path.read_text())
    return out


def main() -> None:
    data = load()
    if not data:
        print("no results yet")
        return
    print("Surrogate fidelity (Spearman between the pairwise surrogate and the true k-ary score)\n")
    print("| disease | pool / eligible | k | feasible subsets | Spearman | surrogate optimum's true rank |")
    print("|---|---|---|---|---|---|")
    for name, payload in data.items():
        for entry in payload["results"]:
            f = entry["surrogate_fidelity"]
            print(f"| {name} | {len(payload['pool'])} / {payload['n_eligible']} | {entry['k']} | "
                  f"{entry['hamiltonian']['feasible_states']:,} | {f['spearman']:.2f} | "
                  f"{f['surrogate_optimum_true_rank']} |")
    print("\nTrue rank of each solver's regimen among all feasible subsets (1 = the true optimum)\n")
    header = "| disease | k | " + " | ".join(LABEL[s] for s in SOLVERS) + " |"
    print(header)
    print("|" + "---|" * (len(SOLVERS) + 2))
    for name, payload in data.items():
        for entry in payload["results"]:
            cells = []
            by = {r["backend"]: r for r in entry["solvers"]}
            for s in SOLVERS:
                r = by.get(s)
                cells.append("—" if not r or "true_rank_of_all" not in r else str(r["true_rank_of_all"]))
            print(f"| {name} | {entry['k']} | " + " | ".join(cells) + " |")
    print("\nConstrained QAOA: how the final state is distributed (uniform = 1% in the top 1%)\n")
    print("| disease | k | top-1% probability | enrichment | P(surrogate optimum) | uniform P | best depth |")
    print("|---|---|---|---|---|---|---|")
    for name, payload in data.items():
        for entry in payload["results"]:
            for backend in ("qaoa_constrained", "qaoa_constrained_cvar"):
                run = next((r for r in entry["solvers"] if r["backend"] == backend), None)
                if not run or not run.get("enrichment"):
                    continue
                e = run["enrichment"]
                sweep = run["detail"]["depth_sweep"]
                depth = max(sweep, key=lambda a: a["p_top_1_percent"])["reps"]
                tag = "CVaR" if backend.endswith("cvar") else "mean"
                print(f"| {name} | {entry['k']} ({tag}) | {e['p_top_1_percent_best_depth']:.3f} | "
                      f"{e['top_1_percent_enrichment']}x | {e['p_optimum_best']:.1e} | "
                      f"{e['uniform_p_optimum']:.1e} | {depth} |")
    print("\nFull-panel annealing, beyond simulator size (no ground truth)\n")
    print("| disease | agents | k | subsets | annealed true score | best of 3000 random | median random |")
    print("|---|---|---|---|---|---|---|")
    for name, payload in data.items():
        for s in payload.get("scale_test", []):
            print(f"| {name} | {s['n_agents']} | {s['k']} | {s['feasible_subsets']:,} | "
                  f"{s['annealed_true_score']:.3f} | {s['random_best_true_score']:.3f} | "
                  f"{s['random_median_true_score']:.3f} |")


if __name__ == "__main__":
    main()
