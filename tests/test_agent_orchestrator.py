import pytest
import os
import json
from datetime import datetime, timezone
from src.intelligence.tools.agent_orchestrator.schema import (
    OrchestrationRequest,
    ToolMetadata,
    ExecutionNode,
    ExecutionContext,
    ExecutionPlan
)
from src.intelligence.tools.agent_orchestrator.registry.simple import SimpleToolRegistry
from src.intelligence.tools.agent_orchestrator.executor.direct import DirectToolExecutor
from src.intelligence.tools.agent_orchestrator.policy.retry import RetryPolicy
from src.intelligence.tools.agent_orchestrator.policy.failure import FailurePolicy, FailureAction
from src.intelligence.tools.agent_orchestrator.resolver.default import DefaultPlanResolver
from src.intelligence.tools.agent_orchestrator.provider import AgentOrchestratorProvider
from src.intelligence.tools.agent_orchestrator.service import AgentOrchestratorService, get_agent_orchestrator_service
from src.intelligence.tools.context_builder.schema import ContextMetadata, ContextSnapshot, ContextInputs, ContextFacts, ContextEvidence, ContextReasoning, ContextOutputs

def test_tool_registry_and_direct_executor():
    registry = SimpleToolRegistry()
    executor = DirectToolExecutor()
    
    meta = ToolMetadata(name="add_numbers", dependencies=[])
    registry.register_tool(meta, lambda x, y: x + y)
    
    context = ExecutionContext(
        trace_id="tr_test_1",
        outputs={"x_val": 10, "y_val": 20}
    )
    
    node = ExecutionNode(
        tool_name="add_numbers",
        arguments_mapping={"x": "x_val", "y": "y_val"}
    )
    
    res = executor.execute(
        node=node,
        metadata=meta,
        func=registry.get_tool("add_numbers"),
        context=context,
        retry_policy=RetryPolicy(),
        failure_policy=FailurePolicy()
    )
    
    assert res == 30

def test_executor_dependency_validation_fails():
    registry = SimpleToolRegistry()
    executor = DirectToolExecutor()
    
    meta = ToolMetadata(name="requires_dep", dependencies=["some_missing_tool"])
    registry.register_tool(meta, lambda: "ok")
    
    context = ExecutionContext(trace_id="tr_test_2", outputs={})
    node = ExecutionNode(tool_name="requires_dep")
    
    with pytest.raises(ValueError, match="Dependency error"):
        executor.execute(
            node=node,
            metadata=meta,
            func=registry.get_tool("requires_dep"),
            context=context,
            retry_policy=RetryPolicy(),
            failure_policy=FailurePolicy()
        )

def test_orchestrator_failure_policy_fallback():
    registry = SimpleToolRegistry()
    executor = DirectToolExecutor()
    resolver = DefaultPlanResolver()
    
    registry.register_tool(ToolMetadata(name="t1"), lambda: "res1")
    
    def failing_func():
        raise RuntimeError("Something went wrong")
    registry.register_tool(ToolMetadata(name="t2"), failing_func)
    
    provider = AgentOrchestratorProvider(registry=registry, executor=executor, resolver=resolver)
    
    plan = ExecutionPlan(
        plan_id="p1", 
        nodes=[ExecutionNode(tool_name="t1"), ExecutionNode(tool_name="t2")]
    )
    
    req = OrchestrationRequest(query_text="hi")
    context = provider.execute_plan(
        plan=plan,
        request=req,
        retry_policy=RetryPolicy(),
        failure_policy=FailurePolicy(action=FailureAction.CONTINUE_WITH_FALLBACK)
    )
    
    assert context.outputs["t1"] == "res1"
    assert "error" in context.outputs["t2"]
    assert context.outputs["t2"]["failed"] is True

def test_orchestrator_service_e2e_mock_flow():
    # Use the lazy getter to retrieve configured service
    service = get_agent_orchestrator_service()
    
    req = OrchestrationRequest(
        query_text="Larry is a python architect with 10 years experience. He has AWS certification.",
        session_id="session_orch_test_88"
    )
    
    res = service.process(req)
    assert res.status.value == "success"
    assert "intent_classifier" in res.completed_steps
    assert "candidate_profiler" in res.completed_steps
    assert "context_builder" in res.completed_steps
    assert "save_memory" in res.completed_steps
    assert res.context_snapshot is not None
    assert res.context_snapshot.facts.role_type == "Backend"

def test_mcp_run_orchestrator():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    req = {
        "jsonrpc": "2.0",
        "id": 991,
        "method": "tools/call",
        "params": {
            "name": "run_orchestrator",
            "arguments": {
                "query_text": "Need Go senior engineer. AWS backend developer.",
                "session_id": "session_mcp_orch_77"
            }
        }
    }
    
    responses, stderr_lines = run_mcp_session([req])
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert "content" in resp["result"]
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert "context_builder" in content["completed_steps"]
