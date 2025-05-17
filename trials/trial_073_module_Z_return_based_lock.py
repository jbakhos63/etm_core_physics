
# trial_073_module_Z_return_based_lock.py

"""
Trial 073: Identity Return Closure and Lock Trigger

Goal:
- Drop two identities (proton + neutron) into recruiter rhythm
- A modular echo (e.g., photon-like identity) is emitted
- Returnee re-enters in phase
- If returnee aligns with recruiter + identities for 20 ticks, recruiter locks
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
ADAPT_RATE = 0.01
DROP_TICK = 20
RETURN_TICK = 50
TOTAL_TICKS = 100
LOCK_IN_THRESHOLD = 20
LOCK_IN_QUORUM = 4
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"
ANCESTRY_R = "return_echo"

# Adaptive recruiter
class AdaptiveRecruiter(RecruiterNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locked = False
        self.lock_tick = None

    def adapt(self, target, locked):
        if not self.locked and not locked:
            error = (target - self.target_phase) % 1.0
            if error > 0.5:
                error -= 1.0
            self.target_phase = (self.target_phase + ADAPT_RATE * error) % 1.0

# Recruiters
recruiters = {
    f"Z_{i}": AdaptiveRecruiter(
        node_id=f"Z_{i}",
        target_ancestry=None,
        target_phase=PHASE_Z,
        phase_tolerance=PHASE_TOLERANCE
    ) for i in range(6)
}

# Lock logic
lock_streak = 0
locked = False
lock_tick = None

def check_quorum(phases, recruiters):
    count = 0
    for r in recruiters.values():
        if all(abs((phi - r.target_phase) % 1.0) <= PHASE_TOLERANCE for phi in phases):
            count += 1
    return count

# Identities
identity_P = ETMNode("identity_P", initial_tick=0, phase=PHASE_Z)
identity_N = ETMNode("identity_N", initial_tick=0, phase=PHASE_Z)
identity_return = ETMNode("identity_return", initial_tick=0, phase=PHASE_Z)
identity_P.set_ancestry(ANCESTRY_P)
identity_N.set_ancestry(ANCESTRY_N)
identity_return.set_ancestry(ANCESTRY_R)
for i in (identity_P, identity_N, identity_return):
    i.phase_increment = DELTA_PHI

return_active = False

tick_log = []

for t in range(TOTAL_TICKS):
    # Reinforcement
    if t < DROP_TICK:
        for r in recruiters.values():
            r.receive_echo(ANCESTRY_P, PHASE_Z, REINFORCEMENT_STRENGTH)
            r.receive_echo(ANCESTRY_N, PHASE_Z, REINFORCEMENT_STRENGTH)

    if t == DROP_TICK:
        identity_P.phase = PHASE_Z
        identity_N.phase = PHASE_Z

    identity_P.tick_forward()
    identity_N.tick_forward()

    if t == RETURN_TICK:
        identity_return.phase = PHASE_Z
        return_active = True

    if return_active:
        identity_return.tick_forward()

    # Recruiter adaptation
    avg_phase = ((identity_P.phase % 1.0) + (identity_N.phase % 1.0)) / 2.0
    for r in recruiters.values():
        r.adapt(avg_phase, locked)

    # Lock check
    if not locked and return_active:
        quorum = check_quorum(
            [identity_P.phase % 1.0, identity_N.phase % 1.0, identity_return.phase % 1.0],
            recruiters
        )
        if quorum >= LOCK_IN_QUORUM:
            lock_streak += 1
            if lock_streak >= LOCK_IN_THRESHOLD:
                locked = True
                lock_tick = t + 1
                for r in recruiters.values():
                    r.locked = True
                    r.lock_tick = lock_tick
        else:
            lock_streak = 0

    tick_log.append({
        "tick": t + 1,
        "identity_P_phase": round(identity_P.phase % 1.0, 6),
        "identity_N_phase": round(identity_N.phase % 1.0, 6),
        "identity_return_phase": round(identity_return.phase % 1.0, 6) if return_active else None,
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "quorum_reached": quorum if "quorum" in locals() else 0,
        "locked": locked,
        "lock_tick": lock_tick,
        "lock_streak": lock_streak,
        "return_active": return_active
    })

# Save results
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_073_summary.json"), "w") as f:
    json.dump({
        "trial": "073",
        "drop_tick": DROP_TICK,
        "return_tick": RETURN_TICK,
        "lock_in_threshold": LOCK_IN_THRESHOLD,
        "lock_in_quorum": LOCK_IN_QUORUM,
        "phase_tolerance": PHASE_TOLERANCE
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial073.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 073 complete. Results written to '../results/' folder.")
