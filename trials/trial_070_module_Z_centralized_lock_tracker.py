
# trial_070_module_Z_centralized_lock_tracker.py

"""
Trial 070: Centralized Lock Tracker for Modular Identity Lock-In

Goal:
- Use centralized tracker to observe phase match across all recruiter nodes
- Lock module if >= 4 recruiters are in-phase with P + N for 20 consecutive ticks
- Once locked, block late identity entry unless phase and ancestry match
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
REINFORCEMENT_STRENGTH = 0.01
DROP_TICK = 20
TOTAL_TICKS = 100
LOCK_IN_THRESHOLD = 20
LOCK_IN_QUORUM = 4
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"
INTRUDER_TICK = DROP_TICK + LOCK_IN_THRESHOLD + 5

# Recruiter module
recruiters = {
    f"Z_{i}": RecruiterNode(
        node_id=f"Z_{i}",
        target_ancestry=None,
        target_phase=PHASE_Z,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(6)
}

# Centralized lock tracker
lock_streak = 0
locked = False
lock_tick = None

def check_phase_match(identity_P, identity_N, recruiters):
    match_count = 0
    for rec in recruiters.values():
        if abs((identity_P.phase - rec.target_phase) % 1.0) <= PHASE_TOLERANCE and            abs((identity_N.phase - rec.target_phase) % 1.0) <= PHASE_TOLERANCE:
            match_count += 1
    return match_count >= LOCK_IN_QUORUM

# Identities
identity_P = ETMNode("identity_P", initial_tick=0, phase=PHASE_Z)
identity_N = ETMNode("identity_N", initial_tick=0, phase=PHASE_Z)
identity_P.set_ancestry(ANCESTRY_P)
identity_N.set_ancestry(ANCESTRY_N)
identity_P.phase_increment = DELTA_PHI
identity_N.phase_increment = DELTA_PHI

# Intruder
identity_intruder = ETMNode("identity_intruder", initial_tick=0, phase=PHASE_Z)
identity_intruder.set_ancestry(ANCESTRY_P)
identity_intruder.phase_increment = DELTA_PHI
intruder_active = False

tick_log = []

for t in range(TOTAL_TICKS):
    # Reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_P, PHASE_Z, REINFORCEMENT_STRENGTH)
            rec.receive_echo(ANCESTRY_N, PHASE_Z, REINFORCEMENT_STRENGTH)

    # Drop core identities
    if t == DROP_TICK:
        identity_P.phase = PHASE_Z
        identity_N.phase = PHASE_Z

    identity_P.tick_forward()
    identity_N.tick_forward()

    # Activate intruder after lock window
    if t == INTRUDER_TICK:
        identity_intruder.phase = PHASE_Z
        intruder_active = True

    if intruder_active:
        identity_intruder.tick_forward()

    # Lock tracker
    if not locked:
        if check_phase_match(identity_P, identity_N, recruiters):
            lock_streak += 1
            if lock_streak >= LOCK_IN_THRESHOLD:
                locked = True
                lock_tick = t + 1
        else:
            lock_streak = 0

    tick_log.append({
        "tick": t + 1,
        "identity_P_phase": round(identity_P.phase % 1.0, 6),
        "identity_N_phase": round(identity_N.phase % 1.0, 6),
        "identity_intruder_phase": round(identity_intruder.phase % 1.0, 6) if intruder_active else None,
        "locked": locked,
        "lock_tick": lock_tick,
        "lock_streak": lock_streak,
        "intruder_active": intruder_active
    })

# Save output
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_070_summary.json"), "w") as f:
    json.dump({
        "trial": "070",
        "drop_tick": DROP_TICK,
        "lock_in_threshold": LOCK_IN_THRESHOLD,
        "lock_in_quorum": LOCK_IN_QUORUM,
        "intruder_tick": INTRUDER_TICK,
        "phase_tolerance": PHASE_TOLERANCE
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial070.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 070 complete. Results written to '../results/' folder.")
