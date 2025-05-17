
# trial_065_module_Z_drift_compensation.py

"""
Trial 065: Return Drift Compensation Test

Goal:
- Introduce one off-phase identity (+0.15 offset) at tick 90
- Gradually reduce its phase increment from 0.01 to 0.007
- Test whether it re-synchronizes with the recruiter rhythm
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_Z = 0.0
INITIAL_PHASE_INCREMENT = 0.01
FINAL_PHASE_INCREMENT = 0.007
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY_N = "H2_neutron"
DROP_TICK = 20
REMOVE_TICK = 60
DRIFT_START_TICK = 61
REJOIN_TICK = 90
TOTAL_TICKS = 100
PHASE_DRIFT = 0.0005
OFFSET = 0.15

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

# Initial identities for rhythm formation
identity_P1 = ETMNode("identity_P1", initial_tick=0, phase=0.25)
identity_P2 = ETMNode("identity_P2", initial_tick=0, phase=0.25)
identity_N1 = ETMNode("identity_N1", initial_tick=0, phase=0.25)
identity_N2 = ETMNode("identity_N2", initial_tick=0, phase=0.25)

for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
    identity.set_ancestry("H2_neutron" if "N" in identity.node_id else "H1_proton")
    identity.phase_increment = INITIAL_PHASE_INCREMENT

# Return identity
identity_return = ETMNode("identity_N_offset", initial_tick=0, phase=PHASE_Z + OFFSET)
identity_return.set_ancestry(ANCESTRY_N)
identity_return.phase_increment = INITIAL_PHASE_INCREMENT
return_active = False

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-drop recruiter reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo("H1_proton", PHASE_Z, RECRUITER_STRENGTH)
            rec.receive_echo("H2_neutron", PHASE_Z, RECRUITER_STRENGTH)

    # Drop identities
    if t == DROP_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.phase = PHASE_Z

    # Tick identities until removal
    if t < REMOVE_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.tick_forward()

    # Drift recruiter phase
    if t >= DRIFT_START_TICK:
        for rec in recruiters.values():
            rec.target_phase += PHASE_DRIFT

    # Reintroduce off-phase return identity
    if t == REJOIN_TICK:
        identity_return.phase = PHASE_Z + OFFSET
        return_active = True

    # Adjust phase increment linearly from 0.01 to 0.007
    if return_active and t >= REJOIN_TICK:
        progression = (t - REJOIN_TICK) / (TOTAL_TICKS - REJOIN_TICK)
        identity_return.phase_increment = INITIAL_PHASE_INCREMENT - progression * (INITIAL_PHASE_INCREMENT - FINAL_PHASE_INCREMENT)
        identity_return.tick_forward()

    tick_entry = {
        "tick": t + 1,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "identity_return_phase": round(identity_return.phase % 1.0, 6) if return_active else None,
        "identity_phase_increment": round(identity_return.phase_increment, 6) if return_active else None
    }

    tick_log.append(tick_entry)

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_065_summary.json"), "w") as f:
    json.dump({
        "trial": "065",
        "drop_tick": DROP_TICK,
        "remove_tick": REMOVE_TICK,
        "drift_start_tick": DRIFT_START_TICK,
        "rejoin_tick": REJOIN_TICK,
        "phase_drift_per_tick": PHASE_DRIFT,
        "initial_offset": OFFSET,
        "initial_phase_increment": INITIAL_PHASE_INCREMENT,
        "final_phase_increment": FINAL_PHASE_INCREMENT,
        "phase_tolerance": PHASE_TOLERANCE,
        "reinforcement_strength": RECRUITER_STRENGTH
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial065.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 065 complete. Results written to '../results/' folder.")
