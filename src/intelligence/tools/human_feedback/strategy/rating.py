from typing import Any, Dict
from .base import FeedbackStrategy

class RatingStrategy(FeedbackStrategy):
    def validate(self, payload: Any) -> bool:
        if isinstance(payload, dict) and "score" in payload:
            return isinstance(payload["score"], (int, float))
        return False

    def normalize(self, payload: Any) -> Dict[str, Any]:
        score = float(payload.get("score", 0.0))
        score = max(0.0, min(5.0, score))
        return {"score": score}
