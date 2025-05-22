
"""
Trial 015: Tick-Phase Tagging and Spin-like Behavior
-----------------------------------------------------
Purpose:
- Test whether two identities, differing only by phase tag (0.0 vs. 0.5),
  can return into the same orbital recruiter structure without conflict.
- Model spin-like exclusion and complementarity via phase interleaving.

Setup:
- Recruiter targets phase = 0.0, tolerance ±0.11
- Identity A1 has return phase = 0.0
- Identity A2 has return phase = 0.5
- Check whether both match recruiter at different ticks
- Confirm whether their 0.5 tick phase difference allows coexistence

Assumptions:
- If A1 and A2 return in phase separation of 0.5, they are allowed to coexist.
- If both return with phase = 0.0, conflict occurs.
"""

import os
import json

PHASE_INCREMENT = 0.05
RECRUITER_PHASE = 0.0
TOLERANCE = 0.11
MAX_TICKS = 100

# Define identities
results = []

for tick in range(MAX_TICKS + 1):
    phase_A1 = (PHASE_INCREMENT * tick) % 1.0
    phase_A2 = (phase_A1 + 0.5) % 1.0  # Offset identity A2 by 0.5 phase

    offset_A1 = abs(phase_A1 - RECRUITER_PHASE)
    offset_A2 = abs(phase_A2 - RECRUITER_PHASE)

    if offset_A1 > 0.5:
        offset_A1 = 1.0 - offset_A1
    if offset_A2 > 0.5:
        offset_A2 = 1.0 - offset_A2

    match_A1 = offset_A1 <= TOLERANCE
    match_A2 = offset_A2 <= TOLERANCE

    conflict = match_A1 and match_A2 and (phase_A1 == phase_A2)
    spin_like_complement = match_A1 and match_A2 and (abs(phase_A1 - phase_A2) == 0.5)

    results.append({
        'tick': tick,
        'phase_A1': round(phase_A1, 3),
        'phase_A2': round(phase_A2, 3),
        'match_A1': match_A1,
        'match_A2': match_A2,
        'conflict': conflict,
        'spin_like_complement': spin_like_complement
    })

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_015_summary.json", "w") as f:
    json.dump(results, f, indent=2)
