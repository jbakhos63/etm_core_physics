
import json
import os
import math

# Constants
TICK_LIMIT = 130
PHASE_INCREMENT_START = 0.01
PHASE_INCREMENT_DRIFT = 0.002
DRIFT_TICK = 50
VOTING_WINDOW = [125, 126, 127, 128, 129]
TOLERANT_PHASE_CENTER = 0.5
PHASE_TOLERANCE = 0.10  # Looser tolerance for field voting
VOTING_REINFORCEMENT = 0.4
REQUIRED_VOTES = 3  # Require 3 out of N recruiters to confirm
LOCK_THRESHOLD = 0.1
UNLOCK_TOLERANCE = 0.08
REINFORCEMENT_DECAY = 0.02
RECRUITER_RING_RADIUS = 6.0
RECRUITER_COUNT = 9
RECRUITER_PHASE_SPREAD = 0.02

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_161_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial161.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Generate recruiters
def generate_recruiters(center_phase):
    ring = []
    for i in range(RECRUITER_COUNT):
        angle = 2 * math.pi * i / RECRUITER_COUNT
        x = RECRUITER_RING_RADIUS * math.cos(angle)
        y = RECRUITER_RING_RADIUS * math.sin(angle)
        phase = (center_phase + RECRUITER_PHASE_SPREAD * math.sin(angle)) % 1.0
        ring.append({'x': x, 'y': y, 'phase': phase})
    return ring

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

# Initialize recruiters
base_recruiters = generate_recruiters(center_phase=TOLERANT_PHASE_CENTER)

# Simulation loop
for tick in range(TICK_LIMIT):
    phase_increment = PHASE_INCREMENT_START + (PHASE_INCREMENT_DRIFT if tick >= DRIFT_TICK else 0.0)
    identity['phase'] = (identity['phase'] + phase_increment) % 1.0

    support = 0.0
    fx = fy = 0.0
    active_recruiters = base_recruiters.copy()

    vote_count = 0

    for r in active_recruiters:
        dx = r['x'] - identity['x']
        dy = r['y'] - identity['y']
        dist = math.sqrt(dx**2 + dy**2) or 0.0001
        phase_diff = phase_distance(identity['phase'], r['phase'])

        reinforcement = max(0.0, 1.0 - REINFORCEMENT_DECAY * dist - phase_diff)

        if tick in VOTING_WINDOW and phase_diff <= PHASE_TOLERANCE:
            reinforcement += VOTING_REINFORCEMENT
            vote_count += 1

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

    if not identity['locked'] and support >= LOCK_THRESHOLD:
        if vote_count >= REQUIRED_VOTES:
            identity['locked'] = True
            if lock_tick is None:
                lock_tick = tick
            elif not identity['relocked']:
                identity['relocked'] = True
                relock_tick = tick

    if identity['locked'] and tick not in VOTING_WINDOW:
        identity['locked'] = False
        unlock_tick = tick

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'y': identity['y'],
        'phase': identity['phase'],
        'vx': identity['vx'],
        'vy': identity['vy'],
        'support': support,
        'locked': identity['locked'],
        'votes': vote_count
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
