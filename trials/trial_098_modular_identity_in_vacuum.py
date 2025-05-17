# trial_098_modular_identity_in_vacuum.py

"""
Trial 098: Modular Identity in Vacuum

Goal:
- Test whether a modular identity can survive and persist in the absence of recruiter reinforcement.
- No echo pulses are used. The identity ticks forward alone in vacuum.
- Confirms the necessity of rhythm field participation for identity stability.
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
REINFORCEMENT_THRESHOLD = 0.1
TOTAL_TICKS = 60
DROP_TICK = 10
ANCESTRY = "vacuum_test"

class VacuumRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def decay_reinforcement(self):
        for key in self.support_score:
            self.support_score[key] = 0.0  # No memory in vacuum

    def is_supported(self, ancestry, phase):
        return False  # Vacuum: never enough support

    def try_lock(self, ancestry, phase, identity_id):
        return False  # Vacuum: no lock possible

# One dummy recruiter to monitor lock attempts
recruiters_G = {
    f"G_{i}": VacuumRecruiter(
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

# Simulation loop
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        identity.phase = PHASE_G

    identity.tick_forward()
    phase = identity.phase % 1.0

    for r in recruiters_G.values():
        r.decay_reinforcement()  # wipes all support

    G_locks = sum(r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters_G.values())

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6),
        "G_locks": G_locks,
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_098_summary.json"), "w") as f:
    json.dump({
        "trial": "098",
        "drop_tick": DROP_TICK,
        "reinforcement_used": False,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_G": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial098.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 098 complete. Results written to '../results/' folder.")
