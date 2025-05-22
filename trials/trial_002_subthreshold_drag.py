
"""
Trial 002: Sub-Threshold Recruiter Drag
---------------------------------------
Purpose:
- Test whether a uniform, low-strength recruiter field affects the rhythm propagation speed.
- Establish whether recruiter drag must exceed a minimum threshold to cause observable timing delay.
- This trial contributes a constraint: if recruiter support is too weak, propagation remains uninhibited.

Setup:
- 1D lattice of 20 nodes.
- Weak recruiter influence applied uniformly across all nodes.
- Rotor identity begins at node 0 and propagates forward.
- No echo memory or conflict logic is used.

Observation:
- If all transitions occur at the same tick as in Trial 001, the recruiter field is considered sub-threshold.
"""

import os
import json

# Config
width = 20
PHASE_INCREMENT = 1.0
RECRUITER_STRENGTH = 0.2
DRAG_FACTOR = 0.1  # Multiplier applied to recruiter strength to compute drag
MAX_TICKS = 40

# Initialize lattice
lattice = [
    {'tick': None, 'active': False, 'phase': 0.0, 'recruiter_strength': RECRUITER_STRENGTH}
    for _ in range(width)
]
lattice[0]['active'] = True
lattice[0]['tick'] = 0

transitions = []

for tick in range(1, MAX_TICKS):
    for i in range(width):
        node = lattice[i]
        if node['active']:
            node['phase'] += PHASE_INCREMENT

            if node['phase'] >= 1.0 and i + 1 < width and not lattice[i + 1]['active']:
                delay = DRAG_FACTOR * lattice[i + 1]['recruiter_strength']
                lattice[i + 1]['active'] = True
                lattice[i + 1]['tick'] = tick + round(delay)
                lattice[i + 1]['phase'] = 0.0
                transitions.append({
                    'from_node': i,
                    'to_node': i + 1,
                    'tick': lattice[i + 1]['tick'],
                    'drag_delay': delay
                })

# Sort transitions by tick
transitions.sort(key=lambda x: x['tick'])

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_002_summary.json", "w") as f:
    json.dump(transitions, f, indent=2)
