import pytest
import json
from src.intelligence.tools.planner.schema import (
    PlannerRequest,
    PlannerContext,
    PlannerDecision,
    PlannerResult,
    PlanningFailure
)
from src.intelligence.tools.planner.catalog.base import WorkflowCatalog
from src.intelligence.tools.planner.resolver.constraint import ConstraintResolver
from src.intelligence.tools.planner.strategy.rule_based import RuleBasedPlanner
from src.intelligence.tools.planner.service import get_planner_service
from src.intelligence.tools.agent_orchestrator.schema import ToolMetadata

def test_rule_based_workflow_selection():
    catalog = WorkflowCatalog()
    strategy = RuleBasedPlanner()
    resolver = ConstraintResolver()
    
    # 1. Candidate Assessment query
    req = PlannerRequest(query_text="Assess candidate resume profile Larry")
    ctx = PlannerContext(available_tools=[ToolMetadata(name="candidate_profiler")])
    constraints = resolver.resolve_constraints(catalog.get_template("CandidateAssessmentWorkflow"), ctx)
    decision = strategy.plan(req, ctx, catalog, constraints)
    assert decision.selected_workflow == "CandidateAssessmentWorkflow"
    
    # 2. Interview Prep query
    req = PlannerRequest(query_text="Generate interview preparation questions")
    decision = strategy.plan(req, ctx, catalog, constraints)
    assert decision.selected_workflow == "InterviewWorkflow"
    
    # 3. Memory Refresh query
    req = PlannerRequest(query_text="Recall history from previous session")
    decision = strategy.plan(req, ctx, catalog, constraints)
    assert decision.selected_workflow == "ConversationWorkflow"

def test_constraint_resolver_violations():
    catalog = WorkflowCatalog()
    resolver = ConstraintResolver()
    
    # Assess template requires intent_classifier, candidate_profiler, etc.
    template = catalog.get_template("CandidateAssessmentWorkflow")
    
    # Scenario A: available tools missing required tools
    ctx = PlannerContext(available_tools=[
        ToolMetadata(name="intent_classifier", enabled=True)
    ])
    
    constraints = resolver.resolve_constraints(template, ctx)
    violations = resolver.validate(constraints)
    assert len(violations) > 0
    assert any("ToolNotFound: Required tool 'candidate_profiler'" in v for v in violations)
    
    # Scenario B: required tool is disabled
    ctx = PlannerContext(available_tools=[
        ToolMetadata(name="intent_classifier", enabled=True),
        ToolMetadata(name="candidate_profiler", enabled=False),
        ToolMetadata(name="deterministic_enricher", enabled=True),
        ToolMetadata(name="knowledge_service", enabled=True),
        ToolMetadata(name="qualification_scorer", enabled=True),
        ToolMetadata(name="summarizer", enabled=True),
        ToolMetadata(name="context_builder", enabled=True),
        ToolMetadata(name="save_memory", enabled=True)
    ])
    constraints = resolver.resolve_constraints(template, ctx)
    violations = resolver.validate(constraints)
    assert len(violations) == 1
    assert "ToolDisabled: Required tool 'candidate_profiler' is currently deactivated." in violations[0]

def test_planner_service_singleton_success():
    service = get_planner_service()
    
    # Satisfying all tools registrations in available list
    active_tools = [
        ToolMetadata(name="intent_classifier", enabled=True),
        ToolMetadata(name="candidate_profiler", enabled=True),
        ToolMetadata(name="deterministic_enricher", enabled=True),
        ToolMetadata(name="knowledge_service", enabled=True),
        ToolMetadata(name="qualification_scorer", enabled=True),
        ToolMetadata(name="summarizer", enabled=True),
        ToolMetadata(name="context_builder", enabled=True),
        ToolMetadata(name="save_memory", enabled=True)
    ]
    
    req = PlannerRequest(query_text="I need to assess Larry's resume profile")
    res = service.plan(request=req, available_tools=active_tools)
    
    assert isinstance(res, PlannerResult)
    assert res.status == "success"
    assert res.selected_workflow == "CandidateAssessmentWorkflow"
    assert res.execution_plan is not None
    assert len(res.execution_plan.nodes) == 8

def test_planner_service_failure():
    service = get_planner_service()
    # Missing required tools
    req = PlannerRequest(query_text="Assess candidate profile")
    res = service.plan(request=req, available_tools=[])
    
    assert isinstance(res, PlanningFailure)
    assert res.status == "failure"
    assert res.error_code == "ConstraintViolation"
    assert len(res.missing_details) > 0

def test_mcp_run_planner():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    req = {
        "jsonrpc": "2.0",
        "id": 881,
        "method": "tools/call",
        "params": {
            "name": "run_planner",
            "arguments": {
                "query_text": "I need to assess candidate Larry's resume.",
                "session_id": "session_mcp_plan_1"
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
    assert content["selected_workflow"] == "CandidateAssessmentWorkflow"
    assert content["execution_plan"] is not None
