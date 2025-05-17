"""
ETM Modular Transition Logic (Corrected for Trial 006)

Handles transitions between identity modules:
- Folding into stable identity (e.g., A → D)
- Decay into neutrino or null state (e.g., D → B or D → C)
- Return or reformation based on recruiter support and timing

Updated to require tick_phase_match for B → D transitions (Trial 006+)
"""

import json

class TransitionEngine:
    def __init__(self):
        self.log = []

    def attempt_transition(self, current_module, conditions):
        result = {
            "from": current_module,
            "to": current_module,
            "conditions": conditions,
            "success": False
        }

        if current_module == "A":
            if conditions.get("recruiter_support", 0) > 2 and conditions.get("ancestry_match", False):
                result["to"] = "D"
                result["success"] = True

        elif current_module == "D":
            if conditions.get("reinforcement_score", 0) < 0.2:
                result["to"] = "B"
                result["success"] = True
            elif conditions.get("tick_phase_match", False) and conditions.get("recruiter_support", 0) > 1:
                result["to"] = "D"
                result["success"] = True

        elif current_module == "B":
            # UPDATED: Return to D only if recruiter support and timing both align
            if (
                conditions.get("recruiter_support", 0) > 3 and
                conditions.get("tick_phase_match", False)
            ):
                result["to"] = "D"
                result["success"] = True

        elif current_module == "C":
            result["to"] = "C"  # Decayed terminal

        self.log.append(result)
        return result["to"]

    def export_transition_log(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.log, f, indent=2)

# Test export (optional for direct script run)
if __name__ == "__main__":
    engine = TransitionEngine()
    engine.export_transition_log("transition_log_example.json")
