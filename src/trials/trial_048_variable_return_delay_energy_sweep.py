
# trial_048_variable_return_delay_energy_sweep.py

"""
Trial 048: Sweep Return Delay After Excitation to Map Energy Spectrum

Goal:
- Use a fixed excited phase (e.g. ϕ = 0.25)
- Vary tick delay between excitation and return attempt
- Measure timing interval from drop to reformation
- Derive energy from rhythm interval variation
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_G = 0.0
PHASE_E = 0.25
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY = "H-048"
TICK_DURATION_SECONDS = 2.174e-17
ETM_PLANCK = 1.325e-34
TOTAL_TICKS = 150

# Sweep return attempt delays: drop after 10, 20, 30, ..., 100 ticks
RETURN_DELAYS = list(range(10, 101, 10))

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

results = {}

for delay in RETURN_DELAYS:
    identity = ETMNode("identity_energy_sweep", initial_tick=0, phase=PHASE_G)
    identity.phase_increment = DELTA_PHI
    identity.set_ancestry(ANCESTRY)

    for _ in range(6):
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY, PHASE_G, RECRUITER_STRENGTH)

    return_tick = None

    for t in range(TOTAL_TICKS):
        if t == 5:
            identity.phase = PHASE_E  # excitation at tick 5

        if t == 5 + delay:
            identity.phase = PHASE_G  # drop at delay tick

        identity.tick_forward()

        if t > 5 + delay and return_tick is None and round(identity.phase % 1.0, 6) == 0.05:
            return_tick = t + 1

    if return_tick:
        interval_ticks = return_tick - (5 + delay)
        time_s = interval_ticks * TICK_DURATION_SECONDS
        energy_joules = ETM_PLANCK / time_s if time_s else None
    else:
        interval_ticks = None
        time_s = None
        energy_joules = None

    results[str(delay)] = {
        "return_delay_ticks": delay,
        "return_tick": return_tick,
        "interval_ticks": interval_ticks,
        "time_interval_s": time_s,
        "derived_energy_joules": energy_joules
    }

# Save result
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

summary_path = os.path.join(output_dir, "trial_048_summary.json")
with open(summary_path, "w") as f:
    json.dump(results, f, indent=2)
    print(f"✓ Wrote: {summary_path}")

print("✓ Trial 048 complete: Return delay sweep for quantized energy mapping recorded.")
