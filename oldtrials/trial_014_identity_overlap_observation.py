"""
Trial 014: Modular Identity Overlap Observation

Goal:
- Observe behavior when two identities with same ancestry and tick phase return into the same modular rhythm
- No exclusion or conflict prevention logic is applied
- Log whether return succeeds and what properties each identity has

This trial helps determine whether exclusion is needed or if ETM supports shared identity occupancy in rhythm.
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
ANCESTRY_TAG = "rotor-A"

# Recruiter scaffold
scaffold_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
recruiters = {
    (x, y): RecruiterNode(
        node_id=f"rec_{x}_{y}",
        target_ancestry=ANCESTRY_TAG,
        target_phase=RETURN_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for (x, y) in scaffold_positions
}

# Reinforce recruiter field
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY_TAG, 0.01, strength=SUPPORT_PER_ECHO)

# Set up transition conditions
tick_phase_match = True
support = sum(r.support_score for r in recruiters.values()) / len(recruiters)

engine = TransitionEngine()
results = {}

# Identity A return
conditions_A = {
    "recruiter_support": support,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}
module_A = engine.attempt_transition("B", conditions_A)

# Identity B return (same everything)
conditions_B = {
    "recruiter_support": support,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}
module_B = engine.attempt_transition("B", conditions_B)

# Record results
results["identity_A"] = {
    "tick_phase": RETURN_PHASE,
    "module_before": "B",
    "module_after": module_A,
    "recruiter_support": support
}
results["identity_B"] = {
    "tick_phase": RETURN_PHASE,
    "module_before": "B",
    "module_after": module_B,
    "recruiter_support": support
}

# Export
os.makedirs("../results", exist_ok=True)
with open("../results/trial_014_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial014.json")
