
# trial_032_planck_energy_cost_by_tick.py

"""
Trial 032: Energy Cost Estimation During Modular Displacement

Goal:
- Hold a modular identity in an excited state (E1) for N ticks
- Measure total recruiter effort (reinforcement input) required to maintain coherence
- This yields a modular "energy burden" corresponding to the τ_ETM return interval
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
ANCESTRY = "rotor-A"
INITIAL_PHASE = 0.20  # Excited phase, offset from G
DELTA_PHI = 0.01
TICK_RATE = 1.0
TICKS_HELD = 3  # Number of ticks identity remains displaced in E1
SUPPORT_PER_ECHO = 0.01
REINFORCEMENT_PER_TICK = 4  # 4 recruiters ping each tick

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
identity = ETMNode("modular_energy_test", initial_tick=0, phase=INITIAL_PHASE)
identity.tick_rate = TICK_RATE
identity.phase_increment = DELTA_PHI
identity.set_ancestry(ANCESTRY)

tick_log = []

# Simulate TICKS_HELD steps of excitation
total_reinforcement = 0.0

for t in range(1, TICKS_HELD + 1):
    # Reinforce recruiter field
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, INITIAL_PHASE, SUPPORT_PER_ECHO)
        total_reinforcement += SUPPORT_PER_ECHO

    identity.tick_forward()

    tick_log.append({
        "tick": t,
        "phase": round(identity.phase, 6),
        "reinforcement_received": SUPPORT_PER_ECHO * REINFORCEMENT_PER_TICK
    })

# Summary
summary = {
    "initial_phase": INITIAL_PHASE,
    "delta_phi": DELTA_PHI,
    "ticks_held": TICKS_HELD,
    "total_reinforcement_input": round(total_reinforcement, 6),
    "reinforcement_per_tick": SUPPORT_PER_ECHO * REINFORCEMENT_PER_TICK
}

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_032_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

with open("../results/transition_log_trial032.json", "w") as f:
    json.dump(tick_log, f, indent=2)
