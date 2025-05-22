
# trial_059_module_Z_rhythm_perturbation_test.py

"""
Trial 059: Recruiter Rhythm Perturbation After Identity Fusion

Goal:
- Drop four identities into a shared recruiter basin (Module Z)
- Allow them to stabilize rhythm (drop at tick 20)
- Remove them at tick 60
- Then perturb the recruiter target phase slightly per tick
- Observe whether the rhythm:
  - Snaps back (resonant memory)
  - Drifts (unstable)
  - Reshapes (adaptive field)

"""

import os
import sys
import json

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
REMOVE_TICK = 60
TOTAL_TICKS = 100
DRIFT_START_TICK = 61
PHASE_DRIFT = 0.0005  # per tick drift after removal

# Recruiters (Module Z)
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
    # Pre-drop reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_P, PHASE_Z, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_N, PHASE_Z, RECRUITER_STRENGTH)

    # Drop all
    if t == DROP_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.phase = PHASE_Z

    # Advance identities only before REMOVE_TICK
    if t < REMOVE_TICK:
        identity_P1.tick_forward()
        identity_P2.tick_forward()
        identity_N1.tick_forward()
        identity_N2.tick_forward()

    # Apply drift to recruiter target phase after REMOVE_TICK
    if t >= DRIFT_START_TICK:
        for rec in recruiters.values():
            rec.target_phase += PHASE_DRIFT

    tick_log.append({
        "tick": t + 1,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "identities_removed": t == REMOVE_TICK,
        "drift_active": t >= DRIFT_START_TICK
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_059_summary.json"), "w") as f:
    json.dump({
        "trial": "059",
        "drop_tick": DROP_TICK,
        "remove_tick": REMOVE_TICK,
        "drift_start_tick": DRIFT_START_TICK,
        "phase_drift_per_tick": PHASE_DRIFT,
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

with open(os.path.join(output_dir, "transition_log_trial059.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 059 complete. Results written to '../results/' folder.")
