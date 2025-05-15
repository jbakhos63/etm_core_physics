
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Recruiter band configuration (all coherent)
recruiter_centers = [8, 10, 12, 14, 16, 18, 20]
period = 40
amplitude = 0.1
phase_offset = 0.0

# Displacement: shift identity's motion path to be off-center from the recruiter band midpoint
identity_initial_position = 4.0  # Start significantly left of recruiter centerline
ticks = 150
identity_phase = 0.0
support_threshold = 3.0
phase_tolerance = 0.05

locks = []
position = identity_initial_position

for t in range(ticks):
    support = 0
    for center in recruiter_centers:
        recruiter_phase = (identity_phase + amplitude * math.sin(2 * math.pi * t / period + phase_offset)) % 1.0
        phase_diff = abs((recruiter_phase - identity_phase + 0.5) % 1.0 - 0.5)
        if phase_diff < phase_tolerance:
            support += 1
    if support >= support_threshold:
        locks.append(t)
    position += 0.032  # Simulated linear motion, now starting off-center

# Write summary to results
results = {
    "recruiter_centers": recruiter_centers,
    "identity_initial_position": identity_initial_position,
    "locked_ticks": locks,
    "total_locks": len(locks),
    "final_position": position
}

with open("../results/trial_190_displaced_offset_summary.json", "w") as f:
    json.dump(results, f, indent=2)
