"""
Trial 015 (Corrected): Spin-Distinguished Identity Return

Goal:
- Test whether two identities with distinct ancestry tags (e.g., rotor-A-up and rotor-A-down)
  can return into the same tick-phase modular rhythm without conflict

Fix:
- Explicitly reinforce recruiter support by checking both ancestry tags
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Parameters
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
REINFORCE_COUNT = 6
RETURN_PHASE = 0.0
TAG_UP = "rotor-A-up"
TAG_DOWN = "rotor-A-down"

# Set recruiter ancestry matching to each specific tag (simulate two sets)
recruiters_up = {
    f"rec_up_{i}": RecruiterNode(
        node_id=f"rec_up_{i}",
        target_ancestry=TAG_UP,
        target_phase=RETURN_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}
recruiters_down = {
    f"rec_down_{i}": RecruiterNode(
        node_id=f"rec_down_{i}",
        target_ancestry=TAG_DOWN,
        target_phase=RETURN_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}

# Reinforce both recruiter sets
for _ in range(REINFORCE_COUNT):
    for rec in recruiters_up.values():
        rec.receive_echo(TAG_UP, 0.01, strength=SUPPORT_PER_ECHO)
    for rec in recruiters_down.values():
        rec.receive_echo(TAG_DOWN, 0.01, strength=SUPPORT_PER_ECHO)

# Calculate support
support_up = sum(r.support_score for r in recruiters_up.values()) / len(recruiters_up)
support_down = sum(r.support_score for r in recruiters_down.values()) / len(recruiters_down)
tick_phase_match = True

engine = TransitionEngine()
results = {}

# Identity with spin up
conditions_up = {
    "recruiter_support": support_up,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}
result_up = engine.attempt_transition("B", conditions_up)

# Identity with spin down
conditions_down = {
    "recruiter_support": support_down,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}
result_down = engine.attempt_transition("B", conditions_down)

# Output results
results["identity_spin_up"] = {
    "tick_phase": RETURN_PHASE,
    "ancestry": TAG_UP,
    "recruiter_support": support_up,
    "module_before": "B",
    "module_after": result_up
}
results["identity_spin_down"] = {
    "tick_phase": RETURN_PHASE,
    "ancestry": TAG_DOWN,
    "recruiter_support": support_down,
    "module_before": "B",
    "module_after": result_down
}

# Export logs
os.makedirs("../results", exist_ok=True)
with open("../results/trial_015_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial015.json")
