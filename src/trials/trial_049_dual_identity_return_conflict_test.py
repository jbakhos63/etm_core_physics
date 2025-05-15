
# trial_049_dual_identity_return_conflict_test.py

"""
Trial 049: Drop Two Modular Identities into Same Orbital Rhythm

Goal:
- Drop two identities (same ancestry, same phase) into same recruiter rhythm
- Observe whether both return successfully
- Detect interference, phase collision, or Pauli-style exclusion
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_G = 0.0
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY = "Pauli-test"
DROP_TICK = 20
TOTAL_TICKS = 50

# Recruiter rhythm at ground phase
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Initialize two identities
identity_A = ETMNode("identity_A", initial_tick=0, phase=0.25)
identity_B = ETMNode("identity_B", initial_tick=0, phase=0.25)
identity_A.phase_increment = DELTA_PHI
identity_B.phase_increment = DELTA_PHI
identity_A.set_ancestry(ANCESTRY)
identity_B.set_ancestry(ANCESTRY)

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-reinforce rhythm
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    # Drop both identities into return phase at the same time
    if t == DROP_TICK:
        identity_A.phase = PHASE_G
        identity_B.phase = PHASE_G

    identity_A.tick_forward()
    identity_B.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "identity_A_phase": round(identity_A.phase % 1.0, 6),
        "identity_B_phase": round(identity_B.phase % 1.0, 6),
        "recruiter_support": round(sum(r.support_score for r in recruiters.values()), 4),
        "drop_event": t == DROP_TICK
    })

# Save result
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

summary_path = os.path.join(output_dir, "trial_049_summary.json")
log_path = os.path.join(output_dir, "transition_log_trial049.json")

with open(summary_path, "w") as f:
    json.dump({
        "trial": "049",
        "drop_tick": DROP_TICK,
        "ancestry": ANCESTRY,
        "initial_phase": 0.25,
        "delta_phi": DELTA_PHI
    }, f, indent=2)
    print(f"✓ Wrote: {summary_path}")

with open(log_path, "w") as f:
    json.dump(tick_log, f, indent=2)
    print(f"✓ Wrote: {log_path}")

print("✓ Trial 049 complete: Dual identity return conflict recorded.")
