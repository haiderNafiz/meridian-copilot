from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .schema import FeedbackRecord, FeedbackType

class ConsensusStrategy(ABC):
    @abstractmethod
    def resolve(self, feedback_records: List[FeedbackRecord]) -> Dict[str, Any]:
        """Aggregate reviewer scores and return agreement indicators."""
        pass

class RatingConsensus(ConsensusStrategy):
    def resolve(self, feedback_records: List[FeedbackRecord]) -> Dict[str, Any]:
        ratings = [
            r.feedback_payload.get("score") 
            for r in feedback_records 
            if isinstance(r.feedback_payload, dict) and "score" in r.feedback_payload
        ]
        if not ratings:
            return {"consensus": True, "average_score": 0.0, "agreement_rate": 1.0, "total_reviews": 0}
            
        avg = sum(ratings) / len(ratings)
        max_diff = max(ratings) - min(ratings)
        agreement = (max_diff <= 1.0)
        return {
            "consensus": agreement,
            "average_score": round(avg, 2),
            "agreement_rate": 1.0 if agreement else 0.0,
            "total_reviews": len(ratings)
        }

class OutcomeConsensus(ConsensusStrategy):
    def resolve(self, feedback_records: List[FeedbackRecord]) -> Dict[str, Any]:
        votes = [
            r.feedback_payload.get("verified") 
            for r in feedback_records 
            if isinstance(r.feedback_payload, dict) and "verified" in r.feedback_payload
        ]
        if not votes:
            return {"consensus": True, "verified_ratio": 0.0, "agreement_rate": 1.0, "total_reviews": 0}
            
        positive = sum(1 for v in votes if v)
        ratio = positive / len(votes)
        
        agreement = (positive == 0 or positive == len(votes))
        return {
            "consensus": agreement,
            "verified_ratio": round(ratio, 2),
            "agreement_rate": 1.0 if agreement else (ratio if ratio >= 0.5 else 1.0 - ratio),
            "total_reviews": len(votes)
        }

class ConsensusRegistry:
    def __init__(self):
        self._strategies = {
            FeedbackType.RATING: RatingConsensus(),
            FeedbackType.OUTCOME: OutcomeConsensus()
        }

    def resolve(self, feedback_type: FeedbackType, records: List[FeedbackRecord]) -> Dict[str, Any]:
        strategy = self._strategies.get(feedback_type)
        if strategy:
            return strategy.resolve(records)
            
        if not records:
            return {"consensus": True, "agreement_rate": 1.0, "total_reviews": 0}
        first = records[0].feedback_payload
        matching = sum(1 for r in records if r.feedback_payload == first)
        agreement = (matching == len(records))
        return {
            "consensus": agreement,
            "agreement_rate": round(matching / len(records), 2),
            "total_reviews": len(records)
        }
