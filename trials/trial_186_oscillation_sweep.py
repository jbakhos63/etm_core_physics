
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
AMPLITUDE_SWEEP = [0.01, 0.02, 0.03, 0.04, 0.05]

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_186_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial186.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

summary_results = []
transition_log = []

for amplitude in AMPLITUDE_SWEEP:
    identity = {
        'id': 'A',
        'x': 4.0,
        'y': 4.0,
        'phase': 0.5,
        'vx': 0.3,
        'ancestry': 'mod',
        'spin': 'up',
        'locked_ticks': [],
        'support_trace': []
    }
    modular_locks = set()

    for tick in range(TICK_LIMIT):
        recruiter_bands = []
        for i, base_phase in enumerate(RECRUITER_BASE_PHASES):
            x = RECRUITER_CENTERS[i]
            modulated_phase = (base_phase + amplitude * math.sin(2 * math.pi * tick / RECRUITER_PERIOD)) % 1.0
            recruiter_bands.append({'x': x, 'phase': modulated_phase})

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

        identity['x'] += identity['vx']
        if identity['x'] <= 4.0 or identity['x'] >= 20.0:
            identity['vx'] *= -1

        transition_log.append({
            'amplitude': amplitude,
            'tick': tick,
            'x': identity['x'],
            'phase': current_phase,
            'support': support,
            'locked': locked
        })

    summary_results.append({
        'amplitude': amplitude,
        'locked_ticks': identity['locked_ticks'],
        'total_locks': len(identity['locked_ticks']),
        'final_position': identity['x']
    })

# Output
os.makedirs(RESULTS_DIR, exist_ok=True)
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary_results, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
