"""
Trial 029: Tick-Based Resolution of Return Threshold

Goal:
- Simulate return attempts at small tick-phase steps
- Quantize the modular return boundary in tick units
- Begin mapping ETM's Planck interval in terms of tick-based timing

Phases: [0.105, 0.110, 0.115, 0.120]
Recruiter phase: 0.0
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
PHASE_SWEEP = [0.105, 0.110, 0.115, 0.120]

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

# Reinforce recruiter field
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Run sweep
engine = TransitionEngine()
results = {}

for phase in PHASE_SWEEP:
    identity = ETMNode("identity_tick_phase", initial_tick=0, phase=phase)
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
with open("../results/trial_029_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial029.json")
