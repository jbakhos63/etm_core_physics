# trial_087_return_with_no_reinforcement.py

"""
Trial 087: Identity Return With No Reinforcement Memory

Goal:
- Confirm failed identity return when all recruiter reinforcement has decayed.
- Echoes are emitted only early on, and identity is removed for long enough that support falls below threshold.
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
ECHO_INTERVAL = 3
REINFORCEMENT_AMOUNT = 0.02
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
LOCK_IN_QUORUM = 4
TOTAL_TICKS = 120
DROP_TICK = 10
REMOVE_TICK = 30
RETURN_TICK = 100
ANCESTRY = "E1_electron"

# Recruiter logic
class MemoryRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_score = {ANCESTRY: 0.0}

    def receive_echo(self, ancestry, phase, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for key in self.support_score:
            self.support_score[key] = max(0.0, self.support_score[key] - REINFORCEMENT_DECAY)

    def is_supported(self):
        return self.support_score[ANCESTRY] >= REINFORCEMENT_THRESHOLD

# Setup
recruiters = {
    f"R_{i}": MemoryRecruiter(
        node_id=f"R_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(6)
}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []
active = True

# Main simulation
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        identity.phase = PHASE_G
        active = True
    if t == REMOVE_TICK:
        active = False
    if t == RETURN_TICK:
        identity.phase = PHASE_G
        active = True

    if active:
        identity.tick_forward()

    if active and DROP_TICK <= t < REMOVE_TICK and (t - DROP_TICK) % ECHO_INTERVAL == 0:
        for r in recruiters.values():
            r.receive_echo(ANCESTRY, identity.phase % 1.0, REINFORCEMENT_AMOUNT)

    for r in recruiters.values():
        r.decay_reinforcement()

    phase = identity.phase % 1.0 if active else None
    quorum = sum(
        1 for r in recruiters.values()
        if r.is_supported() and phase is not None and abs((phase - r.target_phase) % 1.0) <= r.phase_tolerance
    )

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6) if phase is not None else None,
        "active": active,
        "quorum": quorum,
        "recruiter_avg_support": round(sum(r.support_score[ANCESTRY] for r in recruiters.values()) / 6, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_087_summary.json"), "w") as f:
    json.dump({
        "trial": "087",
        "drop_tick": DROP_TICK,
        "remove_tick": REMOVE_TICK,
        "return_tick": RETURN_TICK,
        "echo_interval": ECHO_INTERVAL,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "lock_in_quorum": LOCK_IN_QUORUM
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial087.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 087 complete. Results written to '../results/' folder.")
