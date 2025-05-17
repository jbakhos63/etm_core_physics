
# trial_083_module_Z_snap_tolerance_confirm.py

"""
Trial 083: Snap Logic Float Tolerance Confirmation

Goal:
- Confirm snap-lock behavior with float rounding margin
- Snap threshold increased to 0.035
- All other logic remains unchanged from Trial 082
- Expect snap and recruiter lock once echo proximity is reached
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
ECHO_MEMORY_THRESHOLD = 0.2
REINFORCEMENT_BASE = 0.01
ECHO_INTERVAL = 3
ECHO_OFFSET = 0.02
SNAP_THRESHOLD = 0.035  # Slightly increased from 0.03
RECRUITER_DRIFT = 0.01
DROP_TICK = 20
TOTAL_TICKS = 100
LOCK_IN_THRESHOLD = 20
LOCK_IN_QUORUM = 4
ADAPT_RATE = 0.005
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"
INTRUDER_TICK = DROP_TICK + LOCK_IN_THRESHOLD + 5

# Recruiter with float-tolerant snap logic
class TolerantSnapRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.echo_memory = {ANCESTRY_P: 0.0, ANCESTRY_N: 0.0}
        self.recent_echo = None
        self.locked = False
        self.lock_tick = None

    def receive_echo(self, ancestry, phase, strength):
        super().receive_echo(ancestry, phase, strength)
        if ancestry in self.echo_memory:
            self.echo_memory[ancestry] += strength
            self.recent_echo = phase

    def is_memory_ready(self):
        return all(mem >= ECHO_MEMORY_THRESHOLD for mem in self.echo_memory.values())

    def drift_upward(self):
        if not self.locked:
            self.target_phase = (self.target_phase + RECRUITER_DRIFT) % 1.0

    def adjust_phase(self):
        if self.locked or not self.is_memory_ready() or self.recent_echo is None:
            return
        error = abs(self.recent_echo - self.target_phase)
        snap_error = min(error, 1.0 - error)
        if snap_error <= SNAP_THRESHOLD:
            self.target_phase = self.recent_echo
            self.locked = True
        else:
            step = (self.recent_echo - self.target_phase) % 1.0
            if step > 0.5:
                step -= 1.0
            self.target_phase = (self.target_phase + ADAPT_RATE * step) % 1.0

recruiters = {
    f"Z_{i}": TolerantSnapRecruiter(
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

# Lock logic
lock_streak = 0
locked = False
lock_tick = None

def check_phase_quorum(phases, recruiters):
    return sum(
        1 for r in recruiters.values()
        if all(abs((phi - r.target_phase) % 1.0) <= PHASE_TOLERANCE for phi in phases)
    )

def check_memory_quorum(recruiters):
    return sum(1 for r in recruiters.values() if r.is_memory_ready())

tick_log = []

for t in range(TOTAL_TICKS):
    if t < DROP_TICK:
        for r in recruiters.values():
            r.receive_echo(ANCESTRY_P, PHASE_Z, REINFORCEMENT_BASE)
            r.receive_echo(ANCESTRY_N, PHASE_Z, REINFORCEMENT_BASE)

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

    if (t - DROP_TICK) % ECHO_INTERVAL == 0 and t >= DROP_TICK:
        for r in recruiters.values():
            echo_phase_P = (identity_P.phase + ECHO_OFFSET) % 1.0
            echo_phase_N = (identity_N.phase + ECHO_OFFSET) % 1.0
            r.receive_echo(ANCESTRY_P, echo_phase_P, REINFORCEMENT_BASE)
            r.receive_echo(ANCESTRY_N, echo_phase_N, REINFORCEMENT_BASE)

    for r in recruiters.values():
        r.drift_upward()
        r.adjust_phase()

    phase_quorum = check_phase_quorum(
        [identity_P.phase % 1.0, identity_N.phase % 1.0],
        recruiters
    )
    memory_quorum = check_memory_quorum(recruiters)

    if not locked and phase_quorum >= LOCK_IN_QUORUM and memory_quorum >= LOCK_IN_QUORUM:
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
        "phase_quorum": phase_quorum,
        "memory_quorum": memory_quorum,
        "locked": locked,
        "lock_tick": lock_tick,
        "lock_streak": lock_streak,
        "intruder_active": intruder_active
    })

# Save
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_083_summary.json"), "w") as f:
    json.dump({
        "trial": "083",
        "drop_tick": DROP_TICK,
        "intruder_tick": INTRUDER_TICK,
        "phase_tolerance": PHASE_TOLERANCE,
        "echo_memory_threshold": ECHO_MEMORY_THRESHOLD,
        "lock_in_threshold": LOCK_IN_THRESHOLD,
        "lock_in_quorum": LOCK_IN_QUORUM,
        "echo_offset": ECHO_OFFSET,
        "snap_threshold": SNAP_THRESHOLD,
        "drift_rate": RECRUITER_DRIFT
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial083.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 083 complete. Results written to '../results/' folder.")
