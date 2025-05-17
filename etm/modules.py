"""
ETM Modular Identity Logic
Defines identity modules used in ETM:
- Each module represents a distinct state a node can adopt
- Transition rules and recruitment roles are associated with modules
"""

import json

class IdentityModule:
    def __init__(self, label, allows_recruitment, memory_profile, decay_rate, reformation_score=0):
        self.label = label                  # e.g. "A", "D", "S"
        self.allows_recruitment = allows_recruitment  # Can this module recruit others?
        self.memory_profile = memory_profile          # e.g. "reinforced", "decaying", "transitional"
        self.decay_rate = decay_rate                  # Memory decay factor per tick
        self.reformation_score = reformation_score    # Threshold to enable reformation

    def get_rules(self):
        return {
            "label": self.label,
            "recruitment": self.allows_recruitment,
            "memory_profile": self.memory_profile,
            "decay_rate": self.decay_rate,
            "reformation_score": self.reformation_score
        }

    def describe(self):
        return f"Module {self.label}: recruitment={self.allows_recruitment}, memory='{self.memory_profile}', decay={self.decay_rate}, score={self.reformation_score}"

# Define some key modules
MODULE_LIBRARY = {
    "A": IdentityModule("A", allows_recruitment=True, memory_profile="rotor", decay_rate=0.99),
    "B": IdentityModule("B", allows_recruitment=False, memory_profile="neutrino", decay_rate=1.0),
    "C": IdentityModule("C", allows_recruitment=False, memory_profile="decayed", decay_rate=0.90),
    "D": IdentityModule("D", allows_recruitment=True, memory_profile="stable_mass", decay_rate=0.95),
    "P": IdentityModule("P", allows_recruitment=True, memory_profile="proton", decay_rate=0.97),
    "N": IdentityModule("N", allows_recruitment=True, memory_profile="neutron", decay_rate=0.96),
    "S": IdentityModule("S", allows_recruitment=False, memory_profile="scaffold", decay_rate=0.94)
}

def export_module_table(filepath):
    with open(filepath, 'w') as f:
        json.dump({label: mod.get_rules() for label, mod in MODULE_LIBRARY.items()}, f, indent=2)

# Run test export
if __name__ == "__main__":
    export_module_table("../results/module_table.json")
