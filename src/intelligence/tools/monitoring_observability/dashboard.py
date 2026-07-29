from typing import Dict, Any, List
from .schema import MonitoringEvent, MetricRecord, AlertRecord, TraceSpan
from .analytics import MonitoringAnalyticsRegistry

class DashboardDataAggregator:
    def __init__(self, analytics_registry: MonitoringAnalyticsRegistry):
        self.analytics = analytics_registry

    def compile_dashboard_summary(self, events: List[MonitoringEvent], metrics: List[MetricRecord], alerts: List[AlertRecord], spans: List[TraceSpan]) -> Dict[str, Any]:
        sla = self.analytics.compute_sla_compliance(spans)
        percentiles = self.analytics.compute_percentiles(spans)
        errors_count = sum(1 for e in events if e.severity in ["error", "critical"])
        
        return {
            "sla_compliance_pct": sla,
            "percentiles": percentiles,
            "total_events": len(events),
            "total_metrics": len(metrics),
            "total_alerts": len(alerts),
            "total_spans": len(spans),
            "errors_count": errors_count
        }
