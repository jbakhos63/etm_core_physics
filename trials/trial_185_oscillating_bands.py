
import json
import os
import math

# Constants
TICK_LIMIT = 180
PHASE_INCREMENT = 0.0125
PHASE_TOLERANCE = 0.05
LOCK_THRESHOLD = 0.1
ECHO_STRENGTH = 0.7
RECRUITER_WIDTH = 2.0
RECRUITER_BASE_PHASES = [0.50, 0.48, 0.46, 0.44, 0.42, 0.40, 0.38]
RECRUITER_CENTERS = [6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]
RECRUITER_PERIOD = 40
RECRUITER_AMPLITUDE = 0.01
REFLECT_LEFT = 4.0
REFLECT_RIGHT = 20.0

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_185_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial185.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Identities
identities = [
    {'id': 'A', 'x': REFLECT_LEFT, 'y': 4.0, 'phase': 0.50, 'vx': 0.3, 'ancestry': 'mod', 'spin': 'up', 'locked_ticks': [], 'support_trace': []},
    {'id': 'B', 'x': REFLECT_RIGHT, 'y': 4.0, 'phase': 0.46, 'vx': -0.3, 'ancestry': 'mod', 'spin': 'down', 'locked_ticks': [], 'support_trace': []},
    {'id': 'C', 'x': 12.0, 'y': 4.0, 'phase': 0.48, 'vx': 0.0, 'ancestry': 'mod', 'spin': 'side', 'locked_ticks': [], 'support_trace': []}
]

modular_locks = set()
transition_log = []

for tick in range(TICK_LIMIT):
    # Oscillating recruiter phases
    recruiter_bands = []
    for i, base_phase in enumerate(RECRUITER_BASE_PHASES):
        x = RECRUITER_CENTERS[i]
        modulated_phase = (base_phase + RECRUITER_AMPLITUDE * math.sin(2 * math.pi * tick / RECRUITER_PERIOD)) % 1.0
        recruiter_bands.append({'x': x, 'phase': modulated_phase})

    for identity in identities:
        current_phase = (identity['phase'] + PHASE_INCREMENT * tick) % 1.0
        support = 0.0
        lock_key = (identity['ancestry'], round(current_phase, 3), identity['spin'])

        for band in recruiter_bands:
            if abs(identity['x'] - band['x']) <= RECRUITER_WIDTH:
                phase_diff = phase_distance(current_phase, band['phase'])
                if phase_diff <= PHASE_TOLERANCE:
                    support += max(0.0, ECHO_STRENGTH - phase_diff)

        identity['support_trace'].append({'tick': tick, 'support': support})

        locked = False
        if support >= LOCK_THRESHOLD and lock_key not in modular_locks:
            modular_locks.add(lock_key)
            identity['locked_ticks'].append(tick)
            locked = True

        # Reflect movement
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

# Output
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'locked_ticks': {
        'A': identities[0]['locked_ticks'],
        'B': identities[1]['locked_ticks'],
        'C': identities[2]['locked_ticks']
    },
    'total_locks': {
        'A': len(identities[0]['locked_ticks']),
        'B': len(identities[1]['locked_ticks']),
        'C': len(identities[2]['locked_ticks'])
    },
    'final_positions': {
        'A': identities[0]['x'],
        'B': identities[1]['x'],
        'C': identities[2]['x']
    },
    'recruiter_oscillation': {
        'period': RECRUITER_PERIOD,
        'amplitude': RECRUITER_AMPLITUDE
    }
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
