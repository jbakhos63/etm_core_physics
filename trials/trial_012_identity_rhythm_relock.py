"""
Trial 012: Modular Phase Re-lock Test

Goal:
- Test whether a displaced identity can return only into the same tick phase it originally left
- Confirms that modular identity includes phase rhythm, not just recruiter field and ancestry

Setup:
- Identity drops at phase = 0.0
- Return attempts at same phase and shifted phases
- All other conditions (support, ancestry) are held constant
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
ECHO_REINFORCE_COUNT = 6
ORIGINAL_PHASE = 0.0
TEST_PHASES = [0.0, 0.05, 0.1, 0.15]  # include exact, near-match, and outside return band

# Recruiter scaffold
scaffold_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
recruiters = {
    (x, y): RecruiterNode(
        node_id=f"rec_{x}_{y}",
        target_ancestry="rotor-A",
        target_phase=ORIGINAL_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for (x, y) in scaffold_positions
}

# Preload recruiter support
for _ in range(ECHO_REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo("rotor-A", 0.01, strength=SUPPORT_PER_ECHO)

# Run transitions at specified phases
engine = TransitionEngine()
results = {}

for phase in TEST_PHASES:
    tick_phase_match = abs(phase - ORIGINAL_PHASE) <= PHASE_TOLERANCE
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

# Export results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_012_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial012.json")
