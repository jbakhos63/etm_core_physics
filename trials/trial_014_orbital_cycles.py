
"""
Trial 014: Orbital-like Modularity and Return Cycles
-----------------------------------------------------
Purpose:
- Test whether a single identity can repeatedly cycle in and out of a recruiter region,
  rejoining the modular identity in phase over multiple ticks.
- This models a discrete, timing-based "orbital" structure.

Setup:
- Identity leaves at tick = 0
- Recruiter targets phase = 0.0, tolerance ±0.11
- Identity phase increment = 0.025 per tick
- Check return phase every N ticks (representing orbital delay)
- If return phase matches recruiter window, return succeeds
- Repeat this check for multiple orbital passes

Model:
- Allow up to 10 cycles (passes)
- Log return success/failure, phase alignment, and cumulative stability
"""

import os
import json

PHASE_INCREMENT = 0.025
RECRUITER_PHASE = 0.0
TOLERANCE = 0.11
CYCLE_INTERVAL = 40  # ticks between return attempts
MAX_CYCLES = 10

results = []

stability_counter = 0
tick = 0

for cycle in range(1, MAX_CYCLES + 1):
    tick += CYCLE_INTERVAL
    return_phase = (PHASE_INCREMENT * tick) % 1.0
    offset = abs(return_phase - RECRUITER_PHASE)
    if offset > 0.5:
        offset = 1.0 - offset

    match = offset <= TOLERANCE
    if match:
        stability_counter += 1
    else:
        stability_counter = 0  # reset if a failure breaks the cycle

    results.append({
        'cycle': cycle,
        'tick': tick,
        'return_phase': round(return_phase, 3),
        'phase_offset': round(offset, 3),
        'match': match,
        'sustained_orbital': stability_counter >= cycle
    })

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_014_summary.json", "w") as f:
    json.dump(results, f, indent=2)
