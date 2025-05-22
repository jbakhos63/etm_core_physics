
"""
Trial 006: Quantization of Tick-Based Transition Intervals
----------------------------------------------------------
Purpose:
- Determine whether successful identity return is quantized over discrete tick intervals.
- Confirm if return windows occur only at specific intervals or if they repeat periodically.
- This trial builds on Trial 005 and explores the periodic structure of modular return behavior.

Setup:
- Target phase for return is set to 0.25 (same as Trial 005).
- Use a finer phase increment per tick to sweep more precisely.
- Track all tick delays (up to 100) and log when return occurs based on phase alignment.

Parameters:
- Phase increment = 0.025 per tick
- Tolerance = ±0.11
"""

import os
import json

# Configuration
PHASE_INCREMENT = 0.025
TARGET_PHASE = 0.25
TOLERANCE = 0.11
MAX_TICKS = 100

results = []

for delay in range(MAX_TICKS + 1):
    phase = (PHASE_INCREMENT * delay) % 1.0
    phase_offset = abs(phase - TARGET_PHASE)
    if phase_offset > 0.5:
        phase_offset = 1.0 - phase_offset
    match = phase_offset <= TOLERANCE
    results.append({
        'tick_delay': delay,
        'phase': round(phase, 3),
        'phase_offset_to_target': round(phase_offset, 3),
        'match': match
    })

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_006_summary.json", "w") as f:
    json.dump(results, f, indent=2)
