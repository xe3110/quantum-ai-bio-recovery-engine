"""Does a QAOA circuit guide a classical search better than the classical surrogate ranking?

Each method proposes BUDGET regimens for the true k-ary scorer to evaluate (the expensive step); the
score is the best true rank among them. Run: PYTHONPATH=. qbio-quantum-env/bin/python -u -m experiments.quantum.run_hybrid_guided
Results: results/hybrid_circuit_guided.json; discussion: docs/quantum_regimen_selection.md section 10.
"""
import json, random, sys
import numpy as np
from experiments.quantum.ibm_prepare import build
from core.quantum.gate_qaoa import optimise
from core.quantum.regimen_selection import true_landscape, solve_annealing

DISEASES = ["multiple_sclerosis", "parkinsons", "alzheimers", "epilepsy", "guillain_barre"]
N, K, BUDGET = 12, 4, 20
rows = []
for d in DISEASES:
    try:
        prob = build(d, N, K)
    except Exception as e:
        print(d, "skip", e, flush=True); continue
    land = true_landscape(prob)
    idx = {m: i for i, m in enumerate(prob.identifiers)}
    truth = {tuple(sorted(idx[x] for x in s)): v["true"] for s, v in land.items()}
    sur = {tuple(sorted(idx[x] for x in s)): v["surrogate"] for s, v in land.items()}
    ranked = sorted(truth, key=lambda s: -truth[s]); trank = {s: i + 1 for i, s in enumerate(ranked)}
    def best_rank(cands):
        return min(trank[c] for c in cands)
    out = {"disease": d, "surrogate_opt_true_rank": trank[max(sur, key=sur.get)]}
    rng = random.Random(3)
    out["random"] = float(np.mean([best_rank(rng.sample(list(truth), BUDGET)) for _ in range(200)]))
    out["surrogate_top"] = best_rank(sorted(sur, key=lambda s: -sur[s])[:BUDGET])
    # annealing: distinct subsets it visits are not exposed, so take its best plus neighbours by surrogate
    a = solve_annealing(prob, seed=7)
    best = tuple(sorted(idx[x] for x in a.identifiers))
    near = sorted(sur, key=lambda s: (-len(set(s) & set(best)), -sur[s]))[:BUDGET]
    out["annealing_best_plus_neighbours"] = best_rank(near)
    for alpha in (0.02, 0.05, 0.1, 0.25):
        for layers in (8,):
            spec, sim = optimise(prob, layers=layers, seed=7, restarts=3, maxiter=300, start="dicke", cvar_alpha=alpha)
            pr = sim.probabilities(spec["gammas"], spec["betas"])
            order = np.argsort(-pr)[:BUDGET]
            key = f"circuit_cvar{alpha}_p{layers}"
            out[key] = best_rank([tuple(sim.states[i]) for i in order])
            tt = np.array([truth[tuple(s)] for s in sim.states])
            o = np.argsort(-tt); top = o[:max(1, len(tt)//100)]
            out[key + "_Ptop1pct"] = round(float(pr[top].sum()), 3)
            # shot-based: 4000 samples, unique subsets by frequency
            samp = np.random.default_rng(5).choice(len(pr), 4000, p=pr)
            vals, cnt = np.unique(samp, return_counts=True)
            uniq = [tuple(sim.states[i]) for i in vals[np.argsort(-cnt)][:BUDGET]]
            out[key + "_shots"] = best_rank(uniq)
    rows.append(out); print(json.dumps(out), flush=True)
json.dump(rows, open(str(__import__("pathlib").Path(__file__).resolve().parent / "results/hybrid_circuit_guided.json"), "w"), indent=1)
