"""
ETM Recruiter Node Logic
This module defines the logic for recruiter nodes, which:
- Monitor ancestry and rhythm
- Evaluate incoming support from echo sources
- Decide whether to support identity reformation
"""

import json

class RecruiterNode:
    def __init__(self, node_id, target_ancestry, target_phase, phase_tolerance=0.05):
        self.node_id = node_id
        self.target_ancestry = target_ancestry
        self.target_phase = target_phase  # Expected phase for alignment
        self.phase_tolerance = phase_tolerance
        self.support_score = 0
        self.memory = 1.0
        self.echo_log = []

    def receive_echo(self, ancestry, phase, strength=1.0):
        """Receive an echo and decide whether to support"""
        ancestry_match = (ancestry == self.target_ancestry)
        phase_match = abs((phase - self.target_phase + 1.0) % 1.0) <= self.phase_tolerance

        support = 1 if ancestry_match and phase_match else 0

        self.support_score += support * strength
        self.memory *= 0.97  # Simulate memory decay
        self.echo_log.append({
            "tick": len(self.echo_log) + 1,
            "ancestry": ancestry,
            "phase": round(phase, 4),
            "ancestry_match": ancestry_match,
            "phase_match": phase_match,
            "support_added": support
        })

    def get_summary(self):
        return {
            "node_id": self.node_id,
            "target_ancestry": self.target_ancestry,
            "target_phase": round(self.target_phase, 4),
            "support_score": self.support_score,
            "memory": round(self.memory, 4),
            "echoes_received": len(self.echo_log)
        }

    def export_summary(self, filepath):
        with open(filepath, 'w') as f:
            json.dump({
                "final_state": self.get_summary(),
                "echo_log": self.echo_log
            }, f, indent=2)

# Run a test case if script is executed directly
if __name__ == "__main__":
    recruiter = RecruiterNode("rec_001", target_ancestry="rotor-A", target_phase=0.0)

    # Simulate incoming echoes
    echoes = [
        ("rotor-A", 0.01),  # close match
        ("rotor-B", 0.02),  # ancestry mismatch
        ("rotor-A", 0.12),  # phase mismatch
        ("rotor-A", 0.98),  # wraparound match
    ]

    for ancestry, phase in echoes:
        recruiter.receive_echo(ancestry, phase)

    recruiter.export_summary("../results/recruiter_summary.json")
