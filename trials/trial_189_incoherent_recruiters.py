
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Recruiter band configuration
recruiter_bands = [
    {"center": 6, "period": 40, "phase_offset": 0.0},
    {"center": 8, "period": 60, "phase_offset": 0.2},
    {"center": 10, "period": 90, "phase_offset": 0.4},
    {"center": 12, "period": 40, "phase_offset": 0.0},
    {"center": 14, "period": 40, "phase_offset": 0.0},
    {"center": 16, "period": 40, "phase_offset": 0.0},
    {"center": 18, "period": 40, "phase_offset": 0.0},
]

# Constants
amplitude = 0.1
ticks = 150
identity_phase = 0.0
support_threshold = 3.0
phase_tolerance = 0.05

locks = []
position = 10.0  # Start near center

for t in range(ticks):
    support = 0
    for band in recruiter_bands:
        phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / band["period"] + band["phase_offset"])) % 1.0
        phase_diff = abs((phase - identity_phase + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1
    if support >= support_threshold:
        locks.append(t)
    position += 0.032  # Simulated movement

# Write summary
results = {
    "recruiter_config": recruiter_bands,
    "locked_ticks": locks,
    "total_locks": len(locks),
    "final_position": position
}

with open("../results/trial_189_summary.json", "w") as f:
    json.dump(results, f, indent=2)
