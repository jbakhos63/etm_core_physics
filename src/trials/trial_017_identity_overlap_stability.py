"""
Trial 017: Identity Overlap Stability Test

Goal:
- Observe whether two identities with identical ancestry and tick phase can tick forward stably
- Detect potential rhythm interference, recruiter memory disruption, or identity destabilization

Setup:
- Two identities (A and B) both return into phase 0.0
- Recruiter field reinforced
- Each identity ticks forward independently for several steps
- Output includes tick, phase, ancestry, and recruiter memory

This is the next step in modeling magnetism, where modular identities must remain coherently locked in rhythm.
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
PHASE_TOLERANCE = 0.11
SUPPORT_PER_ECHO = 1.0
REINFORCE_COUNT = 6
RETURN_PHASE = 0.0
ANCESTRY = "rotor-A"
PHASE_INCREMENT = 0.05
TICKS = 10

# Recruiter scaffold
scaffold_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
recruiters = {
    f"rec_{i}": RecruiterNode(
        node_id=f"rec_{i}",
        target_ancestry=ANCESTRY,
        target_phase=RETURN_PHASE,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(4)
}

# Reinforce recruiters
for _ in range(REINFORCE_COUNT):
    for rec in recruiters.values():
        rec.receive_echo(ANCESTRY, 0.01, strength=SUPPORT_PER_ECHO)

# Initialize identities
identity_A = ETMNode("identity_A", initial_tick=0, phase=RETURN_PHASE)
identity_A.set_ancestry(ANCESTRY)

identity_B = ETMNode("identity_B", initial_tick=0, phase=RETURN_PHASE)
identity_B.set_ancestry(ANCESTRY)

# Tick them forward and record state
history = {"identity_A": [], "identity_B": []}

for t in range(TICKS):
    identity_A.tick_forward(PHASE_INCREMENT)
    identity_B.tick_forward(PHASE_INCREMENT)

    history["identity_A"].append({
        "tick": identity_A.tick,
        "phase": round(identity_A.phase, 4),
        "ancestry": identity_A.ancestry_tag
    })
    history["identity_B"].append({
        "tick": identity_B.tick,
        "phase": round(identity_B.phase, 4),
        "ancestry": identity_B.ancestry_tag
    })

# Also store recruiter state
recruiter_summary = {r.node_id: r.get_summary() for r in recruiters.values()}

# Export
os.makedirs("../results", exist_ok=True)
with open("../results/trial_017_summary.json", "w") as f:
    json.dump({
        "identity_tick_history": history,
        "recruiter_state": recruiter_summary
    }, f, indent=2)
