import pytest
from src.intelligence.tools.monitoring_observability.schema import (
    TraceSpan, MetricRecord, MetricType, MonitoringEvent, EventSeverity, MonitoredComponent, ComponentHealth
)

def test_observability_schemas():
    component = MonitoredComponent(
        component_id="agent_x",
        component_type="agent",
        version="v1",
        health_status=ComponentHealth.HEALTHY
    )
    assert component.component_id == "agent_x"

    event = MonitoringEvent(
        event_id="e1",
        event_type="request_started",
        timestamp="2026-07-30",
        correlation_id="c1",
        severity=EventSeverity.INFO
    )
    assert event.event_id == "e1"

    metric = MetricRecord(
        metric_name="latency",
        metric_type=MetricType.TIMER,
        value=150.0,
        unit="ms",
        timestamp="2026-07-30"
    )
    assert metric.value == 150.0

def test_registry_and_metrics():
    from src.intelligence.tools.monitoring_observability.registry import MonitoringRegistry
    from src.intelligence.tools.monitoring_observability.metrics import MetricRegistry
    
    reg = MonitoringRegistry()
    comp = MonitoredComponent(component_id="tool_y", component_type="tool")
    reg.register_component(comp)
    assert reg.get_component("tool_y") is not None
    
    reg.update_health("tool_y", ComponentHealth.DEGRADED)
    assert reg.get_component("tool_y").health_status == ComponentHealth.DEGRADED
    
    m_reg = MetricRegistry()
    m_reg.counter("api_calls", 1.0)
    m_reg.gauge("cpu_usage", 0.45)
    m_reg.timer("db_query", 45.5)
    
    metrics = m_reg.list_all_metrics()
    assert len(metrics) == 3
    assert metrics[0].metric_name == "api_calls"
    assert metrics[1].metric_type == MetricType.GAUGE
    assert metrics[2].unit == "ms"

@pytest.mark.anyio
async def test_tracing_context_and_decorator():
    from src.intelligence.tools.monitoring_observability.trace import TraceContext, trace_operation
    from src.intelligence.tools.monitoring_observability.service import get_monitoring_service
    
    trace_ctx = TraceContext()
    
    with trace_ctx.trace("query_es") as span:
        assert span.operation_name == "query_es"
        assert span.status == "success"
        
    assert span.end_time is not None
    assert span.duration_ms is not None
    
    @trace_operation("do_work")
    def do_work():
        return 42
        
    val = do_work()
    assert val == 42
    
    service = get_monitoring_service()
    metrics = service.metrics.list_all_metrics()
    assert len(metrics) > 0
    assert any(m.metric_name == "do_work_success" for m in metrics)
    assert any(m.metric_name == "do_work_duration" for m in metrics)

def test_health_and_alerting_engine():
    from src.intelligence.tools.monitoring_observability.health import QueueHealthStrategy
    from src.intelligence.tools.monitoring_observability.alert.engine import AlertingEngine
    from src.intelligence.tools.monitoring_observability.alert.threshold import LatencyThresholdPolicy
    from src.intelligence.tools.monitoring_observability.alert.regression import EvaluationRegressionPolicy
    from src.intelligence.tools.monitoring_observability.schema import MetricRecord, MetricType, AlertPolicyConfig
    
    health_strat = QueueHealthStrategy()
    assert health_strat.check_health() == ComponentHealth.HEALTHY
    
    engine = AlertingEngine()
    policy_cfg = AlertPolicyConfig(cooldown_seconds=10)
    latency_policy = LatencyThresholdPolicy(limit_ms=200.0, config=policy_cfg)
    engine.register_policy(latency_policy)
    
    metric_ok = MetricRecord(metric_name="latency", metric_type=MetricType.TIMER, value=150.0, unit="ms", timestamp="2026")
    metric_fail = MetricRecord(metric_name="latency", metric_type=MetricType.TIMER, value=250.0, unit="ms", timestamp="2026")
    
    alerts = engine.evaluate_policies([metric_ok], [])
    assert len(alerts) == 0
    
    alerts = engine.evaluate_policies([metric_fail], [])
    assert len(alerts) == 1
    assert "Latency exceeded threshold" in alerts[0].message
    
    alerts_cooldown = engine.evaluate_policies([metric_fail], [])
    assert len(alerts_cooldown) == 0

