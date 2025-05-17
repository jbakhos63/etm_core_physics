"""
Trial 003: Phase Tolerance Test

Goal:
- Test recruiter scoring under relaxed phase tolerance
- Demonstrate that matching ancestry + phase results in non-zero support
- Reuse 3x3 grid with rotor in center
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Simulation settings
GRID_SIZE = 3
CENTER = (1, 1)
TICKS = 10
PHASE_STEP = 0.05

# Create recruiter grid with relaxed phase tolerance
recruiters = {}
for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        if (x, y) == CENTER:
            continue
        recruiters[(x, y)] = RecruiterNode(
            node_id=f"rec_{x}_{y}",
            target_ancestry="rotor-A",
            target_phase=0.0,
            phase_tolerance=0.11  # Wider tolerance to allow early phase match
        )

# Initialize central rotor node
rotor = ETMNode(node_id="rotor_1_1", initial_tick=0, phase=0.0)
rotor.set_ancestry("rotor-A")

# Simulation loop
for t in range(TICKS):
    rotor.tick_forward(PHASE_STEP)
    echo_phase = rotor.phase
    ancestry = rotor.ancestry_tag

    # Send echo to all 8 neighbors
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            x, y = CENTER[0] + dx, CENTER[1] + dy
            if (x, y) in recruiters:
                recruiters[(x, y)].receive_echo(ancestry, echo_phase)

# Save summary of each recruiter
summary = {
    "tick_count": TICKS,
    "rotor_final_phase": rotor.phase,
    "recruiter_summaries": {
        node_id: rec.get_summary()
        for (x, y), rec in recruiters.items()
        for node_id in [rec.node_id]
    }
}

# Export result
os.makedirs("../results", exist_ok=True)
with open("../results/trial_003_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# Export detailed recruiter logs
for rec in recruiters.values():
    rec.export_summary(f"../results/{rec.node_id}_trial003.json")
