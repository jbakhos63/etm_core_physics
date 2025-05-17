# trial_110_double_pulse_resonance.py

"""
Trial 110: Double-Pulse Resonance

Goal:
- Test whether two strong echo pulses, spaced by a modular tick rhythm,
  can enable identity return in a sparse field that otherwise fails.
- Simulates dual-pulse echo scaffolding across the return window.
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
PULSE_TICKS = [38, 40]
TOTAL_TICKS = 120
REINFORCEMENT_BASE = 0.004
PULSE_BOOST = 0.05
ANCESTRY = "double_pulse_test"

class ResonantRecruiter(RecruiterNode):
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

# Recruiters
recruiters = {
    f"G_{i}": ResonantRecruiter(f"G_{i}", PHASE_G) for i in range(6)
}

identity = ETMNode("identity", initial_tick=0, phase=PHASE_G)
identity.set_ancestry(ANCESTRY)
identity.phase_increment = PHASE_INCREMENT

tick_log = []
active = False

# Main simulation loop
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
    if DROP_TICK <= t < RETURN_TICK and (t - DROP_TICK) % 7 == 0:
        for r in recruiters.values():
            r.receive_echo(REINFORCEMENT_BASE)

    # Strong dual pulses at precise ticks
    if t in PULSE_TICKS:
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

# Save output
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_110_summary.json"), "w") as f:
    json.dump({
        "trial": "110",
        "drop_tick": DROP_TICK,
        "return_tick": RETURN_TICK,
        "pulse_ticks": PULSE_TICKS,
        "base_reinforcement": REINFORCEMENT_BASE,
        "pulse_strength": PULSE_BOOST,
        "reinforcement_decay": REINFORCEMENT_DECAY,
        "reinforcement_threshold": REINFORCEMENT_THRESHOLD,
        "phase": PHASE_G
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial110.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 110 complete. Results written to '../results/' folder.")
