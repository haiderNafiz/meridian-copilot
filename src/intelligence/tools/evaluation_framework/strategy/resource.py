from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class ResourceStrategy(EvaluationStrategy):
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        duration = 0.0
        if context and "resource" in context:
            duration = getattr(context["resource"], "duration_ms", 0.0)
            
        passed = (duration <= 5000.0)
        return MetricResult(
            metric_name="latency_check",
            score=duration,
            passed=passed
        )
