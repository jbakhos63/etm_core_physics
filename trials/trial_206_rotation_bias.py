
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

# Recruiter rotation bias factor — simulates phase momentum (analog of magnetic field)
rotation_bias = 0.1  # Phase accumulates over time

# Rotor identity
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

# Compute delay intervals
timing_intervals = [locked_ticks[i+1] - locked_ticks[i] for i in range(len(locked_ticks)-1)]
if timing_intervals:
    avg_delay = sum(timing_intervals) / len(timing_intervals)
else:
    avg_delay = None

# Write results
results = {
    "rotation_bias": rotation_bias,
    "locked_ticks": locked_ticks,
    "locked_positions": locked_positions,
    "total_locks": len(locked_ticks),
    "average_delay_between_locks": avg_delay,
    "final_position": identity["position"]
}

with open("../results/trial_206_rotation_bias_summary.json", "w") as f:
    json.dump(results, f, indent=2)
