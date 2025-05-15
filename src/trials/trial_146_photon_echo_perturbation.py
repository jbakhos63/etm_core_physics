
import json
import os
import math

# Constants
TICK_LIMIT = 150
PHASE_INCREMENT = 0.01
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.02
RECRUITER_RING_RADIUS = 6.0
RECRUITER_COUNT = 16
RECRUITER_PHASE_CENTER = 0.5
RECRUITER_PHASE_SPREAD = 0.02
PHOTON_TICKS = [30, 60, 90, 120]  # Times to inject photon echo reinforcement
PHOTON_REINFORCEMENT = 0.5

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_146_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial146.json")

# Identity initialization
identity = {
    'x': 6.5,
    'y': 0.0,
    'phase': 0.5,
    'vx': 0.0,
    'vy': 0.6
}

# Helper functions
def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Recruiter ring
recruiters = []
for i in range(RECRUITER_COUNT):
    angle = 2 * math.pi * i / RECRUITER_COUNT
    x = RECRUITER_RING_RADIUS * math.cos(angle)
    y = RECRUITER_RING_RADIUS * math.sin(angle)
    phase = (RECRUITER_PHASE_CENTER + RECRUITER_PHASE_SPREAD * math.sin(angle)) % 1.0
    recruiters.append({'x': x, 'y': y, 'phase': phase})

# Simulation loop
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

        # Photon echo reinforcement
        if tick in PHOTON_TICKS:
            reinforcement += PHOTON_REINFORCEMENT

        support += reinforcement
        fx += reinforcement * dx / dist
        fy += reinforcement * dy / dist

    ax = fx * 0.1
    ay = fy * 0.1
    identity['vx'] += ax
    identity['vy'] += ay
    identity['x'] += identity['vx']
    identity['y'] += identity['vy']

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
        'vx': identity['vx'],
        'vy': identity['vy'],
        'support': support
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
