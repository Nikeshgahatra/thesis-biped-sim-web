#!/usr/bin/env python3
"""Local full-stack mode: static website + REST API on top of the SQLite database.

    python backend/build_db.py     (once, creates db/results.db)
    python backend/server.py       then open http://localhost:8000

GitHub Pages can only host static files, so online the site reads the JSON files in api/
(exported from the same database). This server answers the same URLs live from SQLite.
Endpoints:  /api/runs.json  /api/params.json  /api/standing.json  /api/foot_width.json  /api/timeseries.json
            /api/query?table=runs&gait=tuned&environment=Moon
"""
import json, os, sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "db", "results.db")
TABLES = {"runs": "gait DESC, controller, environment", "params": "controller, name", "standing": "gravity DESC",
          "foot_width": "foot_width_cm, environment", "timeseries": "gait, controller, environment, time_s"}
def rows(sql, args=()):
    con = sqlite3.connect(DB); cur = con.execute(sql, args); cols = [d[0] for d in cur.description]
    out = [dict(zip(cols, r)) for r in cur.fetchall()]; con.close(); return out
class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def send_json(self, obj):
        b = json.dumps(obj).encode(); self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/query":
            q = parse_qs(u.query); t = q.get("table", ["runs"])[0]
            if t not in TABLES: return self.send_json({"error": "unknown table"})
            cols = [r["name"] for r in rows(f"PRAGMA table_info({t})")]
            where = [(c, q[c][0]) for c in cols if c in q]
            sql = f"SELECT * FROM {t}" + (" WHERE " + " AND ".join(f"{c}=?" for c, _ in where) if where else "") + f" ORDER BY {TABLES[t]} LIMIT 2000"
            return self.send_json(rows(sql, [v for _, v in where]))
        name = u.path.rsplit("/", 1)[-1]
        if u.path.startswith("/api/") and name.endswith(".json") and name[:-5] in TABLES and name != "timeseries.json":
            return self.send_json(rows(f"SELECT * FROM {name[:-5]} ORDER BY {TABLES[name[:-5]]}"))
        return super().do_GET()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000")); print(f"http://localhost:{port}")
    ThreadingHTTPServer(("", port), H).serve_forever()
