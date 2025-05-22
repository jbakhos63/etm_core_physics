
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Parameters
periods = [10 * i for i in range(1, 11)]  # 10 to 100
amplitude = 0.1
ticks = 150
recruiter_centers = [6, 8, 10, 12, 14, 16, 18]
identity_phase = 0.0
support_threshold = 3.0
phase_tolerance = 0.05

results = []

for period in periods:
    locks = []
    position = 10.0  # Start near center
    for t in range(ticks):
        support = 0
        for center in recruiter_centers:
            recruiter_phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / period)) % 1.0
            phase_diff = abs((recruiter_phase - identity_phase + 0.5) % 1.0 - 0.5)
            if phase_diff < phase_tolerance:
                support += 1
        if support >= support_threshold:
            locks.append(t)
        position += 0.032  # Simulated movement
    results.append({
        "period": period,
        "locked_ticks": locks,
        "total_locks": len(locks),
        "final_position": position
    })

# Write summary to the results folder
with open("../results/trial_188_summary.json", "w") as f:
    json.dump(results, f, indent=2)
