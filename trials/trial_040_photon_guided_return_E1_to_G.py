
# trial_040_photon_guided_return_E1_to_G.py

"""
Trial 040: Simulate Photon-Guided Return from Excited State (E1) to Ground State (G)

Goal:
- Begin with identity at E1 (ϕ = 0.20)
- Insert photon rotors to reinforce recruiter field at G (ϕ = 0.0)
- Drop identity into G after echo reinforcement
- Test whether modular return occurs with proper guidance
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Configuration
DELTA_PHI = 0.01
PHASE_E1 = 0.20
PHASE_G = 0.0
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
REINFORCE_TICKS = [10, 12, 14]  # Photon rotor ticks
DROP_TICK = 17
TOTAL_TICKS = 25
ANCESTRY = "H-G"

# Recruiters for ground state
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Identity begins in excited phase (E1)
identity = ETMNode("identity_returning", initial_tick=0, phase=PHASE_E1)
identity.phase_increment = DELTA_PHI
identity.set_ancestry(ANCESTRY)

tick_log = []

for t in range(TOTAL_TICKS):
    if t in REINFORCE_TICKS:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    # Drop into return phase after photon echo buildup
    if t == DROP_TICK:
        identity.phase = PHASE_G  # Reset to return-ready phase

    identity.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "phase": round(identity.phase % 1.0, 6),
        "recruiter_total_support": sum(r.support_score for r in recruiters.values())
    })

# Save results
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

summary_file = os.path.join(output_dir, "trial_040_summary.json")
log_file = os.path.join(output_dir, "transition_log_trial040.json")

with open(summary_file, "w") as f:
    json.dump({
        "trial": "040",
        "initial_phase": PHASE_E1,
        "drop_phase": PHASE_G,
        "photon_ticks": REINFORCE_TICKS,
        "drop_tick": DROP_TICK,
        "delta_phi": DELTA_PHI
    }, f, indent=2)
    print(f"✓ Wrote: {summary_file}")

with open(log_file, "w") as f:
    json.dump(tick_log, f, indent=2)
    print(f"✓ Wrote: {log_file}")

print("✓ Trial 040 complete: Photon-guided return simulation finished.")
