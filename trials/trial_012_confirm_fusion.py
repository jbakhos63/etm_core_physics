
"""
Trial 012: Confirming Fusion with Distinct Ancestry and Aligned Phase
----------------------------------------------------------------------
Purpose:
- Create a controlled case where two identities with distinct ancestry return simultaneously
  at identical phase into the same recruiter basin.
- Confirm whether fusion is allowed under these perfect alignment conditions.

Setup:
- Identity A1 returns at tick = 10
- Identity A2 returns at same tick = 10
- Both have distinct ancestry tags
- Phase increment per tick = 0.05
- Return recruiter targets phase = 0.5 (ensures both identities match recruiter phase)
- Tolerance = ±0.11
- Fusion occurs only if both match and share exact tick and phase

Expected Result:
- Fusion = yes
"""

import os
import json

# Constants
RETURN_TICK = 10
PHASE_INCREMENT = 0.05
RECRUITER_PHASE = 0.5
TOLERANCE = 0.11

# Return phases for A1 and A2
phase_A1 = (PHASE_INCREMENT * RETURN_TICK) % 1.0
phase_A2 = (PHASE_INCREMENT * RETURN_TICK) % 1.0

# Phase offset
offset_A1 = abs(phase_A1 - RECRUITER_PHASE)
offset_A2 = abs(phase_A2 - RECRUITER_PHASE)

if offset_A1 > 0.5:
    offset_A1 = 1.0 - offset_A1
if offset_A2 > 0.5:
    offset_A2 = 1.0 - offset_A2

# Match conditions
match_A1 = offset_A1 <= TOLERANCE
match_A2 = offset_A2 <= TOLERANCE

# Assume ancestry is distinct
ancestry_same = False

# Fusion logic
fusion = match_A1 and match_A2 and (phase_A1 == phase_A2) and not ancestry_same

# Output result
result = {
    'tick_A1': RETURN_TICK,
    'tick_A2': RETURN_TICK,
    'phase_A1': round(phase_A1, 3),
    'phase_A2': round(phase_A2, 3),
    'recruiter_phase': RECRUITER_PHASE,
    'phase_offset_A1': round(offset_A1, 3),
    'phase_offset_A2': round(offset_A2, 3),
    'match_A1': match_A1,
    'match_A2': match_A2,
    'fusion': fusion
}

# Write result
os.makedirs("../results", exist_ok=True)
with open("../results/trial_012_summary.json", "w") as f:
    json.dump(result, f, indent=2)
