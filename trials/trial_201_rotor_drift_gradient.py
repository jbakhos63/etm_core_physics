
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Trial 201: Recruiter phase gradient test (static spatial field gradient)

# Recruiter field phase slope: simulate field curvature via phase offset per position
recruiter_centers = list(range(6, 21, 2))  # Recruiter bands at positions 6 through 20
base_phase = 0.0
phase_gradient_per_unit = 0.01  # Gradual phase increase across space

# Rotor identity
identity = {"id": "photon", "phase": 0.0, "position": 6.0}

# Constants
ticks = 150
amplitude = 0.1
period = 40
support_threshold = 3
phase_tolerance = 0.05
velocity = 0.032

# Record rotor drift events
locks = []

for t in range(ticks):
    support = 0
    for center in recruiter_centers:
        spatial_offset = abs(identity["position"] - center)
        phase_shift = base_phase + spatial_offset * phase_gradient_per_unit
        recruiter_phase = (identity["phase"] + amplitude * math.sin(2 * math.pi * t / period + phase_shift)) % 1.0
        phase_diff = abs((recruiter_phase - identity["phase"] + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1

    if support >= support_threshold:
        locks.append(t)

    identity["position"] += velocity  # Rotor motion

# Write summary
results = {
    "recruiter_centers": recruiter_centers,
    "phase_gradient_per_unit": phase_gradient_per_unit,
    "locked_ticks": locks,
    "total_locks": len(locks),
    "final_position": identity["position"]
}

with open("../results/trial_201_rotor_drift_gradient_summary.json", "w") as f:
    json.dump(results, f, indent=2)
