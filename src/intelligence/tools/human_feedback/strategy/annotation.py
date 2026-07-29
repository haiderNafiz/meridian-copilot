from typing import Any, Dict
from .base import FeedbackStrategy

class AnnotationStrategy(FeedbackStrategy):
    def validate(self, payload: Any) -> bool:
        if isinstance(payload, dict) and "tags" in payload:
            return isinstance(payload["tags"], list)
        return False

    def normalize(self, payload: Any) -> Dict[str, Any]:
        tags = [str(t).strip() for t in payload.get("tags", [])]
        return {"tags": tags, "notes": payload.get("notes", "")}
