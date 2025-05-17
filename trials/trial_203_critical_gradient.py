
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Constants
period = 40
amplitude = 0.1
ticks = 150
phase_tolerance = 0.05
support_threshold = 3
recruiter_centers = list(range(6, 21, 2))  # Positions: 6 to 20
velocity = 0.032

# Gradient sweep from 0.05 to 0.10
gradient_steps = [round(0.05 + 0.01 * i, 2) for i in range(6)]  # 0.05 to 0.10
results = []

for gradient in gradient_steps:
    identity_position = 6.0
    identity_phase = 0.0
    locked_ticks = []

    for t in range(ticks):
        support = 0
        for center in recruiter_centers:
            offset = abs(identity_position - center)
            recruiter_phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / period + offset * gradient)) % 1.0
            phase_diff = abs((recruiter_phase - identity_phase + 0.5) % 1.0 - 0.5)
            if phase_diff < phase_tolerance:
                support += 1
        if support >= support_threshold:
            locked_ticks.append(t)
        identity_position += velocity

    results.append({
        "phase_gradient_per_unit": gradient,
        "locked_ticks": locked_ticks,
        "total_locks": len(locked_ticks),
        "final_position": identity_position
    })

# Write summary
with open("../results/trial_203_critical_gradient_summary.json", "w") as f:
    json.dump(results, f, indent=2)
