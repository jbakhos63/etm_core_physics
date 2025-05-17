# trial_099_neutrino_based_remote_return.py

"""
Trial 099: Neutrino-Based Remote Return

Goal:
- Test whether an identity can return to a recruiter basin that was not directly reinforced,
  but received a neutrino echo carrying its ancestry tag.
- This tests whether rhythm ancestry alone can seed modular return.
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
REINFORCEMENT_AMOUNT_NEUTRINO = 0.015
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
TOTAL_TICKS = 60
DROP_TICK = 10
NEUTRINO_PULSE_TICK = 30
RETURN_TICK = 40
ANCESTRY = "neutrino_test"

class NeutrinoRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def receive_neutrino_echo(self, ancestry, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for key in self.support_score:
            self.support_score[key] = max(0.0, self.support_score[key] - REINFORCEMENT_DECAY)

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

# Recruiters (G basin)
recruiters_G = {
    f"G_{i}": NeutrinoRecruiter(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(3)
}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []
active = False

# Main simulation
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        active = False  # identity dropped but inactive

    if t == NEUTRINO_PULSE_TICK:
        for r in recruiters_G.values():
            r.receive_neutrino_echo(ANCESTRY, REINFORCEMENT_AMOUNT_NEUTRINO)

    if t == RETURN_TICK:
        identity.phase = PHASE_G
        active = True

    if active:
        identity.tick_forward()

    phase = identity.phase % 1.0 if active else None

    for r in recruiters_G.values():
        r.decay_reinforcement()

    G_locks = sum(
        r.try_lock(ANCESTRY, phase, identity.node_id) if active else 0
        for r in recruiters_G.values()
    )
    avg_support = sum(r.support_score[ANCESTRY] for r in recruiters_G.values()) / 3

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6) if phase is not None else None,
        "G_locks": G_locks,
        "avg_G_support": round(avg_support, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_099_summary.json"), "w") as f:
    json.dump({
        "trial": "099",
        "drop_tick": DROP_TICK,
        "neutrino_pulse_tick": NEUTRINO_PULSE_TICK,
        "return_tick": RETURN_TICK,
        "reinforcement_amount_neutrino": REINFORCEMENT_AMOUNT_NEUTRINO,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_G": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial099.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 099 complete. Results written to '../results/' folder.")
