import uuid
import datetime
from typing import List, Optional
from .base import AlertPolicyStrategy
from ..schema import AlertRecord, MetricRecord, MonitoringEvent, EventSeverity

class LatencyThresholdPolicy(AlertPolicyStrategy):
    def __init__(self, limit_ms: float, **kwargs):
        super().__init__(**kwargs)
        self.limit_ms = limit_ms

    def evaluate(self, metrics: List[MetricRecord], events: List[MonitoringEvent]) -> Optional[AlertRecord]:
        for m in metrics:
            if m.metric_name == "latency" and m.value > self.limit_ms:
                return AlertRecord(
                    alert_id=f"alt_{uuid.uuid4().hex[:10]}",
                    policy_name="LatencyThreshold",
                    message=f"Latency exceeded threshold: {m.value}ms > {self.limit_ms}ms",
                    severity=EventSeverity.WARNING,
                    timestamp=datetime.datetime.now(datetime.UTC).isoformat()
                )
        return None
