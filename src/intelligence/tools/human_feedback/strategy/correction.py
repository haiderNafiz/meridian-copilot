from typing import Any, Dict
from .base import FeedbackStrategy

class CorrectionStrategy(FeedbackStrategy):
    def validate(self, payload: Any) -> bool:
        if isinstance(payload, dict) and "corrected_output" in payload:
            return True
        return False

    def normalize(self, payload: Any) -> Dict[str, Any]:
        return {"corrected_output": payload.get("corrected_output"), "comment": payload.get("comment", "")}
