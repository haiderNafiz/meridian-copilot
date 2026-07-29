from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class RankingStrategy(EvaluationStrategy):
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        score = 0.0
        if isinstance(prediction, list) and isinstance(target, list):
            found_count = sum(1 for x in target if x in prediction)
            score = found_count / len(target) if target else 1.0
            
        return MetricResult(
            metric_name="ranking_recall",
            score=score,
            passed=(score >= 0.7)
        )
