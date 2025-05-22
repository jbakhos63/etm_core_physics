
# trial_038_hydrogen_ground_state_orbital.py

"""
Trial 038: Simulate Ground State Orbital (Module G) for Hydrogen in ETM

Goal:
- Create a stable recruiter basin representing the hydrogen nucleus
- Introduce a modular identity (electron) at a matched phase
- Allow the identity to tick forward within the recruiter field
- Measure timing alignment, modular persistence, and return behavior
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
DELTA_PHI = 0.01
INITIAL_PHASE = 0.0
RECRUITER_PHASE = 0.0
REINFORCE_STRENGTH = 0.01
NUM_RECRUITERS = 6
NUM_TICKS = 100
PHASE_TOLERANCE = 0.11
ANCESTRY = "H-G"

# Create circular recruiter field (simplified as evenly phased recruiters)
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=RECRUITER_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(NUM_RECRUITERS)
}

# Initialize identity in orbital phase
identity = ETMNode("identity_orbiting", initial_tick=0, phase=INITIAL_PHASE)
identity.phase_increment = DELTA_PHI
identity.tick_rate = 1.0
identity.set_ancestry(ANCESTRY)

# Reinforce the orbital basin before tick begins
for _ in range(6):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, INITIAL_PHASE, REINFORCE_STRENGTH)

# Run ticks
tick_log = []

for t in range(NUM_TICKS):
    identity.tick_forward()

    # Log status
    tick_log.append({
        "tick": t + 1,
        "phase": round(identity.phase % 1.0, 6),
        "tick_rate": identity.tick_rate
    })

# Write output
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

summary_file = os.path.join(output_dir, "trial_038_summary.json")
log_file = os.path.join(output_dir, "transition_log_trial038.json")

with open(summary_file, "w") as f:
    json.dump({
        "trial": "038",
        "ticks_simulated": NUM_TICKS,
        "recruiters": NUM_RECRUITERS,
        "initial_phase": INITIAL_PHASE,
        "delta_phi": DELTA_PHI
    }, f, indent=2)
    print(f"✓ Wrote: {summary_file}")

with open(log_file, "w") as f:
    json.dump(tick_log, f, indent=2)
    print(f"✓ Wrote: {log_file}")

print("✓ Trial 038 complete: Ground state orbital tick cycle recorded.")
