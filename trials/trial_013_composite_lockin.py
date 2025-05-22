
"""
Trial 013: Composite Identity Timing Lock-in
--------------------------------------------
Purpose:
- Test whether two identities (with distinct ancestry) that return in phase alignment into a shared recruiter
  can collectively stabilize into a new composite identity.
- Confirm whether timing lock-in persists for multiple ticks when both identities are active in phase.

Setup:
- Identity A1 and A2 both return at tick = 10 with phase = 0.5
- Ancestry is distinct, recruiter targets phase = 0.5 with tolerance ±0.11
- If both match and phases align, composite structure begins
- Track whether this composite survives more than one tick (minimum lock-in duration = 3 ticks)

Model:
- If both identities are present and active in phase for 3 consecutive ticks → composite = yes
- If either identity drops or dephases → composite = no
"""

import os
import json

# Configuration
TICK_START = 10
PHASE_INCREMENT = 0.05
RECRUITER_PHASE = 0.5
TOLERANCE = 0.11
LOCK_IN_TICKS_REQUIRED = 3

# Simulated tick span
MAX_TICKS = TICK_START + LOCK_IN_TICKS_REQUIRED

results = []

active_A1 = True
active_A2 = True
lock_in_ticks = 0

for tick in range(TICK_START, MAX_TICKS):
    phase_A1 = (PHASE_INCREMENT * tick) % 1.0
    phase_A2 = (PHASE_INCREMENT * tick) % 1.0

    offset_A1 = abs(phase_A1 - RECRUITER_PHASE)
    offset_A2 = abs(phase_A2 - RECRUITER_PHASE)

    if offset_A1 > 0.5:
        offset_A1 = 1.0 - offset_A1
    if offset_A2 > 0.5:
        offset_A2 = 1.0 - offset_A2

    match_A1 = offset_A1 <= TOLERANCE
    match_A2 = offset_A2 <= TOLERANCE

    in_phase = phase_A1 == phase_A2

    both_active = match_A1 and match_A2 and in_phase
    if both_active:
        lock_in_ticks += 1
    else:
        lock_in_ticks = 0

    results.append({
        'tick': tick,
        'phase_A1': round(phase_A1, 3),
        'phase_A2': round(phase_A2, 3),
        'match_A1': match_A1,
        'match_A2': match_A2,
        'in_phase': in_phase,
        'lock_in_ticks': lock_in_ticks,
        'composite_formed': lock_in_ticks >= LOCK_IN_TICKS_REQUIRED
    })

# Save results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_013_summary.json", "w") as f:
    json.dump(results, f, indent=2)
