"""
simulate.py - run the gravity-adaptive biped simulation (pure software, no website needed).

Examples (PowerShell / terminal, inside this folder):
    python simulate.py                                  # asks you questions (easiest)
    python simulate.py --gravity Moon --controller Adaptive --gui
    python simulate.py --gravity 2.5 --controller both --gait tuned
    python simulate.py --gravity Mars --gait first      # the hand-chosen gait that fell

Each run saves a CSV and a graph into the results/ folder and prints a summary.
Physics, fall rule (height < 0.35 m or |roll|,|pitch| > 45 deg) and motor limit (2.0 N*m)
are the ones used in the thesis; they are NOT changed by any option below.
"""
import argparse, csv, json, os, sys

import gait_core as gc

HERE = os.path.dirname(os.path.abspath(__file__))
HEADER = ["time_s", "x_m", "y_m", "height_m", "roll_deg", "pitch_deg",
          "left_contact", "right_contact", "fall_flag"]


def load_params(gait, controller):
    """gait='first' -> hand-chosen first gait; gait='tuned' -> tuned for that controller."""
    if gait == "first":
        return dict(gc.V1_PARAMS)
    prm = dict(gc.V2_PARAMS)
    name = "tuned_fixed.json" if controller == "Fixed" else "tuned_adaptive.json"
    with open(os.path.join(HERE, "params", name)) as f:
        prm.update(json.load(f))
    return prm


def parse_gravity(text):
    key = text.strip().capitalize()
    if key in gc.GRAVITIES:
        return key, gc.GRAVITIES[key]
    try:
        g = float(text)
    except ValueError:
        sys.exit("Gravity must be Earth, Moon, Mars or a number in m/s^2 (got %r)." % text)
    if not 0.1 <= g <= 30:
        sys.exit("Gravity should be between 0.1 and 30 m/s^2.")
    return "g=%.2f" % g, g


def ask(prompt, options, default):
    while True:
        a = input("%s %s [%s]: " % (prompt, "/".join(options), default)).strip() or default
        if a.lower() in [o.lower() for o in options]:
            return [o for o in options if o.lower() == a.lower()][0]
        print("  please type one of:", ", ".join(options))


def interactive():
    print("\n=== Gravity-adaptive biped simulation ===\n")
    gtxt = input("Gravity - Earth, Moon, Mars or a number in m/s^2 [Moon]: ").strip() or "Moon"
    ctrl = ask("Controller", ["Fixed", "Adaptive", "both"], "both")
    gait = ask("Gait", ["first", "tuned"], "tuned")
    gui = ask("Open the 3-D viewer (needs a display)", ["yes", "no"], "no") == "yes"
    ns = argparse.Namespace(gravity=gtxt, controller=ctrl, gait=gait, duration=gc.DURATION,
                            gui=gui, out="results", no_plots=False)
    return ns


def save_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(HEADER); w.writerows(rows)


def plot(results, env, gait, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    for ctrl, r in results.items():
        t = [row[0] for row in r["rows"]]
        lab = "%s (%.3f Hz)" % (ctrl, r["freq"])
        ax[0].plot(t, [row[5] for row in r["rows"]], label=lab)
        ax[1].plot(t, [row[3] for row in r["rows"]], label=lab)
        ax[2].plot(t, [row[1] for row in r["rows"]], label=lab)
    ax[0].set_ylabel("pitch (deg)"); ax[1].set_ylabel("body height (m)"); ax[2].set_ylabel("forward x (m)")
    ax[1].axhline(gc.FALL_HEIGHT, color="r", ls="--", lw=1, label="fall height")
    ax[2].set_xlabel("time (s)")
    for a in ax: a.grid(alpha=.3)
    ax[0].legend(); ax[1].legend()
    ax[0].set_title("%s gravity, %s gait" % (env, gait))
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gravity", default="Moon", help="Earth, Moon, Mars or a number (m/s^2)")
    ap.add_argument("--controller", choices=["Fixed", "Adaptive", "both"], default="both")
    ap.add_argument("--gait", choices=["first", "tuned"], default="tuned")
    ap.add_argument("--duration", type=float, default=gc.DURATION, help="seconds (thesis: 12)")
    ap.add_argument("--gui", action="store_true", help="open the 3-D viewer (one controller at a time)")
    ap.add_argument("--out", default="results")
    ap.add_argument("--no-plots", action="store_true")
    a = ap.parse_args(argv) if (argv is not None or len(sys.argv) > 1) else interactive()

    env, g = parse_gravity(a.gravity)
    ctrls = ["Fixed", "Adaptive"] if a.controller == "both" else [a.controller]
    out = a.out if os.path.isabs(a.out) else os.path.join(HERE, a.out)
    os.makedirs(out, exist_ok=True)

    results = {}
    print("\nGravity %s = %.5f m/s^2 | gait: %s | duration %.1f s\n" % (env, g, a.gait, a.duration))
    for c in ctrls:
        r = gc.run_trial(load_params(a.gait, c), c, g, duration=a.duration, record=True, gui=a.gui)
        results[c] = r
        save_csv(os.path.join(out, "run_%s_%s_%s.csv" % (c, env.replace("=", ""), a.gait)), r["rows"])
    print("%-9s %-9s %-9s %-11s %-10s %-10s" % ("controller", "freq(Hz)", "result", "time(s)", "x(m)", "max pitch"))
    for c, r in results.items():
        print("%-9s %-9.3f %-9s %-11.2f %-+10.3f %-10.1f" % (
            c, r["freq"], "FELL" if r["fell"] else "upright", r["survived"], r["x_disp"], r["max_pitch"]))
    if not a.no_plots:
        png = os.path.join(out, "plot_%s_%s.png" % (env.replace("=", ""), a.gait))
        plot(results, env, a.gait, png)
        print("\nGraph saved:", png)
    print("CSV files saved in:", out)


if __name__ == "__main__":
    main()
