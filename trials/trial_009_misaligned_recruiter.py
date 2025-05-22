
"""
Trial 009: Reformation Failure from Misaligned Recruiter Fields
---------------------------------------------------------------
Purpose:
- Test identity reformation when ancestry matches but recruiter phase is deliberately misaligned.
- Determine the critical phase offset beyond which reformation fails.
- This confirms the exclusion principle for return based on phase incompatibility.

Setup:
- Sweep recruiter target phase from 0.0 to 1.0 in steps of 0.05
- At each step, identity attempts return at phase = 0.0
- Match occurs only if offset to recruiter phase is within ±0.11
"""

import os
import json

RETURN_PHASE = 0.0
TOLERANCE = 0.11
PHASE_STEP = 0.05

results = []

recruiter_phase = 0.0
while recruiter_phase < 1.0:
    offset = abs(RETURN_PHASE - recruiter_phase)
    if offset > 0.5:
        offset = 1.0 - offset

    match = offset <= TOLERANCE

    results.append({
        'recruiter_phase': round(recruiter_phase, 3),
        'return_phase': RETURN_PHASE,
        'phase_offset': round(offset, 3),
        'match': match
    })

    recruiter_phase += PHASE_STEP

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_009_summary.json", "w") as f:
    json.dump(results, f, indent=2)
