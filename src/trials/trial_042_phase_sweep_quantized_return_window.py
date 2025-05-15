
# trial_042_phase_sweep_quantized_return_window.py

"""
Trial 042: Sweep Identity Drop Timing to Resolve Quantized Return Window

Goal:
- Fix photon rotors at ground state recruiter phase (ϕ = 0.0)
- Sweep return drop ticks across a fine range
- Determine which drop ticks result in successful modular return
- Identify sharp phase-timing boundaries of return window
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
ANCESTRY = "H-sweep"
TOTAL_TICKS = 30

# Photon reinforcement ticks (before sweep)
PHOTON_TICKS = [10, 12, 14]

# Sweep drop ticks: test returns at high resolution
DROP_TICKS = list(range(15, 25))  # Sweep across ticks 15–24

# Recruiters
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Begin with identity in excited state
identity = ETMNode("identity_sweep", initial_tick=0, phase=PHASE_E1)
identity.phase_increment = DELTA_PHI
identity.set_ancestry(ANCESTRY)

tick_log = []

for t in range(TOTAL_TICKS):
    # Reinforce recruiters with photon echoes
    if t in PHOTON_TICKS:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    # Sweep phase drop into G across drop ticks
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

# Write output
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_042_summary.json"), "w") as f:
    json.dump({
        "trial": "042",
        "photon_ticks": PHOTON_TICKS,
        "drop_tick_range": DROP_TICKS,
        "delta_phi": DELTA_PHI,
        "recruiter_phase": PHASE_G
    }, f, indent=2)
    print("✓ Wrote: trial_042_summary.json")

with open(os.path.join(output_dir, "transition_log_trial042.json"), "w") as f:
    json.dump(tick_log, f, indent=2)
    print("✓ Wrote: transition_log_trial042.json")

print("✓ Trial 042 complete: Phase sweep to resolve return quantization recorded.")
