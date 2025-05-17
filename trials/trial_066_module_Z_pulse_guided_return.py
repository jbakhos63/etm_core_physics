
# trial_066_module_Z_pulse_guided_return.py

"""
Trial 066: Pulse-Mediated Return Test

Goal:
- Reintroduce off-phase identity (+0.15) at tick 90
- Emit recruiter pulse echoes (reinforcement) at recruiter phase 0.0
- Pulses occur every 2 ticks from tick 90–100
- Test whether rhythmic pulses induce phase-lock or recruiter modulation
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
REINFORCEMENT_BASE = 0.01
REINFORCEMENT_PULSE = 0.05
ANCESTRY_N = "H2_neutron"
DROP_TICK = 20
REMOVE_TICK = 60
DRIFT_START_TICK = 61
REJOIN_TICK = 90
PULSE_START_TICK = 90
PULSE_INTERVAL = 2
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

# Initial rhythm identities
identity_P1 = ETMNode("identity_P1", initial_tick=0, phase=0.25)
identity_P2 = ETMNode("identity_P2", initial_tick=0, phase=0.25)
identity_N1 = ETMNode("identity_N1", initial_tick=0, phase=0.25)
identity_N2 = ETMNode("identity_N2", initial_tick=0, phase=0.25)

for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
    identity.set_ancestry("H2_neutron" if "N" in identity.node_id else "H1_proton")
    identity.phase_increment = DELTA_PHI

# Returnee
identity_return = ETMNode("identity_N_offset", initial_tick=0, phase=PHASE_Z + OFFSET)
identity_return.set_ancestry(ANCESTRY_N)
identity_return.phase_increment = DELTA_PHI
return_active = False

tick_log = []

for t in range(TOTAL_TICKS):
    # Initial recruiter reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo("H1_proton", PHASE_Z, REINFORCEMENT_BASE)
            rec.receive_echo("H2_neutron", PHASE_Z, REINFORCEMENT_BASE)

    # Drop initial rhythm
    if t == DROP_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.phase = PHASE_Z

    # Tick original rhythm
    if t < REMOVE_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.tick_forward()

    # Recruiter phase drift
    if t >= DRIFT_START_TICK:
        for rec in recruiters.values():
            rec.target_phase += PHASE_DRIFT

    # Reintroduce off-phase return identity
    if t == REJOIN_TICK:
        identity_return.phase = PHASE_Z + OFFSET
        return_active = True

    # Apply rhythmic recruiter pulses
    if t >= PULSE_START_TICK and (t - PULSE_START_TICK) % PULSE_INTERVAL == 0:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_N, PHASE_Z, REINFORCEMENT_PULSE)

    # Advance returnee
    if return_active:
        identity_return.tick_forward()

    tick_entry = {
        "tick": t + 1,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "identity_return_phase": round(identity_return.phase % 1.0, 6) if return_active else None
    }

    tick_log.append(tick_entry)

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_066_summary.json"), "w") as f:
    json.dump({
        "trial": "066",
        "drop_tick": DROP_TICK,
        "remove_tick": REMOVE_TICK,
        "drift_start_tick": DRIFT_START_TICK,
        "rejoin_tick": REJOIN_TICK,
        "pulse_start_tick": PULSE_START_TICK,
        "pulse_interval": PULSE_INTERVAL,
        "pulse_strength": REINFORCEMENT_PULSE,
        "phase_drift_per_tick": PHASE_DRIFT,
        "initial_offset": OFFSET,
        "phase_increment": DELTA_PHI,
        "phase_tolerance": PHASE_TOLERANCE
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial066.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 066 complete. Results written to '../results/' folder.")
