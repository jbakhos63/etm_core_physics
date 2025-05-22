
"""
Trial 005: Timing Delay Between Modular Transitions (G → E1)
(Corrected version with advancing return phase)
------------------------------------------------------------
Purpose:
- Measure the delay in ticks required for a ground state (G) identity to successfully transition into
  an excited state (E1) with a recruiter phase offset of +0.25.
- This corrected version sweeps through phases by using fractional phase advancement.

Setup:
- Phase is incremented by 0.05 per tick delay.
- Reformation into E1 is tested by checking phase alignment with target recruiter phase.
- A match is recorded if the phase offset is within the defined return tolerance.
"""

import os
import json

# Configuration
PHASE_INCREMENT = 0.05  # Phase progress per tick
RECRUITER_PHASE_E1 = 0.25
RETURN_TOLERANCE = 0.11
MAX_DELAY_TICKS = 20

results = []

for delay_ticks in range(MAX_DELAY_TICKS + 1):
    return_phase = (PHASE_INCREMENT * delay_ticks) % 1.0
    phase_offset = abs(return_phase - RECRUITER_PHASE_E1)
    if phase_offset > 0.5:
        phase_offset = 1.0 - phase_offset

    match = phase_offset <= RETURN_TOLERANCE

    results.append({
        'delay_ticks': delay_ticks,
        'return_phase': round(return_phase, 3),
        'phase_offset_to_E1': round(phase_offset, 3),
        'match': match
    })

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_005_summary.json", "w") as f:
    json.dump(results, f, indent=2)
