from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class FairnessStrategy(EvaluationStrategy):
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        score = 1.0
        details = {}
        if context and "fairness_delta" in context:
            score = context["fairness_delta"]
            
        passed = (score >= 0.9)
        return MetricResult(
            metric_name="demographic_parity",
            score=score,
            passed=passed,
            details=details
        )
