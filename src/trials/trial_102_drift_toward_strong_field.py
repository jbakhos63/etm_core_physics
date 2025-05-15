# trial_102_drift_toward_strong_field.py

"""
Trial 102: Drift Toward Strong Field

Goal:
- Test whether an identity placed between two recruiter fields will naturally
  drift toward the one with stronger recruiter support.
- Simulates timing-based gravitational pull from a denser rhythm field.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
PHASE_LEFT = 0.0
PHASE_RIGHT = 0.0
PHASE_INCREMENT = 0.01
PHASE_TOLERANCE = 0.11
REINFORCEMENT_LEFT = 0.02
REINFORCEMENT_RIGHT = 0.01  # Weaker field
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
TOTAL_TICKS = 100
DROP_TICK = 10
ANCESTRY = "graviton_test"

class DriftRecruiter(RecruiterNode):
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

# Two recruiter fields: left (strong), right (weak)
recruiters_left = {
    f"L_{i}": DriftRecruiter(f"L_{i}", PHASE_LEFT) for i in range(3)
}
recruiters_right = {
    f"R_{i}": DriftRecruiter(f"R_{i}", PHASE_RIGHT) for i in range(3)
}
recruiters = {**recruiters_left, **recruiters_right}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_LEFT)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []

# Simulation loop
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        identity.phase = PHASE_LEFT

    identity.tick_forward()
    phase = identity.phase % 1.0

    # Echoes reinforce both fields at different strengths
    if (t - DROP_TICK) % 3 == 0 and t >= DROP_TICK:
        for r in recruiters_left.values():
            r.receive_echo(ANCESTRY, phase, REINFORCEMENT_LEFT)
        for r in recruiters_right.values():
            r.receive_echo(ANCESTRY, phase, REINFORCEMENT_RIGHT)

    for r in recruiters.values():
        r.decay_reinforcement()

    L_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_left.values())
    R_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_right.values())

    avg_L = sum(r.support_score[ANCESTRY] for r in recruiters_left.values()) / 3
    avg_R = sum(r.support_score[ANCESTRY] for r in recruiters_right.values()) / 3

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6),
        "left_locks": L_locks,
        "right_locks": R_locks,
        "avg_left_support": round(avg_L, 4),
        "avg_right_support": round(avg_R, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_102_summary.json"), "w") as f:
    json.dump({
        "trial": "102",
        "drop_tick": DROP_TICK,
        "reinforcement_left": REINFORCEMENT_LEFT,
        "reinforcement_right": REINFORCEMENT_RIGHT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase": PHASE_LEFT
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial102.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 102 complete. Results written to '../results/' folder.")
