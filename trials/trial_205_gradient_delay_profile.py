
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
gradient_steps = [round(0.02 + 0.01 * i, 2) for i in range(9)]  # 0.02 to 0.10

results = []

for gradient in gradient_steps:
    identity = {"position": 6.0, "phase": 0.0}
    locked_ticks = []
    locked_positions = []

    for t in range(ticks):
        support = 0
        for center in recruiter_centers:
            offset = abs(identity["position"] - center)
            recruiter_phase = (identity["phase"] + amplitude * math.sin(2 * math.pi * t / period + offset * gradient)) % 1.0
            phase_diff = abs((recruiter_phase - identity["phase"] + 0.5) % 1.0 - 0.5)
            if phase_diff < phase_tolerance:
                support += 1

        if support >= support_threshold:
            locked_ticks.append(t)
            locked_positions.append(round(identity["position"], 3))

        identity["position"] += velocity

    # Delay intervals
    timing_intervals = [locked_ticks[i+1] - locked_ticks[i] for i in range(len(locked_ticks)-1)]
    if timing_intervals:
        average_delay = sum(timing_intervals) / len(timing_intervals)
    else:
        average_delay = None

    results.append({
        "phase_gradient": gradient,
        "total_locks": len(locked_ticks),
        "final_position": identity["position"],
        "average_timing_delay_between_locks": average_delay
    })

# Write results
with open("../results/trial_205_gradient_delay_profile_summary.json", "w") as f:
    json.dump(results, f, indent=2)
