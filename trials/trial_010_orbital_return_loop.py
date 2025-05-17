"""
Trial 010: Orbital Return Loop Using tau_ETM

Goal:
- Simulate repeated identity returns to a modular scaffold at fixed intervals
- Echo reinforcement occurs every tau_ETM = 0.10 phase units
- Detect whether identity return is cyclic and repeatable

This tests whether ETM supports orbital identity reformation driven by rhythmic scaffolding.
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Constants
TAU_ETM = 0.10
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
REINFORCE_CYCLES = 3
REINFORCE_INTERVAL = 1.0  # one full cycle = 1.0
RETURN_PHASES = [round(i * TAU_ETM, 2) for i in range(REINFORCE_CYCLES + 1)]  # [0.0, 0.10, 0.20, 0.30]

# Scaffold setup
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

# Simulated reinforcement at exact return phases
def reinforce_phase(phase):
    for rec in recruiters.values():
        rec.receive_echo("rotor-A", phase, strength=SUPPORT_PER_ECHO)

# Preload recruiter support for each return interval
for phase in RETURN_PHASES:
    reinforce_phase(phase)

# Identity return attempts at matching tick phases
engine = TransitionEngine()
results = {}

for phase in RETURN_PHASES:
    tick_phase_match = abs(phase - 0.0) <= PHASE_TOLERANCE
    return_conditions = {
        "recruiter_support": sum(r.support_score for r in recruiters.values()) / len(recruiters),
        "ancestry_match": True,
        "tick_phase_match": tick_phase_match
    }
    before = "B"
    after = engine.attempt_transition(before, return_conditions)

    results[str(phase)] = {
        "tick_phase": phase,
        "tick_phase_match": tick_phase_match,
        "module_before": before,
        "module_after": after
    }

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_010_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial010.json")
