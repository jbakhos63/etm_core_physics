"""
Trial 009: Timing Phase Bandwidth Sweep (0.05 resolution)

Goal:
- Sweep from tick 386.5 to 388.5 in 0.05 increments
- Confirm return window boundaries
- Derive ETM phase bandwidth for modular reformation
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
TOTAL_ECHOS = 10
SWEEP_TICKS = [round(386.5 + 0.05 * i, 2) for i in range(41)]  # 386.5 to 388.5

# Setup recruiter scaffold
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

# Preload recruiter support
for _ in range(TOTAL_ECHOS):
    for rec in recruiters.values():
        rec.receive_echo("rotor-A", 0.01, strength=SUPPORT_PER_ECHO)

# Phase function
def tick_to_phase(tick_val):
    return tick_val % 1.0

# Sweep and log
engine = TransitionEngine()
results = {}

for tick in SWEEP_TICKS:
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

# Export
os.makedirs("../results", exist_ok=True)
with open("../results/trial_009_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial009.json")
