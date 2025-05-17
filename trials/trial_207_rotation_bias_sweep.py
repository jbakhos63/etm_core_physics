
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
velocity = 0.032
recruiter_centers = list(range(6, 21, 2))  # Positions: 6 to 20
rotation_bias_values = [round(0.05 + 0.01 * i, 2) for i in range(16)]  # 0.05 to 0.20

results = []

for rotation_bias in rotation_bias_values:
    identity = {"position": 6.0, "phase": 0.0}
    locked_ticks = []
    locked_positions = []

    for t in range(ticks):
        support = 0
        for center in recruiter_centers:
            offset = abs(identity["position"] - center)
            dynamic_phase = (identity["phase"] +
                             amplitude * math.sin(2 * math.pi * t / period + offset * 0.01 + rotation_bias * t)) % 1.0
            phase_diff = abs((dynamic_phase - identity["phase"] + 0.5) % 1.0 - 0.5)
            if phase_diff < phase_tolerance:
                support += 1

        if support >= support_threshold:
            locked_ticks.append(t)
            locked_positions.append(round(identity["position"], 3))

        identity["position"] += velocity

    # Compute average delay
    timing_intervals = [locked_ticks[i+1] - locked_ticks[i] for i in range(len(locked_ticks)-1)]
    avg_delay = sum(timing_intervals) / len(timing_intervals) if timing_intervals else None

    results.append({
        "rotation_bias": rotation_bias,
        "total_locks": len(locked_ticks),
        "average_delay_between_locks": avg_delay,
        "final_position": identity["position"]
    })

# Write results
with open("../results/trial_207_rotation_bias_sweep_summary.json", "w") as f:
    json.dump(results, f, indent=2)
