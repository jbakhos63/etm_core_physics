"""
Trial 006: Timing Return Sweep

Goal:
- Detect which ticks allow modular identity return
- Simulate echo support from a scaffold
- Sweep from tick 380 to 390
- Confirm modular reformation occurs only at certain discrete ticks

This lays the groundwork for deriving Planck timing intervals in ETM.
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Scaffold configuration
scaffold_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
TOTAL_ECHOS = 10

# Prepare scaffold recruiters
recruiters = {}
for (x, y) in scaffold_positions:
    recruiters[(x, y)] = RecruiterNode(
        node_id=f"rec_{x}_{y}",
        target_ancestry="rotor-A",
        target_phase=0.0,
        phase_tolerance=PHASE_TOLERANCE
    )

# Simulate sustained echo reinforcement before timing sweep
for _ in range(TOTAL_ECHOS):
    for rec in recruiters.values():
        rec.receive_echo("rotor-A", 0.01, strength=SUPPORT_PER_ECHO)

# Sweep across tick values to test return timing
engine = TransitionEngine()
results = {}

for tick in range(380, 391):
    return_conditions = {
        "recruiter_support": sum(r.support_score for r in recruiters.values()) / len(recruiters),
        "ancestry_match": True,
        "tick_phase_match": (tick % 3 == 0)  # Simulated modular rhythm constraint
    }

    module_before = "B"
    module_after = engine.attempt_transition(module_before, return_conditions)

    results[tick] = {
        "tick": tick,
        "tick_phase_match": return_conditions["tick_phase_match"],
        "support": return_conditions["recruiter_support"],
        "module_before": module_before,
        "module_after": module_after
    }

# Save output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_006_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial006.json")
