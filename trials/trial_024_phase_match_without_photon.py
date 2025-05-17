"""
Trial 024: Return at Matching Phase Without Photon

Goal:
- Test whether identity return to Module G at phase 0.0 succeeds without a photon echo
- Recruiter field matches phase 0.0
- Identity drops at 0.0 (G phase)
- No timing signal from photon is provided

This checks if phase alignment alone is sufficient for modular reformation.
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Constants
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
REINFORCE_COUNT = 5
G_PHASE = 0.0
ANCESTRY = "rotor-A"

# Setup recruiter field for Module G
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=G_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}

# Reinforce recruiter field (no photon)
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Identity drops at phase 0.0
identity = ETMNode("identity_drop", initial_tick=0, phase=G_PHASE)
identity.set_ancestry(ANCESTRY)

# Attempt return
tick_phase_match = abs(identity.phase - G_PHASE) <= PHASE_TOLERANCE
support = sum(r.support_score for r in recruiters.values()) / len(recruiters)

conditions = {
    "recruiter_support": support,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}

engine = TransitionEngine()
result = engine.attempt_transition("B", conditions)

# Export results
recruiter_summary = {r.node_id: r.get_summary() for r in recruiters.values()}

os.makedirs("../results", exist_ok=True)
with open("../results/trial_024_summary.json", "w") as f:
    json.dump({
        "identity_phase": identity.phase,
        "tick_phase_match": tick_phase_match,
        "recruiter_support": support,
        "module_before": "B",
        "module_after": result,
        "recruiter_state": recruiter_summary
    }, f, indent=2)

engine.export_transition_log("../results/transition_log_trial024.json")
