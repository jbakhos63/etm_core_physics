"""
Trial 007: Fractional Tick Timing Sweep

Goal:
- Explore whether identity return occurs only at discrete sub-tick intervals
- Sweep from tick 387.0 to 388.0 in 0.2 increments
- Use phase offset detection instead of modulo
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
FRACTIONAL_TICKS = [round(387.0 + 0.2 * i, 2) for i in range(6)]  # 387.0 to 388.0

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

# Simulated phase function: assume phase wraps every 1.0
def tick_to_phase(tick_value):
    return tick_value % 1.0

# Sweep logic
engine = TransitionEngine()
results = {}

for tick in FRACTIONAL_TICKS:
    phase = tick_to_phase(tick)
    tick_phase_match = abs(phase - 0.0) <= PHASE_TOLERANCE  # centered around phase 0.0
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

# Export results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_007_summary.json", "w") as f:
    json.dump(results, f, indent=2)

engine.export_transition_log("../results/transition_log_trial007.json")
