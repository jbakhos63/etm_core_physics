
# trial_062_module_Z_reentry_phase_tolerance_test.py

"""
Trial 062: Reentry Phase Tolerance Threshold Test

Goal:
- After successful recruiter rhythm drift and dual reentry:
  - Introduce a third identity (neutron) at tick 90 with a phase mismatch (+0.005 offset)
- Determine if recruiter field accepts, rejects, or adjusts the off-phase returnee
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
REJOIN_TICK_P = 80
REJOIN_TICK_N = 85
REJOIN_TICK_MISMATCHED = 90
TOTAL_TICKS = 100
PHASE_DRIFT = 0.0005
PHASE_OFFSET = 0.005  # Slight mismatch

# Recruiters
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

# Reintroduced identities
identity_P_return = ETMNode("identity_P_return", initial_tick=0, phase=0.25)
identity_N_return = ETMNode("identity_N_return", initial_tick=0, phase=0.25)
identity_N_offphase = ETMNode("identity_N_offphase", initial_tick=0, phase=0.25)

identity_P_return.set_ancestry(ANCESTRY_P)
identity_N_return.set_ancestry(ANCESTRY_N)
identity_N_offphase.set_ancestry(ANCESTRY_N)

identity_P_return.phase_increment = DELTA_PHI
identity_N_return.phase_increment = DELTA_PHI
identity_N_offphase.phase_increment = DELTA_PHI

P_active = False
N_active = False
N_mismatch_active = False

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-drop reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_P, PHASE_Z, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_N, PHASE_Z, RECRUITER_STRENGTH)

    # Drop all original identities
    if t == DROP_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.phase = PHASE_Z

    # Tick original identities up to removal
    if t < REMOVE_TICK:
        identity_P1.tick_forward()
        identity_P2.tick_forward()
        identity_N1.tick_forward()
        identity_N2.tick_forward()

    # Begin recruiter phase drift
    if t >= DRIFT_START_TICK:
        for rec in recruiters.values():
            rec.target_phase += PHASE_DRIFT

    # Reintroduce on-phase proton
    if t == REJOIN_TICK_P:
        identity_P_return.phase = PHASE_Z
        P_active = True

    # Reintroduce on-phase neutron
    if t == REJOIN_TICK_N:
        identity_N_return.phase = PHASE_Z
        N_active = True

    # Reintroduce slightly off-phase neutron
    if t == REJOIN_TICK_MISMATCHED:
        identity_N_offphase.phase = PHASE_Z + PHASE_OFFSET
        N_mismatch_active = True

    if P_active:
        identity_P_return.tick_forward()
    if N_active:
        identity_N_return.tick_forward()
    if N_mismatch_active:
        identity_N_offphase.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "identity_P_return_phase": round(identity_P_return.phase % 1.0, 6) if P_active else None,
        "identity_N_return_phase": round(identity_N_return.phase % 1.0, 6) if N_active else None,
        "identity_N_offphase_phase": round(identity_N_offphase.phase % 1.0, 6) if N_mismatch_active else None,
        "P_return_active": P_active,
        "N_return_active": N_active,
        "N_offphase_active": N_mismatch_active,
        "rejoin_P_event": t == REJOIN_TICK_P,
        "rejoin_N_event": t == REJOIN_TICK_N,
        "rejoin_mismatch_event": t == REJOIN_TICK_MISMATCHED
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_062_summary.json"), "w") as f:
    json.dump({
        "trial": "062",
        "drop_tick": DROP_TICK,
        "remove_tick": REMOVE_TICK,
        "drift_start_tick": DRIFT_START_TICK,
        "rejoin_tick_proton": REJOIN_TICK_P,
        "rejoin_tick_neutron": REJOIN_TICK_N,
        "rejoin_tick_offphase": REJOIN_TICK_MISMATCHED,
        "phase_drift_per_tick": PHASE_DRIFT,
        "phase_offset": PHASE_OFFSET,
        "return_identities": ["identity_P_return", "identity_N_return", "identity_N_offphase"],
        "phase_tolerance": PHASE_TOLERANCE,
        "reinforcement_strength": RECRUITER_STRENGTH
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial062.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 062 complete. Results written to '../results/' folder.")
