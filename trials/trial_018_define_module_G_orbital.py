"""
Trial 018: Define Orbital Identity Module G

Goal:
- Define a structured modular orbital identity (Module G)
- Allow a returned identity to lock into this module
- Tick forward and confirm stability over time
- Begin formal ETM orbital modeling

Setup:
- Recruiters form a structured basin
- Identity B reforms into D inside Module G
- Ticks forward under timing guidance

Module G will serve as the stable ground state for future orbital transitions.
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
REINFORCE_COUNT = 6
RETURN_PHASE = 0.0
ANCESTRY = "rotor-A"
PHASE_INCREMENT = 0.05
TICKS = 20

# Define structured Module G recruiter field
module_G_positions = [(0,1), (1,0), (1,2), (2,1), (1,1)]
recruiters = {
    f"modG_{x}_{y}": RecruiterNode(
        node_id=f"modG_{x}_{y}",
        target_ancestry=ANCESTRY,
        target_phase=RETURN_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for (x, y) in module_G_positions
}

# Reinforce Module G
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Initialize identity as returned into Module G
identity = ETMNode("Module_G_identity", initial_tick=0, phase=RETURN_PHASE)
identity.set_ancestry(ANCESTRY)

# Tick forward and track history
history = []

for t in range(TICKS):
    identity.tick_forward(PHASE_INCREMENT)
    history.append({
        "tick": identity.tick,
        "phase": round(identity.phase, 4),
        "ancestry": identity.ancestry_tag
    })

# Record recruiter state
recruiter_summary = {r.node_id: r.get_summary() for r in recruiters.values()}

# Export result
os.makedirs("../results", exist_ok=True)
with open("../results/trial_018_summary.json", "w") as f:
    json.dump({
        "identity_tick_history": history,
        "module_G_recruiters": recruiter_summary
    }, f, indent=2)
