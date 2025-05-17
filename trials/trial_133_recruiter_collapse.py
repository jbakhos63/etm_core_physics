
import json
import os

# Constants
TICK_LIMIT = 100
PHASE_INCREMENT = 0.01
LOCK_THRESHOLD = 0.1
LOCK_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.1
LEFT_CLUSTER_CUTOFF_TICK = 40

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_133_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial133.json")

# Identity initialization
identity = {
    'x': 0.0,
    'y': 0.0,
    'phase': 0.5
}

# Helper function
def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Left recruiter cluster (phases ~0.48)
left_cluster = [
    {'x': -3.0, 'y': -1.0, 'phase': 0.47},
    {'x': -3.0, 'y':  0.0, 'phase': 0.48},
    {'x': -3.0, 'y':  1.0, 'phase': 0.49}
]

# Right recruiter cluster (phases ~0.52)
right_cluster = [
    {'x': 3.0, 'y': -1.0, 'phase': 0.51},
    {'x': 3.0, 'y':  0.0, 'phase': 0.52},
    {'x': 3.0, 'y':  1.0, 'phase': 0.53}
]

# Simulation
transition_log = []
locked = False
lock_tick = None
max_support = 0.0

for tick in range(TICK_LIMIT):
    identity['phase'] = (identity['phase'] + PHASE_INCREMENT) % 1.0

    # Collapse left cluster at tick 40
    recruiters = right_cluster.copy()
    if tick < LEFT_CLUSTER_CUTOFF_TICK:
        recruiters += left_cluster

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
        'support': support,
        'left_cluster_active': tick < LEFT_CLUSTER_CUTOFF_TICK
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
