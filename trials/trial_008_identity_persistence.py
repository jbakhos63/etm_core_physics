
"""
Trial 008: Identity Persistence and Dropout Timing
--------------------------------------------------
Purpose:
- Measure how long a modular identity (e.g., a rotor) can persist on a node under different recruiter strengths.
- Determine the minimum recruiter support required to sustain identity activity.
- Quantify identity lifespan before dropout.

Setup:
- One node starts active with phase = 0.0
- At each tick, phase increments by 0.05
- If recruiter support < support_threshold, identity drops after phase reaches 1.0 and fails to reset
- Sweep recruiter strengths from 0.0 to 1.0 in steps of 0.1
- Record how long identity survives before dropout

Assumptions:
- Threshold for recruiter-required sustain: 0.5
- If recruiter >= threshold, phase resets and identity continues
- If not, identity deactivates after reaching phase 1.0
"""

import os
import json

PHASE_INCREMENT = 0.05
MAX_TICKS = 200
RECRUITER_STRENGTHS = [round(0.1 * i, 1) for i in range(11)]  # 0.0 to 1.0
SUPPORT_THRESHOLD = 0.5

results = []

for strength in RECRUITER_STRENGTHS:
    phase = 0.0
    tick = 0
    active = True
    lifespan = 0

    while active and tick < MAX_TICKS:
        phase += PHASE_INCREMENT
        tick += 1

        if phase >= 1.0:
            if strength >= SUPPORT_THRESHOLD:
                phase = 0.0  # sustain rhythm
            else:
                active = False  # dropout occurs
        if active:
            lifespan += 1

    results.append({
        'recruiter_strength': strength,
        'lifespan_ticks': lifespan
    })

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_008_summary.json", "w") as f:
    json.dump(results, f, indent=2)
