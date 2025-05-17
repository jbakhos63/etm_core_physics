
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Asymmetric recruiter configuration (shifted right)
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

locks = []

for t in range(ticks):
    support = 0
    for center in recruiter_centers:
        recruiter_phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / period + phase_offset)) % 1.0
        phase_diff = abs((recruiter_phase - identity_phase + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1
    if support >= support_threshold:
        locks.append(t)
    position += 0.032

# Write summary to results folder
results = {
    "recruiter_centers": recruiter_centers,
    "locked_ticks": locks,
    "total_locks": len(locks),
    "final_position": position
}

with open("../results/trial_192_asymmetric_field_summary.json", "w") as f:
    json.dump(results, f, indent=2)
