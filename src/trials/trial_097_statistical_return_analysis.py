# trial_097_statistical_return_analysis.py

"""
Trial 097: Statistical Return Analysis

Goal:
- Sweep tick intervals surrounding Δt = 36 (from tick 44 to 48)
- Identify sensitivity and tolerance of modular return to timing offset
- Measure width and sharpness of the return window
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
PHASE_G = 0.0
PHASE_E1 = 0.25
PHASE_INCREMENT = 0.01
PHASE_TOLERANCE = 0.11
REINFORCEMENT_AMOUNT = 0.02
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
DROP_TICK = 10
RETURN_ATTEMPTS = [44, 45, 46, 47, 48]
TOTAL_TICKS = 60
ANCESTRY = "orbital_electron"

class ReturnWindowRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def receive_echo(self, ancestry, phase, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for key in self.support_score:
            self.support_score[key] = max(0.0, self.support_score[key] - REINFORCEMENT_DECAY)

    def is_supported(self, ancestry, phase):
        return self.support_score[ancestry] >= REINFORCEMENT_THRESHOLD and abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance

    def try_lock(self, ancestry, phase, identity_id):
        if self.locked_identity is None and self.is_supported(ancestry, phase):
            self.locked_identity = identity_id
            return True
        elif self.locked_identity == identity_id:
            return True
        return False

# Set up recruiters
recruiters_G = {
    f"G_{i}": ReturnWindowRecruiter(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(3)
}

# Track each return trial separately
results = []

# Sweep return intervals
for attempt_tick in RETURN_ATTEMPTS:
    identity = ETMNode("identity", initial_tick=0, phase=PHASE_E1)
    identity.set_ancestry(ANCESTRY)
    identity.phase_increment = PHASE_INCREMENT

    # Reset recruiters each sweep
    for r in recruiters_G.values():
        r.support_score = {ANCESTRY: 0.0}
        r.locked_identity = None

    log = []
    for t in range(TOTAL_TICKS):
        if t == DROP_TICK:
            identity.phase = PHASE_E1

        identity.tick_forward()
        phase = identity.phase % 1.0

        if t >= DROP_TICK and (t - DROP_TICK) % 3 == 0:
            for r in recruiters_G.values():
                r.receive_echo(ANCESTRY, phase, REINFORCEMENT_AMOUNT)

        for r in recruiters_G.values():
            r.decay_reinforcement()

        G_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_G.values())
        avg_support = sum(r.support_score[ANCESTRY] for r in recruiters_G.values()) / 3

        log.append({
            "tick": t + 1,
            "phase": round(phase, 6),
            "G_locks": G_locks,
            "avg_G_support": round(avg_support, 4)
        })

    results.append({
        "return_attempt_tick": attempt_tick,
        "drop_tick": DROP_TICK,
        "lock_success": any(entry["G_locks"] >= 3 for entry in log),
        "full_log": log
    })

# Save summary
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_097_summary.json"), "w") as f:
    json.dump({
        "trial": "097",
        "drop_tick": DROP_TICK,
        "attempts": RETURN_ATTEMPTS,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_G": PHASE_G,
        "phase_E1": PHASE_E1
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial097.json"), "w") as f:
    json.dump(results, f, indent=2)

print("✓ Trial 097 complete. Results written to '../results/' folder.")
