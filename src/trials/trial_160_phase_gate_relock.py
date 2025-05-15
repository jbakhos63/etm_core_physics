
import json
import os
import math

# Constants
TICK_LIMIT = 130
PHASE_INCREMENT_START = 0.01
PHASE_INCREMENT_DRIFT = 0.002
DRIFT_TICK = 50
GATE_TICKS = [125, 127, 129]  # Specific ticks where phase gate is open
GATE_PHASE = 0.5
GATE_REINFORCEMENT = 0.8
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
UNLOCK_TOLERANCE = 0.08
REINFORCEMENT_DECAY = 0.02
RECRUITER_RING_RADIUS = 6.0
RECRUITER_COUNT = 16
RECRUITER_PHASE_CENTER = 0.5
RECRUITER_PHASE_SPREAD = 0.02

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_160_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial160.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Base recruiter ring
base_recruiters = []
for i in range(RECRUITER_COUNT):
    angle = 2 * math.pi * i / RECRUITER_COUNT
    x = RECRUITER_RING_RADIUS * math.cos(angle)
    y = RECRUITER_RING_RADIUS * math.sin(angle)
    phase = (RECRUITER_PHASE_CENTER + RECRUITER_PHASE_SPREAD * math.sin(angle)) % 1.0
    base_recruiters.append({'x': x, 'y': y, 'phase': phase})

# Identity
identity = {
    'x': 6.5,
    'y': 0.0,
    'phase': 0.5,
    'vx': 0.0,
    'vy': 0.6,
    'locked': False,
    'relocked': False
}

lock_tick = None
unlock_tick = None
relock_tick = None
max_support = 0.0
transition_log = []

# Simulation
for tick in range(TICK_LIMIT):
    phase_increment = PHASE_INCREMENT_START + (PHASE_INCREMENT_DRIFT if tick >= DRIFT_TICK else 0.0)
    identity['phase'] = (identity['phase'] + phase_increment) % 1.0

    support = 0.0
    fx = fy = 0.0
    recruiters = base_recruiters.copy()

    # Inject phase-gated recruiter ring at specific ticks
    if tick in GATE_TICKS:
        for i in range(RECRUITER_COUNT):
            angle = 2 * math.pi * i / RECRUITER_COUNT
            x = RECRUITER_RING_RADIUS * math.cos(angle)
            y = RECRUITER_RING_RADIUS * math.sin(angle)
            recruiters.append({'x': x, 'y': y, 'phase': GATE_PHASE})

    for r in recruiters:
        dx = r['x'] - identity['x']
        dy = r['y'] - identity['y']
        dist = math.sqrt(dx**2 + dy**2) or 0.0001
        phase_diff = phase_distance(identity['phase'], r['phase'])

        reinforcement = max(0.0, 1.0 - REINFORCEMENT_DECAY * dist - phase_diff)
        if tick in GATE_TICKS and r['phase'] == GATE_PHASE:
            reinforcement += GATE_REINFORCEMENT

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

    # Initial lock
    if not identity['locked'] and support >= LOCK_THRESHOLD:
        for r in recruiters:
            if phase_distance(identity['phase'], r['phase']) <= LOCK_TOLERANCE:
                identity['locked'] = True
                lock_tick = tick
                break

    # Unlock logic
    if identity['locked']:
        in_tolerance = any(phase_distance(identity['phase'], r['phase']) <= UNLOCK_TOLERANCE for r in recruiters)
        if not in_tolerance:
            identity['locked'] = False
            unlock_tick = tick

    # Re-lock under gated condition
    if not identity['locked'] and not identity['relocked'] and unlock_tick is not None and support >= LOCK_THRESHOLD:
        for r in recruiters:
            if phase_distance(identity['phase'], r['phase']) <= LOCK_TOLERANCE:
                identity['locked'] = True
                identity['relocked'] = True
                relock_tick = tick
                break

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'y': identity['y'],
        'phase': identity['phase'],
        'vx': identity['vx'],
        'vy': identity['vy'],
        'support': support,
        'locked': identity['locked']
    })

# Output results
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'lock_tick': lock_tick,
    'unlock_tick': unlock_tick,
    'relock_tick': relock_tick,
    'max_support': max_support
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
