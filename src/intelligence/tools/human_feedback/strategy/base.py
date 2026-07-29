from abc import ABC, abstractmethod
from typing import Any, Dict

class FeedbackStrategy(ABC):
    @abstractmethod
    def validate(self, payload: Any) -> bool:
        """Validate if the feedback payload conforms to expected schema formats."""
        pass

    @abstractmethod
    def normalize(self, payload: Any) -> Dict[str, Any]:
        """Normalize payload values into standard comparable structures."""
        pass
