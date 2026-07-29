import os
import json
from typing import List, Optional
from .base import StorageProvider
from ..schema import MonitoringEvent, MetricRecord, AlertRecord, TraceSpan

class LocalFilesystemStorageProvider(StorageProvider):
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../../observability_platform")
            )
        else:
            self.base_dir = os.path.abspath(base_dir)

        os.makedirs(self.base_dir, exist_ok=True)
        self.events_file = os.path.join(self.base_dir, "events.jsonl")
        self.metrics_file = os.path.join(self.base_dir, "metrics.jsonl")
        self.alerts_file = os.path.join(self.base_dir, "alerts.jsonl")
        self.spans_file = os.path.join(self.base_dir, "spans.jsonl")

    def save_event(self, event: MonitoringEvent) -> None:
        self._append_jsonl(self.events_file, event.model_dump())

    def save_metric(self, metric: MetricRecord) -> None:
        self._append_jsonl(self.metrics_file, metric.model_dump())

    def save_alert(self, alert: AlertRecord) -> None:
        self._append_jsonl(self.alerts_file, alert.model_dump())

    def save_span(self, span: TraceSpan) -> None:
        self._append_jsonl(self.spans_file, span.model_dump())

    def load_events(self) -> List[MonitoringEvent]:
        data = self._read_jsonl(self.events_file)
        return [MonitoringEvent.model_validate(d) for d in data]

    def load_metrics(self) -> List[MetricRecord]:
        data = self._read_jsonl(self.metrics_file)
        return [MetricRecord.model_validate(d) for d in data]

    def load_alerts(self) -> List[AlertRecord]:
        data = self._read_jsonl(self.alerts_file)
        return [AlertRecord.model_validate(d) for d in data]

    def load_spans(self) -> List[TraceSpan]:
        data = self._read_jsonl(self.spans_file)
        return [TraceSpan.model_validate(d) for d in data]

    def _append_jsonl(self, filepath: str, data: dict) -> None:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def _read_jsonl(self, filepath: str) -> List[dict]:
        if not os.path.exists(filepath):
            return []
        items = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    try:
                        items.append(json.loads(line_str))
                    except Exception:
                        pass
        return items
