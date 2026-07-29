import time
from typing import List, Dict
from .base import AlertPolicyStrategy
from ..schema import AlertRecord, MetricRecord, MonitoringEvent

class AlertingEngine:
    def __init__(self):
        self._policies: List[AlertPolicyStrategy] = []
        self._last_triggered: Dict[str, float] = {}

    def register_policy(self, policy: AlertPolicyStrategy) -> None:
        self._policies.append(policy)

    def evaluate_policies(self, metrics: List[MetricRecord], events: List[MonitoringEvent]) -> List[AlertRecord]:
        alerts = []
        now = time.time()
        for policy in self._policies:
            policy_name = policy.__class__.__name__
            
            # Cooldown check
            cooldown = getattr(policy.config, "cooldown_seconds", 300)
            if policy_name in self._last_triggered:
                if now - self._last_triggered[policy_name] < cooldown:
                    continue
                    
            alert = policy.evaluate(metrics, events)
            if alert:
                self._last_triggered[policy_name] = now
                alerts.append(alert)
        return alerts
