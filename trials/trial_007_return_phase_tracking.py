
"""
Trial 007: Return Window Tracking for Shifted Recruiter Phases
--------------------------------------------------------------
Purpose:
- Confirm that modular return windows re-center around any recruiter phase.
- Sweep return attempts across a full phase cycle for several recruiter targets.
- Check that return success bands align with each recruiter's specific phase.

Setup:
- Phase increment per tick = 0.025
- Tolerance = ±0.11
- Recruiter target phases: 0.25, 0.5, 0.75
- Sweep tick delays from 0 to 100
"""

import os
import json

PHASE_INCREMENT = 0.025
TOLERANCE = 0.11
RECRUITER_PHASES = [0.25, 0.5, 0.75]
MAX_TICKS = 100

full_results = {}

for target_phase in RECRUITER_PHASES:
    result_list = []
    for delay in range(MAX_TICKS + 1):
        phase = (PHASE_INCREMENT * delay) % 1.0
        offset = abs(phase - target_phase)
        if offset > 0.5:
            offset = 1.0 - offset
        match = offset <= TOLERANCE
        result_list.append({
            'tick_delay': delay,
            'return_phase': round(phase, 3),
            'target_phase': target_phase,
            'phase_offset': round(offset, 3),
            'match': match
        })
    full_results[str(target_phase)] = result_list

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_007_summary.json", "w") as f:
    json.dump(full_results, f, indent=2)
