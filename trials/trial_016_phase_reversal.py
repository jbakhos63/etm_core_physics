
"""
Trial 016: Phase Reversal and Symmetry Breaking
------------------------------------------------
Purpose:
- Determine whether identity coherence is preserved when the timing direction is reversed.
- Test whether a phase reversal (moving backward through the tick-phase cycle) breaks return eligibility or identity rhythm.

Setup:
- Identity normally advances by +0.025 phase per tick.
- In reversal mode, phase decrements by -0.025 per tick.
- Recruiter targets phase = 0.0 with ±0.11 tolerance.
- Compare return eligibility across forward and reversed cycles.

Model:
- Run both forward and reverse sweeps for 40 ticks.
- At each tick, check if return phase is within recruiter window.
- Record return success/failure and compare symmetry.

Expectation:
- If ETM is time-symmetric, both directions yield same return pattern.
- If not, this trial will expose symmetry breaking.
"""

import os
import json

PHASE_INCREMENT = 0.025
RECRUITER_PHASE = 0.0
TOLERANCE = 0.11
CYCLE_TICKS = 40

results = {
    'forward': [],
    'reverse': []
}

# Forward sweep
for tick in range(1, CYCLE_TICKS + 1):
    phase = (PHASE_INCREMENT * tick) % 1.0
    offset = abs(phase - RECRUITER_PHASE)
    if offset > 0.5:
        offset = 1.0 - offset
    match = offset <= TOLERANCE
    results['forward'].append({
        'tick': tick,
        'phase': round(phase, 3),
        'offset': round(offset, 3),
        'match': match
    })

# Reverse sweep
for tick in range(1, CYCLE_TICKS + 1):
    phase = (-PHASE_INCREMENT * tick) % 1.0
    offset = abs(phase - RECRUITER_PHASE)
    if offset > 0.5:
        offset = 1.0 - offset
    match = offset <= TOLERANCE
    results['reverse'].append({
        'tick': tick,
        'phase': round(phase, 3),
        'offset': round(offset, 3),
        'match': match
    })

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_016_summary.json", "w") as f:
    json.dump(results, f, indent=2)
