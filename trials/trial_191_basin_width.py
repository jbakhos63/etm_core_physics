
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Parameters
period = 40
amplitude = 0.1
phase_offset = 0.0
ticks = 150
identity_phase = 0.0
support_threshold = 3.0
phase_tolerance = 0.05

results = []

# Test decreasing number of recruiter bands from 7 to 1
for band_count in range(7, 0, -1):
    recruiter_centers = [8 + 2 * i for i in range(band_count)]  # start at 8, step by 2
    locks = []
    position = 10.0  # centered start

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

    results.append({
        "band_count": band_count,
        "recruiter_centers": recruiter_centers,
        "locked_ticks": locks,
        "total_locks": len(locks),
        "final_position": position
    })

# Write results
with open("../results/trial_191_basin_width_summary.json", "w") as f:
    json.dump(results, f, indent=2)
