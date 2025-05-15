
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Recruiter configuration
recruiter_centers = [12, 14]
period = 40
amplitude = 0.1
phase_offset = 0.0

# Identity parameters
ticks = 150
identity_phase = 0.0
support_threshold = 3.0  # Still requires 3 recruiters, but only 2 will be available after phase 1
phase_tolerance = 0.05
position = 10.0

# Phase structure
prelock_duration = 30  # First 30 ticks use full 3-band rhythm
locks = []

for t in range(ticks):
    support = 0

    # Phase 1: include an extra virtual band at center 16
    if t < prelock_duration:
        centers = recruiter_centers + [16]
    else:
        centers = recruiter_centers  # Drop to 2 recruiters

    for center in centers:
        recruiter_phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / period + phase_offset)) % 1.0
        phase_diff = abs((recruiter_phase - identity_phase + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1

    if support >= support_threshold:
        locks.append(t)
    position += 0.032

# Write summary
results = {
    "recruiter_centers_phase1": recruiter_centers + [16],
    "recruiter_centers_phase2": recruiter_centers,
    "prelock_duration": prelock_duration,
    "locked_ticks": locks,
    "total_locks": len(locks),
    "final_position": position
}

with open("../results/trial_196_reinforcement_memory_summary.json", "w") as f:
    json.dump(results, f, indent=2)
