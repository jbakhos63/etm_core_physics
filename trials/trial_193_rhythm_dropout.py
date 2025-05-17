
import math
import json
import os

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

# Dropout window configuration
# Every 50 ticks, disable recruiter support for 10 ticks
dropout_length = 10
dropout_every = 50

locks = []

for t in range(ticks):
    dropout = (t % dropout_every) < dropout_length
    support = 0

    for center in recruiter_centers:
        if dropout:
            continue  # recruiters inactive during dropout window

        recruiter_phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / period + phase_offset)) % 1.0
        phase_diff = abs((recruiter_phase - identity_phase + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1

    if support >= support_threshold:
        locks.append(t)
    position += 0.032

# Write summary to results
results = {
    "recruiter_centers": recruiter_centers,
    "dropout_length": dropout_length,
    "dropout_every": dropout_every,
    "locked_ticks": locks,
    "total_locks": len(locks),
    "final_position": position
}

with open("../results/trial_193_rhythm_dropout_summary.json", "w") as f:
    json.dump(results, f, indent=2)
