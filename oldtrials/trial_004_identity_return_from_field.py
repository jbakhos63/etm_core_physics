"""
Trial 004: Identity Return from Field Support

Goal:
- Simulate identity reformation (e.g., B → D) if recruiter field support is strong enough
- Echo propagation builds recruiter support first
- After field reinforcement, a "dropped" node tests for transition to Module D
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Simulation settings
GRID_SIZE = 3
CENTER = (1, 1)
TICKS = 10
PHASE_STEP = 0.05
PHASE_TOLERANCE = 0.11

# Create recruiters around the center
recruiters = {}
for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        if (x, y) == CENTER:
            continue
        recruiters[(x, y)] = RecruiterNode(
            node_id=f"rec_{x}_{y}",
            target_ancestry="rotor-A",
            target_phase=0.0,
            phase_tolerance=PHASE_TOLERANCE
        )

# Initialize a rotor to build support
rotor = ETMNode(node_id="rotor_1_1", initial_tick=0, phase=0.0)
rotor.set_ancestry("rotor-A")

# Phase propagation for field reinforcement
for t in range(TICKS):
    rotor.tick_forward(PHASE_STEP)
    echo_phase = rotor.phase
    ancestry = rotor.ancestry_tag
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            x, y = CENTER[0] + dx, CENTER[1] + dy
            if (x, y) in recruiters:
                recruiters[(x, y)].receive_echo(ancestry, echo_phase)

# Simulate a dropped identity trying to return at center
return_node_conditions = {
    "recruiter_support": sum(r.support_score for r in recruiters.values()) / len(recruiters),
    "ancestry_match": True,
    "tick_phase_match": True
}

# Apply transition logic
engine = TransitionEngine()
module_before = "B"
module_after = engine.attempt_transition(module_before, return_node_conditions)

# Save outputs
summary = {
    "tick_count": TICKS,
    "recruiter_avg_support": return_node_conditions["recruiter_support"],
    "return_conditions": return_node_conditions,
    "module_before": module_before,
    "module_after": module_after
}

os.makedirs("../results", exist_ok=True)
with open("../results/trial_004_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

engine.export_transition_log("../results/transition_log_trial004.json")
for rec in recruiters.values():
    rec.export_summary(f"../results/{rec.node_id}_trial004.json")
