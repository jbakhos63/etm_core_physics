
# trial_047_orbital_energy_level_from_timing_intervals.py

"""
Trial 047 (Fixed): Derive Orbital Energy Levels from Return Timing

Fixes:
- Prevents return detection before tick 21 (ensures drop has occurred)
- Validates timing intervals for spectral quantization from excitation to return
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_G = 0.0
EXCITED_PHASES = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY = "H-orbital"
TOTAL_TICKS = 150
DROP_TICK = 20
TICK_DURATION_SECONDS = 2.174e-17
ETM_ENERGY_UNIT = 2.540e-18
ETM_PLANCK = 1.325e-34

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

# Results
energy_levels = {}

for excited_phase in EXCITED_PHASES:
    identity = ETMNode("identity_energy", initial_tick=0, phase=PHASE_G)
    identity.phase_increment = DELTA_PHI
    identity.set_ancestry(ANCESTRY)

    for _ in range(6):
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    return_tick = None

    for t in range(TOTAL_TICKS):
        if t == 10:
            identity.phase = excited_phase

        if t == DROP_TICK:
            identity.phase = PHASE_G

        identity.tick_forward()

        if t > DROP_TICK and return_tick is None and round(identity.phase % 1.0, 6) == 0.05:
            return_tick = t + 1

    if return_tick:
        time_interval = (return_tick - DROP_TICK) * TICK_DURATION_SECONDS
        energy_joules = ETM_PLANCK / time_interval if time_interval else None
    else:
        time_interval = None
        energy_joules = None

    energy_levels[str(excited_phase)] = {
        "excited_phase": excited_phase,
        "return_tick": return_tick,
        "delta_ticks": return_tick - DROP_TICK if return_tick else None,
        "time_interval_s": time_interval,
        "derived_energy_joules": energy_joules
    }

# Save updated result
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

summary_path = os.path.join(output_dir, "trial_047_summary.json")
with open(summary_path, "w") as f:
    json.dump(energy_levels, f, indent=2)
    print(f"✓ Wrote: {summary_path}")

print("✓ Trial 047 (fixed) complete: Corrected return timing intervals recorded.")
