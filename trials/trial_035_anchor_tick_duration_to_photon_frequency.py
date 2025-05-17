
# trial_035_anchor_tick_duration_to_photon_frequency.py

"""
Trial 035 (Final Fixed): Anchor ETM Tick Duration to Photon Frequency

Goal:
- Simulate identity completing one full rhythm cycle (0.0 to 1.0)
- Anchor this to a real-world red photon frequency: 4.60e14 Hz
- Derive ETM tick duration in seconds (SI)
- Avoid infinite loops by using explicit tick count
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode

# Constants
PHOTON_FREQUENCY_HZ = 4.60e14
PHOTON_PERIOD_SECONDS = 1.0 / PHOTON_FREQUENCY_HZ  # ~2.1739e-15 s
DELTA_PHI = 0.01
NUM_TICKS = int(1.0 / DELTA_PHI)  # 100 ticks to reach 1.0

# Initialize identity
identity = ETMNode("photon_cycle_identity", initial_tick=0, phase=0.0)
identity.phase_increment = DELTA_PHI

tick_log = []

for t in range(NUM_TICKS):
    identity.tick_forward()
    tick_log.append({
        "tick": t + 1,
        "phase": round(identity.phase % 1.0, 6)
    })

# Compute tick duration in seconds
tick_duration_seconds = PHOTON_PERIOD_SECONDS / NUM_TICKS

# Prepare summary
summary = {
    "trial": "035",
    "photon_frequency_hz": PHOTON_FREQUENCY_HZ,
    "photon_period_seconds": PHOTON_PERIOD_SECONDS,
    "etm_ticks_per_cycle": NUM_TICKS,
    "derived_tick_duration_seconds": tick_duration_seconds
}

# Write outputs
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_035_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
    print("✓ Wrote trial_035_summary.json")

with open(os.path.join(output_dir, "transition_log_trial035.json"), "w") as f:
    json.dump(tick_log, f, indent=2)
    print("✓ Wrote transition_log_trial035.json")

print(f"✓ Trial 035 complete — {NUM_TICKS} ticks per photon cycle")
print(f"✓ Tick duration: {tick_duration_seconds:.3e} seconds")
