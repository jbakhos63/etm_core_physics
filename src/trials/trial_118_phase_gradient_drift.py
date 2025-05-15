
import json
import os

# Simulation Parameters
TICK_LIMIT = 100
RECRUITER_COUNT = 6
RECRUITER_SPACING = 2.0  # Linear spacing
RECRUITER_START_X = -5.0
RECRUITER_Y = 0.0
PHASE_START = 0.0
PHASE_INCREMENT = 0.02  # Increasing phase to create a gradient
PHASE_TOLERANCE = 0.05
LOCK_THRESHOLD = 0.1
PHASE_ADVANCE_PER_TICK = 0.01
REINFORCEMENT_DECAY = 0.1  # Decay per unit distance

# Output files
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_118_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial118.json")

# Initialize recruiters linearly along x with increasing phase
recruiters = []
for i in range(RECRUITER_COUNT):
    x = RECRUITER_START_X + i * RECRUITER_SPACING
    phase = (PHASE_START + i * PHASE_INCREMENT) % 1.0
    recruiters.append({'x': x, 'y': RECRUITER_Y, 'phase': phase})

# Identity initialization
identity = {
    'x': 0.0,
    'y': -5.0,
    'phase': 0.5
}

# Helper for modular phase distance
def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Run simulation
transition_log = []
locked = False
lock_tick = None
max_support = 0.0

for tick in range(TICK_LIMIT):
    identity['phase'] = (identity['phase'] + PHASE_ADVANCE_PER_TICK) % 1.0
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
            if phase_distance(identity['phase'], r['phase']) <= PHASE_TOLERANCE:
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

# Save output
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
