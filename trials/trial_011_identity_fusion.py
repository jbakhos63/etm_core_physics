
"""
Trial 011: Identity Fusion from Distinct Ancestry
-------------------------------------------------
Purpose:
- Test whether two identities with distinct ancestry can return into overlapping recruiter fields.
- Determine whether fusion is allowed when ancestry tags differ and phases are compatible.
- Establish whether distinguishability permits identity coexistence or unification.

Setup:
- Two identities (A1, A2) have distinct ancestry tags.
- Both return into a shared recruiter targeting phase 0.0 with tolerance ±0.11.
- Phase increment per tick = 0.05
- Sweep return delay of A2; A1 is fixed at tick 10.

Conflict (fusion) occurs if both match and return with same phase, even with distinct ancestry.
"""

import os
import json

PHASE_INCREMENT = 0.05
RECRUITER_PHASE = 0.0
TOLERANCE = 0.11
MAX_TICKS = 30

results = []

return_tick_A1 = 10
ancestry_same = False  # For future logic

for delay in range(MAX_TICKS + 1):
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

    fusion = match_A1 and match_A2 and (phase_A1 == phase_A2) and not ancestry_same

    results.append({
        'delay_A2': delay,
        'tick_A1': return_tick_A1,
        'tick_A2': tick_A2,
        'phase_A1': round(phase_A1, 3),
        'phase_A2': round(phase_A2, 3),
        'match_A1': match_A1,
        'match_A2': match_A2,
        'fusion': fusion
    })

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_011_summary.json", "w") as f:
    json.dump(results, f, indent=2)
