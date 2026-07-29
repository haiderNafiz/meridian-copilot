from typing import Any, Dict
from .base import EvaluationStrategy
from ..schema import MetricResult

class ExplainabilityStrategy(EvaluationStrategy):
    def evaluate(self, prediction: Any, target: Any, context: Dict[str, Any] = None) -> MetricResult:
        score = 0.0
        details = {}
        if isinstance(prediction, dict):
            explanation = prediction.get("explanation", "")
            evidence = prediction.get("evidence", [])
            
            if explanation and len(explanation) > 10:
                score = 1.0
                if evidence and any(e.lower() in explanation.lower() for e in evidence):
                    score = 1.0
                else:
                    score = 0.8
                    
        passed = (score >= 0.7)
        return MetricResult(
            metric_name="evidence_coverage",
            score=score,
            passed=passed,
            details=details
        )
