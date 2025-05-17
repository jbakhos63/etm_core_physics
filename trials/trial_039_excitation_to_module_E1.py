
# trial_039_excitation_to_module_E1.py

"""
Trial 039: Simulate Excitation from Ground State (Module G) to Excited State (Module E1)

Goal:
- Simulate a modular identity leaving Module G and entering Module E1
- Shift recruiter basin to phase = 0.20 (E1)
- Observe identity stability in displaced state
- No photon guidance yet (pure excitation by phase offset)
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
DELTA_PHI = 0.01
TICKS_HELD = 100
INITIAL_PHASE = 0.20
RECRUITER_PHASE = 0.20
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
NUM_RECRUITERS = 6
ANCESTRY = "H-E1"

# Initialize recruiters for Module E1
recruiters = {
    f"E1_{i}": RecruiterNode(
        node_id=f"E1_{i}",
        target_ancestry=ANCESTRY,
        target_phase=RECRUITER_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(NUM_RECRUITERS)
}

# Identity initialization (in excited phase)
identity = ETMNode("identity_excited", initial_tick=0, phase=INITIAL_PHASE)
identity.phase_increment = DELTA_PHI
identity.tick_rate = 1.0
identity.set_ancestry(ANCESTRY)

# Pre-reinforce the excited basin
for _ in range(6):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, INITIAL_PHASE, RECRUITER_STRENGTH)

# Run ticks
tick_log = []

for t in range(TICKS_HELD):
    identity.tick_forward()
    tick_log.append({
        "tick": t + 1,
        "phase": round(identity.phase % 1.0, 6),
        "tick_rate": identity.tick_rate
    })

# Save output
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

summary_file = os.path.join(output_dir, "trial_039_summary.json")
log_file = os.path.join(output_dir, "transition_log_trial039.json")

with open(summary_file, "w") as f:
    json.dump({
        "trial": "039",
        "ticks_simulated": TICKS_HELD,
        "recruiter_phase": RECRUITER_PHASE,
        "initial_phase": INITIAL_PHASE,
        "delta_phi": DELTA_PHI
    }, f, indent=2)
    print(f"✓ Wrote: {summary_file}")

with open(log_file, "w") as f:
    json.dump(tick_log, f, indent=2)
    print(f"✓ Wrote: {log_file}")

print("✓ Trial 039 complete: Identity behavior in Module E1 recorded.")
