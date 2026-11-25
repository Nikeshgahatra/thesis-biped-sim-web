# Gravity-Adaptive Biped - Software Simulation

A stand-alone PyBullet simulation of the six-joint biped robot from the thesis
*Development of a Gravity-Adaptive Gait Control Algorithm for a Bipedal Robot Using Arduino Mega*
(Nikesh Gahatraj, 2317390). It needs no website and no hardware.

## What is inside
| File | Purpose |
|---|---|
| `simulate.py` | Run one condition (any gravity, Fixed / Adaptive / both, first or tuned gait). Easiest entry point. |
| `run_all.py` | Reproduce all 12 thesis runs and write `results/summary_all_runs.csv`. |
| `gait_core.py` | Robot loading, gait generator, fall test, trial runner (shared by everything). |
| `biped.urdf` | Robot model (2.10 kg, 20 cm thigh and shin, 14 cm foot). |
| `params/` | The tuned parameter sets (Fixed and Adaptive). |
| `tune_gait.py` | Optional: repeat the random-search tuning (10-30 min). |
| `Run_in_Colab.ipynb` | Same thing in Google Colab, if PyBullet will not install on your PC. |

## Install and run (Windows PowerShell or any terminal, inside this folder)
    pip install -r requirements.txt
    python simulate.py                                       # answers a few questions, then runs
    python simulate.py --gravity Moon --controller both --gait tuned
    python simulate.py --gravity Mars --gait first           # the hand-chosen gait that fell
    python simulate.py --gravity 2.5 --controller Adaptive --gui   # any gravity; 3-D viewer
    python run_all.py                                        # the full experiment

Outputs go to `results/` (CSV time series and a graph with pitch, body height and forward distance).

## Rules that are never changed
Fall = body height < 0.35 m or |roll| or |pitch| > 45 degrees. Motor limit 2.0 N*m. 240 Hz step, 12 s run.
Adaptive frequency: f(g) = f0 * sqrt(g / 9.80665); the Fixed controller keeps f0.

## Notes
* "first" gait = the hand-chosen parameters (falls in every run); "tuned" = parameters found by random search,
  tuned separately for each controller.
* The viewer (`--gui`) runs in real time and only changes the speed of display, not the physics.
* Results come from a simulation of the model only; they do not show walking on the physical robot.
* Tested with Python 3.10+; if `pip install pybullet` fails on Windows, install the "Microsoft C++ Build Tools" or use Colab.
