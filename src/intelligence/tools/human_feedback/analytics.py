from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
from .schema import FeedbackRecord

class FeedbackMetric(ABC):
    @abstractmethod
    def calculate(self, records: List[FeedbackRecord]) -> Any:
        """Run calculations on feedback records list."""
        pass

class AgreementRateMetric(FeedbackMetric):
    def calculate(self, records: List[FeedbackRecord]) -> float:
        if not records:
            return 1.0
        ratings = [
            r.feedback_payload.get("score") 
            for r in records 
            if isinstance(r.feedback_payload, dict) and "score" in r.feedback_payload
        ]
        if not ratings:
            return 1.0
        avg = sum(ratings) / len(ratings)
        agreed = sum(1 for x in ratings if abs(x - avg) <= 0.75)
        return round(agreed / len(ratings), 2)

class CorrectionFrequencyMetric(FeedbackMetric):
    def calculate(self, records: List[FeedbackRecord]) -> float:
        if not records:
            return 0.0
        from .schema import FeedbackType
        corrections = sum(1 for r in records if r.feedback_type == FeedbackType.CORRECTION)
        return round(corrections / len(records), 2)

class AnalyticsRegistry:
    def __init__(self):
        self._metrics: Dict[str, FeedbackMetric] = {
            "agreement_rate": AgreementRateMetric(),
            "correction_frequency": CorrectionFrequencyMetric()
        }

    def register_metric(self, name: str, metric: FeedbackMetric):
        self._metrics[name] = metric

    def compute_all(self, records: List[FeedbackRecord]) -> Dict[str, Any]:
        results = {}
        for name, metric in self._metrics.items():
            try:
                results[name] = metric.calculate(records)
            except Exception:
                results[name] = None
        return results
