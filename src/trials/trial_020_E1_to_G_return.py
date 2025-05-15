"""
Trial 020: Return from E1 to G (De-Excitation)

Goal:
- Simulate modular identity return from excited state Module E1 to ground state Module G
- Identity starts at phase 0.2
- Recruiter field at phase 0.0 (G) is reinforced
- Identity attempts return into Module G

This establishes quantized modular transition intervals and supports Planck constant modeling in ETM.
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
E1_PHASE = 0.2
G_PHASE = 0.0
ANCESTRY = "rotor-A"

# Module G recruiters (target return)
g_positions = [(0, 1), (1, 0), (1, 1)]
recruiters = {
    f"G_{x}_{y}": RecruiterNode(
        node_id=f"G_{x}_{y}",
        target_ancestry=ANCESTRY,
        target_phase=G_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for (x, y) in g_positions
}

# Reinforce Module G recruiter field
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Identity starts in E1 (phase 0.2)
identity = ETMNode("identity_E1", initial_tick=0, phase=E1_PHASE)
identity.set_ancestry(ANCESTRY)

# Attempt return to G
tick_phase_match = abs(identity.phase - G_PHASE) <= PHASE_TOLERANCE
support = sum(r.support_score for r in recruiters.values()) / len(recruiters)

conditions = {
    "recruiter_support": support,
    "ancestry_match": True,
    "tick_phase_match": tick_phase_match
}

engine = TransitionEngine()
result = engine.attempt_transition("B", conditions)

# Output summary
recruiter_summary = {r.node_id: r.get_summary() for r in recruiters.values()}

os.makedirs("../results", exist_ok=True)
with open("../results/trial_020_summary.json", "w") as f:
    json.dump({
        "identity_phase": identity.phase,
        "target_return_phase": G_PHASE,
        "tick_phase_match": tick_phase_match,
        "recruiter_support": support,
        "module_before": "B",
        "module_after": result,
        "recruiter_state": recruiter_summary
    }, f, indent=2)

engine.export_transition_log("../results/transition_log_trial020.json")
