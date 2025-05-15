"""
Trial 019: Modular Excitation from Module G to Module E1

Goal:
- Define a second modular rhythm (Module E1) distinct from Module G
- Simulate excitation from G to E1
- Establish modular transition behavior for future Planck modeling

Setup:
- Module G: phase 0.0
- Module E1: phase 0.2
- Identity starts in G, then is excited to E1 and ticks forward

Future trial will return identity from E1 → G via photon logic.
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
PHASE_INCREMENT = 0.05
TICKS = 20
ANCESTRY = "rotor-A"

# Define recruiter fields for Module G and Module E1
module_G_phase = 0.0
module_E1_phase = 0.2

module_G_positions = [(0, 1), (1, 0), (1, 1)]
module_E1_positions = [(1, 2), (2, 1), (2, 2)]

recruiters = {}

# Module G recruiters
for (x, y) in module_G_positions:
    recruiters[f"G_{x}_{y}"] = RecruiterNode(
        node_id=f"G_{x}_{y}",
        target_ancestry=ANCESTRY,
        target_phase=module_G_phase,
        phase_tolerance=PHASE_TOLERANCE
    )

# Module E1 recruiters
for (x, y) in module_E1_positions:
    recruiters[f"E1_{x}_{y}"] = RecruiterNode(
        node_id=f"E1_{x}_{y}",
        target_ancestry=ANCESTRY,
        target_phase=module_E1_phase,
        phase_tolerance=PHASE_TOLERANCE
    )

# Reinforce both modules
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Identity begins in Module G
identity = ETMNode("identity_GE", initial_tick=0, phase=module_G_phase)
identity.set_ancestry(ANCESTRY)

# Excite identity to E1: shift phase by +0.2
identity.phase = module_E1_phase

# Tick forward from E1
tick_log = []
for t in range(TICKS):
    identity.tick_forward(PHASE_INCREMENT)
    tick_log.append({
        "tick": identity.tick,
        "phase": round(identity.phase, 4),
        "ancestry": identity.ancestry_tag
    })

# Export results
recruiter_summary = {r.node_id: r.get_summary() for r in recruiters.values()}

os.makedirs("../results", exist_ok=True)
with open("../results/trial_019_summary.json", "w") as f:
    json.dump({
        "identity_tick_history": tick_log,
        "recruiter_state": recruiter_summary
    }, f, indent=2)
