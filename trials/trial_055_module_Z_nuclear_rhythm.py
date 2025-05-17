
# trial_055_module_Z_nuclear_rhythm.py

"""
Trial 055: Module Z Nuclear Rhythm Under Dual Ancestry Pressure

Goal:
- Simulate a stable nucleus rhythm (Module Z) in 3D lattice space
- Introduce two identities with proton-like and neutron-like ancestry
- Drop them into a common recruiter basin (shared modular rhythm)
- Observe identity coherence, phase divergence, or collapse over time
"""

import os
import sys
import json

# Ensure the parent directory is in the Python path
sys.path.append(os.path.abspath(".."))

from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Parameters
PHASE_Z = 0.0
DELTA_PHI = 0.01
PHASE_TOLERANCE = 0.11
RECRUITER_STRENGTH = 0.01
ANCESTRY_P = "H1_proton"
ANCESTRY_N = "H2_neutron"
DROP_TICK = 20
TOTAL_TICKS = 80

# Create recruiter nodes for Module Z
recruiters = {
    f"Z_{i}": RecruiterNode(
        node_id=f"Z_{i}",
        target_ancestry=None,
        target_phase=PHASE_Z,
        phase_tolerance=PHASE_TOLERANCE
    )
    for i in range(6)
}

# Create proton and neutron identities
identity_P = ETMNode("identity_P", initial_tick=0, phase=0.25)
identity_N = ETMNode("identity_N", initial_tick=0, phase=0.25)
identity_P.phase_increment = DELTA_PHI
identity_N.phase_increment = DELTA_PHI
identity_P.set_ancestry(ANCESTRY_P)
identity_N.set_ancestry(ANCESTRY_N)

# Tick loop with logging
tick_log = []

for t in range(TOTAL_TICKS):
    # Pre-drop reinforcement
    if t < DROP_TICK:
        for rec in recruiters.values():
            rec.receive_echo(ANCESTRY_P, PHASE_Z, RECRUITER_STRENGTH)
            rec.receive_echo(ANCESTRY_N, PHASE_Z, RECRUITER_STRENGTH)

    # Drop both identities into phase-aligned state
    if t == DROP_TICK:
        identity_P.phase = PHASE_Z
        identity_N.phase = PHASE_Z

    identity_P.tick_forward()
    identity_N.tick_forward()

    tick_log.append({
        "tick": t + 1,
        "identity_P_phase": round(identity_P.phase % 1.0, 6),
        "identity_N_phase": round(identity_N.phase % 1.0, 6),
        "recruiter_avg_phase": round(sum(r.target_phase for r in recruiters.values()) / len(recruiters), 6),
        "drop_event": t == DROP_TICK
    })

# Save to the proper results folder in the parent directory
output_dir = os.path.join(os.path.dirname(os.getcwd()), "results")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "trial_055_summary.json"), "w") as f:
    json.dump({
        "trial": "055",
        "drop_tick": DROP_TICK,
        "ancestry_P": ANCESTRY_P,
        "ancestry_N": ANCESTRY_N,
        "phase_tolerance": PHASE_TOLERANCE,
        "reinforcement_strength": RECRUITER_STRENGTH
    }, f, indent=2)

with open(os.path.join(output_dir, "transition_log_trial055.json"), "w") as f:
    json.dump(tick_log, f, indent=2)

print("✓ Trial 055 complete. Results written to '../results/' folder.")
