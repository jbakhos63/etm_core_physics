"""
Trial 016: Same Ancestry Conflict Test

Goal:
- Test whether two identities with identical ancestry and tick phase can both return into the same modular rhythm
- Checks for implicit ancestry-based exclusion (e.g., Pauli-like conflict due to indistinguishability)

Setup:
- Two identities with ancestry "rotor-A"
- Return phase = 0.0
- Recruiter support reinforced equally
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
TAG = "rotor-A"

# Create shared recruiters for ancestry "rotor-A"
recruiters = {
    f"rec_{i}": RecruiterNode(
        node_id=f"rec_{i}",
        target_ancestry=TAG,
        target_phase=RETURN_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}

# Reinforce recruiters
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(TAG, 0.01, strength=SUPPORT_PER_ECHO)

# Compute support
support = sum(r.support_score for r in recruiters.values()) / len(recruiters)
tick_phase_match = True

engine = TransitionEngine()
results = {}

# Identity A
conditions_A = {
    "recruiter_support": support,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}
result_A = engine.attempt_transition("B", conditions_A)

# Identity B (identical ancestry)
conditions_B = {
    "recruiter_support": support,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}
result_B = engine.attempt_transition("B", conditions_B)

# Record results
results["identity_A"] = {
    "tick_phase": RETURN_PHASE,
    "ancestry": TAG,
    "module_before": "B",
    "module_after": result_A,
    "recruiter_support": support
}
results["identity_B"] = {
    "tick_phase": RETURN_PHASE,
    "ancestry": TAG,
    "module_before": "B",
    "module_after": result_B,
    "recruiter_support": support
}

# Export
os.makedirs("../results", exist_ok=True)
with open("../results/trial_016_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial016.json")
