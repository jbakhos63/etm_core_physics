
# trial_085_module_Z_memory_weighted_lock.py

"""
Trial 085: Memory-Weighted Lock-In with Tuned Reinforcement and Decay

Goal:
- Increase echo reinforcement strength and reduce decay rate
- Recruiters accumulate ancestry-based support and lock if sustained
- Lock-in occurs when 4+ recruiters meet support and phase criteria for 20 ticks
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
ECHO_INTERVAL = 3
REINFORCEMENT_AMOUNT = 0.02
REINFORCEMENT_DECAY = 0.0025
REINFORCEMENT_THRESHOLD = 0.1
LOCK_IN_THRESHOLD = 20
LOCK_IN_QUORUM = 4
DROP_TICK = 20
TOTAL_TICKS = 100
INTRUDER_TICK = DROP_TICK + LOCK_IN_THRESHOLD + 5
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"

# Recruiter with tunable reinforcement memory
class MemoryRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_score = {ANCESTRY_P: 0.0, ANCESTRY_N: 0.0}
        self.locked = False
        self.lock_tick = None

    def receive_echo(self, ancestry, phase, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for key in self.support_score:
            self.support_score[key] = max(0.0, self.support_score[key] - REINFORCEMENT_DECAY)

    def is_supported(self):
        return all(score >= REINFORCEMENT_THRESHOLD for score in self.support_score.values())

recruiters = {
    f"Z_{i}": MemoryRecruiter(
        node_id=f"Z_{i}",
        target_ancestry=None,
        target_phase=PHASE_Z,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(6)
}

# Identities
identity_P = ETMNode("identity_P", initial_tick=0, phase=PHASE_Z)
identity_N = ETMNode("identity_N", initial_tick=0, phase=PHASE_Z)
identity_intruder = ETMNode("identity_intruder", initial_tick=0, phase=PHASE_Z)

identity_P.set_ancestry(ANCESTRY_P)
identity_N.set_ancestry(ANCESTRY_N)
identity_intruder.set_ancestry(ANCESTRY_P)

identity_P.phase_increment = DELTA_PHI
identity_N.phase_increment = DELTA_PHI
identity_intruder.phase_increment = DELTA_PHI
intruder_active = False

# Lock tracking
lock_streak = 0
locked = False
lock_tick = None

def check_phase_match(phase, recruiter):
    return abs((phase - recruiter.target_phase) % 1.0) <= recruiter.phase_tolerance

def check_quorum(recruiters, p_phase, n_phase):
    count = 0
    for r in recruiters.values():
        if r.is_supported() and check_phase_match(p_phase, r) and check_phase_match(n_phase, r):
            count += 1
    return count

tick_log = []

for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        identity_P.phase = PHASE_Z
        identity_N.phase = PHASE_Z

    identity_P.tick_forward()
    identity_N.tick_forward()

    if t == INTRUDER_TICK:
        identity_intruder.phase = PHASE_Z
        intruder_active = True

    if intruder_active:
        identity_intruder.tick_forward()

    if t >= DROP_TICK and (t - DROP_TICK) % ECHO_INTERVAL == 0:
        for r in recruiters.values():
            r.receive_echo(ANCESTRY_P, identity_P.phase % 1.0, REINFORCEMENT_AMOUNT)
            r.receive_echo(ANCESTRY_N, identity_N.phase % 1.0, REINFORCEMENT_AMOUNT)

    for r in recruiters.values():
        r.decay_reinforcement()

    p_phase = identity_P.phase % 1.0
    n_phase = identity_N.phase % 1.0
    quorum = check_quorum(recruiters, p_phase, n_phase)

    if not locked and quorum >= LOCK_IN_QUORUM:
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
        "identity_P_phase": round(p_phase, 6),
        "identity_N_phase": round(n_phase, 6),
        "identity_intruder_phase": round(identity_intruder.phase % 1.0, 6) if intruder_active else None,
        "quorum": quorum,
        "locked": locked,
        "lock_tick": lock_tick,
        "lock_streak": lock_streak,
        "intruder_active": intruder_active,
        "recruiter_avg_support": round(sum(r.support_score[ANCESTRY_P] + r.support_score[ANCESTRY_N] for r in recruiters.values()) / 6, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_085_summary.json"), "w") as f:
    json.dump({
        "trial": "085",
        "drop_tick": DROP_TICK,
        "intruder_tick": INTRUDER_TICK,
        "echo_interval": ECHO_INTERVAL,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "lock_in_threshold": LOCK_IN_THRESHOLD,
        "lock_in_quorum": LOCK_IN_QUORUM
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial085.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 085 complete. Results written to '../results/' folder.")
