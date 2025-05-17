
import json
import os
import math

# Constants
TICK_LIMIT = 120
PHASE_INCREMENT = 0.01
LOCK_THRESHOLD = 0.1
PHASE_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.02
GRID_WIDTH = 9
GRID_HEIGHT = 9
RECRUITER_SPACING = 2.0

# Dual oscillating sources
SOURCES = [
    {'x': 4.0, 'y': 4.0, 'phase_base': 0.5, 'amplitude': 0.25, 'period': 40},
    {'x': 12.0, 'y': 4.0, 'phase_base': 0.25, 'amplitude': 0.25, 'period': 40}
]

ECHO_STRENGTH = 0.7

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_166_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial166.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Grid node initialization
grid = []
for i in range(GRID_WIDTH):
    for j in range(GRID_HEIGHT):
        x = i * RECRUITER_SPACING
        y = j * RECRUITER_SPACING
        grid.append({
            'x': x,
            'y': y,
            'phase': None,
            'active': False,
            'tick_locked': None
        })

# Echo records
echo_records = []

# Simulation loop
transition_log = []

for tick in range(TICK_LIMIT):
    source_phases = []
    for src in SOURCES:
        osc_phase = (src['phase_base'] + src['amplitude'] * math.sin(2 * math.pi * tick / src['period'])) % 1.0
        source_phases.append({'x': src['x'], 'y': src['y'], 'phase': osc_phase})

    for node in grid:
        if node['active']:
            continue

        echo_support = 0.0
        current_phase = (PHASE_INCREMENT * tick) % 1.0

        for echo in source_phases:
            dx = node['x'] - echo['x']
            dy = node['y'] - echo['y']
            dist = math.sqrt(dx**2 + dy**2)
            if dist <= RECRUITER_SPACING * 2 + 0.1:
                phase_diff = phase_distance(current_phase, echo['phase'])
                if phase_diff <= PHASE_TOLERANCE:
                    echo_support += max(0.0, ECHO_STRENGTH - phase_diff)

        if echo_support >= LOCK_THRESHOLD:
            node['phase'] = current_phase
            node['active'] = True
            node['tick_locked'] = tick
            echo_records.append({'tick': tick, 'x': node['x'], 'y': node['y'], 'phase': current_phase})

    for node in grid:
        transition_log.append({
            'tick': tick,
            'x': node['x'],
            'y': node['y'],
            'phase': node['phase'],
            'locked': node['active'],
            'tick_locked': node['tick_locked']
        })

# Output
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'locked_nodes': sum(1 for node in grid if node['active']),
    'final_tick': TICK_LIMIT,
    'grid_width': GRID_WIDTH,
    'grid_height': GRID_HEIGHT
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
