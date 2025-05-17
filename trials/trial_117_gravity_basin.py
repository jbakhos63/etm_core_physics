
import json
import math
import os

# Simulation Parameters
TICK_LIMIT = 100
RECRUITER_PHASE = 0.0
RECRUITER_COUNT = 6
RECRUITER_RADIUS = 5.0
REINFORCEMENT_DECAY = 0.01
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
IDENTITY_INITIAL_PHASE = 0.5
PHASE_INCREMENT = 0.01

# Output Directory
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_117_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial117.json")

# Initialize Recruiters in a circular pattern
recruiters = []
for i in range(RECRUITER_COUNT):
    angle = 2 * math.pi * i / RECRUITER_COUNT
    x = RECRUITER_RADIUS * math.cos(angle)
    y = RECRUITER_RADIUS * math.sin(angle)
    recruiters.append({'x': x, 'y': y, 'phase': RECRUITER_PHASE})

# Identity starts outside the basin
identity = {
    'x': 0.0,
    'y': -10.0,
    'phase': IDENTITY_INITIAL_PHASE
}

# Phase distance function
def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Run Simulation
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
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            dist = 0.0001
        phase_diff = phase_distance(identity['phase'], r['phase'])
        reinforcement = max(0.0, 1.0 - REINFORCEMENT_DECAY * dist - phase_diff)
        support += reinforcement
        fx += reinforcement * dx / dist
        fy += reinforcement * dy / dist

    # Update position toward recruiter field
    identity['x'] += fx * 0.1
    identity['y'] += fy * 0.1

    max_support = max(max_support, support)

    if not locked and support >= LOCK_THRESHOLD and phase_distance(identity['phase'], RECRUITER_PHASE) <= LOCK_TOLERANCE:
        locked = True
        lock_tick = tick

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'y': identity['y'],
        'phase': identity['phase'],
        'support': support
    })

# Output Results
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
