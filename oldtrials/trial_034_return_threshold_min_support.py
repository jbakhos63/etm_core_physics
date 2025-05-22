
# trial_034_return_threshold_min_support.py

"""
Trial 034: Minimal Support Threshold for Modular Return

Goal:
- Hold an identity at excited phase for τ_ETM (3 ticks)
- Vary reinforcement levels to find the minimum recruiter support needed for successful return
- Establish an effective energy floor below which return fails
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Constants
ANCESTRY = "rotor-A"
INITIAL_PHASE = 0.20
DELTA_PHI = 0.01
TICK_RATE = 1.0
TICKS_HELD = 3
REINFORCEMENT_LEVELS = [0.01, 0.02, 0.03, 0.04]  # Test descending support levels

results = {}

for support_per_echo in REINFORCEMENT_LEVELS:
    # Setup recruiters
    recruiters = {
        f"E1_{i}": RecruiterNode(
            node_id=f"E1_{i}",
            target_ancestry=ANCESTRY,
            target_phase=INITIAL_PHASE,
            phase_tolerance=0.11
        )
        for i in range(4)
    }

    # Identity setup
    identity = ETMNode("threshold_return_test", initial_tick=0, phase=INITIAL_PHASE)
    identity.tick_rate = TICK_RATE
    identity.phase_increment = DELTA_PHI
    identity.set_ancestry(ANCESTRY)

    # Reinforce for TICKS_HELD ticks
    for t in range(TICKS_HELD):
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, INITIAL_PHASE, support_per_echo)
        identity.tick_forward()

    # Attempt return
    engine = TransitionEngine()
    support = sum(r.support_score for r in recruiters.values()) / len(recruiters)
    tick_phase_match = abs(identity.phase - 0.0) <= 0.11

    conditions = {
        "recruiter_support": support,
        "ancestry_match": True,
        "tick_phase_match": tick_phase_match
    }

    result = engine.attempt_transition("B", conditions)

    results[str(support_per_echo)] = {
        "ticks_held": TICKS_HELD,
        "total_support": round(support, 6),
        "tick_phase_match": tick_phase_match,
        "module_before": "B",
        "module_after": result
    }

# Save results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_034_summary.json", "w") as f:
    json.dump(results, f, indent=2)
