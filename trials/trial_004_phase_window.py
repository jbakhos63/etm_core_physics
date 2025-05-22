
"""
Trial 004: Phase Window for Modular Identity Return
---------------------------------------------------
Purpose:
- Determine the allowable phase offset range (phase window) for successful return of a modular identity.
- This tests modular identity reformation based on ancestry and phase compatibility.
- Contributes a discrete timing constraint to the overall ETM rhythm model.

Setup:
- Single recruiter node fixed at origin.
- Sweep across phase values in the return node.
- For each phase, test whether identity return occurs (match = True/False).

Notes:
- A match occurs if phase is within defined tolerance.
- Tolerance is currently hard-coded and can be adjusted for sensitivity analysis.
"""

import os
import json

# Configuration
PHASE_SWEEP_START = 0.0
PHASE_SWEEP_END = 1.0
PHASE_STEP = 0.05
PHASE_TOLERANCE = 0.11  # Defined identity return window: +-0.11 around 0.0

# Simulate a single return node exposed to a recruiter targeting phase 0.0
target_phase = 0.0
results = []

current_phase = PHASE_SWEEP_START
while current_phase <= PHASE_SWEEP_END:
    phase_offset = abs(current_phase - target_phase)
    # Account for wrap-around at 1.0
    if phase_offset > 0.5:
        phase_offset = 1.0 - phase_offset

    match = phase_offset <= PHASE_TOLERANCE

    results.append({
        'test_phase': round(current_phase, 3),
        'phase_offset': round(phase_offset, 3),
        'match': match
    })

    current_phase += PHASE_STEP

# Output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_004_summary.json", "w") as f:
    json.dump(results, f, indent=2)
