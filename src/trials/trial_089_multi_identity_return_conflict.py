# trial_089_multi_identity_return_conflict.py

"""
Trial 089: Multi-Identity Return Conflict

Goal:
- Test conflict resolution when two identities of overlapping ancestry and phase
  attempt to return into the same recruiter basin.
- Confirm exclusion logic (Pauli-style) prevents simultaneous reformation.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
PHASE_G = 0.0
PHASE_INCREMENT = 0.01
PHASE_TOLERANCE = 0.11
ECHO_INTERVAL = 3
REINFORCEMENT_AMOUNT = 0.02
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
TOTAL_TICKS = 100
DROP_TICK = 10
ANCESTRY_A = "H1_electron"
ANCESTRY_B = "H2_electron"

# Recruiter logic with ancestry-aware exclusion
class ConflictRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_score = {ANCESTRY_A: 0.0, ANCESTRY_B: 0.0}
        self.locked_identity = None

    def receive_echo(self, ancestry, phase, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for k in self.support_score:
            self.support_score[k] = max(0.0, self.support_score[k] - REINFORCEMENT_DECAY)

    def is_supported(self, ancestry, phase):
        return (self.support_score[ancestry] >= REINFORCEMENT_THRESHOLD
                and abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance)

    def try_lock(self, ancestry, phase, identity_id):
        if self.locked_identity is None and self.is_supported(ancestry, phase):
            self.locked_identity = identity_id
            return True
        elif self.locked_identity == identity_id:
            return True  # already accepted
        return False  # conflict

# Recruiters
recruiters = {
    f"R_{i}": ConflictRecruiter(
        node_id=f"R_{i}",
        target_ancestry=None,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(6)
}

# Identities A and B
identity_A = ETMNode("identity_A", initial_tick=0, phase=PHASE_G)
identity_B = ETMNode("identity_B", initial_tick=0, phase=PHASE_G)

identity_A.set_ancestry(ANCESTRY_A)
identity_B.set_ancestry(ANCESTRY_B)
identity_A.phase_increment = PHASE_INCREMENT
identity_B.phase_increment = PHASE_INCREMENT

tick_log = []

# Simulation loop
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        identity_A.phase = PHASE_G
        identity_B.phase = PHASE_G

    identity_A.tick_forward()
    identity_B.tick_forward()

    if t >= DROP_TICK and (t - DROP_TICK) % ECHO_INTERVAL == 0:
        for r in recruiters.values():
            r.receive_echo(ANCESTRY_A, identity_A.phase % 1.0, REINFORCEMENT_AMOUNT)
            r.receive_echo(ANCESTRY_B, identity_B.phase % 1.0, REINFORCEMENT_AMOUNT)

    for r in recruiters.values():
        r.decay_reinforcement()

    A_phase = identity_A.phase % 1.0
    B_phase = identity_B.phase % 1.0

    A_locks = sum(r.try_lock(ANCESTRY_A, A_phase, identity_A.node_id) for r in recruiters.values())
    B_locks = sum(r.try_lock(ANCESTRY_B, B_phase, identity_B.node_id) for r in recruiters.values())

    tick_log.append({
        "tick": t + 1,
        "A_phase": round(A_phase, 6),
        "B_phase": round(B_phase, 6),
        "A_locks": A_locks,
        "B_locks": B_locks,
        "recruiter_avg_support_A": round(sum(r.support_score[ANCESTRY_A] for r in recruiters.values()) / 6, 4),
        "recruiter_avg_support_B": round(sum(r.support_score[ANCESTRY_B] for r in recruiters.values()) / 6, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_089_summary.json"), "w") as f:
    json.dump({
        "trial": "089",
        "drop_tick": DROP_TICK,
        "echo_interval": ECHO_INTERVAL,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial089.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 089 complete. Results written to '../results/' folder.")
