
# trial_031_tick_interval_to_tau_etm.py

"""
Trial 031: Tick Interval Required for Phase Shift to Reach τ_ETM

Goal:
- Measure how many ticks (with fixed ∆ϕ) are required for an identity phase to drift from ϕ = 0.0 to ϕ = 0.11
- This tick interval maps directly to τ_ETM and is needed to calibrate timing quantization
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode

# Parameters
DELTA_PHI = 0.01  # phase increment per tick
TARGET_PHASE = 0.11
START_PHASE = 0.0
TICK_RATE = 1.0

# Initialize identity node
node = ETMNode("tick_phase_measurement", initial_tick=0, phase=START_PHASE)
node.tick_rate = TICK_RATE
node.phase_increment = DELTA_PHI

tick_log = []
tick_counter = 0

# Advance until phase passes TARGET_PHASE
while node.phase < TARGET_PHASE:
    node.tick_forward()  # use the correct method that advances the node
    tick_counter += 1
    tick_log.append({
        "step": tick_counter,
        "phase": round(node.phase, 6)
    })

# Export result
summary = {
    "delta_phi": DELTA_PHI,
    "target_phase": TARGET_PHASE,
    "ticks_required": tick_counter
}

os.makedirs("../results", exist_ok=True)
with open("../results/trial_031_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

with open("../results/transition_log_trial031.json", "w") as f:
    json.dump(tick_log, f, indent=2)
