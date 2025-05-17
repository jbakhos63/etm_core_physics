
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# ETM speed of light derived from prior trials:
# c_ETM = 1 / sqrt(epsilon * mu) ≈ 1 / sqrt(2.2 * 2.9) ≈ 0.395 units per tick
c_etm = 1 / math.sqrt(2.2 * 2.9)

# Simulation parameters
ticks = 150
recruiter_centers = list(range(6, 21, 2))
period = 40
amplitude = 0.1
phase_tolerance = 0.05
support_threshold = 3
phase_gradient = 0.05
rotation_bias = 0.1

# Rotor
identity = {"position": 6.0, "phase": 0.0, "velocity": c_etm}
locked_ticks = []
locked_positions = []

for t in range(ticks):
    support = 0
    for center in recruiter_centers:
        offset = abs(identity["position"] - center)
        recruiter_phase = (identity["phase"] +
                           amplitude * math.sin(2 * math.pi * t / period + offset * phase_gradient + rotation_bias * t)) % 1.0
        phase_diff = abs((recruiter_phase - identity["phase"] + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1

    if support >= support_threshold:
        locked_ticks.append(t)
        locked_positions.append(round(identity["position"], 3))

    identity["position"] += identity["velocity"]

# Delay calculation
timing_intervals = [locked_ticks[i+1] - locked_ticks[i] for i in range(len(locked_ticks)-1)]
avg_delay = sum(timing_intervals) / len(timing_intervals) if timing_intervals else None

# Write results
results = {
    "c_etm": c_etm,
    "locked_ticks": locked_ticks,
    "locked_positions": locked_positions,
    "total_locks": len(locked_ticks),
    "average_delay_between_locks": avg_delay,
    "final_position": identity["position"]
}

with open("../results/trial_208_etm_speedoflight_constant_summary.json", "w") as f:
    json.dump(results, f, indent=2)
