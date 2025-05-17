
# trial_041_repeated_photon_guided_return_cycles.py

"""
Trial 041: Simulate Multiple Photon-Guided Excitation and Return Cycles

Goal:
- Alternate identity between G (ϕ = 0.0) and E1 (ϕ = 0.20)
- Use photon rotors to reinforce recruiters at return points
- Confirm whether identity re-entrains reliably with each phase drop
- Measure phase reset, return intervals, and stability across cycles
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Configuration
PHASE_G = 0.0
PHASE_E1 = 0.20
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY = "H-cycle"
TOTAL_TICKS = 120

# Return cycle events
# Three return intervals: drop to G at ticks 17, 57, 97
DROP_TICKS = [17, 57, 97]
PHOTON_TICKS = [14, 16, 54, 56, 94, 96]

# Ground state recruiters
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Identity initialized in excited state
identity = ETMNode("identity_cycling", initial_tick=0, phase=PHASE_E1)
identity.phase_increment = DELTA_PHI
identity.set_ancestry(ANCESTRY)

tick_log = []

for t in range(TOTAL_TICKS):
    if t in PHOTON_TICKS:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    if t in DROP_TICKS:
        identity.phase = PHASE_G

    identity.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "phase": round(identity.phase % 1.0, 6),
        "recruiter_support": round(sum(r.support_score for r in recruiters.values()), 4),
        "drop_event": t in DROP_TICKS,
        "photon_event": t in PHOTON_TICKS
    })

# Save results
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_041_summary.json"), "w") as f:
    json.dump({
        "trial": "041",
        "drop_ticks": DROP_TICKS,
        "photon_ticks": PHOTON_TICKS,
        "delta_phi": DELTA_PHI,
        "phase_G": PHASE_G,
        "phase_E1": PHASE_E1
    }, f, indent=2)
    print("✓ Wrote: trial_041_summary.json")

with open(os.path.join(output_dir, "transition_log_trial041.json"), "w") as f:
    json.dump(tick_log, f, indent=2)
    print("✓ Wrote: transition_log_trial041.json")

print("✓ Trial 041 complete: Multiple photon-guided return cycles recorded.")
