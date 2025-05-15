
import json
import os
import math

# Constants
TICK_LIMIT = 180
PHASE_INCREMENT = 0.0125
PHASE_TOLERANCE = 0.05
LOCK_THRESHOLD = 0.1
ECHO_STRENGTH = 0.7
RECRUITER_WIDTH = 2.0  # Overlapping range
RECRUITER_BANDS = [
    {'x': 6.0, 'phase': 0.50},
    {'x': 8.0, 'phase': 0.48},
    {'x': 10.0, 'phase': 0.46},
    {'x': 12.0, 'phase': 0.44},
    {'x': 14.0, 'phase': 0.42},
    {'x': 16.0, 'phase': 0.40},
    {'x': 18.0, 'phase': 0.38}
]
REFLECT_LEFT = 4.0
REFLECT_RIGHT = 20.0

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_182_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial182.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Identity setup
identity = {
    'id': 'A',
    'x': REFLECT_LEFT,
    'y': 4.0,
    'phase': 0.5,
    'vx': 0.3,
    'ancestry': 'banded',
    'spin': 'up',
    'locked_ticks': [],
    'support_trace': []
}

modular_locks = set()
transition_log = []

for tick in range(TICK_LIMIT):
    current_phase = (identity['phase'] + PHASE_INCREMENT * tick) % 1.0
    support = 0.0
    lock_key = (identity['ancestry'], round(current_phase, 3), identity['spin'])

    for band in RECRUITER_BANDS:
        if abs(identity['x'] - band['x']) <= RECRUITER_WIDTH:
            phase_diff = phase_distance(current_phase, band['phase'])
            if phase_diff <= PHASE_TOLERANCE:
                support += max(0.0, ECHO_STRENGTH - phase_diff)

    identity['support_trace'].append({'tick': tick, 'support': support})

    locked = False
    if support >= LOCK_THRESHOLD and lock_key not in modular_locks:
        modular_locks.add(lock_key)
        identity['locked_ticks'].append(tick)
        locked = True

    identity['x'] += identity['vx']
    if identity['x'] <= REFLECT_LEFT or identity['x'] >= REFLECT_RIGHT:
        identity['vx'] *= -1

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'phase': current_phase,
        'support': support,
        'locked': locked
    })

# Output
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'locked_ticks': identity['locked_ticks'],
    'total_locks': len(identity['locked_ticks']),
    'final_position': identity['x'],
    'recruiter_bands': RECRUITER_BANDS
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
