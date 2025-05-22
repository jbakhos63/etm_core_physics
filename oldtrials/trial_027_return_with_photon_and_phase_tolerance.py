"""
Trial 027: Return with Photon and Phase Tolerance Sweep

Goal:
- Identity begins at E1-like phases: 0.10 to 0.14
- Recruiter field fixed at Module G phase (0.0)
- Emit photon echoes at both identity phase and recruiter phase
- Detect whether photon support enables return near the edge of the return window

This probes tolerance boundaries in photon-guided return behavior.
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
RECRUITER_PHASE = 0.0
ANCESTRY = "rotor-A"
PHASE_SWEEP = [0.10, 0.11, 0.12, 0.13, 0.14]

# Setup recruiter field
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=RECRUITER_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}

# Pre-reinforce recruiter field
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Test sweep
engine = TransitionEngine()
results = {}

for phase in PHASE_SWEEP:
    # Emit photons at both the identity and recruiter phase
    for rec in recruiters.values():
        rec.receive_echo("photon", phase, strength=SUPPORT_PER_ECHO / 2)
        rec.receive_echo("photon", RECRUITER_PHASE, strength=SUPPORT_PER_ECHO / 2)

    # Create identity at test phase
    identity = ETMNode("identity_test", initial_tick=0, phase=phase)
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
with open("../results/trial_027_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial027.json")
