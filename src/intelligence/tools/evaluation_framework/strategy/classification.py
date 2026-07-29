from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class ClassificationStrategy(EvaluationStrategy):
    def __init__(self, metric_name: str = "accuracy", threshold: float = 0.8):
        self.metric_name = metric_name
        self.threshold = threshold

    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        # Check exact equality for labels, or custom comparison logic
        correct = (prediction == target)
        score = 1.0 if correct else 0.0
        passed = (score >= self.threshold)
        
        return MetricResult(
            metric_name=self.metric_name,
            score=score,
            passed=passed,
            details={"prediction": str(prediction), "expected": str(target)}
        )
