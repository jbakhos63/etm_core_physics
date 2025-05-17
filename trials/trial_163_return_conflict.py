
import json
import os
import math

# Constants
TICK_LIMIT = 140
PHASE_INCREMENT_BASE = 0.01
PHASE_INCREMENT_DRIFT = 0.002
DRIFT_TICK_B = 50
RETURN_TICK_B = 115
RETURN_DURATION = 20
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
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_163_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial163.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Recruiters
recruiters = []
for i in range(RECRUITER_COUNT):
    angle = 2 * math.pi * i / RECRUITER_COUNT
    x = RECRUITER_RING_RADIUS * math.cos(angle)
    y = RECRUITER_RING_RADIUS * math.sin(angle)
    phase = (RECRUITER_PHASE_CENTER + RECRUITER_PHASE_SPREAD * math.sin(angle)) % 1.0
    recruiters.append({'x': x, 'y': y, 'phase': phase})

# Two identities with the same ancestry and phase
identities = [
    {
        'id': 'A',
        'x': 6.5,
        'y': 0.0,
        'phase': 0.5,
        'vx': 0.0,
        'vy': 0.6,
        'locked': False,
        'lock_tick': None,
        'unlock_tick': None,
        'relocked': False,
        'relock_tick': None,
        'ancestry': 'root'
    },
    {
        'id': 'B',
        'x': 6.5,
        'y': 0.0,
        'phase': 0.5,
        'vx': 0.0,
        'vy': 0.6,
        'locked': False,
        'lock_tick': None,
        'unlock_tick': None,
        'relocked': False,
        'relock_tick': None,
        'ancestry': 'root'
    }
]

# Modular lock registry to track occupancy
modular_lock = {}

# Simulation log
transition_log = []
max_support = {'A': 0.0, 'B': 0.0}

# Simulation
for tick in range(TICK_LIMIT):
    for identity in identities:
        # Phase drift/resync for B only
        if identity['id'] == 'B':
            if tick < DRIFT_TICK_B:
                phase_increment = PHASE_INCREMENT_BASE
            elif tick < RETURN_TICK_B:
                phase_increment = PHASE_INCREMENT_BASE + PHASE_INCREMENT_DRIFT
            elif tick < RETURN_TICK_B + RETURN_DURATION:
                decay_ratio = (tick - RETURN_TICK_B) / RETURN_DURATION
                phase_increment = PHASE_INCREMENT_BASE + PHASE_INCREMENT_DRIFT * (1 - decay_ratio)
            else:
                phase_increment = PHASE_INCREMENT_BASE
        else:
            phase_increment = PHASE_INCREMENT_BASE

        identity['phase'] = (identity['phase'] + phase_increment) % 1.0

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

        ax = fx * 0.1
        ay = fy * 0.1
        identity['vx'] += ax
        identity['vy'] += ay
        identity['x'] += identity['vx']
        identity['y'] += identity['vy']

        max_support[identity['id']] = max(max_support[identity['id']], support)

        phase_key = round(identity['phase'], 2)
        ancestry_key = (identity['ancestry'], phase_key)

        # Locking logic with modular exclusion
        if not identity['locked'] and support >= LOCK_THRESHOLD:
            if ancestry_key not in modular_lock:
                for r in recruiters:
                    if phase_distance(identity['phase'], r['phase']) <= LOCK_TOLERANCE:
                        identity['locked'] = True
                        if identity['lock_tick'] is None:
                            identity['lock_tick'] = tick
                        elif not identity['relocked']:
                            identity['relocked'] = True
                            identity['relock_tick'] = tick
                        modular_lock[ancestry_key] = identity['id']
                        break

        # Unlocking if phase drift breaks resonance
        if identity['locked']:
            in_tolerance = any(phase_distance(identity['phase'], r['phase']) <= UNLOCK_TOLERANCE for r in recruiters)
            if not in_tolerance:
                identity['locked'] = False
                identity['unlock_tick'] = tick
                modular_lock.pop(ancestry_key, None)

        transition_log.append({
            'tick': tick,
            'id': identity['id'],
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
    'lock_ticks': {id['id']: id['lock_tick'] for id in identities},
    'unlock_ticks': {id['id']: id['unlock_tick'] for id in identities},
    'relock_ticks': {id['id']: id['relock_tick'] for id in identities},
    'max_support': max_support
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
