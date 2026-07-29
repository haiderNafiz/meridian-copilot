from typing import Any, Dict
from .base import FeedbackStrategy

class PreferenceStrategy(FeedbackStrategy):
    def validate(self, payload: Any) -> bool:
        if isinstance(payload, dict) and "preferred_id" in payload:
            return "alternative_id" in payload
        return False

    def normalize(self, payload: Any) -> Dict[str, Any]:
        return {
            "preferred_id": str(payload.get("preferred_id")),
            "alternative_id": str(payload.get("alternative_id")),
            "reason": payload.get("reason", "")
        }
