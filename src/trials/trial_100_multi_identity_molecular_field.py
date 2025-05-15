# trial_100_multi_identity_molecular_field.py

"""
Trial 100: Multi-Identity Molecular Field (e.g., H2)

Goal:
- Test whether two modular identities (each with their own recruiter support)
  can stabilize a shared rhythm field.
- Simulates molecular bonding via overlapping recruiter rhythm fields (e.g., H2 structure).
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
PHASE_A = 0.0
PHASE_B = 0.0  # Same phase to encourage overlap
PHASE_INCREMENT = 0.01
PHASE_TOLERANCE = 0.11
REINFORCEMENT_AMOUNT = 0.02
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
TOTAL_TICKS = 100
DROP_TICK_A = 10
DROP_TICK_B = 20
ANCESTRY_A = "H1_electron"
ANCESTRY_B = "H2_electron"

class MolecularRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase, phase_tolerance):
        super().__init__(node_id, None, target_phase, phase_tolerance)
        self.support_score = {
            ANCESTRY_A: 0.0,
            ANCESTRY_B: 0.0
        }
        self.locked_identities = set()

    def receive_echo(self, ancestry, phase, strength):
        if ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for k in self.support_score:
            self.support_score[k] = max(0.0, self.support_score[k] - REINFORCEMENT_DECAY)

    def is_supported(self, ancestry, phase):
        return (
            self.support_score[ancestry] >= REINFORCEMENT_THRESHOLD and
            abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance
        )

    def try_lock(self, ancestry, phase, identity_id):
        if identity_id in self.locked_identities:
            return True
        if self.is_supported(ancestry, phase):
            self.locked_identities.add(identity_id)
            return True
        return False

# Shared molecular field recruiters
recruiters = {
    f"M_{i}": MolecularRecruiter(
        node_id=f"M_{i}",
        target_phase=PHASE_A,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(6)
}

identity_A = ETMNode("identity_A", initial_tick=0, phase=PHASE_A)
identity_B = ETMNode("identity_B", initial_tick=0, phase=PHASE_B)

identity_A.set_ancestry(ANCESTRY_A)
identity_B.set_ancestry(ANCESTRY_B)

identity_A.phase_increment = PHASE_INCREMENT
identity_B.phase_increment = PHASE_INCREMENT

tick_log = []

# Main loop
for t in range(TOTAL_TICKS):
    if t >= DROP_TICK_A:
        identity_A.tick_forward()
    if t >= DROP_TICK_B:
        identity_B.tick_forward()

    phase_A = identity_A.phase % 1.0 if t >= DROP_TICK_A else None
    phase_B = identity_B.phase % 1.0 if t >= DROP_TICK_B else None

    if t >= DROP_TICK_A and (t - DROP_TICK_A) % 3 == 0:
        for r in recruiters.values():
            r.receive_echo(ANCESTRY_A, phase_A, REINFORCEMENT_AMOUNT)

    if t >= DROP_TICK_B and (t - DROP_TICK_B) % 3 == 0:
        for r in recruiters.values():
            r.receive_echo(ANCESTRY_B, phase_B, REINFORCEMENT_AMOUNT)

    for r in recruiters.values():
        r.decay_reinforcement()

    A_locks = sum(r.try_lock(ANCESTRY_A, phase_A, identity_A.node_id) for r in recruiters.values()) if phase_A is not None else 0
    B_locks = sum(r.try_lock(ANCESTRY_B, phase_B, identity_B.node_id) for r in recruiters.values()) if phase_B is not None else 0

    avg_support_A = sum(r.support_score[ANCESTRY_A] for r in recruiters.values()) / 6
    avg_support_B = sum(r.support_score[ANCESTRY_B] for r in recruiters.values()) / 6

    tick_log.append({
        "tick": t + 1,
        "phase_A": round(phase_A, 6) if phase_A is not None else None,
        "phase_B": round(phase_B, 6) if phase_B is not None else None,
        "A_locks": A_locks,
        "B_locks": B_locks,
        "avg_support_A": round(avg_support_A, 4),
        "avg_support_B": round(avg_support_B, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_100_summary.json"), "w") as f:
    json.dump({
        "trial": "100",
        "drop_tick_A": DROP_TICK_A,
        "drop_tick_B": DROP_TICK_B,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_A": PHASE_A,
        "phase_B": PHASE_B
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial100.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 100 complete. Results written to '../results/' folder.")
