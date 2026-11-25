"""
gait_core.py  -  shared simulation core (v2)

One place for: loading the URDF, the gait controller, the fall test and the
trial runner.  Every v2 script (experiment, tuner) imports this, so the
controller can never differ between scripts again (in v1 the same
constants were copy-pasted into 5 different files).

Fall criteria are IDENTICAL to v1 and are NOT relaxed:
    base height < 0.35 m   or   |roll| > 45 deg   or   |pitch| > 45 deg
"""
import os
import math
import time

import pybullet as p
import pybullet_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROBOT_FILE = os.path.join(BASE_DIR, "biped.urdf")

EARTH_GRAVITY = 9.80665
GRAVITIES = {"Earth": 9.80665, "Moon": 1.62, "Mars": 3.73}

TIME_STEP = 1.0 / 240.0
DURATION = 12.0

# --- fall thresholds (same as v1, do not edit to "win") -------------------
FALL_HEIGHT = 0.35
FALL_ANGLE_DEG = 45.0

# --- hard physical limit: never exceed the v1 motor force ------------------
MAX_MOTOR_FORCE = 2.0

JOINTS = ["left_hip", "left_knee", "left_ankle",
          "right_hip", "right_knee", "right_ankle"]

# v1 parameters (reference baseline, reproduces the thesis numbers)
V1_PARAMS = dict(
    freq=0.25, hip_amp=0.08, knee_amp=0.12, ankle_amp=0.04,
    startup=2.0,
    ankle_kp=-0.15, ankle_kd=-0.03,      # v1 used  -KP*pitch  (see README_v2)
    hip_kp=0.0, hip_kd=0.0,
    ankle_bias=0.0, hip_bias=0.0,
    max_corr=0.12,
    force=2.0, pos_gain=0.3, vel_gain=1.0,
    init_height=0.58,
)

# v2 defaults: the ONE structural fix = sign of the pitch feedback.
# (tune_gait.py searches around / beyond these values on your machine)
V2_PARAMS = dict(V1_PARAMS)
V2_PARAMS.update(
    ankle_kp=0.15, ankle_kd=0.03,
    init_height=0.552,          # feet nearly touching: no 3 cm drop transient
)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def gait_frequency(controller, gravity, base_freq):
    if controller == "Fixed":
        return base_freq
    return base_freq * math.sqrt(gravity / EARTH_GRAVITY)   # f(g)=f0*sqrt(g/g0)


def targets_at(t, freq, prm, pitch, pitch_rate):
    ramp = clamp(t / prm["startup"], 0.0, 1.0)
    ramp = ramp * ramp * (3.0 - 2.0 * ramp)
    ph = 2.0 * math.pi * freq * t
    lw = math.sin(ph)
    rw = -lw

    a_corr = clamp(prm["ankle_kp"] * pitch + prm["ankle_kd"] * pitch_rate,
                   -prm["max_corr"], prm["max_corr"])
    h_corr = clamp(prm["hip_kp"] * pitch + prm["hip_kd"] * pitch_rate,
                   -prm["max_corr"], prm["max_corr"])
    # biases fade in with the ramp so they do not shock the robot at t=0
    ab = ramp * prm["ankle_bias"]
    hb = ramp * prm["hip_bias"]

    return {
        "left_hip":    ramp * prm["hip_amp"] * lw + hb + h_corr,
        "right_hip":   ramp * prm["hip_amp"] * rw + hb + h_corr,
        "left_knee":   ramp * prm["knee_amp"] * max(0.0, lw),
        "right_knee":  ramp * prm["knee_amp"] * max(0.0, rw),
        "left_ankle":  -ramp * prm["ankle_amp"] * lw + ab + a_corr,
        "right_ankle": -ramp * prm["ankle_amp"] * rw + ab + a_corr,
    }


