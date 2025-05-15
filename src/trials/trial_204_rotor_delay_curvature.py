
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
gradient = 0.05  # Recruiter phase gradient

# Rotor identity
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

# Compute rotor delay metrics
timing_intervals = [locked_ticks[i+1] - locked_ticks[i] for i in range(len(locked_ticks)-1)]
spatial_intervals = [locked_positions[i+1] - locked_positions[i] for i in range(len(locked_positions)-1)]
propagation_metrics = list(zip(locked_ticks, locked_positions))

# Write results
results = {
    "gradient": gradient,
    "locked_ticks": locked_ticks,
    "locked_positions": locked_positions,
    "timing_intervals": timing_intervals,
    "spatial_intervals": spatial_intervals,
    "propagation_metrics": propagation_metrics,
    "final_position": identity["position"]
}

with open("../results/trial_204_rotor_delay_curvature_summary.json", "w") as f:
    json.dump(results, f, indent=2)
