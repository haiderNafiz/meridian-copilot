from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ComponentHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RECOVERING = "recovering"

class EventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class MonitoredComponent(BaseModel):
    component_id: str
    component_type: str
    version: str = "v1"
    health_status: ComponentHealth = ComponentHealth.HEALTHY
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MonitoringEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    correlation_id: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    severity: EventSeverity = EventSeverity.INFO
    payload: Dict[str, Any] = Field(default_factory=dict)

class MetricRecord(BaseModel):
    metric_name: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: str
    tags: Dict[str, str] = Field(default_factory=dict)

class AlertPolicyConfig(BaseModel):
    cooldown_seconds: int = 300
    deduplication_key: Optional[str] = None
    suppression_rules: List[str] = Field(default_factory=list)
    escalation_channel: Optional[str] = None
    grouping_key: Optional[str] = None

class AlertRecord(BaseModel):
    alert_id: str
    policy_name: str
    message: str
    severity: EventSeverity
    timestamp: str
    triggered_by_event_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TraceSpan(BaseModel):
    span_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    operation_name: str
    start_time: str
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    status: str = "success"
    tags: Dict[str, str] = Field(default_factory=dict)
    events: List[MonitoringEvent] = Field(default_factory=list)

class MonitoringResponse(BaseModel):
    status: str
    message: Optional[str] = None
    component: Optional[MonitoredComponent] = None
    events: Optional[List[MonitoringEvent]] = None
    metrics: Optional[List[MetricRecord]] = None
    alerts: Optional[List[AlertRecord]] = None
    span: Optional[TraceSpan] = None
    analytics_summary: Optional[Dict[str, Any]] = None
    dashboard_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
