import datetime
from typing import List, Dict, Optional, Callable
from .schema import MetricRecord, MetricType

class MetricRegistry:
    def __init__(self, on_record: Optional[Callable[[MetricRecord], None]] = None):
        self._metrics: List[MetricRecord] = []
        self.on_record = on_record

    def record(self, record: MetricRecord) -> None:
        self._metrics.append(record)
        if self.on_record:
            self.on_record(record)

    def counter(self, name: str, value: float = 1.0, unit: str = "count", tags: Optional[Dict[str, str]] = None) -> MetricRecord:
        rec = MetricRecord(
            metric_name=name,
            metric_type=MetricType.COUNTER,
            value=value,
            unit=unit,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            tags=tags or {}
        )
        self.record(rec)
        return rec

    def gauge(self, name: str, value: float, unit: str = "ratio", tags: Optional[Dict[str, str]] = None) -> MetricRecord:
        rec = MetricRecord(
            metric_name=name,
            metric_type=MetricType.GAUGE,
            value=value,
            unit=unit,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            tags=tags or {}
        )
        self.record(rec)
        return rec

    def histogram(self, name: str, value: float, unit: str = "bytes", tags: Optional[Dict[str, str]] = None) -> MetricRecord:
        rec = MetricRecord(
            metric_name=name,
            metric_type=MetricType.HISTOGRAM,
            value=value,
            unit=unit,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            tags=tags or {}
        )
        self.record(rec)
        return rec

    def timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None) -> MetricRecord:
        rec = MetricRecord(
            metric_name=name,
            metric_type=MetricType.TIMER,
            value=duration_ms,
            unit="ms",
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            tags=tags or {}
        )
        self.record(rec)
        return rec

    def list_all_metrics(self) -> List[MetricRecord]:
        return self._metrics
