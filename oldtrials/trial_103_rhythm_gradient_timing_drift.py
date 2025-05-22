# trial_103_rhythm_gradient_timing_drift.py

"""
Trial 103: Rhythm Gradient Timing Drift

Goal:
- Test whether a timing-based rhythm gradient (i.e., asymmetrical recruiter support)
  causes identity return to favor one field over another.
- This replaces the concept of curvature with echo pressure and rhythm bias.
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
REINFORCEMENT_LEFT = 0.02  # Stronger echo pressure
REINFORCEMENT_RIGHT = 0.015
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
TOTAL_TICKS = 100
DROP_TICK = 10
RETURN_TICK = 40
ANCESTRY = "gradient_test"

class GradientRecruiter(RecruiterNode):
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

# Recruiters on left and right
recruiters_left = {
    f"L_{i}": GradientRecruiter(f"L_{i}", PHASE_LEFT) for i in range(3)
}
recruiters_right = {
    f"R_{i}": GradientRecruiter(f"R_{i}", PHASE_RIGHT) for i in range(3)
}
recruiters = {**recruiters_left, **recruiters_right}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_LEFT)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []
active = False

# Main simulation
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        active = False

    if t == RETURN_TICK:
        identity.phase = PHASE_LEFT
        active = True

    if active:
        identity.tick_forward()

    phase = identity.phase % 1.0 if active else None

    # Reinforce left and right with different strengths
    if t >= DROP_TICK and (t - DROP_TICK) % 3 == 0:
        for r in recruiters_left.values():
            r.receive_echo(ANCESTRY, phase, REINFORCEMENT_LEFT)
        for r in recruiters_right.values():
            r.receive_echo(ANCESTRY, phase, REINFORCEMENT_RIGHT)

    for r in recruiters.values():
        r.decay_reinforcement()

    left_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_left.values()) if active else 0
    right_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_right.values()) if active else 0

    avg_left = sum(r.support_score[ANCESTRY] for r in recruiters_left.values()) / 3
    avg_right = sum(r.support_score[ANCESTRY] for r in recruiters_right.values()) / 3

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6) if active else None,
        "left_locks": left_locks,
        "right_locks": right_locks,
        "avg_left_support": round(avg_left, 4),
        "avg_right_support": round(avg_right, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_103_summary.json"), "w") as f:
    json.dump({
        "trial": "103",
        "drop_tick": DROP_TICK,
        "return_tick": RETURN_TICK,
        "reinforcement_left": REINFORCEMENT_LEFT,
        "reinforcement_right": REINFORCEMENT_RIGHT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase": PHASE_LEFT
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial103.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 103 complete. Results written to '../results/' folder.")
