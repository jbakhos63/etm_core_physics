"""
Trial 013: Rhythm Conflict and Exclusion Test (ETM Pauli analog)

Goal:
- Test whether two identities with same ancestry and phase can return into the same modular rhythm
- Expectation: one or both returns should be blocked due to timing conflict (Pauli exclusion analog)

Setup:
- Two identities with same ancestry try to return at phase 0.0
- Recruiter field is strong and matched for both
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Constants
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
REINFORCE_COUNT = 6
RETURN_PHASE = 0.0

# Create shared recruiters
scaffold_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
recruiters = {
    (x, y): RecruiterNode(
        node_id=f"rec_{x}_{y}",
        target_ancestry="rotor-A",
        target_phase=RETURN_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for (x, y) in scaffold_positions
}

# Echo reinforcement
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo("rotor-A", 0.01, strength=SUPPORT_PER_ECHO)

# Phase matching check
tick_phase_match = True

# Prepare transition engine
engine = TransitionEngine()
results = {}

# Identity A tries to return
conditions_A = {
    "recruiter_support": sum(r.support_score for r in recruiters.values()) / len(recruiters),
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}
result_A = engine.attempt_transition("B", conditions_A)

# Identity B tries to return afterward, same ancestry and phase
conditions_B = conditions_A.copy()
result_B = engine.attempt_transition("B", conditions_B)

# Store both results
results["identity_A"] = {
    "tick_phase": RETURN_PHASE,
    "module_before": "B",
    "module_after": result_A,
    "recruiter_support": conditions_A["recruiter_support"]
}
results["identity_B"] = {
    "tick_phase": RETURN_PHASE,
    "module_before": "B",
    "module_after": result_B,
    "recruiter_support": conditions_B["recruiter_support"]
}

# Export
os.makedirs("../results", exist_ok=True)
with open("../results/trial_013_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial013.json")
