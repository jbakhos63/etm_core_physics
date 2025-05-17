
# trial_071_module_Z_adaptive_recruiter_lock_in.py

"""
Trial 071: Adaptive Recruiter Lock-In with Follower Phase

Goal:
- Recruiter nodes adjust target phase toward identity pair average
- If recruiter + identities remain phase-aligned for 20 ticks (with quorum), recruiter field locks
- After lock, test whether intruder is blocked unless ancestry/phase match
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
ADAPT_RATE = 0.01
PHASE_TOLERANCE = 0.11
REINFORCEMENT_STRENGTH = 0.01
DROP_TICK = 20
TOTAL_TICKS = 100
LOCK_IN_THRESHOLD = 20
LOCK_IN_QUORUM = 4
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"
INTRUDER_TICK = DROP_TICK + LOCK_IN_THRESHOLD + 5

# Recruiter module with adaptive phase
class AdaptiveRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locked = False
        self.streak = 0
        self.lock_tick = None

    def adapt(self, phase_target):
        # Smoothly shift toward phase target
        error = (phase_target - self.target_phase) % 1.0
        if error > 0.5:
            error -= 1.0
        self.target_phase = (self.target_phase + ADAPT_RATE * error) % 1.0

recruiters = {
    f"Z_{i}": AdaptiveRecruiter(
        node_id=f"Z_{i}",
        target_ancestry=None,
        target_phase=PHASE_Z,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Centralized lock tracker
lock_streak = 0
locked = False
lock_tick = None

def check_phase_quorum(p_phase, n_phase, recruiters):
    count = 0
    for r in recruiters.values():
        if abs((p_phase - r.target_phase) % 1.0) <= PHASE_TOLERANCE and            abs((n_phase - r.target_phase) % 1.0) <= PHASE_TOLERANCE:
            count += 1
    return count

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
        for r in recruiters.values():
            r.receive_echo(ANCESTRY_P, PHASE_Z, REINFORCEMENT_STRENGTH)
            r.receive_echo(ANCESTRY_N, PHASE_Z, REINFORCEMENT_STRENGTH)

    # Drop identities
    if t == DROP_TICK:
        identity_P.phase = PHASE_Z
        identity_N.phase = PHASE_Z

    identity_P.tick_forward()
    identity_N.tick_forward()

    # Activate intruder
    if t == INTRUDER_TICK:
        identity_intruder.phase = PHASE_Z
        intruder_active = True

    if intruder_active:
        identity_intruder.tick_forward()

    # Recruiters adapt toward identity pair
    avg_identity_phase = ((identity_P.phase % 1.0) + (identity_N.phase % 1.0)) / 2.0
    for r in recruiters.values():
        if not r.locked:
            r.adapt(avg_identity_phase)

    # Check quorum and lock
    if not locked:
        quorum = check_phase_quorum(identity_P.phase % 1.0, identity_N.phase % 1.0, recruiters)
        if quorum >= LOCK_IN_QUORUM:
            lock_streak += 1
            if lock_streak >= LOCK_IN_THRESHOLD:
                locked = True
                lock_tick = t + 1
                for r in recruiters.values():
                    r.locked = True
                    r.lock_tick = lock_tick
        else:
            lock_streak = 0

    tick_log.append({
        "tick": t + 1,
        "identity_P_phase": round(identity_P.phase % 1.0, 6),
        "identity_N_phase": round(identity_N.phase % 1.0, 6),
        "identity_intruder_phase": round(identity_intruder.phase % 1.0, 6) if intruder_active else None,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "quorum_reached": quorum,
        "locked": locked,
        "lock_tick": lock_tick,
        "lock_streak": lock_streak,
        "intruder_active": intruder_active
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_071_summary.json"), "w") as f:
    json.dump({
        "trial": "071",
        "drop_tick": DROP_TICK,
        "lock_in_threshold": LOCK_IN_THRESHOLD,
        "lock_in_quorum": LOCK_IN_QUORUM,
        "intruder_tick": INTRUDER_TICK,
        "phase_tolerance": PHASE_TOLERANCE,
        "adapt_rate": ADAPT_RATE
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial071.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 071 complete. Results written to '../results/' folder.")
