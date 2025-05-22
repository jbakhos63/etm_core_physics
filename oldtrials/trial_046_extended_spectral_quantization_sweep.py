
# trial_046_extended_spectral_quantization_sweep.py

"""
Trial 046: Extend Spectral Quantization Sweep with Higher Orbital Phases

Goal:
- Excite identity to phases beyond E1: [0.30, 0.35, 0.40, 0.45, 0.50]
- Track return behavior and tick cycle timing
- Continue building the ETM orbital spectral energy ladder
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Config
PHASE_G = 0.0
EXCITED_PHASES = [0.30, 0.35, 0.40, 0.45, 0.50]
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY = "H-spectrum"
TOTAL_TICKS = 120

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

# Results
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
            identity.phase = excited_phase  # simulate excitation

        if t == 20:
            identity.phase = PHASE_G  # simulate drop attempt

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

# Save output
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_046_summary.json"), "w") as f:
    json.dump(spectral_results, f, indent=2)
    print("✓ Wrote: trial_046_summary.json")

print("✓ Trial 046 complete: Higher orbital excitation-return intervals recorded.")
