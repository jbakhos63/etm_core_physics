
import json
import os
import math

# Constants
TICK_LIMIT = 120
PHASE_INCREMENT = 0.01
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.02
GRID_WIDTH = 7
GRID_HEIGHT = 7
RECRUITER_SPACING = 2.0
SOURCE_X = 6.0
SOURCE_Y = 6.0
SOURCE_PHASE_BASE = 0.5
OSCILLATION_AMPLITUDE = 0.25
OSCILLATION_PERIOD = 40
ECHO_DELAY = 1
ECHO_STRENGTH = 0.7
PHASE_TOLERANCE = 0.05

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_165_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial165.json")

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
    # Oscillating source phase
    osc_phase = (SOURCE_PHASE_BASE + OSCILLATION_AMPLITUDE * math.sin(2 * math.pi * tick / OSCILLATION_PERIOD)) % 1.0

    for node in grid:
        if node['active']:
            continue

        # Distance from source
        dx = node['x'] - SOURCE_X
        dy = node['y'] - SOURCE_Y
        dist = math.sqrt(dx**2 + dy**2)

        # Expected activation tick
        expected_tick = int(dist / ECHO_DELAY)

        if abs(tick - expected_tick) <= 1:
            phase_diff = phase_distance((osc_phase + PHASE_INCREMENT * tick) % 1.0, osc_phase)
            if phase_diff <= PHASE_TOLERANCE:
                node['phase'] = (osc_phase + PHASE_INCREMENT * tick) % 1.0
                node['active'] = True
                node['tick_locked'] = tick
                echo_records.append({'tick': tick, 'x': node['x'], 'y': node['y'], 'phase': node['phase']})
        else:
            echo_support = 0.0
            for echo in echo_records:
                dx_echo = node['x'] - echo['x']
                dy_echo = node['y'] - echo['y']
                dist_echo = math.sqrt(dx_echo**2 + dy_echo**2)
                if dist_echo <= RECRUITER_SPACING + 0.1:
                    phase_diff = phase_distance((osc_phase + PHASE_INCREMENT * tick) % 1.0, echo['phase'])
                    if phase_diff <= PHASE_TOLERANCE:
                        echo_support += max(0.0, ECHO_STRENGTH - phase_diff)

            if echo_support >= LOCK_THRESHOLD:
                node['phase'] = (osc_phase + PHASE_INCREMENT * tick) % 1.0
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
