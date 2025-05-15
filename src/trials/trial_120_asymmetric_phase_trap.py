
import json
import os

# Constants
TICK_LIMIT = 100
PHASE_INCREMENT = 0.01
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.1

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_120_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial120.json")

# Identity initialization
identity = {
    'x': 0.0,
    'y': -5.0,
    'phase': 0.5
}

# Helper function
def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Recruiters: asymmetric phase gradients
recruiters = []

# Left array: steep phase increase (0.0 to 0.3)
for i in range(6):
    x = -5.0 + i * 1.0
    phase = (0.0 + i * 0.06) % 1.0
    recruiters.append({'x': x, 'y': 0.0, 'phase': phase})

# Right array: shallow phase decrease (1.0 to 0.9)
for i in range(6):
    x = 1.0 + i * 1.0
    phase = (1.0 - i * 0.02) % 1.0
    recruiters.append({'x': x, 'y': 0.0, 'phase': phase})

# Simulation
transition_log = []
locked = False
lock_tick = None
max_support = 0.0

for tick in range(TICK_LIMIT):
    identity['phase'] = (identity['phase'] + PHASE_INCREMENT) % 1.0
    support = 0.0
    fx = fy = 0.0

    for r in recruiters:
        dx = r['x'] - identity['x']
        dy = r['y'] - identity['y']
        dist = (dx**2 + dy**2) ** 0.5 or 0.0001
        phase_diff = phase_distance(identity['phase'], r['phase'])
        reinforcement = max(0.0, 1.0 - REINFORCEMENT_DECAY * dist - phase_diff)
        support += reinforcement
        fx += reinforcement * dx / dist
        fy += reinforcement * dy / dist

    identity['x'] += fx * 0.1
    identity['y'] += fy * 0.1
    max_support = max(max_support, support)

    if not locked and support >= LOCK_THRESHOLD:
        for r in recruiters:
            if phase_distance(identity['phase'], r['phase']) <= LOCK_TOLERANCE:
                locked = True
                lock_tick = tick
                break

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'y': identity['y'],
        'phase': identity['phase'],
        'support': support
    })

# Output
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
