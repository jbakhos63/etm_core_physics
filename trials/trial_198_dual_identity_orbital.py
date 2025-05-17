
import math
import json
import os

# Ensure results folder exists
os.makedirs("../results", exist_ok=True)

# Parameters
period = 40
amplitude = 0.1
phase_offset = 0.0
ticks = 150
phase_tolerance = 0.05
support_threshold = 3

# Dual identities: A and B
identity_A = {"id": "A", "ancestry": "rotorA", "spin": "up", "phase": 0.0, "position": 9.0}
identity_B = {"id": "B", "ancestry": "rotorB", "spin": "up", "phase": 0.0, "position": 15.0}

# Shared recruiter field
recruiter_centers = [10, 12, 14]

# Results
locks = {"A": [], "B": []}

for t in range(ticks):
    for identity in [identity_A, identity_B]:
        support = 0
        for center in recruiter_centers:
            recruiter_phase = (identity["phase"] + amplitude * math.sin(2 * math.pi * t / period + phase_offset)) % 1.0
            phase_diff = abs((recruiter_phase - identity["phase"] + 0.5) % 1.0 - 0.5)
            if phase_diff < phase_tolerance:
                support += 1
        if support >= support_threshold:
            locks[identity["id"]].append(t)
        identity["position"] += 0.032  # Move both identities rightward

# Write summary
results = {
    "identities": [
        {"id": identity_A["id"], "ancestry": identity_A["ancestry"], "spin": identity_A["spin"]},
        {"id": identity_B["id"], "ancestry": identity_B["ancestry"], "spin": identity_B["spin"]}
    ],
    "recruiter_centers": recruiter_centers,
    "locked_ticks": locks,
    "final_positions": {
        "A": identity_A["position"],
        "B": identity_B["position"]
    },
    "total_locks": {
        "A": len(locks["A"]),
        "B": len(locks["B"])
    }
}

with open("../results/trial_198_dual_identity_orbital_summary.json", "w") as f:
    json.dump(results, f, indent=2)
