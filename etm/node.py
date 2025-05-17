"""
ETM Core Node Module
This file defines the basic node object for the Euclidean Timing Mechanics simulation framework.

Each node represents a local rhythm point in the timing lattice.
Nodes are responsible for:
- Maintaining a tick counter
- Managing phase
- Handling ancestry
- Updating memory
"""

import math
import json
import os

class ETMNode:
    def __init__(self, node_id, initial_tick=0, phase=0.0, memory_decay=0.98):
        self.node_id = node_id
        self.tick = initial_tick
        self.phase = phase  # Value in [0, 1)
        self.memory = 1.0   # Memory starts full and decays
        self.memory_decay = memory_decay
        self.ancestry_tag = None
        self.coherence_score = 0.0
        self.history = []

    def tick_forward(self, delta_phase=0.05):
        """Advance time and phase"""
        self.tick += 1
        self.phase = (self.phase + delta_phase) % 1.0
        self.memory *= self.memory_decay
        self.record_state()

    def set_ancestry(self, tag):
        """Assign ancestry label (rotor, electron, etc.)"""
        self.ancestry_tag = tag

    def reinforce_memory(self, amount=0.1):
        """Reinforce memory from a photon echo or identity pulse"""
        self.memory = min(1.0, self.memory + amount)

    def get_status(self):
        """Return summary of current node state"""
        return {
            "node_id": self.node_id,
            "tick": self.tick,
            "phase": round(self.phase, 4),
            "memory": round(self.memory, 4),
            "ancestry": self.ancestry_tag,
            "coherence_score": round(self.coherence_score, 4)
        }

    def record_state(self):
        """Log internal state for debug or export"""
        self.history.append(self.get_status())

    def export_summary(self, filepath):
        """Write summary to a JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump({
                "final_state": self.get_status(),
                "history_length": len(self.history)
            }, f, indent=2)

# If run as a test script:
if __name__ == "__main__":
    node = ETMNode(node_id="test_001")
    node.set_ancestry("rotor-A")
    for _ in range(20):
        node.tick_forward()
        if node.tick % 5 == 0:
            node.reinforce_memory(0.2)
    node.export_summary("../results/node_summary.json")
