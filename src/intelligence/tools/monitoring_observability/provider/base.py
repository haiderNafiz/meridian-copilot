from abc import ABC, abstractmethod
from typing import List
from ..schema import MonitoringEvent, MetricRecord, AlertRecord, TraceSpan

class StorageProvider(ABC):
    @abstractmethod
    def save_event(self, event: MonitoringEvent) -> None: pass

    @abstractmethod
    def save_metric(self, metric: MetricRecord) -> None: pass

    @abstractmethod
    def save_alert(self, alert: AlertRecord) -> None: pass

    @abstractmethod
    def save_span(self, span: TraceSpan) -> None: pass

    @abstractmethod
    def load_events(self) -> List[MonitoringEvent]: pass

    @abstractmethod
    def load_metrics(self) -> List[MetricRecord]: pass

    @abstractmethod
    def load_alerts(self) -> List[AlertRecord]: pass

    @abstractmethod
    def load_spans(self) -> List[TraceSpan]: pass
