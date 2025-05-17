
# trial_045_spectral_quantization_from_phase_interval_sweep.py

"""
Trial 045: Derive Spectral Quantization by Sweeping Excitation–Return Timing Intervals

Goal:
- Begin with identity in Module G (ground state, phase 0.0)
- Simulate excitation to various higher phases (E1, E2, etc.)
- Track tick interval from excitation to return
- Derive timing-based energy levels via ETM rhythm model
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Config
PHASE_G = 0.0
EXCITED_PHASES = [0.05, 0.10, 0.15, 0.20, 0.25]  # Define multiple excited modules
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY = "H-spectrum"
TOTAL_TICKS = 100

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

# Results for each phase
spectral_results = {}

for excited_phase in EXCITED_PHASES:
    identity = ETMNode("identity_spectral", initial_tick=0, phase=PHASE_G)
    identity.phase_increment = DELTA_PHI
    identity.set_ancestry(ANCESTRY)

    # Pre-reinforce ground state recruiters
    for _ in range(6):
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    tick_log = []
    return_detected = False
    return_tick = None

    for t in range(TOTAL_TICKS):
        if t == 10:
            # Excite at tick 10 to higher phase
            identity.phase = excited_phase

        if t == 20:
            # Drop into return-ready phase (test if return occurs)
            identity.phase = PHASE_G

        identity.tick_forward()

        tick_log.append({
            "tick": t + 1,
            "phase": round(identity.phase % 1.0, 6),
            "excited_phase": excited_phase
        })

        if not return_detected and round(identity.phase % 1.0, 6) == 0.05:
            return_detected = True
            return_tick = t + 1

    spectral_results[str(excited_phase)] = {
        "excited_phase": excited_phase,
        "return_tick": return_tick,
        "tick_log": tick_log
    }

# Save files
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_045_summary.json"), "w") as f:
    json.dump(spectral_results, f, indent=2)
    print("✓ Wrote: trial_045_summary.json")

print("✓ Trial 045 complete: Spectral timing intervals recorded.")
