# trial_109_pulse_amplified_echo_threshold.py

"""
Trial 109: Pulse-Amplified Echo Threshold

Goal:
- Test whether a delayed but strong reinforcement pulse, applied just before identity return,
  can trigger modular identity reformation even when prior support was sub-threshold.
- Models ETM analog of photon/neutrino impact or late echo memory surge.
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
REINFORCEMENT_DECAY = 0.002
REINFORCEMENT_THRESHOLD = 0.1
DROP_TICK = 10
RETURN_TICK = 40
STRONG_PULSE_TICK = 38  # Just before return
TOTAL_TICKS = 120
REINFORCEMENT_BASE = 0.004
PULSE_BOOST = 0.05
ANCESTRY = "pulse_trigger_test"

class PulseRecruiter(RecruiterNode):
    def __init__(self, node_id, target_phase):
        super().__init__(node_id, None, target_phase, PHASE_TOLERANCE)
        self.support_score = {ANCESTRY: 0.0}
        self.locked_identity = None

    def receive_echo(self, strength):
        self.support_score[ANCESTRY] += strength

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

# Recruiter group
recruiters = {
    f"G_{i}": PulseRecruiter(f"G_{i}", PHASE_G) for i in range(6)
}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []
active = False

# Simulation loop
for t in range(TOTAL_TICKS):
    if t == DROP_TICK:
        active = False

    if t == RETURN_TICK:
        identity.phase = PHASE_G
        active = True

    if active:
        identity.tick_forward()

    phase = identity.phase % 1.0 if active else None

    # Base reinforcement every 7 ticks
    if DROP_TICK <= t < STRONG_PULSE_TICK and (t - DROP_TICK) % 7 == 0:
        for r in recruiters.values():
            r.receive_echo(REINFORCEMENT_BASE)

    # Strong pulse just before return
    if t == STRONG_PULSE_TICK:
        for r in recruiters.values():
            r.receive_echo(PULSE_BOOST)

    for r in recruiters.values():
        r.decay_reinforcement()

    G_locks = sum(r.try_lock(phase, identity.node_id) for r in recruiters.values()) if active else 0
    avg_support = sum(r.support_score[ANCESTRY] for r in recruiters.values()) / 6

    tick_log.append({
        "tick": t + 1,
        "phase": round(phase, 6) if active else None,
        "G_locks": G_locks,
        "avg_support": round(avg_support, 4)
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_109_summary.json"), "w") as f:
    json.dump({
        "trial": "109",
        "drop_tick": DROP_TICK,
        "return_tick": RETURN_TICK,
        "base_reinforcement_amount": REINFORCEMENT_BASE,
        "pulse_boost": PULSE_BOOST,
        "pulse_tick": STRONG_PULSE_TICK,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase_G": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial109.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 109 complete. Results written to '../results/' folder.")
