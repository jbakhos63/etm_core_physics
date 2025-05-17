
# trial_050_distinct_identities_with_observer_disruption.py

"""
Trial 050: Distinct Modular Identities with Mid-Orbit Disruption

Goal:
- Drop two modular identities with different ancestry into same orbital rhythm
- Confirm initial coexistence (simulated opposite spin)
- Introduce mid-orbit echo spike (simulated observation/disruption)
- Detect divergence, ejection, or reactive identity reshaping
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
ANCESTRY_A = "opposite-A"
ANCESTRY_B = "opposite-B"
DROP_TICK = 20
DISRUPT_TICK = 25
TOTAL_TICKS = 50

# Recruiters at ground phase
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=None,  # Accept all ancestries
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Initialize identities with distinct ancestry
identity_A = ETMNode("identity_A", initial_tick=0, phase=0.25)
identity_B = ETMNode("identity_B", initial_tick=0, phase=0.25)
identity_A.phase_increment = DELTA_PHI
identity_B.phase_increment = DELTA_PHI
identity_A.set_ancestry(ANCESTRY_A)
identity_B.set_ancestry(ANCESTRY_B)

tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-reinforce rhythm field
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_A, PHASE_G, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_B, PHASE_G, RECRUITER_STRENGTH)

    # Drop both identities into return phase
    if t == DROP_TICK:
        identity_A.phase = PHASE_G
        identity_B.phase = PHASE_G

    # Inject disruptive echo at midpoint
    if t == DISRUPT_TICK:
        for rec in recruiters.values():
            rec.receive_echo("observer-pulse", PHASE_G, 0.10)

    identity_A.tick_forward()
    identity_B.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "identity_A_phase": round(identity_A.phase % 1.0, 6),
        "identity_B_phase": round(identity_B.phase % 1.0, 6),
        "recruiter_support": round(sum(r.support_score for r in recruiters.values()), 4),
        "drop_event": t == DROP_TICK,
        "disruption_event": t == DISRUPT_TICK
    })

# Save
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_050_summary.json"), "w") as f:
    json.dump({
        "trial": "050",
        "drop_tick": DROP_TICK,
        "disruption_tick": DISRUPT_TICK,
        "ancestry_A": ANCESTRY_A,
        "ancestry_B": ANCESTRY_B
    }, f, indent=2)
    print("✓ Wrote: trial_050_summary.json")

with open(os.path.join(output_dir, "transition_log_trial050.json"), "w") as f:
    json.dump(tick_log, f, indent=2)
    print("✓ Wrote: transition_log_trial050.json")

print("✓ Trial 050 complete: Dual identity return with disruption recorded.")
