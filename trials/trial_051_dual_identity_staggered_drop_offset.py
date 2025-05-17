
# trial_051_dual_identity_staggered_drop_offset.py

"""
Trial 051: Vary Drop Timing Offset Between Two Identities

Goal:
- Drop two identities (same ancestry) into the same recruiter field with timing offset
- Observe whether staggered return timing triggers phase interference, exclusion, or absorption
- Detect rhythm pressure caused by near-identical modular return
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
ANCESTRY = "timing-test"
DROP_TICK_A = 20
DROP_TICK_B = 22
TOTAL_TICKS = 60

# Recruiter rhythm
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Initialize two identities with same ancestry
identity_A = ETMNode("identity_A", initial_tick=0, phase=0.25)
identity_B = ETMNode("identity_B", initial_tick=0, phase=0.25)
identity_A.phase_increment = DELTA_PHI
identity_B.phase_increment = DELTA_PHI
identity_A.set_ancestry(ANCESTRY)
identity_B.set_ancestry(ANCESTRY)

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-reinforce rhythm
    if t < DROP_TICK_A:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    # Drop A early, B late
    if t == DROP_TICK_A:
        identity_A.phase = PHASE_G
    if t == DROP_TICK_B:
        identity_B.phase = PHASE_G

    identity_A.tick_forward()
    identity_B.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "identity_A_phase": round(identity_A.phase % 1.0, 6),
        "identity_B_phase": round(identity_B.phase % 1.0, 6),
        "recruiter_support": round(sum(r.support_score for r in recruiters.values()), 4),
        "drop_event_A": t == DROP_TICK_A,
        "drop_event_B": t == DROP_TICK_B
    })

# Save result
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_051_summary.json"), "w") as f:
    json.dump({
        "trial": "051",
        "drop_tick_A": DROP_TICK_A,
        "drop_tick_B": DROP_TICK_B,
        "ancestry": ANCESTRY
    }, f, indent=2)
    print(f"✓ Wrote: trial_051_summary.json")

with open(os.path.join(output_dir, "transition_log_trial051.json"), "w") as f:
    json.dump(tick_log, f, indent=2)
    print(f"✓ Wrote: transition_log_trial051.json")

print("✓ Trial 051 complete: Dual identity staggered return recorded.")
