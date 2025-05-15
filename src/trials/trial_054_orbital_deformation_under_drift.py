
# trial_054_orbital_deformation_under_drift.py

"""
Trial 054: Deform Shared Orbital Rhythm Basin

Goal:
- Drop two identities into the same recruiter basin (molecular orbital)
- Apply drift (phase pressure) to recruiter rhythm over time
- Detect identity instability, rhythm desynchronization, or collapse
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_G = 0.0
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY_A = "H1"
ANCESTRY_B = "H2"
DROP_TICK = 20
DRIFT_START_TICK = 30
TOTAL_TICKS = 60

# Recruiters that drift after a set point
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=None,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Modular identities
identity_A = ETMNode("identity_A", initial_tick=0, phase=0.25)
identity_B = ETMNode("identity_B", initial_tick=0, phase=0.25)
identity_A.phase_increment = DELTA_PHI
identity_B.phase_increment = DELTA_PHI
identity_A.set_ancestry(ANCESTRY_A)
identity_B.set_ancestry(ANCESTRY_B)

tick_log = []

for t in range(TOTAL_TICKS):
    # Reinforce rhythm with both ancestries
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_A, PHASE_G, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_B, PHASE_G, RECRUITER_STRENGTH)

    # Drop both into basin
    if t == DROP_TICK:
        identity_A.phase = PHASE_G
        identity_B.phase = PHASE_G

    # Start rhythm drift after DRIFT_START_TICK
    if t >= DRIFT_START_TICK:
        for rec in recruiters.values():
            rec.target_phase += 0.0005  # slow drift per tick

    identity_A.tick_forward()
    identity_B.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "identity_A_phase": round(identity_A.phase % 1.0, 6),
        "identity_B_phase": round(identity_B.phase % 1.0, 6),
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "drop_event": t == DROP_TICK,
        "drift_active": t >= DRIFT_START_TICK
    })

# Save result
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_054_summary.json"), "w") as f:
    json.dump({
        "trial": "054",
        "drop_tick": DROP_TICK,
        "drift_start_tick": DRIFT_START_TICK,
        "drift_per_tick": 0.0005,
        "ancestry_A": ANCESTRY_A,
        "ancestry_B": ANCESTRY_B
    }, f, indent=2)
    print(f"✓ Wrote: trial_054_summary.json")

with open(os.path.join(output_dir, "transition_log_trial054.json"), "w") as f:
    json.dump(tick_log, f, indent=2)
    print(f"✓ Wrote: transition_log_trial054.json")

print("✓ Trial 054 complete: Rhythm basin deformation recorded.")
