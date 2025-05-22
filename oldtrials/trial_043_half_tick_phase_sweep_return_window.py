
# trial_043_half_tick_phase_sweep_return_window.py

"""
Trial 043: Fractional-Tick Sweep to Resolve Fine Return Quantization

Goal:
- Drop identity into G phase at sub-tick intervals (e.g., 15.0, 15.5, 16.0, ...)
- Fixed photon echo reinforcement at standard intervals
- Identify narrow return window boundaries that define Planck-scale timing structure
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Config
PHASE_E1 = 0.20
PHASE_G = 0.00
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY = "H-043"
PHOTON_TICKS = [10, 12, 14]
SWEEP_START = 15.0
SWEEP_END = 17.0
SWEEP_STEP = 0.5

# Recruiters at ground state
recruiters = {
    f"G_{i}": RecruiterNode(
        node_id=f"G_{i}",
        target_ancestry=ANCESTRY,
        target_phase=PHASE_G,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Generate sweep ticks
drop_ticks = [round(SWEEP_START + i * SWEEP_STEP, 1) for i in range(int((SWEEP_END - SWEEP_START) / SWEEP_STEP) + 1)]

# Identity starts in excited phase
identity = ETMNode("identity_fractional", initial_tick=0, phase=PHASE_E1)
identity.phase_increment = DELTA_PHI
identity.set_ancestry(ANCESTRY)

tick_log = []

TICKS_TOTAL = 30
for t in range(TICKS_TOTAL * 2):  # double resolution
    tick_exact = t / 2.0

    if tick_exact in PHOTON_TICKS:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    if tick_exact in drop_ticks:
        identity.phase = PHASE_G

    identity.tick_forward()

    tick_log.append({
        "tick": tick_exact,
        "phase": round(identity.phase % 1.0, 6),
        "recruiter_support": round(sum(r.support_score for r in recruiters.values()), 4),
        "drop_event": tick_exact in drop_ticks,
        "photon_event": tick_exact in PHOTON_TICKS
    })

# Save
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_043_summary.json"), "w") as f:
    json.dump({
        "trial": "043",
        "photon_ticks": PHOTON_TICKS,
        "drop_ticks": drop_ticks,
        "sweep_step": SWEEP_STEP,
        "delta_phi": DELTA_PHI
    }, f, indent=2)
    print("✓ Wrote: trial_043_summary.json")

with open(os.path.join(output_dir, "transition_log_trial043.json"), "w") as f:
    json.dump(tick_log, f, indent=2)
    print("✓ Wrote: transition_log_trial043.json")

print("✓ Trial 043 complete: Half-tick sweep to resolve return quantization window recorded.")
