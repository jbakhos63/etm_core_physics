
# trial_057_module_Z_four_identity_density.py

"""
Trial 057: Module Z Nuclear Rhythm with Four Identity Saturation

Goal:
- Drop four identities (2 protons, 2 neutrons) into Module Z rhythm basin
- Monitor for natural synchronization, desync, or early signs of modular unification
- Rhythm is allowed to evolve freely; no exclusion logic imposed
"""

import os
import sys
import json

# Ensure parent directory import path is set
sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_Z = 0.0
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"
DROP_TICK = 20
TOTAL_TICKS = 120

# Create recruiters for Module Z
recruiters = {
    f"Z_{i}": RecruiterNode(
        node_id=f"Z_{i}",
        target_ancestry=None,
        target_phase=PHASE_Z,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Four identities
identity_P1 = ETMNode("identity_P1", initial_tick=0, phase=0.25)
identity_P2 = ETMNode("identity_P2", initial_tick=0, phase=0.25)
identity_N1 = ETMNode("identity_N1", initial_tick=0, phase=0.25)
identity_N2 = ETMNode("identity_N2", initial_tick=0, phase=0.25)

for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
    identity.phase_increment = DELTA_PHI

identity_P1.set_ancestry(ANCESTRY_P)
identity_P2.set_ancestry(ANCESTRY_P)
identity_N1.set_ancestry(ANCESTRY_N)
identity_N2.set_ancestry(ANCESTRY_N)

tick_log = []

for t in range(TOTAL_TICKS):
    # Reinforce recruiter basin
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_P, PHASE_Z, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_N, PHASE_Z, RECRUITER_STRENGTH)

    # Drop all identities into rhythm basin
    if t == DROP_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.phase = PHASE_Z

    # Advance phases
    identity_P1.tick_forward()
    identity_P2.tick_forward()
    identity_N1.tick_forward()
    identity_N2.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "identity_P1_phase": round(identity_P1.phase % 1.0, 6),
        "identity_P2_phase": round(identity_P2.phase % 1.0, 6),
        "identity_N1_phase": round(identity_N1.phase % 1.0, 6),
        "identity_N2_phase": round(identity_N2.phase % 1.0, 6),
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "drop_event": t == DROP_TICK
    })

# Save results to parent directory results folder
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_057_summary.json"), "w") as f:
    json.dump({
        "trial": "057",
        "drop_tick": DROP_TICK,
        "identities": ["identity_P1", "identity_P2", "identity_N1", "identity_N2"],
        "ancestry": {
            "identity_P1": ANCESTRY_P,
            "identity_P2": ANCESTRY_P,
            "identity_N1": ANCESTRY_N,
            "identity_N2": ANCESTRY_N
        },
        "phase_tolerance": PHASE_TOLERANCE,
        "reinforcement_strength": RECRUITER_STRENGTH
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial057.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 057 complete. Results written to '../results/' folder.")
