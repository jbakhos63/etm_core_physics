"""
Trial 023: Dual-Phase Photon-Guided Return

Goal:
- Test whether synchronized photon echoes at identity phase (0.2) and recruiter phase (0.0) enable return into Module G
- Identity begins at phase 0.2 (E1)
- Recruiters fixed at phase 0.0 (G)
- Photons precede return at both 0.2 and 0.0

This tests whether dual-phase photon resonance enables modular transition despite phase offset.
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
PHOTON_PHASE_IDENTITY = 0.2
PHOTON_PHASE_RECRUITER = 0.0
E1_PHASE = 0.2
G_PHASE = 0.0
ANCESTRY = "rotor-A"

# Recruiters for Module G
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=G_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}

# Reinforce recruiter field
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Emit dual photon echoes (timing signals)
for rec in recruiters.values():
    rec.receive_echo("photon", PHOTON_PHASE_IDENTITY, strength=SUPPORT_PER_ECHO / 2)
    rec.receive_echo("photon", PHOTON_PHASE_RECRUITER, strength=SUPPORT_PER_ECHO / 2)

# Identity in E1
identity = ETMNode("identity_E1", initial_tick=0, phase=E1_PHASE)
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

# Export
recruiter_summary = {r.node_id: r.get_summary() for r in recruiters.values()}

os.makedirs("../results", exist_ok=True)
with open("../results/trial_023_summary.json", "w") as f:
    json.dump({
        "identity_phase": identity.phase,
        "tick_phase_match": tick_phase_match,
        "recruiter_support": support,
        "module_before": "B",
        "module_after": result,
        "recruiter_state": recruiter_summary
    }, f, indent=2)

engine.export_transition_log("../results/transition_log_trial023.json")
