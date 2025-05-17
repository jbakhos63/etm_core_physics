"""
Trial 001: Identity Lifecycle Test
Simulates a node's modular transition sequence:
A (rotor) → D (identity) → B (decay) → D (reformation)
Uses node, recruiter, and transition modules
"""

import sys
import os
sys.path.append(os.path.abspath(".."))  # Allow import from etm/

import json
from etm.node import ETMNode
from etm.recruiter import RecruiterNode
from etm.transition import TransitionEngine

# Create simulation directory if needed
os.makedirs("../results", exist_ok=True)

# Initialize node and recruiter
node = ETMNode("node_001")
node.set_ancestry("rotor-A")

recruiter = RecruiterNode("rec_001", target_ancestry="rotor-A", target_phase=0.0)
transition_engine = TransitionEngine()

# Step 1: Rotor attempts to fold into stable identity
# Simulate rotor support
for _ in range(3):
    recruiter.receive_echo("rotor-A", 0.01)  # good match

transition = transition_engine.attempt_transition("A", {
    "recruiter_support": recruiter.support_score,
    "ancestry_match": True
})
node_module = transition

# Step 2: Identity undergoes decay due to low reinforcement
if node_module == "D":
    transition = transition_engine.attempt_transition("D", {
        "reinforcement_score": 0.1
    })
    node_module = transition

# Step 3: Neutrino attempts to reform back into identity
if node_module == "B":
    transition = transition_engine.attempt_transition("B", {
        "recruiter_support": 4  # strong field support
    })
    node_module = transition

# Log final state
summary = {
    "final_module": node_module,
    "recruiter_score": recruiter.support_score,
    "node_status": node.get_status(),
    "transition_log_path": "../results/transition_log.json"
}

# Export all logs
with open("../results/trial_001_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

recruiter.export_summary("../results/recruiter_trial001.json")
transition_engine.export_transition_log("../results/transition_log.json")
