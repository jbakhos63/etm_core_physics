
"""
Trial 010: Identity Conflict with Overlapping Ancestry
------------------------------------------------------
Purpose:
- Test whether two identities with the same ancestry can simultaneously return into overlapping recruiter fields.
- Confirm whether a conflict occurs (i.e., exclusion behavior), preventing both identities from returning.

Setup:
- Two identities (A1 and A2) share ancestry.
- Both attempt to return into the same recruiter basin (phase = 0.0, tolerance = ±0.11).
- Only one should be allowed to return due to overlap.
- Sweep return delays for A1 and A2 to test simultaneous vs. staggered return timing.

Assumption:
- Return fails if two identities with same ancestry and phase try to occupy the same node window.
"""

import os
import json

# Constants
PHASE_INCREMENT = 0.05
RECRUITER_PHASE = 0.0
TOLERANCE = 0.11
MAX_TICKS = 30

results = []

# Sweep return tick delays for identity A2 (A1 fixed at tick 10)
return_tick_A1 = 10

for delay in range(0, MAX_TICKS + 1):
    tick_A2 = delay
    phase_A1 = (PHASE_INCREMENT * return_tick_A1) % 1.0
    phase_A2 = (PHASE_INCREMENT * tick_A2) % 1.0

    offset_A1 = abs(phase_A1 - RECRUITER_PHASE)
    offset_A2 = abs(phase_A2 - RECRUITER_PHASE)

    if offset_A1 > 0.5:
        offset_A1 = 1.0 - offset_A1
    if offset_A2 > 0.5:
        offset_A2 = 1.0 - offset_A2

    match_A1 = offset_A1 <= TOLERANCE
    match_A2 = offset_A2 <= TOLERANCE

    conflict = match_A1 and match_A2 and (phase_A1 == phase_A2)

    results.append({
        'delay_A2': delay,
        'tick_A1': return_tick_A1,
        'tick_A2': tick_A2,
        'phase_A1': round(phase_A1, 3),
        'phase_A2': round(phase_A2, 3),
        'match_A1': match_A1,
        'match_A2': match_A2,
        'conflict': conflict
    })

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_010_summary.json", "w") as f:
    json.dump(results, f, indent=2)
