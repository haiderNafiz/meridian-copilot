from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class CostStrategy(EvaluationStrategy):
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        score = 0.0
        if isinstance(prediction, dict):
            score = prediction.get("estimated_cost", 0.0)
        elif context and "cost" in context:
            score = getattr(context["cost"], "estimated_cost", 0.0)
            
        passed = (score <= 0.05)
        return MetricResult(
            metric_name="cost_check",
            score=score,
            passed=passed
        )
