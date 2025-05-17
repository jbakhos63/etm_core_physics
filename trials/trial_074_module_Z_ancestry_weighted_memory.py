
# trial_074_module_Z_ancestry_weighted_memory.py

"""
Trial 074: Ancestry-Weighted Field Memory Lock-In

Goal:
- Recruiter nodes accumulate ancestry-tagged echo memory over time
- Lock-in occurs if:
  1. Identities match recruiter ancestry and phase
  2. Total echo memory weight for each ancestry exceeds a threshold
- Once locked, field resists intruder entry unless ancestry + phase match
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
ECHO_MEMORY_THRESHOLD = 0.2  # Minimum total reinforcement weight to allow lock
DROP_TICK = 20
TOTAL_TICKS = 100
LOCK_IN_THRESHOLD = 20
LOCK_IN_QUORUM = 4
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"
INTRUDER_TICK = DROP_TICK + LOCK_IN_THRESHOLD + 5

# Enhanced recruiter with echo memory
class MemoryRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.echo_memory = {ANCESTRY_P: 0.0, ANCESTRY_N: 0.0}
        self.locked = False
        self.lock_tick = None

    def receive_echo(self, ancestry, phase, strength):
        super().receive_echo(ancestry, phase, strength)
        if ancestry in self.echo_memory:
            self.echo_memory[ancestry] += strength

# Initialize recruiters
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

# Lock tracker
lock_streak = 0
locked = False
lock_tick = None

def check_phase_quorum(phases, recruiters):
    count = 0
    for r in recruiters.values():
        if all(abs((phi - r.target_phase) % 1.0) <= PHASE_TOLERANCE for phi in phases):
            count += 1
    return count

def check_memory_quorum(recruiters):
    count = 0
    for r in recruiters.values():
        if all(mem >= ECHO_MEMORY_THRESHOLD for mem in r.echo_memory.values()):
            count += 1
    return count

tick_log = []

for t in range(TOTAL_TICKS):
    # Echo reinforcement
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

    # Check for combined ancestry+phase lock
    quorum = check_phase_quorum(
        [identity_P.phase % 1.0, identity_N.phase % 1.0],
        recruiters
    )
    memory_quorum = check_memory_quorum(recruiters)

    if not locked and quorum >= LOCK_IN_QUORUM and memory_quorum >= LOCK_IN_QUORUM:
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
        "memory_quorum": memory_quorum,
        "locked": locked,
        "lock_tick": lock_tick,
        "lock_streak": lock_streak,
        "intruder_active": intruder_active
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_074_summary.json"), "w") as f:
    json.dump({
        "trial": "074",
        "drop_tick": DROP_TICK,
        "intruder_tick": INTRUDER_TICK,
        "phase_tolerance": PHASE_TOLERANCE,
        "echo_memory_threshold": ECHO_MEMORY_THRESHOLD,
        "lock_in_threshold": LOCK_IN_THRESHOLD,
        "lock_in_quorum": LOCK_IN_QUORUM
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial074.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 074 complete. Results written to '../results/' folder.")
