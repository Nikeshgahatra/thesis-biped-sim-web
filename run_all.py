"""
run_all.py - reproduce the thesis experiment: 2 controllers x 3 gravities x 2 gaits (first, tuned) = 12 runs.
Writes results/summary_all_runs.csv and one comparison graph per gait. Takes a few minutes.

    python run_all.py
"""
import csv, os
import gait_core as gc
import simulate as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for gait in ("first", "tuned"):
        for ctrl in ("Fixed", "Adaptive"):
            for env, g in gc.GRAVITIES.items():
                r = gc.run_trial(sim.load_params(gait, ctrl), ctrl, g, record=True)
                sim.save_csv(os.path.join(OUT, "run_%s_%s_%s.csv" % (ctrl, env, gait)), r["rows"])
                rows.append([gait, ctrl, env, g, round(r["freq"], 4), int(r["fell"]),
                             "" if r["fall_time"] is None else round(r["fall_time"], 3),
                             round(r["survived"], 3), round(r["x_disp"], 4), round(r["max_pitch"], 2), round(r["max_roll"], 2)])
                print("%-6s %-8s %-5s fell=%-5s survived=%5.2fs x=%+.3f m" % (gait, ctrl, env, r["fell"], r["survived"], r["x_disp"]))
    with open(os.path.join(OUT, "summary_all_runs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gait", "controller", "environment", "gravity_m_s2", "frequency_hz", "fell",
                    "fall_time_s", "survived_s", "x_displacement_m", "max_abs_pitch_deg", "max_abs_roll_deg"])
        w.writerows(rows)
    print("\nSaved results/summary_all_runs.csv")
    print("Falls with the first gait: %d/6 | with the tuned gait: %d/6" % (
        sum(r[5] for r in rows if r[0] == "first"), sum(r[5] for r in rows if r[0] == "tuned")))


if __name__ == "__main__":
    main()
