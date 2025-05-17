# trial_106_staggered_echo_sparse_field.py

"""
Trial 106: Staggered Echo Support in Sparse Field

Goal:
- Test whether intermittent echo reinforcement in a sparse rhythm environment
  can eventually lead to modular identity return.
- Confirms if long-delay return is possible through slow memory buildup.
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
REINFORCEMENT_AMOUNT = 0.01  # Slightly higher than Trial 105
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
DROP_TICK = 10
RETURN_TICK = 40
TOTAL_TICKS = 150
ANCESTRY = "staggered_sparse_return"

class StaggeredRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase):
        super().__init__(node_id, None, target_phase, PHASE_TOLERANCE)
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def receive_echo(self, ancestry, phase, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for key in self.support_score:
            self.support_score[key] = max(0.0, self.support_score[key] - REINFORCEMENT_DECAY)

    def is_supported(self, ancestry, phase):
        return (
            self.support_score[ancestry] >= REINFORCEMENT_THRESHOLD and
            abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance
        )

    def try_lock(self, ancestry, phase, identity_id):
        if self.locked_identity == identity_id:
            return True
        if self.locked_identity is None and self.is_supported(ancestry, phase):
            self.locked_identity = identity_id
            return True
        return False

# Recruiter field (6 nodes)
recruiters = {
    f"G_{i}": StaggeredRecruiter(f"G_{i}", PHASE_G) for i in range(6)
}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []
active = False

# Simulation loop
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        active = False  # Identity removed

    if t == RETURN_TICK:
        identity.phase = PHASE_G
        active = True  # Identity returns

    if active:
        identity.tick_forward()

    phase = identity.phase % 1.0 if active else None

    # Intermittent sparse reinforcement: echo every 6 ticks
    if DROP_TICK <= t < RETURN_TICK and (t - DROP_TICK) % 6 == 0:
        for r in recruiters.values():
            r.receive_echo(ANCESTRY, phase, REINFORCEMENT_AMOUNT)

    for r in recruiters.values():
        r.decay_reinforcement()

    G_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters.values()) if active else 0
    avg_support = sum(r.support_score[ANCESTRY] for r in recruiters.values()) / 6

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6) if active else None,
        "G_locks": G_locks,
        "avg_G_support": round(avg_support, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_106_summary.json"), "w") as f:
    json.dump({
        "trial": "106",
        "drop_tick": DROP_TICK,
        "return_tick": RETURN_TICK,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "reinforcement_pattern": "echo every 6 ticks",
        "phase_G": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial106.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 106 complete. Results written to '../results/' folder.")
