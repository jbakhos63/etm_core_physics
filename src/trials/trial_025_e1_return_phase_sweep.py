"""
Trial 025: E1 → G Return Phase Sweep

Goal:
- Identity begins at E1 phase (0.2)
- Recruiter field fixed at G phase (0.0)
- Sweep identity return attempts across phases near 0.0
- Detect quantized return intervals
- Begin modeling tick-based ETM transition interval (Planck analog)

Sweep phases: 0.0 to 0.25 in 0.05 steps
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
PHASE_SWEEP = [round(i * 0.05, 2) for i in range(6)]  # [0.0, 0.05, ..., 0.25]

# Recruiter setup for Module G
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

# Sweep test
engine = TransitionEngine()
results = {}

for phase in PHASE_SWEEP:
    identity = ETMNode("test_E1", initial_tick=0, phase=phase)
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

# Export
os.makedirs("../results", exist_ok=True)
with open("../results/trial_025_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial025.json")
