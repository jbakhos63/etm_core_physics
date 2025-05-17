"""
Trial 022: Photon-Guided Return from Module E1 to G

Goal:
- Test whether identity reformation into Module G (phase 0.0) can occur only if preceded by a photon (rotor echo) at the correct timing
- Photon serves as timing signal or phase carrier

Setup:
- Identity begins in phase 0.2 (E1)
- Recruiters fixed at phase 0.0 (G)
- Rotor emits phase 0.0 echo just before identity return attempt

This simulates ETM photons as rhythm-carriers required for de-excitation.
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
PHOTON_ECHO_PHASE = 0.0
E1_PHASE = 0.2
G_PHASE = 0.0
ANCESTRY = "rotor-A"

# Create recruiter field for Module G
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=G_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}

# Pre-reinforce recruiter field
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Emit final timing signal from photon (phase 0.0 echo)
for rec in recruiters.values():
    rec.receive_echo("photon", PHOTON_ECHO_PHASE, strength=SUPPORT_PER_ECHO)

# Identity drops from E1 at phase 0.2
identity = ETMNode("identity_E1", initial_tick=0, phase=E1_PHASE)
identity.set_ancestry(ANCESTRY)

# Attempt return into G
tick_phase_match = abs(identity.phase - G_PHASE) <= PHASE_TOLERANCE
support = sum(r.support_score for r in recruiters.values()) / len(recruiters)

conditions = {
    "recruiter_support": support,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}

engine = TransitionEngine()
result = engine.attempt_transition("B", conditions)

# Export result
recruiter_summary = {r.node_id: r.get_summary() for r in recruiters.values()}

os.makedirs("../results", exist_ok=True)
with open("../results/trial_022_summary.json", "w") as f:
    json.dump({
        "identity_phase": identity.phase,
        "target_return_phase": G_PHASE,
        "tick_phase_match": tick_phase_match,
        "recruiter_support": support,
        "module_before": "B",
        "module_after": result,
        "recruiter_state": recruiter_summary
    }, f, indent=2)

engine.export_transition_log("../results/transition_log_trial022.json")
