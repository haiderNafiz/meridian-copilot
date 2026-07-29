import datetime
import uuid
from typing import Optional, List, Dict, Any
from .schema import MonitoredComponent, MonitoringEvent, MetricRecord, AlertRecord, TraceSpan
from .registry import MonitoringRegistry
from .metrics import MetricRegistry
from .event import EventDispatcher
from .trace import TraceContext
from .alert.engine import AlertingEngine
from .provider.base import StorageProvider
from .provider.file import LocalFilesystemStorageProvider

class MonitoringService:
    def __init__(self, provider: Optional[StorageProvider] = None):
        self.provider = provider or LocalFilesystemStorageProvider()
        self.registry = MonitoringRegistry()
        self.metrics = MetricRegistry(on_record=self.provider.save_metric)
        self.events = EventDispatcher()
        self.tracing = TraceContext(on_span_end=self.provider.save_span)
        self.alerts = AlertingEngine()
        
        self.events.register_listener(self.provider.save_event)

    def log_event(self, event_type: str, severity: str, payload: Dict[str, Any], correlation_id: Optional[str] = None, trace_id: Optional[str] = None, span_id: Optional[str] = None) -> MonitoringEvent:
        event = MonitoringEvent(
            event_id=f"evt_{uuid.uuid4().hex[:10]}",
            event_type=event_type,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:10]}",
            trace_id=trace_id,
            span_id=span_id,
            severity=severity,
            payload=payload
        )
        self.events.dispatch(event)
        
        triggered_alerts = self.alerts.evaluate_policies(self.metrics.list_all_metrics(), self.provider.load_events())
        for alert in triggered_alerts:
            self.provider.save_alert(alert)
            
        return event

    def log_metric(self, name: str, category: str, value: float, unit: str, tags: Optional[Dict[str, str]] = None) -> MetricRecord:
        record = self.metrics.gauge(name, value, unit, tags)
        return record

_service_instance = None

def get_monitoring_service() -> MonitoringService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MonitoringService()
    return _service_instance
