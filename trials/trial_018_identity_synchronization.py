
"""
Trial 018: Synchronization Between Distinct Identities
--------------------------------------------------------
Purpose:
- Determine whether two identities with different ancestry and phase offset
  can eventually return in phase to the same recruiter basin.
- Establish whether synchronization is possible via periodic alignment.

Setup:
- A1 starts with tick = 0 (phase increment = 0.025)
- A2 starts with tick = 5 (phase offset = 5 * 0.025 = 0.125)
- Recruiter targets phase = 0.0 with ±0.11 tolerance
- Check both identities over 200 ticks for:
    - Phase alignment with recruiter
    - Simultaneous recruiter match
    - Phase alignment with each other (optional: within ε)

Goal:
- Identify tick(s) when both identities return simultaneously into recruiter
- Confirm or refute long-term synchronizability
"""

import os
import json

PHASE_INCREMENT = 0.025
RECRUITER_PHASE = 0.0
TOLERANCE = 0.11
MAX_TICKS = 200
OFFSET_TICKS = 5  # A2 delayed start

results = []

for tick in range(MAX_TICKS + 1):
    tick_A1 = tick
    tick_A2 = tick - OFFSET_TICKS if tick >= OFFSET_TICKS else None

    if tick_A2 is not None:
        phase_A1 = (PHASE_INCREMENT * tick_A1) % 1.0
        phase_A2 = (PHASE_INCREMENT * tick_A2) % 1.0

        offset_A1 = abs(phase_A1 - RECRUITER_PHASE)
        offset_A2 = abs(phase_A2 - RECRUITER_PHASE)

        if offset_A1 > 0.5:
            offset_A1 = 1.0 - offset_A1
        if offset_A2 > 0.5:
            offset_A2 = 1.0 - offset_A2

        match_A1 = offset_A1 <= TOLERANCE
        match_A2 = offset_A2 <= TOLERANCE
        phase_sync = abs(phase_A1 - phase_A2) % 1.0 == 0.0

        results.append({
            'tick': tick,
            'phase_A1': round(phase_A1, 3),
            'phase_A2': round(phase_A2, 3),
            'match_A1': match_A1,
            'match_A2': match_A2,
            'phase_sync': phase_sync,
            'sync_and_match': match_A1 and match_A2 and phase_sync
        })

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_018_summary.json", "w") as f:
    json.dump(results, f, indent=2)
