from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class RobustnessStrategy(EvaluationStrategy):
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        text = str(prediction).lower()
        has_error = "error" in text or "exception" in text or "fail" in text
        score = 0.0 if has_error else 1.0
        return MetricResult(
            metric_name="robustness_stability",
            score=score,
            passed=(score == 1.0),
            details={"has_error": has_error}
        )
