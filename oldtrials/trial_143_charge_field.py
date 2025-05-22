
import json
import os
import math

# Constants
TICK_LIMIT = 100
PHASE_INCREMENT = 0.01
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.1
CHARGE_CORE_PHASE = 0.5

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_143_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial143.json")

# Identity initialization (starts far from the origin)
identity = {
    'x': 0.0,
    'y': -10.0,
    'phase': 0.5
}

# Charge core at the origin
charge_core = {
    'x': 0.0,
    'y': 0.0,
    'phase': CHARGE_CORE_PHASE
}

# Helper function
def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Simulation
transition_log = []
locked = False
lock_tick = None
max_support = 0.0
prev_y = identity['y']
prev_vy = 0.0

for tick in range(TICK_LIMIT):
    identity['phase'] = (identity['phase'] + PHASE_INCREMENT) % 1.0
    dx = charge_core['x'] - identity['x']
    dy = charge_core['y'] - identity['y']
    dist = math.sqrt(dx**2 + dy**2) or 0.0001
    phase_diff = phase_distance(identity['phase'], charge_core['phase'])
    reinforcement = max(0.0, 1.0 - REINFORCEMENT_DECAY * dist - phase_diff)

    fx = reinforcement * dx / dist
    fy = reinforcement * dy / dist

    identity['x'] += fx * 0.1
    identity['y'] += fy * 0.1
    max_support = max(max_support, reinforcement)

    vy = identity['y'] - prev_y
    ay = vy - prev_vy
    prev_y = identity['y']
    prev_vy = vy

    if not locked and reinforcement >= LOCK_THRESHOLD and phase_diff <= LOCK_TOLERANCE:
        locked = True
        lock_tick = tick

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'y': identity['y'],
        'phase': identity['phase'],
        'support': reinforcement,
        'vy': vy,
        'ay': ay
    })

# Output results
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'locked': locked,
    'lock_tick': lock_tick,
    'max_support': max_support
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