def test_storage_provider_jsonl_and_dashboard():
    import tempfile
    from src.intelligence.tools.monitoring_observability.provider.file import LocalFilesystemStorageProvider
    from src.intelligence.tools.monitoring_observability.analytics import MonitoringAnalyticsRegistry
    from src.intelligence.tools.monitoring_observability.dashboard import DashboardDataAggregator
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemStorageProvider(base_dir=tmpdir)
        
        metric = MetricRecord(metric_name="latency", metric_type=MetricType.TIMER, value=150.0, unit="ms", timestamp="2026")
        provider.save_metric(metric)
        
        loaded = provider.load_metrics()
        assert len(loaded) == 1
        assert loaded[0].metric_name == "latency"
        
        analytics = MonitoringAnalyticsRegistry()
        dashboard = DashboardDataAggregator(analytics)
        
        span = TraceSpan(span_id="s1", trace_id="t1", operation_name="task", start_time="2026", duration_ms=100.0)
        summary = dashboard.compile_dashboard_summary([], [metric], [], [span])
        assert summary["total_spans"] == 1
        assert summary["total_metrics"] == 1
        assert summary["sla_compliance_pct"] == 100.0

def test_monitoring_service_integration():
    import tempfile
    from src.intelligence.tools.monitoring_observability.service import MonitoringService
    from src.intelligence.tools.monitoring_observability.provider.file import LocalFilesystemStorageProvider
    from src.intelligence.tools.monitoring_observability.alert.threshold import LatencyThresholdPolicy
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemStorageProvider(base_dir=tmpdir)
        service = MonitoringService(provider=provider)
        
        latency_policy = LatencyThresholdPolicy(limit_ms=300.0)
        service.alerts.register_policy(latency_policy)
        
        service.log_metric("latency", "timer", 350.0, "ms")
        evt = service.log_event("test_event", "error", {"details": "something failed"})
        
        assert evt.event_type == "test_event"
        
        stored_alerts = provider.load_alerts()
        assert len(stored_alerts) == 1
        assert "Latency exceeded threshold" in stored_alerts[0].message

@pytest.mark.anyio
async def test_mcp_observability_tools():
    import json
    import tempfile
    import os
    from src.intelligence.mcp.server import monitoring_status, monitoring_metrics, monitoring_events, monitoring_health, monitoring_alerts, monitoring_trace
    from src.intelligence.tools.monitoring_observability.service import get_monitoring_service
    from src.intelligence.tools.monitoring_observability.provider.file import LocalFilesystemStorageProvider
    from src.intelligence.tools.monitoring_observability.schema import MonitoredComponent
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemStorageProvider(base_dir=tmpdir)
        import src.intelligence.tools.monitoring_observability.service as service_module
        service = service_module.MonitoringService(provider=provider)
        service_module._service_instance = service
        
        comp = MonitoredComponent(component_id="agent_mcp", component_type="agent")
        service.registry.register_component(comp)
        
        res_stat = await monitoring_status()
        data_stat = json.loads(res_stat)
        assert data_stat["status"] == "success"
        
        res_hlth = await monitoring_health(component_id="agent_mcp")
        data_hlth = json.loads(res_hlth)
        assert data_hlth["component"]["component_id"] == "agent_mcp"
        
        service.log_metric("cpu_load", "system", 0.75, "ratio")
        res_met = await monitoring_metrics()
        data_met = json.loads(res_met)
        assert len(data_met["metrics"]) == 1
        assert data_met["metrics"][0]["metric_name"] == "cpu_load"
