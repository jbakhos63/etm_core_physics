
import math
import json
import os
import random

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Recruiter setup
recruiter_centers = [12, 14, 16]
period = 40
amplitude = 0.1
phase_offset = 0.0

# Identity parameters
ticks = 150
identity_phase = 0.0
support_threshold = 3.0
phase_tolerance = 0.05
position = 10.0

# Phase-selective dropout: each recruiter has its own dropout map
random.seed(195)
dropout_maps = {
    center: {t: random.random() < 0.3 for t in range(ticks)}  # 30% chance dropout per band per tick
    for center in recruiter_centers
}

locks = []

for t in range(ticks):
    support = 0
    for center in recruiter_centers:
        if dropout_maps[center][t]:
            continue  # recruiter is off
        recruiter_phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / period + phase_offset)) % 1.0
        phase_diff = abs((recruiter_phase - identity_phase + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1
    if support >= support_threshold:
        locks.append(t)
    position += 0.032

# Write summary
results = {
    "recruiter_centers": recruiter_centers,
    "dropout_maps": {
        str(center): [t for t in range(ticks) if dropout_maps[center][t]]
        for center in recruiter_centers
    },
    "locked_ticks": locks,
    "total_locks": len(locks),
    "final_position": position
}

with open("../results/trial_195_phase_selective_dropout_summary.json", "w") as f:
    json.dump(results, f, indent=2)
