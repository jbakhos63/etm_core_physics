
# trial_068_module_Z_lock_in_identity.py

"""
Trial 068: Recruiter-Based Identity Lock-In Test

Goal:
- Drop two identities (proton + neutron) into recruiter basin (Module Z)
- Allow them to tick in-phase
- If both remain in rhythm for N ticks (e.g., 20), recruiter module becomes "locked"
- After lock-in, no new identity may join unless phase and ancestry match
"""

import os
import sys
import json

sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_Z = 0.0
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
REINFORCEMENT_STRENGTH = 0.01
LOCK_IN_THRESHOLD = 20
DROP_TICK = 20
TOTAL_TICKS = 100
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"

# Recruiter rhythm module
class LockableRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locked = False
        self.lock_tick = None

    def check_lock_condition(self, p_phase, n_phase, tick):
        if self.locked:
            return
        in_phase = abs((p_phase - self.target_phase) % 1.0) <= PHASE_TOLERANCE and                    abs((n_phase - self.target_phase) % 1.0) <= PHASE_TOLERANCE
        if in_phase:
            if not hasattr(self, "streak"):
                self.streak = 1
            else:
                self.streak += 1
            if self.streak >= LOCK_IN_THRESHOLD:
                self.locked = True
                self.lock_tick = tick
        else:
            self.streak = 0

recruiters = {
    f"Z_{i}": LockableRecruiter(
        node_id=f"Z_{i}",
        target_ancestry=None,
        target_phase=PHASE_Z,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(6)
}

# Identities
identity_P = ETMNode("identity_P", initial_tick=0, phase=PHASE_Z)
identity_N = ETMNode("identity_N", initial_tick=0, phase=PHASE_Z)
identity_P.set_ancestry(ANCESTRY_P)
identity_N.set_ancestry(ANCESTRY_N)
identity_P.phase_increment = DELTA_PHI
identity_N.phase_increment = DELTA_PHI

# A third returnee identity that will attempt late entry after lock-in
identity_intruder = ETMNode("identity_intruder", initial_tick=0, phase=PHASE_Z)
identity_intruder.set_ancestry(ANCESTRY_P)
identity_intruder.phase_increment = DELTA_PHI
intruder_active = False
INTRUDER_TICK = DROP_TICK + LOCK_IN_THRESHOLD + 5

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-drop reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_P, PHASE_Z, REINFORCEMENT_STRENGTH)
            rec.receive_echo(ANCESTRY_N, PHASE_Z, REINFORCEMENT_STRENGTH)

    # Drop both proton and neutron into recruiter rhythm
    if t == DROP_TICK:
        identity_P.phase = PHASE_Z
        identity_N.phase = PHASE_Z

    identity_P.tick_forward()
    identity_N.tick_forward()

    # Attempt to drop intruder after lock window
    if t == INTRUDER_TICK:
        identity_intruder.phase = PHASE_Z
        intruder_active = True

    if intruder_active:
        identity_intruder.tick_forward()

    # Check lock conditions
    for rec in recruiters.values():
        rec.check_lock_condition(identity_P.phase % 1.0, identity_N.phase % 1.0, t + 1)

    tick_log.append({
        "tick": t + 1,
        "identity_P_phase": round(identity_P.phase % 1.0, 6),
        "identity_N_phase": round(identity_N.phase % 1.0, 6),
        "identity_intruder_phase": round(identity_intruder.phase % 1.0, 6) if intruder_active else None,
        "recruiter_locked": any(rec.locked for rec in recruiters.values()),
        "lock_tick": next((rec.lock_tick for rec in recruiters.values() if rec.locked), None),
        "intruder_active": intruder_active
    })

# Save output
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_068_summary.json"), "w") as f:
    json.dump({
        "trial": "068",
        "drop_tick": DROP_TICK,
        "lock_in_threshold": LOCK_IN_THRESHOLD,
        "intruder_entry_tick": INTRUDER_TICK,
        "phase_tolerance": PHASE_TOLERANCE
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial068.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 068 complete. Results written to '../results/' folder.")
