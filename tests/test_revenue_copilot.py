import pytest
import json
from src.intelligence.tools.revenue_copilot.schema import (
    RevenueCopilotRequest, RevenueCopilotResult, PlaybookCategory
)
from src.intelligence.tools.revenue_copilot.playbook.default import DefaultPlaybookStrategy
from src.intelligence.tools.revenue_copilot.action.planner import ActionPlanner
from src.intelligence.tools.revenue_copilot.explanation.builder import ExplanationBuilder
from src.intelligence.tools.revenue_copilot.communication.email import EmailStrategy
from src.intelligence.tools.revenue_copilot.communication.crm import CRMStrategy
from src.intelligence.tools.revenue_copilot.communication.agenda import AgendaStrategy
from src.intelligence.tools.revenue_copilot.communication.proposal import ProposalStrategy
from src.intelligence.tools.revenue_copilot.service import get_revenue_copilot_service
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment, AssessmentType
from tests.test_opportunity_intelligence import create_test_snapshot

def create_mock_assessment(score=0.5, recommended_plan="candidate_screening") -> OpportunityAssessment:
    return OpportunityAssessment(
        assessment_type=AssessmentType.CANDIDATE,
        business_intent="Mock business intent",
        lifecycle_stage="Vetting",
        confidence=0.85,
        opportunity_score=score,
        strengths=["Strong AWS background"],
        risks=["Location mismatches"],
        blockers=["Visa requirements"],
        missing_information=["Missing certificate verification"],
        evidence_summary={},
        recommended_next_actions=["CRITICAL: Resolve blockers", "REQUIRED: Fetch details"],
        recommended_plan=recommended_plan,
        follow_up_items=["Is he available?"],
        decision_guidance="Standard review",
        explanation="Default evaluation logic reasoning",
        telemetry={}
    )

def test_default_playbook_selection():
    strat = DefaultPlaybookStrategy()
    
    # 1. High score -> EVALUATION
    rec1 = strat.select_playbook(create_mock_assessment(score=0.9, recommended_plan="technical_interview"))
    assert rec1.category == PlaybookCategory.EVALUATION
    assert rec1.playbook_name == "technical_interview"
    
    # 2. Low score -> DISCOVERY
    rec2 = strat.select_playbook(create_mock_assessment(score=0.2, recommended_plan="client_followup"))
    assert rec2.category == PlaybookCategory.DISCOVERY
    assert rec2.playbook_name == "client_followup"

def test_action_prioritization():
    planner = ActionPlanner()
    checklist = planner.plan_actions(create_mock_assessment())
    assert "Blocker resolution: Visa requirements" in checklist.critical_actions
    assert "Request missing attribute: Missing certificate verification" in checklist.required_actions
    assert "Mitigate flagged risk: Location mismatches" in checklist.advisory_actions

def test_explanation_compilation():
    builder = ExplanationBuilder()
    summary = builder.build_explanation(create_mock_assessment())
    assert "Vetting" in summary.rationale
    assert "Visa requirements" not in summary.evidence_backed # only strengths and risks
    assert "Strong AWS background" in summary.evidence_backed

def test_communication_strategies():
    email = EmailStrategy()
    crm = CRMStrategy()
    agenda = AgendaStrategy()
    prop = ProposalStrategy()
    
    snapshot = create_test_snapshot()
    assessment = create_mock_assessment()
    
    e_draft = email.generate(assessment, snapshot)
    c_draft = crm.generate(assessment, snapshot)
    a_draft = agenda.generate(assessment, snapshot)
    p_draft = prop.generate(assessment, snapshot)
    
    assert e_draft.recipient_group == "external"
    assert c_draft.recipient_group == "internal"
    assert a_draft.recipient_group == "internal"
    assert p_draft.recipient_group == "external"

def test_revenue_copilot_service():
    service = get_revenue_copilot_service()
    
    snapshot = create_test_snapshot(timezone_str="UTC+2")
    assessment = create_mock_assessment(score=0.8)
    
    req = RevenueCopilotRequest(
        opportunity_assessment=assessment,
        context_snapshot=snapshot
    )
    
    res = service.run(req)
    assert isinstance(res, RevenueCopilotResult)
    assert res.status == "success"
    assert res.recommendation.playbook.category == PlaybookCategory.EVALUATION
    assert len(res.recommendation.drafts) == 4

def test_mcp_run_revenue_copilot():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    snapshot_dict = {
        "metadata": {
            "context_id": "c1",
            "timestamp_utc": "2026-07-27T12:00:00Z",
            "provenance": ["CandidateProfilerService"],
            "overall_confidence": 1.0
        },
        "inputs": {
            "document_references": []
        },
        "facts": {
            "role_type": "Backend",
            "seniority": "Senior",
            "normalized_technologies": ["python"]
        },
        "evidence": {},
        "reasoning": {},
        "outputs": {}
    }
    
    assessment_dict = {
        "assessment_type": "candidate",
        "business_intent": "Vetting query",
        "lifecycle_stage": "Discovery",
        "confidence": 0.8,
        "opportunity_score": 0.5,
        "strengths": ["Strong skills"],
        "risks": [],
        "blockers": [],
        "missing_information": [],
        "evidence_summary": {},
        "recommended_next_actions": ["REQUIRED: Obtain email"],
        "recommended_plan": "candidate_screening",
        "follow_up_items": [],
        "decision_guidance": "Standard vetting screen",
        "explanation": "No issues found",
        "telemetry": {}
    }
    
    req = {
        "jsonrpc": "2.0",
        "id": 994,
        "method": "tools/call",
        "params": {
            "name": "run_revenue_copilot",
            "arguments": {
                "opportunity_assessment": assessment_dict,
                "context_snapshot": snapshot_dict
            }
        }
    }
    
    responses, _ = run_mcp_session([req])
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert "content" in resp["result"]
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert content["recommendation"]["playbook"]["category"] == "qualification"
