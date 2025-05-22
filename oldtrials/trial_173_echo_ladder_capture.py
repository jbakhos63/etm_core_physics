
import json
import os
import math

# Constants
TICK_LIMIT = 150
PHASE_INCREMENT_IDENTITY = 0.0125
PHASE_TOLERANCE = 0.05
LOCK_THRESHOLD = 0.1
ECHO_STRENGTH = 0.7
REINFORCEMENT_DECAY = 0.02
REFLECT_LEFT = 4.0
REFLECT_RIGHT = 20.0
LADDER_ZONE_LEFT = 8.0
LADDER_ZONE_RIGHT = 16.0
LADDER_PHASE_START = 0.5
LADDER_PHASE_STEP = -0.01
LADDER_TICKS = [60, 80, 100, 120, 140]

# Output paths
RESULTS_DIR = "../results"
SUMMARY_FILENAME = os.path.join(RESULTS_DIR, "trial_173_summary.json")
TRANSITION_LOG_FILENAME = os.path.join(RESULTS_DIR, "transition_log_trial173.json")

def phase_distance(a, b):
    return min(abs(a - b), 1 - abs(a - b))

# Identity setup
identity = {
    'x': REFLECT_LEFT,
    'y': 4.0,
    'phase': 0.5,
    'vx': 0.3,
    'vy': 0.0,
    'locked_ticks': [],
    'support_trace': []
}

# Echo ladder configuration
echo_ladder = []
for i, tick in enumerate(LADDER_TICKS):
    phase = (LADDER_PHASE_START + i * LADDER_PHASE_STEP) % 1.0
    echo_ladder.append({'tick': tick, 'phase': phase})

transition_log = []

for tick in range(TICK_LIMIT):
    current_identity_phase = (identity['phase'] + PHASE_INCREMENT_IDENTITY * tick) % 1.0
    support = 0.0

    # Wall recruiter support (static phase match)
    for wall_x in [REFLECT_LEFT, REFLECT_RIGHT]:
        if abs(identity['x'] - wall_x) <= 1.0:
            phase_diff = phase_distance(current_identity_phase, LADDER_PHASE_START)
            if phase_diff <= PHASE_TOLERANCE:
                support += max(0.0, ECHO_STRENGTH - phase_diff)

    # Echo ladder pulses inside rhythm trap zone
    if LADDER_ZONE_LEFT <= identity['x'] <= LADDER_ZONE_RIGHT:
        for echo in echo_ladder:
            if tick == echo['tick']:
                phase_diff = phase_distance(current_identity_phase, echo['phase'])
                if phase_diff <= PHASE_TOLERANCE:
                    support += max(0.0, ECHO_STRENGTH - phase_diff)

    identity['support_trace'].append({'tick': tick, 'support': support})

    if support >= LOCK_THRESHOLD:
        identity['locked_ticks'].append(tick)

    # Move and reflect
    identity['x'] += identity['vx']
    if identity['x'] <= REFLECT_LEFT or identity['x'] >= REFLECT_RIGHT:
        identity['vx'] *= -1

    transition_log.append({
        'tick': tick,
        'x': identity['x'],
        'phase': current_identity_phase,
        'support': support,
        'locked': support >= LOCK_THRESHOLD
    })

# Output results
os.makedirs(RESULTS_DIR, exist_ok=True)
summary = {
    'locked_ticks': identity['locked_ticks'],
    'final_position': {'x': identity['x'], 'y': identity['y']},
    'total_locks': len(identity['locked_ticks']),
    'echo_ladder': echo_ladder
}
with open(SUMMARY_FILENAME, 'w') as f:
    json.dump(summary, f, indent=2)
with open(TRANSITION_LOG_FILENAME, 'w') as f:
    json.dump(transition_log, f, indent=2)
