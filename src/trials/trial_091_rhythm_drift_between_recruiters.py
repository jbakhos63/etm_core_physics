# trial_091_rhythm_drift_between_recruiters.py

"""
Trial 091: Rhythm Drift Between Recruiters

Goal:
- Test whether an identity can naturally drift from one recruiter field to another
  without reinforcement in the new zone.
- Reinforce only the left recruiter basin, then observe if identity transitions
  or remains locked when a second field exists.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
PHASE_LEFT = 0.0
PHASE_RIGHT = 0.25
PHASE_INCREMENT = 0.01
PHASE_TOLERANCE = 0.11
REINFORCEMENT_AMOUNT = 0.02
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
TOTAL_TICKS = 100
DROP_TICK = 10
ANCESTRY = "drifter_electron"

# Recruiter field with identity locking
class PassiveDriftRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def receive_echo(self, ancestry, phase, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for k in self.support_score:
            self.support_score[k] = max(0.0, self.support_score[k] - REINFORCEMENT_DECAY)

    def is_supported(self, ancestry, phase):
        return (self.support_score[ancestry] >= REINFORCEMENT_THRESHOLD and
                abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance)

    def try_lock(self, ancestry, phase, identity_id):
        if self.locked_identity is None and self.is_supported(ancestry, phase):
            self.locked_identity = identity_id
            return True
        elif self.locked_identity == identity_id:
            return True
        return False

# Left and right recruiters
recruiters_left = {
    f"L_{i}": PassiveDriftRecruiter(
        node_id=f"L_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_LEFT,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(3)
}

recruiters_right = {
    f"R_{i}": PassiveDriftRecruiter(
        node_id=f"R_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_RIGHT,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(3)
}

recruiters = {**recruiters_left, **recruiters_right}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_LEFT)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []

# Main simulation
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        identity.phase = PHASE_LEFT

    identity.tick_forward()
    phase = identity.phase % 1.0

    # Only reinforce the left side throughout
    if t >= DROP_TICK and (t - DROP_TICK) % 3 == 0:
        for r in recruiters_left.values():
            r.receive_echo(ANCESTRY, phase, REINFORCEMENT_AMOUNT)

    for r in recruiters.values():
        r.decay_reinforcement()

    left_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_left.values())
    right_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_right.values())

    avg_left = sum(r.support_score[ANCESTRY] for r in recruiters_left.values()) / 3
    avg_right = sum(r.support_score[ANCESTRY] for r in recruiters_right.values()) / 3

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6),
        "left_locks": left_locks,
        "right_locks": right_locks,
        "avg_left_support": round(avg_left, 4),
        "avg_right_support": round(avg_right, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_091_summary.json"), "w") as f:
    json.dump({
        "trial": "091",
        "drop_tick": DROP_TICK,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "left_phase": PHASE_LEFT,
        "right_phase": PHASE_RIGHT,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial091.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 091 complete. Results written to '../results/' folder.")
