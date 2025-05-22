
import json
import os
import math

# Constants
TICK_LIMIT = 80
PHASE_INCREMENT = 0.01
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.02
GRID_WIDTH = 5
GRID_HEIGHT = 5
RECRUITER_SPACING = 2.0
SOURCE_X = 0.0
SOURCE_Y = 0.0
SOURCE_PHASE = 0.5
SOURCE_TICK = 0
PHASE_TOLERANCE = 0.05
ECHO_DELAY = 1
ECHO_STRENGTH = 0.7

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_164_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial164.json")

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

# Timing echo injection record
echo_records = []

# Simulation loop
transition_log = []

for tick in range(TICK_LIMIT):
    active_nodes = []

    for node in grid:
        if node['active']:
            continue

        # Measure timing distance to source and existing echo nodes
        dx = node['x'] - SOURCE_X
        dy = node['y'] - SOURCE_Y
        dist = math.sqrt(dx**2 + dy**2)

        # Activate echo if timing matches
        expected_tick = SOURCE_TICK + int(dist / ECHO_DELAY)
        if tick == expected_tick:
            phase = (SOURCE_PHASE + PHASE_INCREMENT * tick) % 1.0
            node['phase'] = phase
            node['active'] = True
            node['tick_locked'] = tick
            echo_records.append({'tick': tick, 'x': node['x'], 'y': node['y'], 'phase': phase})

        # Check if recruiter receives echo from neighbors (simulated propagation)
        elif tick > SOURCE_TICK:
            echo_support = 0.0
            for echo in echo_records:
                dx_echo = node['x'] - echo['x']
                dy_echo = node['y'] - echo['y']
                dist_echo = math.sqrt(dx_echo**2 + dy_echo**2)
                if dist_echo <= RECRUITER_SPACING + 0.1:
                    phase_diff = phase_distance((SOURCE_PHASE + PHASE_INCREMENT * tick) % 1.0, echo['phase'])
                    if phase_diff <= PHASE_TOLERANCE:
                        echo_support += max(0.0, ECHO_STRENGTH - phase_diff)

            if echo_support >= LOCK_THRESHOLD:
                node['phase'] = (SOURCE_PHASE + PHASE_INCREMENT * tick) % 1.0
                node['active'] = True
                node['tick_locked'] = tick
                echo_records.append({'tick': tick, 'x': node['x'], 'y': node['y'], 'phase': node['phase']})

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