def run_trial(prm, controller, gravity, duration=DURATION,
              record=False, gui=False):
    """Run one simulation.  Returns a dict of metrics (+ 'rows' if record)."""
    client = p.connect(p.GUI if gui else p.DIRECT)
    if client < 0:
        raise RuntimeError("Could not connect to PyBullet.")
    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath(),
                                  physicsClientId=client)
        p.setGravity(0, 0, -gravity, physicsClientId=client)
        p.setTimeStep(TIME_STEP, physicsClientId=client)
        p.setPhysicsEngineParameter(numSolverIterations=100,
                                    physicsClientId=client)
        plane = p.loadURDF("plane.urdf", physicsClientId=client)
        robot = p.loadURDF(ROBOT_FILE, basePosition=[0, 0, prm["init_height"]],
                           useFixedBase=False, physicsClientId=client)

        jid, lim, lnk = {}, {}, {}
        for i in range(p.getNumJoints(robot, physicsClientId=client)):
            info = p.getJointInfo(robot, i, physicsClientId=client)
            jid[info[1].decode()] = i
            lnk[info[12].decode()] = i
            lim[info[1].decode()] = (info[8], info[9])
        for n in JOINTS:
            if n not in jid:
                raise ValueError("Missing joint: " + n)
        lfoot, rfoot = lnk["left_foot"], lnk["right_foot"]   # no hard-coded 5/11

        freq = gait_frequency(controller, gravity, prm["freq"])
        force = min(prm["force"], MAX_MOTOR_FORCE)

        rows, fall_t, fell = [], None, False
        max_pitch = max_roll = 0.0
        x0 = 0.0
        steps = int(duration / TIME_STEP)

        for k in range(steps):
            t = k * TIME_STEP
            pos, orn = p.getBasePositionAndOrientation(
                robot, physicsClientId=client)
            roll, pitch, _ = p.getEulerFromQuaternion(orn)
            _, ang = p.getBaseVelocity(robot, physicsClientId=client)
            pitch_rate = ang[1]

            tg = targets_at(t, freq, prm, pitch, pitch_rate)
            for n in JOINTS:
                lo, hi = lim[n]
                p.setJointMotorControl2(
                    robot, jid[n], p.POSITION_CONTROL,
                    targetPosition=clamp(tg[n], lo, hi), force=force,
                    positionGain=prm["pos_gain"], velocityGain=prm["vel_gain"],
                    physicsClientId=client)
            p.stepSimulation(physicsClientId=client)
            if gui:
                time.sleep(TIME_STEP)   # real-time viewing only; physics unchanged

            pos, orn = p.getBasePositionAndOrientation(
                robot, physicsClientId=client)
            roll, pitch, _ = p.getEulerFromQuaternion(orn)
            rd, pd = math.degrees(roll), math.degrees(pitch)
            max_pitch = max(max_pitch, abs(pd))
            max_roll = max(max_roll, abs(rd))

            fell = (pos[2] < FALL_HEIGHT or abs(rd) > FALL_ANGLE_DEG
                    or abs(pd) > FALL_ANGLE_DEG)

            if record and k % 24 == 0 or (record and fell):
                lc = len(p.getContactPoints(robot, plane, lfoot, -1,
                                            physicsClientId=client)) > 0
                rc = len(p.getContactPoints(robot, plane, rfoot, -1,
                                            physicsClientId=client)) > 0
                rows.append([round((k + 1) * TIME_STEP, 4), pos[0], pos[1],
                             pos[2], rd, pd, int(lc), int(rc), int(fell)])
            if fell:
                fall_t = (k + 1) * TIME_STEP
                break

        out = dict(controller=controller, gravity=gravity, freq=freq,
                   fell=bool(fell), fall_time=fall_t,
                   survived=fall_t if fell else duration,
                   x_disp=pos[0] - x0, y_dev=pos[1],
                   max_pitch=max_pitch, max_roll=max_roll,
                   final_height=pos[2])
        if record:
            out["rows"] = rows
        return out
    finally:
        p.disconnect(physicsClientId=client)
