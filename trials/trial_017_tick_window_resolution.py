
"""
Trial 017: Tick Quantization Width vs. Return Window Width
-----------------------------------------------------------
Purpose:
- Measure how the granularity of tick-phase resolution affects return eligibility.
- Refine understanding of return window width (e.g., ±0.11) in relation to phase increment size.

Setup:
- Phase increment varies: [0.1, 0.05, 0.025, 0.0125]
- Recruiter targets phase = 0.0, tolerance ±0.11
- For each increment, sweep 80 ticks and log number of return matches

Goal:
- Determine how many successful return ticks occur per full 360° cycle
- Assess how return window size aligns with tick-phase quantization
"""

import os
import json

RECRUITER_PHASE = 0.0
TOLERANCE = 0.11
INCREMENTS = [0.1, 0.05, 0.025, 0.0125]
MAX_TICKS = 80

results = []

for increment in INCREMENTS:
    match_ticks = []
    for tick in range(1, MAX_TICKS + 1):
        phase = (increment * tick) % 1.0
        offset = abs(phase - RECRUITER_PHASE)
        if offset > 0.5:
            offset = 1.0 - offset
        match = offset <= TOLERANCE
        if match:
            match_ticks.append(tick)
    results.append({
        'phase_increment': increment,
        'match_count': len(match_ticks),
        'matching_ticks': match_ticks
    })

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_017_summary.json", "w") as f:
    json.dump(results, f, indent=2)
