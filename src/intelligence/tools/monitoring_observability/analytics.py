from typing import List, Dict, Any
from .schema import MetricRecord, AlertRecord, TraceSpan

class MonitoringAnalyticsRegistry:
    def compute_sla_compliance(self, spans: List[TraceSpan], threshold_ms: float = 2000.0) -> float:
        if not spans:
            return 100.0
        success_spans = [s for s in spans if s.duration_ms is not None and s.duration_ms <= threshold_ms]
        return (len(success_spans) / len(spans)) * 100.0

    def compute_percentiles(self, spans: List[TraceSpan]) -> Dict[str, float]:
        durations = sorted([s.duration_ms for s in spans if s.duration_ms is not None])
        if not durations:
            return {"P50": 0.0, "P95": 0.0, "P99": 0.0}
        n = len(durations)
        return {
            "P50": durations[int(n * 0.50)],
            "P95": durations[int(n * 0.95)],
            "P99": durations[int(n * 0.99)]
        }
