from typing import List

class MetricAggregator:
    @staticmethod
    def aggregate(scores: List[float], method: str = "macro") -> float:
        if not scores:
            return 0.0
            
        if method == "worst_case":
            return min(scores)
        elif method == "weighted":
            # Default weighting logic placeholder
            return sum(scores) / len(scores)
        else: # Default macro average
            return sum(scores) / len(scores)
