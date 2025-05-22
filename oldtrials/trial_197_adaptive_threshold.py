
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Recruiter configuration
recruiter_centers_phase1 = [12, 14, 16]
recruiter_centers_phase2 = [12, 14]
period = 40
amplitude = 0.1
phase_offset = 0.0

# Identity parameters
ticks = 150
identity_phase = 0.0
support_threshold_phase1 = 3
support_threshold_phase2 = 2
phase_tolerance = 0.05
position = 10.0

prelock_duration = 30
locks = []

for t in range(ticks):
    if t < prelock_duration:
        recruiters = recruiter_centers_phase1
        threshold = support_threshold_phase1
    else:
        recruiters = recruiter_centers_phase2
        threshold = support_threshold_phase2

    support = 0
    for center in recruiters:
        recruiter_phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / period + phase_offset)) % 1.0
        phase_diff = abs((recruiter_phase - identity_phase + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1

    if support >= threshold:
        locks.append(t)
    position += 0.032

# Write summary
results = {
    "recruiter_centers_phase1": recruiter_centers_phase1,
    "recruiter_centers_phase2": recruiter_centers_phase2,
    "prelock_duration": prelock_duration,
    "threshold_phase1": support_threshold_phase1,
    "threshold_phase2": support_threshold_phase2,
    "locked_ticks": locks,
    "total_locks": len(locks),
    "final_position": position
}

with open("../results/trial_197_adaptive_threshold_summary.json", "w") as f:
    json.dump(results, f, indent=2)
