
# trial_033_modular_energy_vs_duration.py

"""
Trial 033: Energy Cost Scaling with Displacement Duration

Goal:
- Measure modular reinforcement cost as a function of identity duration held in displaced state
- Confirm linear scaling between ticks held and recruiter effort
- Solidify hbar_ETM relationship as a predictive law
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
ANCESTRY = "rotor-A"
INITIAL_PHASE = 0.20
DELTA_PHI = 0.01
TICK_RATE = 1.0
SUPPORT_PER_ECHO = 0.01
REINFORCEMENT_PER_TICK = 4
DURATION_SET = [2, 3, 4, 5]

results = {}
detailed_log = {}

for ticks_held in DURATION_SET:
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

    # Initialize identity
    identity = ETMNode("energy_duration_test", initial_tick=0, phase=INITIAL_PHASE)
    identity.tick_rate = TICK_RATE
    identity.phase_increment = DELTA_PHI
    identity.set_ancestry(ANCESTRY)

    total_reinforcement = 0.0
    tick_log = []

    for t in range(1, ticks_held + 1):
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, INITIAL_PHASE, SUPPORT_PER_ECHO)
            total_reinforcement += SUPPORT_PER_ECHO

        identity.tick_forward()

        tick_log.append({
            "tick": t,
            "phase": round(identity.phase, 6),
            "reinforcement_received": SUPPORT_PER_ECHO * REINFORCEMENT_PER_TICK
        })

    results[str(ticks_held)] = {
        "ticks_held": ticks_held,
        "total_reinforcement_input": round(total_reinforcement, 6),
        "reinforcement_per_tick": SUPPORT_PER_ECHO * REINFORCEMENT_PER_TICK
    }

    detailed_log[str(ticks_held)] = tick_log

# Save results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_033_summary.json", "w") as f:
    json.dump(results, f, indent=2)

with open("../results/transition_log_trial033.json", "w") as f:
    json.dump(detailed_log, f, indent=2)
