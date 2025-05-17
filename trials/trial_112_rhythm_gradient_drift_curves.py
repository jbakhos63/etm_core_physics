# trial_112_rhythm_gradient_drift_curves.py

"""
Trial 112: Rhythm Gradient Drift Curves

Goal:
- Measure modular return delay as a function of rhythm gradient strength.
- Simulates gravitational timing acceleration in ETM.
- Sweep across recruiter reinforcement levels and compare lock timing.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Base config
PHASE_G = 0.0
PHASE_INCREMENT = 0.01
PHASE_TOLERANCE = 0.11
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
DROP_TICK = 10
RETURN_TICK = 40
TOTAL_TICKS = 150
GRADIENT_STEPS = [0.005, 0.01, 0.015, 0.02, 0.025]
ANCESTRY = "gradient_drift_test"

class GradientRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase, echo_strength):
        super().__init__(node_id, None, target_phase, PHASE_TOLERANCE)
        self.echo_strength = echo_strength
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def reinforce(self):
        self.support_score[ANCESTRY] += self.echo_strength

    def decay_reinforcement(self):
        self.support_score[ANCESTRY] = max(0.0, self.support_score[ANCESTRY] - REINFORCEMENT_DECAY)

    def is_supported(self, phase):
        return self.support_score[ANCESTRY] >= REINFORCEMENT_THRESHOLD and abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance

    def try_lock(self, phase, identity_id):
        if self.locked_identity == identity_id:
            return True
        if self.locked_identity is None and self.is_supported(phase):
            self.locked_identity = identity_id
            return True
        return False

results = []

for strength in GRADIENT_STEPS:
    recruiters = {
        f"G_{i}": GradientRecruiter(f"G_{i}", PHASE_G, strength) for i in range(6)
    }

    identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
    identity.set_ancestry(ANCESTRY)
    identity.phase_increment = PHASE_INCREMENT

    tick_log = []
    active = False
    lock_tick = None

    for t in range(TOTAL_TICKS):
        if t == DROP_TICK:
            active = False
        if t == RETURN_TICK:
            identity.phase = PHASE_G
            active = True

        if active:
            identity.tick_forward()

        phase = identity.phase % 1.0 if active else None

        if DROP_TICK <= t < RETURN_TICK and (t - DROP_TICK) % 3 == 0:
            for r in recruiters.values():
                r.reinforce()

        for r in recruiters.values():
            r.decay_reinforcement()

        if active:
            G_locks = sum(r.try_lock(phase, identity.node_id) for r in recruiters.values())
        else:
            G_locks = 0

        avg_support = sum(r.support_score[ANCESTRY] for r in recruiters.values()) / 6
        tick_log.append({
            "tick": t + 1,
            "phase": round(phase, 6) if active else None,
            "G_locks": G_locks,
            "avg_support": round(avg_support, 4)
        })

        if lock_tick is None and G_locks == 6:
            lock_tick = t + 1

    results.append({
        "echo_strength": strength,
        "lock_tick": lock_tick,
        "full_log": tick_log
    })

# Save outputs
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_112_summary.json"), "w") as f:
    json.dump({
        "trial": "112",
        "drop_tick": DROP_TICK,
        "return_tick": RETURN_TICK,
        "gradient_steps": GRADIENT_STEPS,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial112.json"), "w") as f:
    json.dump(results, f, indent=2)

print("✓ Trial 112 complete. Results written to '../results/' folder.")
