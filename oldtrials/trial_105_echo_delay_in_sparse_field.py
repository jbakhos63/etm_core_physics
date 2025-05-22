# trial_105_echo_delay_in_sparse_field.py

"""
Trial 105: Echo Delay in Sparse Field

Goal:
- Test whether modular identity return occurs in a recruiter field with very low echo reinforcement.
- Confirms that sparse rhythm fields delay identity reformation due to slow memory accumulation.
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
REINFORCEMENT_AMOUNT = 0.005  # Very weak
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
DROP_TICK = 10
RETURN_TICK = 40
TOTAL_TICKS = 120
ANCESTRY = "sparse_return"

class SparseRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase):
        super().__init__(node_id, None, target_phase, PHASE_TOLERANCE)
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def receive_echo(self, ancestry, phase, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for k in self.support_score:
            self.support_score[k] = max(0.0, self.support_score[k] - REINFORCEMENT_DECAY)

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

# Recruiters (G-type, sparse support)
recruiters = {
    f"G_{i}": SparseRecruiter(f"G_{i}", PHASE_G) for i in range(6)
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

    # Weak echo reinforcement
    if DROP_TICK <= t < RETURN_TICK and (t - DROP_TICK) % 3 == 0:
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

with open(os.path.join(output_dir, "trial_105_summary.json"), "w") as f:
    json.dump({
        "trial": "105",
        "drop_tick": DROP_TICK,
        "return_tick": RETURN_TICK,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_G": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial105.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 105 complete. Results written to '../results/' folder.")
