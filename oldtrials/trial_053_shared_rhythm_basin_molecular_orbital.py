
# trial_053_shared_rhythm_basin_molecular_orbital.py

"""
Trial 053: Simulate Two Identities Sharing One Orbital Rhythm Basin

Goal:
- Drop two identities into the same extended recruiter rhythm
- Allow both to reinforce and orbit simultaneously
- Detect whether a stable shared orbital rhythm forms (molecular-style identity basin)
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
ANCESTRY_A = "H1"
ANCESTRY_B = "H2"
DROP_TICK = 20
TOTAL_TICKS = 60

# Recruiters that accept both ancestry types
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=None,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Identities with distinct ancestry (to simulate two atoms)
identity_A = ETMNode("identity_A", initial_tick=0, phase=0.25)
identity_B = ETMNode("identity_B", initial_tick=0, phase=0.25)
identity_A.phase_increment = DELTA_PHI
identity_B.phase_increment = DELTA_PHI
identity_A.set_ancestry(ANCESTRY_A)
identity_B.set_ancestry(ANCESTRY_B)

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-reinforce with both identities
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_A, PHASE_G, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_B, PHASE_G, RECRUITER_STRENGTH)

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

with open(os.path.join(output_dir, "trial_053_summary.json"), "w") as f:
    json.dump({
        "trial": "053",
        "drop_tick": DROP_TICK,
        "ancestry_A": ANCESTRY_A,
        "ancestry_B": ANCESTRY_B,
        "phase_increment": DELTA_PHI
    }, f, indent=2)
    print(f"✓ Wrote: trial_053_summary.json")

with open(os.path.join(output_dir, "transition_log_trial053.json"), "w") as f:
    json.dump(tick_log, f, indent=2)
    print(f"✓ Wrote: transition_log_trial053.json")

print("✓ Trial 053 complete: Shared rhythm basin simulation recorded.")
