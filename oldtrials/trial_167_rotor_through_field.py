
import json
import os
import math

# Constants
TICK_LIMIT = 120
PHASE_INCREMENT_IDENTITY = 0.01
PHASE_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.02
ECHO_STRENGTH = 0.7
LOCK_THRESHOLD = 0.1
GRID_WIDTH = 9
GRID_HEIGHT = 9
RECRUITER_SPACING = 2.0

# Oscillating source configuration
SOURCE = {
    'x': 4.0,
    'y': 4.0,
    'phase_base': 0.5,
    'amplitude': 0.25,
    'period': 40
}

# Identity rotor initialization
identity = {
    'x': 0.0,
    'y': 4.0,
    'phase': 0.5,
    'vx': 0.2,
    'vy': 0.0,
    'locked_ticks': [],
    'support_trace': []
}

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_167_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial167.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Recruiter grid setup
grid = []
for i in range(GRID_WIDTH):
    for j in range(GRID_HEIGHT):
        x = i * RECRUITER_SPACING
        y = j * RECRUITER_SPACING
        grid.append({'x': x, 'y': y, 'phase': None, 'tick_locked': None})

echo_records = []
transition_log = []

for tick in range(TICK_LIMIT):
    # Oscillating recruiter phase
    osc_phase = (SOURCE['phase_base'] + SOURCE['amplitude'] * math.sin(2 * math.pi * tick / SOURCE['period'])) % 1.0
    current_phase = (identity['phase'] + PHASE_INCREMENT_IDENTITY * tick) % 1.0

    support = 0.0

    for r in grid:
        dx = identity['x'] - r['x']
        dy = identity['y'] - r['y']
        dist = math.sqrt(dx**2 + dy**2)

        if dist <= RECRUITER_SPACING * 1.2:
            phase_diff = phase_distance(current_phase, osc_phase)
            if phase_diff <= PHASE_TOLERANCE:
                support += max(0.0, ECHO_STRENGTH - phase_diff)

    identity['support_trace'].append({'tick': tick, 'support': support})

    if support >= LOCK_THRESHOLD:
        identity['locked_ticks'].append(tick)

    identity['x'] += identity['vx']
    identity['y'] += identity['vy']

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'y': identity['y'],
        'phase': current_phase,
        'support': support,
        'locked': support >= LOCK_THRESHOLD
    })

# Output
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'locked_ticks': identity['locked_ticks'],
    'final_position': {'x': identity['x'], 'y': identity['y']},
    'total_locks': len(identity['locked_ticks'])
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
