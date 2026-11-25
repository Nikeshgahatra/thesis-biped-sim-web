"""
tune_gait.py  -  find controller parameters with ZERO falls (run on your PC)

    python tune_gait.py              # 300 random samples + refinement
    python tune_gait.py --samples 600 --workers 4
    python tune_gait.py --controller Fixed   # fair baseline: tune Fixed on its own

How it stays honest
  * uses the SAME fall rule as v1 (gait_core.py) - thresholds are never loosened
  * motor force is capped at the v1 value (2.0 N*m) - no extra torque
  * a candidate must survive the full 12 s on Earth, Moon AND Mars with the
    gravity-adaptive controller, AND on +-10 % gravity variants (so it is not
    a knife-edge result), AND must actually walk forward (>= --min-progress m)
    - otherwise "just stand still" would count as success
  * result is saved to best_params.json, used by adaptive_gait_experiment_v2.py
"""
import argparse, csv, json, os, random, time
from multiprocessing import Pool

import gait_core as gc

HERE = os.path.dirname(os.path.abspath(__file__))

# (low, high) search ranges - signed feedback gains on purpose, so the search
# also confirms the sign of the pitch feedback empirically.
SPACE = dict(
    freq=(0.15, 0.80),
    hip_amp=(0.03, 0.16),
    knee_amp=(0.05, 0.30),
    ankle_amp=(0.0, 0.10),
    startup=(0.5, 4.0),
    ankle_kp=(-0.6, 0.6),
    ankle_kd=(-0.15, 0.15),
    hip_kp=(-0.6, 0.6),
    hip_kd=(-0.15, 0.15),
    ankle_bias=(-0.25, 0.25),
    hip_bias=(-0.25, 0.25),
    pos_gain=(0.15, 0.6),
    vel_gain=(0.5, 1.5),
)


def sample(rng, around=None, scale=0.15):
    prm = dict(gc.V2_PARAMS)
    for k, (lo, hi) in SPACE.items():
        if around is None:
            prm[k] = rng.uniform(lo, hi)
        else:
            prm[k] = gc.clamp(rng.gauss(around[k], scale * (hi - lo)), lo, hi)
    return prm


def evaluate(args):
    prm, min_progress, robust, ctrl = args
    worlds = [("Earth", 9.80665), ("Moon", 1.62), ("Mars", 3.73)]
    if robust:
        worlds += [("Earth-10%", 9.80665 * .9), ("Earth+10%", 9.80665 * 1.1),
                   ("Moon+10%", 1.62 * 1.1), ("Mars-10%", 3.73 * .9)]
    cost, falls, details = 0.0, 0, []
    for name, g in worlds:
        r = gc.run_trial(prm, ctrl, g)
        details.append((name, r["fell"], r["survived"], r["x_disp"],
                        r["max_pitch"], r["max_roll"]))
        cost += (gc.DURATION - r["survived"]) * 10.0
        falls += int(r["fell"])
        if not r["fell"]:
            cost += 0.02 * (r["max_pitch"] + r["max_roll"])
            if r["x_disp"] < min_progress:           # must really walk
                cost += 20.0 * (min_progress - r["x_disp"]) + 5.0
    return cost, falls, prm, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=300)
    ap.add_argument("--refine", type=int, default=150)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--min-progress", type=float, default=0.10)
    ap.add_argument("--controller", choices=["Adaptive", "Fixed"], default="Adaptive")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    t0 = time.time()

    seeds = [dict(gc.V2_PARAMS)] + [sample(rng) for _ in range(a.samples - 1)]
    with Pool(a.workers) as pool:
        print(f"Stage 1: {len(seeds)} random candidates on {a.workers} workers ...")
        res = pool.map(evaluate, [(s, a.min_progress, False, a.controller) for s in seeds])
        res.sort(key=lambda r: r[0])
        print("  best cost %.2f  falls %d   (%.0fs)" % (res[0][0], res[0][1], time.time() - t0))

        best = res[0][2]
        print(f"Stage 2: refining around the best candidate ({a.refine}) ...")
        for rnd in range(3):
            cands = [sample(rng, best, 0.12 / (rnd + 1)) for _ in range(a.refine // 3)] + [best]
            r2 = pool.map(evaluate, [(c, a.min_progress, False, a.controller) for c in cands])
            r2.sort(key=lambda r: r[0])
            if r2[0][0] <= res[0][0]:
                res = r2 + res
                res.sort(key=lambda r: r[0])
            best = res[0][2]
            print("  round %d best cost %.2f falls %d" % (rnd + 1, res[0][0], res[0][1]))

        print("Stage 3: robustness check (+-10 %% gravity) on top 8 ...")
        top = [r[2] for r in res[:8]]
        rob = pool.map(evaluate, [(c, a.min_progress, True, a.controller) for c in top])
        rob.sort(key=lambda r: r[0])

    cost, falls, prm, det = rob[0]
    print("\nBEST  cost=%.2f  falls=%d (over %d worlds)" % (cost, falls, len(det)))
    for d in det:
        print("  %-10s fell=%-5s survived=%5.2fs  x=%+.3f m  max|pitch|=%4.1f  max|roll|=%4.1f" % d)

    suffix = "" if a.controller == "Adaptive" else "_fixed"
    with open(os.path.join(HERE, "best_params%s.json" % suffix), "w") as f:
        json.dump(prm, f, indent=2)
    with open(os.path.join(HERE, "tuning_top_candidates%s.csv" % suffix), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "cost", "falls"] + list(SPACE))
        for i, (c, fl, pr, _) in enumerate(rob):
            w.writerow([i + 1, round(c, 3), fl] + [round(pr[k], 4) for k in SPACE])
    print("\nSaved best_params.json  (zero falls)" if falls == 0 else
          "\nSaved best_params.json  (STILL has falls - see README_v2 'if not zero')")
    print("Next:  python adaptive_gait_experiment_v2.py")


if __name__ == "__main__":
    main()
