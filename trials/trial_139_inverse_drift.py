
import json
import os
import math

# Constants
TICK_LIMIT = 100
PHASE_INCREMENT = 0.01
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.1
RECRUITER_RADIUS = 4.0
RECRUITER_COUNT = 12
RECRUITER_PHASE_CENTER = 0.5
RECRUITER_PHASE_SPREAD = 0.04

# Distances to drop from
initial_ys = [-6.0, -7.0, -8.0, -9.0]
runs = []

# Helper function
def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Generate circular recruiter ring
recruiters = []
for i in range(RECRUITER_COUNT):
    angle = 2 * math.pi * i / RECRUITER_COUNT
    x = RECRUITER_RADIUS * math.cos(angle)
    y = RECRUITER_RADIUS * math.sin(angle)
    phase = (RECRUITER_PHASE_CENTER + RECRUITER_PHASE_SPREAD * math.sin(angle)) % 1.0
    recruiters.append({'x': x, 'y': y, 'phase': phase})

# Simulation for each drop distance
for y0 in initial_ys:
    identity = {
        'x': 0.0,
        'y': y0,
        'phase': 0.5
    }

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
            dist = math.sqrt(dx**2 + dy**2) or 0.0001
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

    runs.append({
        'initial_y': y0,
        'lock_tick': lock_tick,
        'max_support': max_support,
        'transition_log': transition_log
    })

# Output paths
RESULTS_DIR = "../results"
os.makedirs(RESULTS_DIR, exist_ok=True)

with open(os.path.join(RESULTS_DIR, "trial_139_summary.json"), "w") as f:
    json.dump([{
        'initial_y': r['initial_y'],
        'lock_tick': r['lock_tick'],
        'max_support': r['max_support']
    } for r in runs], f, indent=2)

with open(os.path.join(RESULTS_DIR, "transition_log_trial139.json"), "w") as f:
    json.dump(runs, f, indent=2)
