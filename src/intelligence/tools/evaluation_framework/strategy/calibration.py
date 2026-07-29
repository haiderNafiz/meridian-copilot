from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class CalibrationStrategy(EvaluationStrategy):
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        confidence = 0.9
        if isinstance(prediction, dict):
            confidence = prediction.get("confidence", 0.9)
            pred_val = prediction.get("value")
        else:
            pred_val = prediction
            
        correct = (pred_val == target)
        if correct:
            score = confidence
        else:
            score = 1.0 - confidence
            
        passed = (score >= 0.5)
        return MetricResult(
            metric_name="confidence_calibration",
            score=score,
            passed=passed
        )
