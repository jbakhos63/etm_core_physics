
# trial_056_module_Z_three_identity_overlap.py

"""
Trial 056: Module Z Nuclear Rhythm with Redundant Ancestry

Goal:
- Drop three identities (P1, P2, N) into a shared recruiter basin (Module Z)
- Two identities share ancestry (H1_proton), one is distinct (H2_neutron)
- Test whether rhythm conflict, desync, or exclusion emerges naturally
- Follow ETM's rhythm-first logic, not forced exclusion assumptions
"""

import os
import sys
import json

# Add parent directory to import path for etm modules
sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
PHASE_Z = 0.0
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"
DROP_TICK = 20
TOTAL_TICKS = 100

# Recruiter field for Module Z
recruiters = {
    f"Z_{i}": RecruiterNode(
        node_id=f"Z_{i}",
        target_ancestry=None,
        target_phase=PHASE_Z,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Identities
identity_P1 = ETMNode("identity_P1", initial_tick=0, phase=0.25)
identity_P2 = ETMNode("identity_P2", initial_tick=0, phase=0.25)
identity_N = ETMNode("identity_N", initial_tick=0, phase=0.25)

for identity in (identity_P1, identity_P2, identity_N):
    identity.phase_increment = DELTA_PHI

identity_P1.set_ancestry(ANCESTRY_P)
identity_P2.set_ancestry(ANCESTRY_P)
identity_N.set_ancestry(ANCESTRY_N)

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-drop rhythm reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_P, PHASE_Z, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_N, PHASE_Z, RECRUITER_STRENGTH)

    # Drop all three into rhythm basin
    if t == DROP_TICK:
        identity_P1.phase = PHASE_Z
        identity_P2.phase = PHASE_Z
        identity_N.phase = PHASE_Z

    # Advance all identity phases
    identity_P1.tick_forward()
    identity_P2.tick_forward()
    identity_N.tick_forward()

    # Log
    tick_log.append({
        "tick": t + 1,
        "identity_P1_phase": round(identity_P1.phase % 1.0, 6),
        "identity_P2_phase": round(identity_P2.phase % 1.0, 6),
        "identity_N_phase": round(identity_N.phase % 1.0, 6),
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "drop_event": t == DROP_TICK
    })

# Save to parent-level 'results' folder
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_056_summary.json"), "w") as f:
    json.dump({
        "trial": "056",
        "drop_tick": DROP_TICK,
        "identities": ["identity_P1", "identity_P2", "identity_N"],
        "ancestry": {
            "identity_P1": ANCESTRY_P,
            "identity_P2": ANCESTRY_P,
            "identity_N": ANCESTRY_N
        },
        "phase_tolerance": PHASE_TOLERANCE,
        "reinforcement_strength": RECRUITER_STRENGTH
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial056.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 056 complete. Results written to '../results/' folder.")
