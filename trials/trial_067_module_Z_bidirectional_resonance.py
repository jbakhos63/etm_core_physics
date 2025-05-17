
# trial_067_module_Z_bidirectional_resonance.py

"""
Trial 067: Bidirectional Resonance Synchronization Test

Goal:
- Reintroduce off-phase identity at tick 90 (+0.15)
- Recruiter emits rhythmic pulses (every 2 ticks)
- Returnee sends echo pulses back (every 3 ticks)
- Test for mutual timing reinforcement and phase convergence
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
RECRUITER_BASE = 0.01
RECRUITER_PULSE = 0.05
RETURN_ECHO = 0.05
ANCESTRY_N = "H2_neutron"
DROP_TICK = 20
REMOVE_TICK = 60
DRIFT_START_TICK = 61
REJOIN_TICK = 90
PULSE_INTERVAL_RECRUITER = 2
PULSE_INTERVAL_RETURN = 3
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
    # Initial reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo("H1_proton", PHASE_Z, RECRUITER_BASE)
            rec.receive_echo("H2_neutron", PHASE_Z, RECRUITER_BASE)

    # Drop core identity rhythm
    if t == DROP_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.phase = PHASE_Z

    # Tick forward initial identity rhythm
    if t < REMOVE_TICK:
        for identity in (identity_P1, identity_P2, identity_N1, identity_N2):
            identity.tick_forward()

    # Recruiter drift
    if t >= DRIFT_START_TICK:
        for rec in recruiters.values():
            rec.target_phase += PHASE_DRIFT

    # Recruiter rhythmic pulses
    if t >= REJOIN_TICK and (t - REJOIN_TICK) % PULSE_INTERVAL_RECRUITER == 0:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_N, PHASE_Z, RECRUITER_PULSE)

    # Reintroduce returnee
    if t == REJOIN_TICK:
        identity_return.phase = PHASE_Z + OFFSET
        return_active = True

    if return_active:
        identity_return.tick_forward()
        if (t - REJOIN_TICK) % PULSE_INTERVAL_RETURN == 0:
            for rec in recruiters.values():
                rec.receive_echo(ANCESTRY_N, identity_return.phase % 1.0, RETURN_ECHO)

    tick_log.append({
        "tick": t + 1,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "identity_return_phase": round(identity_return.phase % 1.0, 6) if return_active else None
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_067_summary.json"), "w") as f:
    json.dump({
        "trial": "067",
        "drop_tick": DROP_TICK,
        "remove_tick": REMOVE_TICK,
        "drift_start_tick": DRIFT_START_TICK,
        "rejoin_tick": REJOIN_TICK,
        "recruiter_pulse_interval": PULSE_INTERVAL_RECRUITER,
        "return_echo_interval": PULSE_INTERVAL_RETURN,
        "recruiter_pulse_strength": RECRUITER_PULSE,
        "return_echo_strength": RETURN_ECHO,
        "phase_drift_per_tick": PHASE_DRIFT,
        "initial_offset": OFFSET,
        "phase_increment": DELTA_PHI,
        "phase_tolerance": PHASE_TOLERANCE
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial067.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 067 complete. Results written to '../results/' folder.")
