#!/usr/bin/env python3
"""Backend build step: CSV/JSON results  ->  SQLite database  ->  static JSON API files.

Run from the repository root:   python backend/build_db.py
Creates  db/results.db  (SQLite)  and  api/*.json  (what the website reads).
Only the Python standard library is needed.
"""
import csv, json, os, sqlite3
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, API, DB = (os.path.join(ROOT, p) for p in ("data", "api", "db/results.db"))
os.makedirs(API, exist_ok=True); os.makedirs(os.path.dirname(DB), exist_ok=True)
if os.path.exists(DB): os.remove(DB)
con = sqlite3.connect(DB); cur = con.cursor()
cur.executescript("""
CREATE TABLE runs(gait TEXT, controller TEXT, environment TEXT, gravity REAL, frequency_hz REAL,
  fell INTEGER, fall_time_s REAL, observed_s REAL, x_displacement_m REAL, max_pitch_deg REAL, max_roll_deg REAL);
CREATE TABLE timeseries(gait TEXT, controller TEXT, environment TEXT, time_s REAL, x_m REAL, height_m REAL,
  pitch_deg REAL, roll_deg REAL, fall_flag INTEGER);
CREATE TABLE params(controller TEXT, name TEXT, value REAL);
CREATE TABLE standing(environment TEXT, gravity REAL, both_contact_pct REAL, max_roll_deg REAL, max_pitch_deg REAL);
CREATE TABLE foot_width(foot_width_cm REAL, environment TEXT, both_contact_pct REAL, max_roll_deg REAL);
CREATE INDEX ix_runs ON runs(gait, controller, environment);
CREATE INDEX ix_ts ON timeseries(gait, controller, environment);
""")
f = lambda v: None if v in ("", None) else float(v)
for r in csv.DictReader(open(f"{DATA}/initial_summary.csv")):
    cur.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)", ("first", r["controller"], r["environment"], f(r["gravity_m_s2"]), f(r["frequency_hz"]),
        1 - int(r["survived_12s"]), f(r["fall_time_s"]), f(r["observation_time_s"]), f(r["x_displacement_before_fall_m"]), f(r["max_pitch_before_fall_deg"]), f(r["max_roll_before_fall_deg"])))
for r in csv.DictReader(open(f"{DATA}/tuned_summary.csv")):
    cur.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)", ("tuned", r["controller"], r["environment"], f(r["gravity_m_s2"]), f(r["frequency_hz"]),
        int(r["fall_detected"]), f(r["fall_time_s"]), f(r["survived_s"]), f(r["x_displacement_m"]), f(r["max_abs_pitch_deg"]), f(r["max_abs_roll_deg"])))
for gait, fn in (("first", "initial_timeseries.csv"), ("tuned", "tuned_timeseries.csv")):
    for r in csv.DictReader(open(f"{DATA}/{fn}")):
        cur.execute("INSERT INTO timeseries VALUES(?,?,?,?,?,?,?,?,?)", (gait, r["controller"], r["environment"], f(r["time_s"]), f(r["x_m"]), f(r["height_m"]), f(r["pitch_deg"]), f(r["roll_deg"]), int(r["fall_threshold_active"])))
V1 = dict(freq=0.25, hip_amp=0.08, knee_amp=0.12, ankle_amp=0.04, startup=2.0, ankle_kp=-0.15, ankle_kd=-0.03, hip_kp=0.0, hip_kd=0.0, ankle_bias=0.0, hip_bias=0.0, max_corr=0.12)
sets = {"first (both)": V1, "tuned Fixed": json.load(open(f"{DATA}/tuned_params_fixed.json")), "tuned Adaptive": json.load(open(f"{DATA}/tuned_params_adaptive.json"))}
for name, p in sets.items():
    for k in ("freq","hip_amp","knee_amp","ankle_amp","startup","ankle_kp","ankle_kd","hip_kp","hip_kd","ankle_bias","hip_bias","max_corr"):
        cur.execute("INSERT INTO params VALUES(?,?,?)", (name, k, p[k]))
for r in csv.DictReader(open(f"{DATA}/standing.csv")):
    cur.execute("INSERT INTO standing VALUES(?,?,?,?,?)", (r["environment"], f(r["gravity_m_s2"]), f(r["both_contact_percent"]), f(r["max_roll_deg"]), f(r["max_pitch_deg"])))
for r in csv.DictReader(open(f"{DATA}/foot_width.csv")):
    cur.execute("INSERT INTO foot_width VALUES(?,?,?,?)", (round(float(r["foot_width_m"]) * 100), r["environment"], f(r["both_contact_percent"]), f(r["max_roll_deg"])))
con.commit()

def q(sql, args=()):
    c = con.execute(sql, args); cols = [d[0] for d in c.description]; return [dict(zip(cols, r)) for r in c.fetchall()]
json.dump(q("SELECT * FROM runs ORDER BY gait DESC, controller, environment"), open(f"{API}/runs.json", "w"))
json.dump(q("SELECT * FROM standing"), open(f"{API}/standing.json", "w"))
json.dump(q("SELECT * FROM foot_width ORDER BY foot_width_cm, environment"), open(f"{API}/foot_width.json", "w"))
json.dump(q("SELECT * FROM params"), open(f"{API}/params.json", "w"))
ts = {}
for r in con.execute("SELECT gait,controller,environment,time_s,x_m,height_m,pitch_deg,roll_deg,fall_flag FROM timeseries ORDER BY gait,controller,environment,time_s"):
    ts.setdefault("|".join(r[:3]), []).append([round(v, 5) for v in r[3:8]] + [r[8]])
json.dump(ts, open(f"{API}/timeseries.json", "w"), separators=(",", ":"))
print("database written:", DB, "| tables:", [r[0] for r in con.execute("select name from sqlite_master where type='table'")])
con.close()
