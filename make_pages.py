#!/usr/bin/env python3
"""Builds the HTML pages (shared header and footer) into the repository root."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = [("index", "Home"), ("simulator", "Simulator"), ("results", "Results"), ("method", "Method"), ("hardware", "Hardware"), ("database", "Database"), ("about", "About")]
TITLE = "Gravity-Adaptive Gait Control for a Biped Robot"
def page(slug, title, body, scripts=(), hero=""):
    nav = "".join('<a class="l%s" href="%s.html">%s</a>' % (" on" if s == slug else "", s, n) for s, n in PAGES)
    sc = "".join('<script src="assets/%s"></script>' % s for s in scripts)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · {TITLE}</title>
<meta name="description" content="Parametric PyBullet study of fixed and gravity-adaptive gait control for a six-joint biped on Earth, the Moon and Mars. Bachelor thesis by Nikesh Gahatraj.">
<link rel="stylesheet" href="assets/style.css"></head><body>
<nav class="top"><div class="wrap"><a class="brand" href="index.html">🚀 Biped · Earth · Moon · Mars</a>{nav}</div></nav>
{hero}<main class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">Nikesh Gahatraj · ID 2317390 · Smart Computing, Kyungdong University Global · Supervisor: Dr. Nyrod Villa<br>Data: PyBullet simulation, one run per condition. Nothing on this site was measured on the physical robot.</div></footer>
{sc}</body></html>'''
def write(slug, *a, **k):
    open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf8").write(page(slug, *a, **k))

# ---------------------------------------------------------------- Home
hero = '''<header class="hero"><div class="planets"><div class="pl e"></div><div class="pl m"></div><div class="pl r"></div></div><div class="wrap">
<p class="eyebrow">Bachelor thesis · Smart Computing · Kyungdong University Global</p>
<h1>Can a walking robot adapt its gait to the gravity of another world?</h1>
<p class="lead">A six-joint biped controlled by an Arduino-style gait controller was simulated under Earth, lunar and Martian gravity. Watch the runs, read the results and explore the data.</p>
<div class="btns"><a class="btn" href="simulator.html">Open the simulator</a><a class="btn ghost" href="results.html">See the results</a></div></div></header>'''
body = '''
<section class="card"><div class="grid">
<div class="stat"><b>12</b><span>simulated runs: 3 gravities × 2 controllers × 2 gaits</span></div>
<div class="stat"><b class="fall">6 of 6</b><span>first-gait runs fell within 1.7 to 3.2 s</span></div>
<div class="stat"><b class="up">6 of 6</b><span>tuned runs stayed upright for the full 12 s</span></div>
<div class="stat"><b>13</b><span>parameters searched for each controller</span></div></div></section>
<section class="card"><h2>Explore the project</h2><div class="grid">
<a class="tile" href="simulator.html"><b>Simulator</b><span>Animated replay of all 12 runs with graph and run table.</span></a>
<a class="tile" href="results.html"><b>Results</b><span>Charts and tables: first gait, tuned gait, standing, foot width.</span></a>
<a class="tile" href="method.html"><b>Method</b><span>Robot model, controllers, equations, tuning and experiments.</span></a>
<a class="tile" href="hardware.html"><b>Hardware</b><span>The Arduino Mega prototype and how it relates to the simulation.</span></a>
<a class="tile" href="database.html"><b>Database</b><span>Browse the SQLite data, filter, sort and download CSV.</span></a>
<a class="tile" href="about.html"><b>About</b><span>The thesis, the author, limits and how to run the code.</span></a></div></section>
<section class="card two"><div><h2>The question</h2><p>Moon gravity is about 1.62 m/s² and Mars gravity about 3.73 m/s², against 9.81 m/s² on Earth. A gait tuned on Earth may not suit those worlds. This project tests a simple idea: slow the walking rhythm down with gravity, using f = f<sub>0</sub>·√(g / 9.81), and compare it with a gait that keeps the same frequency everywhere.</p></div>
<div><h2>The short answer</h2><p>The gravity-scaled frequency delayed the first gait's fall by 13.3% on the Moon and 11.4% on Mars, but did not stop it. A parameter search then made both controllers walk for 12 s without falling. The search mattered far more than the frequency law, and neither controller was best in every respect.</p></div></section>'''
write("index", "Home", body, hero=hero)

# ---------------------------------------------------------------- Simulator
body = '''<section class="card"><h2>Simulation replay</h2>
<div class="controls">
<label>Gravity<select id="env"><option>Earth</option><option selected>Moon</option><option>Mars</option></select></label>
<label>Controller<select id="ctl"><option value="Fixed">Fixed frequency</option><option value="Adaptive" selected>Gravity-adaptive</option></select></label>
<label>Gait<select id="gait"><option value="tuned" selected>Tuned gait</option><option value="first">First gait (falls)</option></select></label>
<label>Speed<select id="spd"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="4">4×</option></select></label></div>
<div class="stage"><canvas id="cv" width="960" height="420" aria-label="Side view of the simulated biped"></canvas>
<div class="hud"><div><span>Gravity</span><b id="hg">–</b></div><div><span>Gait frequency</span><b id="hf">–</b></div><div><span>Time</span><b id="ht">–</b></div><div><span>Distance</span><b id="hx">–</b></div><div><span>Pitch</span><b id="hp">–</b></div></div>
<div id="badge" class="badge" hidden></div></div>
<div class="bar"><button class="btn" id="play" type="button">Pause</button><input id="seek" type="range" min="0" max="1000" value="0" aria-label="Time"></div>
<canvas id="chart" width="960" height="190" aria-label="Pitch, roll and distance over time"></canvas>
<p class="note">Body position, height and tilt are the values logged by PyBullet at 0.1 s steps. The leg angles are rebuilt from the gait equations (see Method) and drawn as a flat side view, so the picture is a schematic and not a render of the physics engine. Both legs are drawn, the far leg lighter.</p></section>
<section class="card"><h2>Result of this run</h2><div id="sum" class="sum"></div>
<h3>All 12 runs (click a row to replay it)</h3><div class="tablewrap"><table id="tbl" class="click"></table></div></section>'''
write("simulator", "Simulator", body, scripts=["sim.js"])

# ---------------------------------------------------------------- Results
body = '''<section class="card"><h1 style="margin:0 0 8px;font-size:30px">Results</h1><p>All numbers come from the SQLite database in this repository. Each condition was simulated once.</p></section>
<section class="card chartbox"><h2>1. First gait: fixed versus adaptive</h2>
<p>The hand-chosen gait fell in all six runs. The gravity-scaled frequency only delayed the fall.</p>
<canvas id="c1" width="960" height="300"></canvas><div class="legend"></div>
<div class="tablewrap"><table id="t1"></table></div>
<canvas id="c5" width="960" height="260" style="margin-top:14px"></canvas><div class="legend"></div>
<p class="note">The body moved backwards (negative distance) in every first-gait run, so a longer survival time was not a gain in walking.</p></section>
<section class="card chartbox"><h2>2. Tuned gait</h2>
<p>After a separate 13-parameter search for each controller, all six runs stayed upright for 12 s.</p>
<canvas id="c3" width="960" height="280"></canvas><div class="legend"></div>
<canvas id="c4" width="960" height="280" style="margin-top:14px"></canvas><div class="legend"></div>
<p class="note">The adaptive controller kept the body nearly upright (largest pitch 3.1° to 4.6°). The fixed controller leaned forward by about 5° to 7° and moved farther on Earth and the Moon. On Mars the adaptive controller advanced farther. There is no single winner.</p></section>
<section class="card chartbox"><h2>3. Before and after tuning</h2>
<canvas id="c2" width="960" height="300"></canvas><div class="legend"></div>
<p class="note">Tuning raised the survival time from 1.7 to 3.2 s to the full 12 s. That change is about ten times larger than the 11% to 13% gained from the frequency law.</p></section>
<section class="card"><h2>4. Standing tests</h2><p>Neutral-pose standing for 10 s in each environment, and three foot widths with no disturbance. Differences are tiny and without practical meaning.</p>
<div class="tablewrap"><table id="t2"></table></div><h3>Foot width (7, 9 and 11 cm)</h3><div class="tablewrap"><table id="t3"></table></div></section>
<section class="card"><h2>What the results do not show</h2><ul class="clean">
<li>One run per condition, so there is no estimate of spread.</li>
<li>The simulated motors can give 2.0 N·m, about twice what an MG996R servo can give at best.</li>
<li>The controller reads exact pitch values, while a real one would use a filtered sensor estimate.</li>
<li>Several tuned values lie near the edge of the search range, so better settings may exist.</li></ul></section>'''
write("results", "Results", body, scripts=["charts.js", "results.js"])

# ---------------------------------------------------------------- Method
body = '''<section class="card"><h1 style="margin:0 0 8px;font-size:30px">Method</h1><p>The study moves from the simplest test to the most demanding one, so that the model is understood before controllers are compared.</p></section>
<section class="card two"><div><h2>The simulated robot</h2><ul class="clean"><li>Six revolute joints: hip, knee and ankle on each leg, all bending in the pitch plane.</li><li>Total mass 2.10 kg; standing height about 0.55 m; thigh and shin 0.20 m each; foot 0.14 m.</li><li>PyBullet at 240 Hz, flat ground, position-controlled motors limited to 2.0 N·m.</li><li>Joint limits: hip ±0.6 rad, knee −0.1 to 1.2 rad, ankle ±0.5 rad.</li></ul></div>
<div><h2>Fall rule</h2><p>A run stops when the body height drops below 0.35 m, or when the roll or pitch angle passes 45°. Runs last at most 12 s.</p><p class="note">The link masses and widths are modelling assumptions. Only the foot length was taken from the physical prototype.</p></div></section>
<section class="card"><h2>The gait and the gravity law</h2>
<p>Each joint follows a sine wave with a smooth start-up. For the left leg (the right leg uses −sin):</p>
<div class="eq">hip&nbsp;&nbsp;&nbsp;= s(t)·A<sub>h</sub>·sin(2πft) + b<sub>h</sub> + c<sub>h</sub><br>knee&nbsp;&nbsp;= s(t)·A<sub>k</sub>·max(0, sin(2πft))<br>ankle = −s(t)·A<sub>a</sub>·sin(2πft) + b<sub>a</sub> + c<sub>a</sub></div>
<p>The feedback corrections come from the body pitch θ and pitch rate ω, limited to ±0.12 rad:</p>
<div class="eq">c = clip(k<sub>p</sub>·θ + k<sub>d</sub>·ω, −0.12, +0.12)</div>
<p>The fixed controller uses the same frequency everywhere. The adaptive controller scales it with gravity:</p>
<div class="eq">f(g) = f<sub>0</sub> · √(g / 9.80665)</div>
<p class="note">With f<sub>0</sub> = 0.25 Hz the first gait ran at 0.2500 Hz on Earth, 0.1016 Hz on the Moon and 0.1542 Hz on Mars.</p></section>
<section class="card"><h2>Experiments</h2><div class="tablewrap"><table>
<tr><th>#</th><th>Purpose</th><th>Conditions</th><th>Runs</th></tr>
<tr><td>1</td><td>Standing stability</td><td>Earth, Moon, Mars; neutral pose; 10 s</td><td>3</td></tr>
<tr><td>2</td><td>Foot width</td><td>7, 9, 11 cm × 3 gravities; no disturbance</td><td>9</td></tr>
<tr><td>3</td><td>Preliminary walking</td><td>Earth; up to 12 s</td><td>2</td></tr>
<tr><td>4</td><td>First gait, fixed vs adaptive</td><td>2 controllers × 3 gravities</td><td>6</td></tr>
<tr><td>5</td><td>Tuned gait, fixed vs adaptive</td><td>2 controllers × 3 gravities</td><td>6</td></tr></table></div></section>
<section class="card"><h2>Automatic tuning</h2><p>A random search over 13 parameters (frequency, three amplitudes, start-up time, ankle and hip feedback gains, two bias angles and the motor gains) was run separately and with equal effort for each controller. The fall rule and the 2.0 N·m limit were not changed. Search ranges: frequency 0.15 to 0.80 Hz; hip amplitude 0.03 to 0.16 rad; knee 0.05 to 0.30 rad; ankle 0.00 to 0.10 rad; start-up 0.5 to 4.0 s; feedback gains −0.6 to 0.6 (kp) and −0.15 to 0.15 (kd); biases ±0.25 rad.</p>
<h3>Parameters used (from the database)</h3><div class="tablewrap"><table id="tp"></table></div></section>'''
write("method", "Method", body, scripts=["method.js"])

# ---------------------------------------------------------------- Hardware
body = '''<section class="card"><h1 style="margin:0 0 8px;font-size:30px">Hardware prototype</h1>
<p>A small two-legged prototype was built around an Arduino Mega 2560. It sets the joint layout and the foot length used in the simulation, and it shows what the real servos can and cannot do. All gravity experiments were done in simulation, because gravity cannot be changed in a laboratory.</p></section>
<section class="card"><h2>Components</h2><div class="tablewrap"><table>
<tr><th>Part</th><th>Qty</th><th>Role</th></tr>
<tr><td>Arduino Mega 2560</td><td>1</td><td>Controller: generates the servo signals and reads the tilt sensor</td></tr>
<tr><td>MG996R metal-gear servo</td><td>6</td><td>Hip, knee and ankle of each leg</td></tr>
<tr><td>MPU6050 (accelerometer and gyroscope)</td><td>1</td><td>Body tilt, read over I²C</td></tr>
<tr><td>LiPo battery with regulator</td><td>1</td><td>Servo supply; the servos must not be fed from the Arduino 5 V pin</td></tr>
<tr><td>3D-printed frame, bearings</td><td>1 set</td><td>Torso, thighs, shins and feet</td></tr></table></div>
<img class="fig" src="assets/fig_hw.png" alt="Block diagram of the prototype electronics"><p class="note" style="text-align:center">Block diagram of the prototype electronics.</p></section>
<section class="card two"><div><h2>How it connects to the simulation</h2><ul class="clean"><li>Same six-joint layout: hip, knee and ankle per leg, all in the pitch plane.</li><li>Same foot length, 14 cm.</li><li>Gait amplitudes found in the simulation are small (about 3° to 12°) and the frequencies are below 1 Hz, which suits hobby servos.</li></ul></div>
<div><h2>Status and limits</h2><ul class="clean"><li>The joints move through a limited range, but the prototype does not walk on two legs.</li><li>All joints bend in one plane, so there is no active sideways balance.</li><li>An MG996R gives about 0.9 to 1.1 N·m at stall, while the simulated motor allows 2.0 N·m. On Earth a modest lever arm can already reach the stall torque.</li><li>No measurements were taken on the hardware, so none are reported.</li></ul></div></section>
<section class="card"><h2>Static torque estimate</h2><p>Weight of a 2.10 kg robot acting at an assumed lever arm of 5 cm. The lever arm is an illustration, not a measurement.</p>
<div class="tablewrap"><table><tr><th>Gravity</th><th>Weight (N)</th><th>Torque (N·m)</th><th>Compared with servo stall (about 1.0 N·m)</th></tr>
<tr><td>Earth</td><td>20.59</td><td>1.03</td><td>Equal to the stall torque</td></tr><tr><td>Mars</td><td>7.83</td><td>0.39</td><td>About 40%</td></tr><tr><td>Moon</td><td>3.40</td><td>0.17</td><td>About 17%</td></tr></table></div></section>'''
write("hardware", "Hardware", body)

# ---------------------------------------------------------------- Database
body = '''<section class="card"><h1 style="margin:0 0 8px;font-size:30px">Database</h1>
<p>Every number on this site comes from one SQLite database, <code>db/results.db</code>. A Python script (<code>backend/build_db.py</code>) loads the simulation CSV files into it and exports JSON files into <code>api/</code>. This page reads those files, so you can filter, sort and download the data.</p>
<p class="note">GitHub Pages hosts static files only, so there is no live server online. To run the real REST API on SQLite, use <code>python backend/server.py</code> on your computer (see About). The SQL shown below is the query equivalent to your filters.</p></section>
<section class="card"><h2>Explorer</h2>
<div class="controls"><label>Table<select id="tbl"><option value="runs">runs (12 summary rows)</option><option value="params">params</option><option value="standing">standing</option><option value="foot_width">foot_width</option><option value="timeseries">timeseries (time samples)</option></select></label>
<span id="filters" class="controls" style="margin:0"></span><label>Search<input id="q" type="text" placeholder="type to filter"></label>
<label>&nbsp;<button class="btn" id="csv" type="button">Download CSV</button></label></div>
<p class="note"><span id="count"></span> · click a column title to sort</p>
<div class="tablewrap" style="max-height:480px;overflow:auto"><table id="grid"></table></div>
<h3>Equivalent SQL</h3><pre id="sql"></pre><h3>Table definition</h3><pre id="schema"></pre></section>
<section class="card"><h2>Tables</h2><ul class="clean"><li><b>runs</b>: one row per run (gait, controller, environment, gravity, frequency, fall time, distance, largest pitch and roll).</li><li><b>timeseries</b>: body position, height, pitch and roll every 0.1 s of every run.</li><li><b>params</b>: the controller parameters of the first and the tuned gaits.</li><li><b>standing</b> and <b>foot_width</b>: the static stability tests.</li></ul>
<p><a class="btn ghost" href="db/results.db" download>Download results.db</a></p></section>'''
write("database", "Database", body, scripts=["explorer.js"])

# ---------------------------------------------------------------- About
body = '''<section class="card"><h1 style="margin:0 0 8px;font-size:30px">About</h1>
<p><b>Development of a Gravity-Adaptive Gait Control Algorithm for a Bipedal Robot Using Arduino Mega: A Parametric Simulation Approach for Earth, Lunar, and Martian Environments</b></p>
<p>Bachelor thesis by Nikesh Gahatraj (ID 2317390), Department of Smart Computing, Kyungdong University Global. Supervisor: Dr. Nyrod Villa.</p></section>
<section class="card two"><div><h2>Findings</h2><ul class="clean"><li>The model stood stably in all three gravities.</li><li>The hand-chosen gait fell in all six runs; scaling the frequency with gravity delayed the fall by 13.3% (Moon) and 11.4% (Mars).</li><li>After separate tuning, both controllers stayed upright for 12 s in all conditions.</li><li>Tuning mattered far more than the frequency law, and there was no single best controller.</li></ul></div>
<div><h2>Limitations</h2><ul class="clean"><li>Results come from simulation only; nothing was measured on the robot.</li><li>One run per condition.</li><li>Idealised motors and exact tilt readings.</li><li>All joints bend in one plane.</li></ul></div></section>
<section class="card"><h2>How the site is built</h2><div class="grid">
<div class="tile"><b>Front end</b><span>Plain HTML, CSS and JavaScript with canvas drawing. No framework.</span></div>
<div class="tile"><b>Data layer</b><span>SQLite database <code>db/results.db</code> exported to JSON in <code>api/</code>.</span></div>
<div class="tile"><b>Backend</b><span><code>backend/</code>: build script and a local REST server on the same database.</span></div>
<div class="tile"><b>Simulation</b><span>Python and PyBullet in <code>simulation/</code>.</span></div></div></section>
<section class="card"><h2>Run it yourself</h2>
<h3>The real physics simulation</h3><pre><code>cd simulation
pip install -r requirements.txt
python simulate.py --gravity Moon --controller Adaptive --gait tuned --gui</code></pre>
<h3>The website with its REST API on your computer</h3><pre><code>python backend/build_db.py
python backend/server.py      # then open http://localhost:8000</code></pre>
<p class="note">Online, the site only replays saved results. The physics engine does not run in the browser.</p></section>'''
write("about", "About", body)
print("pages written")
