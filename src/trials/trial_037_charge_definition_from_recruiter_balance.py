
# trial_037_charge_definition_from_recruiter_balance.py

"""
Trial 037: Derive ETM Analog of Elementary Charge (e) via Recruiter Field Balance

Goal:
- Simulate two identities at fixed distance with opposing timing strain
- Apply recruiter field between them
- Find the minimal recruiter effort (ETM "charge") needed to balance strain and prevent collapse
- Use this to define an effective e^2 term for use in alpha calculation

This will form the ETM analog of:
    alpha = e^2 / (4 * pi * epsilon_0 * hbar * c)
"""

import sys
import os
sys.path.append(os.path.abspath(".."))

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode

# Constants
PHASE_LEFT = 0.0
PHASE_RIGHT = 0.11  # ETM return window edge
DELTA_PHI = 0.01
RECRUITER_PHASE = 0.055  # midpoint between identities
SUPPORT_TRIALS = [0.01, 0.02, 0.03, 0.04, 0.05]  # sweep support per echo

identity_left = ETMNode("identity_L", initial_tick=0, phase=PHASE_LEFT)
identity_right = ETMNode("identity_R", initial_tick=0, phase=PHASE_RIGHT)

identity_left.phase_increment = DELTA_PHI
identity_right.phase_increment = DELTA_PHI

identity_left.set_ancestry("e-test")
identity_right.set_ancestry("e-test")

results = {}

for support_strength in SUPPORT_TRIALS:
    # Reset recruiter
    recruiter = RecruiterNode(
        node_id="recruiter_center",
        target_ancestry="e-test",
        target_phase=RECRUITER_PHASE,
        phase_tolerance=0.11
    )

    # Reinforce recruiter from both identities for 3 ticks
    for _ in range(3):
        recruiter.receive_echo("e-test", PHASE_LEFT, support_strength)
        recruiter.receive_echo("e-test", PHASE_RIGHT, support_strength)

    # Measure resulting support
    total_support = recruiter.support_score
    results[str(support_strength)] = {
        "recruiter_phase": RECRUITER_PHASE,
        "support_per_echo": support_strength,
        "total_support_accumulated": total_support
    }

# Save results
output_dir = os.path.join(os.getcwd(), "results")
os.makedirs(output_dir, exist_ok=True)

summary_file = os.path.join(output_dir, "trial_037_summary.json")
with open(summary_file, "w") as f:
    json.dump(results, f, indent=2)
    print(f"✓ Wrote: {summary_file}")

print("✓ Trial 037 complete: recruiter balance simulated across timing strain.")
