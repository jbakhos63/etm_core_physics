"""
Trial 011: Orbital Return with Increased Recruiter Support

Goal:
- Test identity return with stronger echo reinforcement
- Reinforce recruiters at least 6 times (support > 3.0)
- Use tau_ETM = 0.10 as timing gate

Confirms that both timing phase match and support threshold must be satisfied.
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Constants
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
REINFORCE_COUNT = 6
RETURN_PHASES = [0.0, 0.1, 0.2, 0.3]

# Scaffold recruiters
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

# Apply echo reinforcement multiple times
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo("rotor-A", 0.01, strength=SUPPORT_PER_ECHO)

# Run transitions at fixed return phases
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
        "recruiter_support": return_conditions["recruiter_support"],
        "module_before": before,
        "module_after": after
    }

# Export
os.makedirs("../results", exist_ok=True)
with open("../results/trial_011_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial011.json")
