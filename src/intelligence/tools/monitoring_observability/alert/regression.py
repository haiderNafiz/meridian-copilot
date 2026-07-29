import uuid
import datetime
from typing import List, Optional
from .base import AlertPolicyStrategy
from ..schema import AlertRecord, MetricRecord, MonitoringEvent, EventSeverity

class EvaluationRegressionPolicy(AlertPolicyStrategy):
    def __init__(self, min_score: float, **kwargs):
        super().__init__(**kwargs)
        self.min_score = min_score

    def evaluate(self, metrics: List[MetricRecord], events: List[MonitoringEvent]) -> Optional[AlertRecord]:
        for m in metrics:
            if m.metric_name == "evaluation_score" and m.value < self.min_score:
                return AlertRecord(
                    alert_id=f"alt_{uuid.uuid4().hex[:10]}",
                    policy_name="EvaluationRegression",
                    message=f"Evaluation score dropped: {m.value} < {self.min_score}",
                    severity=EventSeverity.CRITICAL,
                    timestamp=datetime.datetime.now(datetime.UTC).isoformat()
                )
        return None
