
# trial_113_return_timing_window_sweep.py

"""
Trial 113: Return Timing Window Sweep

Goal:
- Determine the exact range of ticks (after return) in which modular identity reformation occurs
  under fixed echo pressure.
- Maps the ETM analog of a gravitational well's return basin width.
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
REINFORCEMENT_STRENGTH = 0.020
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
DROP_TICK = 10
RETURN_SWEEP_RANGE = range(41, 61)
TOTAL_TICKS = 100
ANCESTRY = "return_window_sweep"

class SweepRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase):
        super().__init__(node_id, None, target_phase, PHASE_TOLERANCE)
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def reinforce(self):
        self.support_score[ANCESTRY] += REINFORCEMENT_STRENGTH

    def decay(self):
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

for ret_tick in RETURN_SWEEP_RANGE:
    recruiters = {
        f"G_{i}": SweepRecruiter(f"G_{i}", PHASE_G) for i in range(6)
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
            r.decay()

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

    results.append({
        "return_tick": ret_tick,
        "lock_tick": lock_tick,
        "lock_delay": None if lock_tick is None else lock_tick - ret_tick,
        "full_log": tick_log
    })

# Save outputs to ../results/
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_113_summary.json"), "w") as f:
    json.dump({
        "trial": "113",
        "drop_tick": DROP_TICK,
        "return_sweep_range": [min(RETURN_SWEEP_RANGE), max(RETURN_SWEEP_RANGE)],
        "reinforcement_strength": REINFORCEMENT_STRENGTH,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_G": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial113.json"), "w") as f:
    json.dump(results, f, indent=2)

print("✓ Trial 113 complete. Results written to '../results/' folder.")
