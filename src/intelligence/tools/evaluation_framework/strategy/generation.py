from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class GenerationStrategy(EvaluationStrategy):
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        p_str = str(prediction).lower()
        t_str = str(target).lower()
        score = 1.0 if t_str in p_str or p_str in t_str else 0.0
        return MetricResult(
            metric_name="generation_similarity",
            score=score,
            passed=(score >= 0.5)
        )
