
# trial_060_module_Z_reinvitation_test.py

"""
Trial 060: Recruiter Reinvitation Test After Modular Rhythm Persistence

Goal:
- Drop four identities (2 protons, 2 neutrons) at tick 20 to establish rhythm
- Remove all identities at tick 60
- Apply gentle drift to recruiter phase starting at tick 61 (+0.0005 per tick)
- At tick 80, reintroduce a single identity (proton) and observe:
  - Phase-lock success
  - Rhythm pull-in
  - Or mismatch rejection
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
DRIFT_START_TICK = 61
REJOIN_TICK = 80
TOTAL_TICKS = 100
PHASE_DRIFT = 0.0005

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

# Initial identities
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

# Reintroduced identity
identity_return = ETMNode("identity_return", initial_tick=0, phase=0.25)
identity_return.set_ancestry(ANCESTRY_P)
identity_return.phase_increment = DELTA_PHI
return_active = False

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-drop reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_P, PHASE_Z, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_N, PHASE_Z, RECRUITER_STRENGTH)

    # Drop initial 4 identities
    if t == DROP_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.phase = PHASE_Z

    # Tick forward before removal
    if t < REMOVE_TICK:
        identity_P1.tick_forward()
        identity_P2.tick_forward()
        identity_N1.tick_forward()
        identity_N2.tick_forward()

    # Drift recruiter phase after drift start tick
    if t >= DRIFT_START_TICK:
        for rec in recruiters.values():
            rec.target_phase += PHASE_DRIFT

    # Reintroduce return identity
    if t == REJOIN_TICK:
        identity_return.phase = PHASE_Z
        return_active = True

    if return_active:
        identity_return.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "identity_return_phase": round(identity_return.phase % 1.0, 6) if return_active else None,
        "identity_return_active": return_active,
        "identities_removed": t == REMOVE_TICK,
        "drift_active": t >= DRIFT_START_TICK,
        "rejoin_event": t == REJOIN_TICK
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_060_summary.json"), "w") as f:
    json.dump({
        "trial": "060",
        "drop_tick": DROP_TICK,
        "remove_tick": REMOVE_TICK,
        "drift_start_tick": DRIFT_START_TICK,
        "rejoin_tick": REJOIN_TICK,
        "phase_drift_per_tick": PHASE_DRIFT,
        "rejoin_identity": "identity_return",
        "rejoin_ancestry": ANCESTRY_P,
        "initial_identities": ["identity_P1", "identity_P2", "identity_N1", "identity_N2"],
        "phase_tolerance": PHASE_TOLERANCE,
        "reinforcement_strength": RECRUITER_STRENGTH
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial060.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 060 complete. Results written to '../results/' folder.")
