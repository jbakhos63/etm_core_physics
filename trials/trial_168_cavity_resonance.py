
import json
import os
import math

# Constants
TICK_LIMIT = 150
PHASE_INCREMENT_IDENTITY = 0.01
PHASE_TOLERANCE = 0.05
REINFORCEMENT_DECAY = 0.02
LOCK_THRESHOLD = 0.1
ECHO_STRENGTH = 0.7
CAVITY_WIDTH = 16.0
REFLECT_LEFT = 4.0
REFLECT_RIGHT = 20.0

# Oscillating source parameters
SOURCE_PHASE_BASE = 0.5
SOURCE_AMPLITUDE = 0.25
SOURCE_PERIOD = 40

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_168_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial168.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Identity rotor setup
identity = {
    'x': REFLECT_LEFT,
    'y': 4.0,
    'phase': 0.5,
    'vx': 0.3,
    'vy': 0.0,
    'locked_ticks': [],
    'support_trace': []
}

# Recruiter records (oscillating phase at cavity ends)
transition_log = []

for tick in range(TICK_LIMIT):
    # Oscillating field phase
    field_phase = (SOURCE_PHASE_BASE + SOURCE_AMPLITUDE * math.sin(2 * math.pi * tick / SOURCE_PERIOD)) % 1.0
    current_phase = (identity['phase'] + PHASE_INCREMENT_IDENTITY * tick) % 1.0
    support = 0.0

    # Left wall recruiter (reflection source)
    if abs(identity['x'] - REFLECT_LEFT) <= 1.0:
        phase_diff = phase_distance(current_phase, field_phase)
        if phase_diff <= PHASE_TOLERANCE:
            support += max(0.0, ECHO_STRENGTH - phase_diff)

    # Right wall recruiter (reflection source)
    if abs(identity['x'] - REFLECT_RIGHT) <= 1.0:
        phase_diff = phase_distance(current_phase, field_phase)
        if phase_diff <= PHASE_TOLERANCE:
            support += max(0.0, ECHO_STRENGTH - phase_diff)

    identity['support_trace'].append({'tick': tick, 'support': support})

    if support >= LOCK_THRESHOLD:
        identity['locked_ticks'].append(tick)

    # Move identity and reflect at cavity walls
    identity['x'] += identity['vx']
    if identity['x'] <= REFLECT_LEFT or identity['x'] >= REFLECT_RIGHT:
        identity['vx'] *= -1

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'phase': current_phase,
        'support': support,
        'locked': support >= LOCK_THRESHOLD
    })

# Output results
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'locked_ticks': identity['locked_ticks'],
    'final_position': {'x': identity['x'], 'y': identity['y']},
    'total_locks': len(identity['locked_ticks'])
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
