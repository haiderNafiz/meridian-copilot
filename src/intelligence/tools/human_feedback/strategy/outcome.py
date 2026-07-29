from typing import Any, Dict
from .base import FeedbackStrategy

class OutcomeStrategy(FeedbackStrategy):
    def validate(self, payload: Any) -> bool:
        if isinstance(payload, dict) and "verified" in payload:
            return isinstance(payload["verified"], bool)
        return False

    def normalize(self, payload: Any) -> Dict[str, Any]:
        return {"verified": bool(payload.get("verified")), "details": payload.get("details", {})}
