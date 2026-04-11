import math

class StrategyEngine:
    """
    Core logic for predicting pit stops and tyre strategies based on 
    current race state and historical degradation data.
    """
    def __init__(self, total_laps=57):
        self.total_laps = total_laps
        
        # Estimated useful life for compounds (laps) before major drop-off
        self.tyre_data = {
            "SOFT": {"max_life": 20, "optimum_range": (12, 18)},
            "MEDIUM": {"max_life": 32, "optimum_range": (20, 28)},
            "HARD": {"max_life": 50, "optimum_range": (35, 45)},
            "INTER": {"max_life": 25, "optimum_range": (15, 22)},
            "WET": {"max_life": 20, "optimum_range": (12, 18)},
            "UNKNOWN": {"max_life": 25, "optimum_range": (15, 20)}
        }

    def find_optimum_strategy(self, curr_lap, current_compound):
        """
        Calculates the best remaining stint plan.
        Returns: (best_stints, score)
        best_stints format: [('TYRE', laps_in_stint), ('TYRE', laps_in_stint)]
        """
        remaining_laps = self.total_laps - curr_lap
        if remaining_laps <= 0:
            return [], 0

        data = self.tyre_data.get(current_compound, self.tyre_data["UNKNOWN"])
        
        # 1. Determine how much longer to stay on current tyre
        # For this sim, we aim for the middle of the 'optimum' window
        target_pit_lap = data["optimum_range"][1] 
        # Duration is how many laps from NOW until we pit
        # This is a simplification; a real engine would check tyre age (data['tyre_life'])
        stint0_duration = max(1, target_pit_lap - 10) # Placeholder logic
        
        # Ensure we don't predict a pit stop after the race is over
        if stint0_duration >= remaining_laps:
            return [(current_compound, remaining_laps)], 100

        # 2. Decide the next compound (Simplification: Medium -> Hard, Soft -> Medium)
        if current_compound == "SOFT":
            next_compound = "MEDIUM"
        elif current_compound == "MEDIUM":
            next_compound = "HARD"
        else:
            next_compound = "MEDIUM"

        # Construct the stint list
        # Stint 0: Current tyre remaining laps
        # Stint 1: Next tyre until finish
        best_stints = [
            (current_compound, stint0_duration),
            (next_compound, remaining_laps - stint0_duration)
        ]

        return best_stints, 1.0