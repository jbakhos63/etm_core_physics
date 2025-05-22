"""
Trial 021: Modular Return Phase Sweep to Module G

Goal:
- Sweep return attempts at various identity phases to detect the allowed window for return into Module G
- Recruiter field remains fixed at phase 0.0

This refines the quantized modular transition profile and contributes to ETM's Planck modeling.
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
REINFORCE_COUNT = 6
RECRUITER_PHASE = 0.0
ANCESTRY = "rotor-A"

# Phases to test for return
PHASE_SWEEP = [0.1, 0.15, 0.2, 0.25, 0.3]

# Setup recruiter field for Module G
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=RECRUITER_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}

# Reinforce Module G field
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Run sweep test
engine = TransitionEngine()
results = {}

for phase in PHASE_SWEEP:
    identity = ETMNode("test_identity", initial_tick=0, phase=phase)
    identity.set_ancestry(ANCESTRY)

    tick_phase_match = abs(identity.phase - RECRUITER_PHASE) <= PHASE_TOLERANCE
    support = sum(r.support_score for r in recruiters.values()) / len(recruiters)

    conditions = {
        "recruiter_support": support,
        "ancestry_match": True,
        "tick_phase_match": tick_phase_match
    }

    result = engine.attempt_transition("B", conditions)

    results[str(phase)] = {
        "identity_phase": phase,
        "tick_phase_match": tick_phase_match,
        "recruiter_support": support,
        "module_before": "B",
        "module_after": result
    }

# Export results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_021_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial021.json")
