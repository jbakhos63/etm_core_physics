
# trial_064_module_Z_phase_rejection_threshold.py

"""
Trial 064: Reentry Phase Rejection Threshold Test

Goal:
- Introduce returnees at tick 90 with larger phase offsets:
  +0.13, +0.14, +0.15, +0.20
- Detect rhythmic desynchronization, recruiter drift, or return identity instability
- Find ETM’s outer boundary of phase-coherent return
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
ANCESTRY_N = "H2_neutron"
DROP_TICK = 20
REMOVE_TICK = 60
DRIFT_START_TICK = 61
REJOIN_TICK = 90
TOTAL_TICKS = 100
PHASE_DRIFT = 0.0005
OFFSETS = [0.13, 0.14, 0.15, 0.20]

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

# Initial identities to seed rhythm
identity_P1 = ETMNode("identity_P1", initial_tick=0, phase=0.25)
identity_P2 = ETMNode("identity_P2", initial_tick=0, phase=0.25)
identity_N1 = ETMNode("identity_N1", initial_tick=0, phase=0.25)
identity_N2 = ETMNode("identity_N2", initial_tick=0, phase=0.25)

for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
    identity.set_ancestry("H2_neutron" if "N" in identity.node_id else "H1_proton")
    identity.phase_increment = DELTA_PHI

# Return identities with large offsets
return_identities = {}
for offset in OFFSETS:
    ident = ETMNode(f"identity_N_offset_{str(offset)}", initial_tick=0, phase=PHASE_Z + offset)
    ident.set_ancestry(ANCESTRY_N)
    ident.phase_increment = DELTA_PHI
    return_identities[offset] = ident

return_active = {offset: False for offset in OFFSETS}

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-drop reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo("H1_proton", PHASE_Z, RECRUITER_STRENGTH)
            rec.receive_echo("H2_neutron", PHASE_Z, RECRUITER_STRENGTH)

    # Drop initial identities
    if t == DROP_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.phase = PHASE_Z

    # Tick forward until removal
    if t < REMOVE_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.tick_forward()

    # Recruiter phase drift begins
    if t >= DRIFT_START_TICK:
        for rec in recruiters.values():
            rec.target_phase += PHASE_DRIFT

    # Reintroduce offset identities
    if t == REJOIN_TICK:
        for offset, identity in return_identities.items():
            identity.phase = PHASE_Z + offset
            return_active[offset] = True

    for offset, identity in return_identities.items():
        if return_active[offset]:
            identity.tick_forward()

    tick_record = {
        "tick": t + 1,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6)
    }

    for offset in OFFSETS:
        if return_active[offset]:
            tick_record[f"identity_offset_{offset}_phase"] = round(return_identities[offset].phase % 1.0, 6)

    tick_log.append(tick_record)

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_064_summary.json"), "w") as f:
    json.dump({
        "trial": "064",
        "drop_tick": DROP_TICK,
        "remove_tick": REMOVE_TICK,
        "drift_start_tick": DRIFT_START_TICK,
        "rejoin_tick": REJOIN_TICK,
        "phase_drift_per_tick": PHASE_DRIFT,
        "test_offsets": OFFSETS,
        "phase_tolerance": PHASE_TOLERANCE,
        "reinforcement_strength": RECRUITER_STRENGTH
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial064.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 064 complete. Results written to '../results/' folder.")
