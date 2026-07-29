from abc import ABC, abstractmethod
from typing import List, Optional
from ..schema import AlertRecord, MetricRecord, MonitoringEvent, AlertPolicyConfig

class AlertPolicyStrategy(ABC):
    def __init__(self, config: Optional[AlertPolicyConfig] = None):
        self.config = config or AlertPolicyConfig()

    @abstractmethod
    def evaluate(self, metrics: List[MetricRecord], events: List[MonitoringEvent]) -> Optional[AlertRecord]:
        """Verify thresholds or regressions across metrics/events logs."""
        pass
