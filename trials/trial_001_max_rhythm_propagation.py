
"""
Trial 001: Maximum Rhythm Propagation
-------------------------------------
Purpose:
- Measure the natural propagation rate of a rotor identity across an empty ETM lattice.
- This trial establishes the ETM rhythm speed limit: the fastest possible tick-to-tick propagation with zero interference.
- This rate defines the base unit from which other delays, drags, and phase shifts will be measured in later trials.

Setup:
- 1D lattice of static nodes, 20 wide.
- No recruiters, no echo fields, no ancestry conflicts.
- Rotor initialized at node 0, allowed to propagate forward.
- Phase increments by 1.0 per tick; nodes activate neighbors when phase reaches 1.0.
"""

import os
import json

# Configuration
width = 20
PHASE_INCREMENT = 1.0

# Node list
lattice = [{'tick': None, 'active': False, 'phase': 0.0} for _ in range(width)]
lattice[0]['active'] = True
lattice[0]['tick'] = 0

transitions = []

for current_tick in range(1, 40):
    for i in range(width):
        node = lattice[i]
        if node['active']:
            node['phase'] += PHASE_INCREMENT

            if node['phase'] >= 1.0 and i + 1 < width and not lattice[i + 1]['active']:
                lattice[i + 1]['active'] = True
                lattice[i + 1]['tick'] = current_tick
                lattice[i + 1]['phase'] = 0.0
                transitions.append({
                    'from_node': i,
                    'to_node': i + 1,
                    'tick': current_tick
                })

# Output results
os.makedirs("../results", exist_ok=True)
with open("../results/trial_001_summary.json", "w") as f:
    json.dump(transitions, f, indent=2)
