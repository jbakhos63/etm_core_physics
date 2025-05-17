# trial_108_phase_synchronized_echo_cascade.py

"""
Trial 108: Phase-Synchronized Echo Cascade

Goal:
- Test whether weak echoes from multiple ancestry tags,
  if emitted in phase synchrony, can enable modular identity return.
- Models constructive echo interference in sparse but synchronized recruiter fields.
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
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
DROP_TICK = 10
RETURN_TICK = 40
TOTAL_TICKS = 150
REINFORCEMENT_AMOUNT = 0.004  # Still weak, but synchronized
ANCESTRIES = ["S1", "S2", "S3", "S4", "S5", "S6"]

class SynchronizedRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase):
        super().__init__(node_id, None, target_phase, PHASE_TOLERANCE)
        self.support_score = {a: 0.0 for a in ANCESTRIES}
        self.locked_identity = None

    def receive_echo(self, ancestry, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for a in self.support_score:
            self.support_score[a] = max(0.0, self.support_score[a] - REINFORCEMENT_DECAY)

    def total_support(self):
        return sum(self.support_score.values())

    def is_supported(self, phase):
        return self.total_support() >= REINFORCEMENT_THRESHOLD and abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance

    def try_lock(self, phase, identity_id):
        if self.locked_identity == identity_id:
            return True
        if self.locked_identity is None and self.is_supported(phase):
            self.locked_identity = identity_id
            return True
        return False

# Recruiter group
recruiters = {
    f"G_{i}": SynchronizedRecruiter(f"G_{i}", PHASE_G) for i in range(6)
}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
identity.set_ancestry("resonance_test")
identity.phase_increment = PHASE_INCREMENT

tick_log = []
active = False

# Simulation loop
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        active = False

    if t == RETURN_TICK:
        identity.phase = PHASE_G
        active = True

    if active:
        identity.tick_forward()

    phase = identity.phase % 1.0 if active else None

    # Emit all ancestry echoes in phase synchrony every 6 ticks
    if DROP_TICK <= t < RETURN_TICK and (t - DROP_TICK) % 6 == 0:
        for ancestry in ANCESTRIES:
            for r in recruiters.values():
                r.receive_echo(ancestry, REINFORCEMENT_AMOUNT)

    for r in recruiters.values():
        r.decay_reinforcement()

    locks = sum(r.try_lock(phase, identity.node_id) for r in recruiters.values()) if active else 0
    avg_support = sum(r.total_support() for r in recruiters.values()) / 6

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6) if active else None,
        "G_locks": locks,
        "avg_total_support": round(avg_support, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_108_summary.json"), "w") as f:
    json.dump({
        "trial": "108",
        "drop_tick": DROP_TICK,
        "return_tick": RETURN_TICK,
        "reinforcement_amount_per_ancestry": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_G": PHASE_G,
        "ancestry_count": len(ANCESTRIES),
        "pattern": "synchronized echo cascade"
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial108.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 108 complete. Results written to '../results/' folder.")
