
import json
import os
import math

# Constants
TICK_LIMIT = 180
PHASE_INCREMENT = 0.0125
PHASE_TOLERANCE = 0.05
LOCK_THRESHOLD = 0.1
ECHO_STRENGTH = 0.7
REFLECT_LEFT = 4.0
REFLECT_RIGHT = 20.0
LADDER_ZONE_LEFT = 8.0
LADDER_ZONE_RIGHT = 16.0
LADDER_PHASE_START = 0.5
LADDER_PHASE_STEP = -0.005
LADDER_STEPS = 12
LADDER_START_TICK = 60
LADDER_INTERVAL = 10

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_179_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial179.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Two identities, same ancestry & spin, with wider phase separation (0.5 vs 0.40)
identities = [
    {'id': 'A', 'x': REFLECT_LEFT, 'y': 4.0, 'phase': 0.5, 'vx': 0.3, 'ancestry': 'common', 'spin': 'up', 'locked_ticks': [], 'support_trace': []},
    {'id': 'B', 'x': REFLECT_RIGHT, 'y': 4.0, 'phase': 0.40, 'vx': -0.3, 'ancestry': 'common', 'spin': 'up', 'locked_ticks': [], 'support_trace': []}
]

modular_locks = set()
transition_log = []

# Echo ladder construction
echo_ladder = []
for i in range(LADDER_STEPS):
    tick = LADDER_START_TICK + i * LADDER_INTERVAL
    phase = (LADDER_PHASE_START + i * LADDER_PHASE_STEP) % 1.0
    echo_ladder.append({'tick': tick, 'phase': phase})

for tick in range(TICK_LIMIT):
    for identity in identities:
        current_phase = (identity['phase'] + PHASE_INCREMENT * tick) % 1.0
        support = 0.0
        lock_key = (identity['ancestry'], round(current_phase, 3), identity['spin'])

        # Wall recruiter support
        for wall_x in [REFLECT_LEFT, REFLECT_RIGHT]:
            if abs(identity['x'] - wall_x) <= 1.0:
                phase_diff = phase_distance(current_phase, LADDER_PHASE_START)
                if phase_diff <= PHASE_TOLERANCE:
                    support += max(0.0, ECHO_STRENGTH - phase_diff)

        # Echo ladder pulses
        if LADDER_ZONE_LEFT <= identity['x'] <= LADDER_ZONE_RIGHT:
            for echo in echo_ladder:
                if tick == echo['tick']:
                    phase_diff = phase_distance(current_phase, echo['phase'])
                    if phase_diff <= PHASE_TOLERANCE:
                        support += max(0.0, ECHO_STRENGTH - phase_diff)

        identity['support_trace'].append({'tick': tick, 'support': support})

        locked = False
        if support >= LOCK_THRESHOLD and lock_key not in modular_locks:
            modular_locks.add(lock_key)
            identity['locked_ticks'].append(tick)
            locked = True

        # Reflect logic
        identity['x'] += identity['vx']
        if identity['x'] <= REFLECT_LEFT or identity['x'] >= REFLECT_RIGHT:
            identity['vx'] *= -1

        transition_log.append({
            'tick': tick,
            'id': identity['id'],
            'x': identity['x'],
            'phase': current_phase,
            'support': support,
            'locked': locked
        })

# Output results
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'locked_ticks': {
        'A': identities[0]['locked_ticks'],
        'B': identities[1]['locked_ticks']
    },
    'total_locks': {
        'A': len(identities[0]['locked_ticks']),
        'B': len(identities[1]['locked_ticks'])
    },
    'final_positions': {
        'A': identities[0]['x'],
        'B': identities[1]['x']
    },
    'echo_ladder': echo_ladder
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
