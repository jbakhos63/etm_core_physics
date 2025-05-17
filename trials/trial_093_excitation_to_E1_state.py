# trial_093_excitation_to_E1_state.py

"""
Trial 093: Excitation to E1 State

Goal:
- Confirm excitation from Module G (phase 0.0) to Module E1 (phase 0.25).
- Only Module E1 receives echo reinforcement.
- Observe whether identity leaves G and locks into E1.
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
TOTAL_TICKS = 100
DROP_TICK = 10
ANCESTRY = "orbital_electron"

class ExcitationRecruiter(RecruiterNode):
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

# Recruiters for G and E1
recruiters_G = {
    f"G_{i}": ExcitationRecruiter(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(3)
}

recruiters_E1 = {
    f"E1_{i}": ExcitationRecruiter(
        node_id=f"E1_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_E1,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(3)
}

recruiters = {**recruiters_G, **recruiters_E1}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []

# Main loop
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        identity.phase = PHASE_G

    identity.tick_forward()
    phase = identity.phase % 1.0

    # Only E1 receives reinforcement (pure excitation)
    if t >= DROP_TICK and (t - DROP_TICK) % 3 == 0:
        for r in recruiters_E1.values():
            r.receive_echo(ANCESTRY, phase, REINFORCEMENT_AMOUNT)

    for r in recruiters.values():
        r.decay_reinforcement()

    G_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_G.values())
    E1_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_E1.values())

    avg_G = sum(r.support_score[ANCESTRY] for r in recruiters_G.values()) / 3
    avg_E1 = sum(r.support_score[ANCESTRY] for r in recruiters_E1.values()) / 3

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6),
        "G_locks": G_locks,
        "E1_locks": E1_locks,
        "avg_G_support": round(avg_G, 4),
        "avg_E1_support": round(avg_E1, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_093_summary.json"), "w") as f:
    json.dump({
        "trial": "093",
        "drop_tick": DROP_TICK,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "phase_G": PHASE_G,
        "phase_E1": PHASE_E1,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial093.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 093 complete. Results written to '../results/' folder.")
