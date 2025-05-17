
# trial_114_decay_rate_sweep.py

"""
Trial 114: Variable Decay Rate Sweep

Goal:
- Measure the width of the return timing window as a function of recruiter decay rate.
- Builds on Trial 113 to explore how slower or faster memory decay influences identity return duration.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Fixed configuration
PHASE_G = 0.0
PHASE_INCREMENT = 0.01
PHASE_TOLERANCE = 0.11
REINFORCEMENT_STRENGTH = 0.020
REINFORCEMENT_THRESHOLD = 0.1
DROP_TICK = 10
RETURN_SWEEP_RANGE = range(41, 61)
TOTAL_TICKS = 100
DECAY_SWEEP = [0.001, 0.002, 0.003, 0.004]
ANCESTRY = "decay_sweep_test"

class DecaySweepRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase, decay):
        super().__init__(node_id, None, target_phase, PHASE_TOLERANCE)
        self.decay = decay
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def reinforce(self):
        self.support_score[ANCESTRY] += REINFORCEMENT_STRENGTH

    def decay_reinforcement(self):
        self.support_score[ANCESTRY] = max(0.0, self.support_score[ANCESTRY] - self.decay)

    def is_supported(self, phase):
        return self.support_score[ANCESTRY] >= REINFORCEMENT_THRESHOLD and abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance

    def try_lock(self, phase, identity_id):
        if self.locked_identity == identity_id:
            return True
        if self.locked_identity is None and self.is_supported(phase):
            self.locked_identity = identity_id
            return True
        return False

full_results = []

for decay in DECAY_SWEEP:
    decay_results = {
        "decay_rate": decay,
        "return_results": []
    }

    for ret_tick in RETURN_SWEEP_RANGE:
        recruiters = {
            f"G_{i}": DecaySweepRecruiter(f"G_{i}", PHASE_G, decay) for i in range(6)
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
            if t == ret_tick:
                identity.phase = PHASE_G
                active = True

            if active:
                identity.tick_forward()

            phase = identity.phase % 1.0 if active else None

            if DROP_TICK <= t < ret_tick and (t - DROP_TICK) % 3 == 0:
                for r in recruiters.values():
                    r.reinforce()

            for r in recruiters.values():
                r.decay_reinforcement()

            G_locks = (
                sum(r.try_lock(phase, identity.node_id) for r in recruiters.values())
                if active else 0
            )

            avg_support = sum(
                r.support_score[ANCESTRY] for r in recruiters.values()
            ) / 6

            tick_log.append({
                "tick": t + 1,
                "phase": round(phase, 6) if active else None,
                "G_locks": G_locks,
                "avg_support": round(avg_support, 4)
            })

            if lock_tick is None and G_locks == 6:
                lock_tick = t + 1

        decay_results["return_results"].append({
            "return_tick": ret_tick,
            "lock_tick": lock_tick,
            "lock_delay": None if lock_tick is None else lock_tick - ret_tick,
            "full_log": tick_log
        })

    full_results.append(decay_results)

# Save outputs
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_114_summary.json"), "w") as f:
    json.dump({
        "trial": "114",
        "drop_tick": DROP_TICK,
        "return_sweep_range": [min(RETURN_SWEEP_RANGE), max(RETURN_SWEEP_RANGE)],
        "reinforcement_strength": REINFORCEMENT_STRENGTH,
        "decay_sweep": DECAY_SWEEP,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_G": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial114.json"), "w") as f:
    json.dump(full_results, f, indent=2)

print("✓ Trial 114 complete. Results written to '../results/' folder.")
