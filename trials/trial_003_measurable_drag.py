
"""
Trial 003: Measurable Recruiter Drag
------------------------------------
Purpose:
- Test the recruiter field strength required to cause a discrete delay in rotor propagation.
- Identify the threshold where drag becomes observable in tick logic.
- Contribute a measurable timing inequality or breakpoint to the system of relationships.

Setup:
- 1D lattice of 20 ETM nodes.
- Uniform recruiter field with adjustable strength.
- Rotor identity starts at node 0 and propagates forward.
- Timing delay per node is a function of recruiter strength and a global drag factor.

We vary recruiter strength across a list to find the lowest value that produces tick > 1.
"""

import os
import json

# Constants
width = 20
PHASE_INCREMENT = 1.0
DRAG_FACTOR = 0.1
MAX_TICKS = 50
recruiter_strengths = [0.2, 0.3, 0.4, 0.5, 0.6]

# Run a test for each recruiter strength
results_by_strength = {}

for strength in recruiter_strengths:
    lattice = [
        {'tick': None, 'active': False, 'phase': 0.0, 'recruiter_strength': strength}
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

    transitions.sort(key=lambda x: x['tick'])
    results_by_strength[strength] = transitions

# Save output
os.makedirs("../results", exist_ok=True)
with open("../results/trial_003_summary.json", "w") as f:
    json.dump(results_by_strength, f, indent=2)
