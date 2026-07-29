from abc import ABC, abstractmethod
from typing import Any, Dict
from ..schema import MetricResult

class EvaluationStrategy(ABC):
    @abstractmethod
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        """Run standard evaluation check and return MetricResult."""
        pass
