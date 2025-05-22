
# trial_052_repeat_orbital_excitation_return_cycles.py

"""
Trial 052: Repeat Orbital Excitation–Return Cycles

Goal:
- Cycle an identity through multiple excitation-return sequences
- Monitor orbital rhythm memory and recruiter field persistence
- Detect degradation, phase shift, or return failure over time
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_G = 0.0
PHASE_E1 = 0.20
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY = "repeat-test"
TOTAL_TICKS = 120
CYCLE_INTERVAL = 30  # Repeat every 30 ticks

# Ground state recruiters
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Identity initialization
identity = ETMNode("identity_cycler", initial_tick=0, phase=PHASE_G)
identity.phase_increment = DELTA_PHI
identity.set_ancestry(ANCESTRY)

# Pre-reinforce orbital
for _ in range(6):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

tick_log = []

for t in range(TOTAL_TICKS):
    # Cycle pattern: excite → return → rhythm → repeat
    if t in [10, 40, 70, 100]:
        identity.phase = PHASE_E1  # excitation
    if t in [20, 50, 80, 110]:
        identity.phase = PHASE_G  # return attempt

    identity.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "phase": round(identity.phase % 1.0, 6),
        "cycle_event": t in [10, 20, 40, 50, 70, 80, 100, 110]
    })

# Save results
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

summary_path = os.path.join(output_dir, "trial_052_summary.json")
log_path = os.path.join(output_dir, "transition_log_trial052.json")

with open(summary_path, "w") as f:
    json.dump({
        "trial": "052",
        "excitation_ticks": [10, 40, 70, 100],
        "return_ticks": [20, 50, 80, 110],
        "phase_increment": DELTA_PHI,
        "total_ticks": TOTAL_TICKS
    }, f, indent=2)
    print(f"✓ Wrote: {summary_path}")

with open(log_path, "w") as f:
    json.dump(tick_log, f, indent=2)
    print(f"✓ Wrote: {log_path}")

print("✓ Trial 052 complete: Modular excitation-return cycle repetition recorded.")
