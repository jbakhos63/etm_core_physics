# trial_104_orbital_period_and_radius_law.py

"""
Trial 104: Orbital Period and Radius Law

Goal:
- Test whether the timing rhythm of identity reformation into modular recruiters
  varies as a function of recruiter basin strength and spacing.
- Models ETM analog of Kepler's law: period squared ∝ support or rhythm spacing cubed.
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
REINFORCEMENT_AMOUNT = 0.02
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
TOTAL_TICKS = 150
DROP_TICK = 10
ANCESTRY = "orbital_test"

# Recruiter with resettable support to simulate rhythm gate openings
class OrbitalRhythmRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase, toggle_interval):
        super().__init__(node_id, None, target_phase, PHASE_TOLERANCE)
        self.toggle_interval = toggle_interval
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None
        self.active = False

    def reinforce_if_open(self, t, ancestry, phase, strength):
        self.active = (t % self.toggle_interval == 0)
        if self.active and ancestry in self.support_score:
            self.support_score[ancestry] += strength

    def decay_reinforcement(self):
        for key in self.support_score:
            self.support_score[key] = max(0.0, self.support_score[key] - REINFORCEMENT_DECAY)

    def is_supported(self, ancestry, phase):
        return self.support_score[ancestry] >= REINFORCEMENT_THRESHOLD and abs((phase - self.target_phase) % 1.0) <= self.phase_tolerance

    def try_lock(self, ancestry, phase, identity_id):
        if self.locked_identity == identity_id:
            return True
        if self.locked_identity is None and self.is_supported(ancestry, phase):
            self.locked_identity = identity_id
            return True
        return False

# Simulate 3 recruiters each with different toggle intervals
recruiters = {
    f"R1": OrbitalRhythmRecruiter("R1", PHASE_G, toggle_interval=30),
    f"R2": OrbitalRhythmRecruiter("R2", PHASE_G, toggle_interval=40),
    f"R3": OrbitalRhythmRecruiter("R3", PHASE_G, toggle_interval=50),
}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []

# Main simulation
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        identity.phase = PHASE_G

    identity.tick_forward()
    phase = identity.phase % 1.0

    for r in recruiters.values():
        r.reinforce_if_open(t, ANCESTRY, phase, REINFORCEMENT_AMOUNT)
        r.decay_reinforcement()

    locks = {r.node_id: r.try_lock(ANCESTRY, phase, identity.node_id) for r in recruiters.values()}
    supports = {r.node_id: r.support_score[ANCESTRY] for r in recruiters.values()}

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6),
        "locks": locks,
        "support": {k: round(v, 4) for k, v in supports.items()}
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_104_summary.json"), "w") as f:
    json.dump({
        "trial": "104",
        "drop_tick": DROP_TICK,
        "reinforcement_amount": REINFORCEMENT_AMOUNT,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase": PHASE_G,
        "toggle_intervals": {k: r.toggle_interval for k, r in recruiters.items()}
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial104.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 104 complete. Results written to '../results/' folder.")
