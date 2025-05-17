"""
Trial 005: Orbital Scaffold Return Test

Goal:
- Simulate identity reformation using scaffold-style recruiters
- Recruiters act as timing loop that sustains echo support
- Dropped identity re-forms if support is strong and persistent
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Define scaffold shape: ring around center
GRID_SIZE = 3
CENTER = (1, 1)
TICKS = 12
PHASE_STEP = 0.05
PHASE_TOLERANCE = 0.11

# Create scaffold recruiters (ring only)
scaffold_positions = [
    (0, 1), (1, 0), (1, 2), (2, 1),  # cardinal neighbors only
]

recruiters = {}
for (x, y) in scaffold_positions:
    recruiters[(x, y)] = RecruiterNode(
        node_id=f"rec_{x}_{y}",
        target_ancestry="rotor-A",
        target_phase=0.0,
        phase_tolerance=PHASE_TOLERANCE
    )

# Simulate scaffold reinforcement: echo loop from rotor
rotor = ETMNode(node_id="rotor_1_1", initial_tick=0, phase=0.0)
rotor.set_ancestry("rotor-A")

for t in range(TICKS):
    rotor.tick_forward(PHASE_STEP)
    echo_phase = rotor.phase
    ancestry = rotor.ancestry_tag
    for pos in scaffold_positions:
        recruiters[pos].receive_echo(ancestry, echo_phase)

# Identity drop at center
return_conditions = {
    "recruiter_support": sum(r.support_score for r in recruiters.values()) / len(recruiters),
    "ancestry_match": True,
    "tick_phase_match": True
}

engine = TransitionEngine()
module_before = "B"
module_after = engine.attempt_transition(module_before, return_conditions)

# Save results
summary = {
    "tick_count": TICKS,
    "return_conditions": return_conditions,
    "module_before": module_before,
    "module_after": module_after
}

os.makedirs("../results", exist_ok=True)
with open("../results/trial_005_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

engine.export_transition_log("../results/transition_log_trial005.json")
for rec in recruiters.values():
    rec.export_summary(f"../results/{rec.node_id}_trial005.json")
