"""
Trial 008: Fine-Grained Timing Sweep (0.1 tick steps)

Goal:
- Sweep from tick 387.0 to 388.0 in 0.1 increments
- Confirm timing return window boundaries
- Determine whether reformation occurs in sharp bands or across phase ranges
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Setup
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
TOTAL_ECHOS = 10
FINE_TICKS = [round(387.0 + 0.1 * i, 2) for i in range(11)]  # 387.0 to 388.0

# Scaffold recruiter setup
scaffold_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
recruiters = {
    (x, y): RecruiterNode(
        node_id=f"rec_{x}_{y}",
        target_ancestry="rotor-A",
        target_phase=0.0,
        phase_tolerance=PHASE_TOLERANCE
    )
    for (x, y) in scaffold_positions
}

# Load echo support
for _ in range(TOTAL_ECHOS):
    for rec in recruiters.values():
        rec.receive_echo("rotor-A", 0.01, strength=SUPPORT_PER_ECHO)

# Phase computation
def tick_to_phase(tick_val):
    return tick_val % 1.0

# Transition sweep
engine = TransitionEngine()
results = {}

for tick in FINE_TICKS:
    phase = tick_to_phase(tick)
    tick_phase_match = abs(phase - 0.0) <= PHASE_TOLERANCE
    return_conditions = {
        "recruiter_support": sum(r.support_score for r in recruiters.values()) / len(recruiters),
        "ancestry_match": True,
        "tick_phase_match": tick_phase_match
    }
    before = "B"
    after = engine.attempt_transition(before, return_conditions)

    results[str(tick)] = {
        "tick": tick,
        "phase": round(phase, 4),
        "tick_phase_match": tick_phase_match,
        "module_before": before,
        "module_after": after
    }

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_008_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial008.json")
