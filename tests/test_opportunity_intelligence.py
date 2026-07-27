import pytest
import json
from datetime import datetime, timezone
from src.intelligence.tools.opportunity_intelligence.schema import (
    OpportunityAssessment, AssessmentType, OpportunityIntelligenceResult
)
from src.intelligence.tools.opportunity_intelligence.evidence.analyzer import EvidenceAnalyzer
from src.intelligence.tools.opportunity_intelligence.policy.confidence import ConfidencePolicy
from src.intelligence.tools.opportunity_intelligence.recommendation.builder import RecommendationBuilder
from src.intelligence.tools.opportunity_intelligence.strategy.default import DefaultAssessmentStrategy
from src.intelligence.tools.opportunity_intelligence.service import get_opportunity_intelligence_service
from src.intelligence.tools.context_builder.schema import (
    ContextSnapshot, ContextMetadata, ContextInputs, ContextFacts, ContextEvidence, ContextReasoning, ContextOutputs
)
from src.intelligence.tools.qualification_scorer.schema import QualificationPayload, DimensionScore

def create_test_snapshot(
    context_id="ctx_123",
    provenance=None,
    raw_text=None,
    role_type=None,
    seniority=None,
    normalized_technologies=None,
    timezone_str=None,
    qualification_scores=None
) -> ContextSnapshot:
    meta = ContextMetadata(
        context_id=context_id,
        session_id="session_123",
        timestamp_utc=datetime.now(timezone.utc),
        provenance=provenance or ["CandidateProfilerService"],
        overall_confidence=1.0
    )
    inputs = ContextInputs(
        document_references=[],
        raw_text=raw_text
    )
    facts = ContextFacts(
        role_type=role_type,
        seniority=seniority,
        normalized_technologies=normalized_technologies or [],
        timezone=timezone_str
    )
    evidence = ContextEvidence()
    reasoning = ContextReasoning()
    outputs = ContextOutputs(
        qualification_scores=qualification_scores
    )
    
    return ContextSnapshot(
        metadata=meta,
        inputs=inputs,
        facts=facts,
        evidence=evidence,
        reasoning=reasoning,
        outputs=outputs
    )

def test_evidence_completeness_calculation():
    analyzer = EvidenceAnalyzer()
    
    # 1. Empty snapshot
    snapshot = create_test_snapshot(context_id="c1")
    res = analyzer.analyze_evidence(snapshot)
    assert round(res["evidence_completeness"], 1) == 0.2
    assert any("Seniority: Seniority level is not populated." in m for m in res["missing_information"])
    
    # 2. Populated snapshot
    snapshot_populated = create_test_snapshot(
        context_id="c2",
        seniority="Senior",
        normalized_technologies=["python", "aws"],
        timezone_str="UTC+2"
    )
    res2 = analyzer.analyze_evidence(snapshot_populated)
    assert len(res2["risks"]) == 0
    assert "Seniority: Profile indicates solid senior level history." in res2["strengths"]

def test_confidence_policy():
    policy = ConfidencePolicy()
    conf = policy.calculate_confidence(
        enrichment_confidence=0.9,
        qualification_confidence=0.8,
        evidence_completeness=0.7,
        conversation_context_quality=0.9
    )
    # Expected weighted: (0.9*0.2) + (0.8*0.3) + (0.7*0.4) + (0.9*0.1) = 0.18 + 0.24 + 0.28 + 0.09 = 0.79
    assert conf == 0.79

def test_recommendation_builder_ranking():
    builder = RecommendationBuilder()
    risks = ["Risk A"]
    blockers = ["Blocker B"]
    missing = ["Missing C"]
    
    actions = builder.build_recommendations(risks, blockers, missing)
    assert len(actions) == 3
    assert actions[0] == "CRITICAL: Resolve blocker - Blocker B"
    assert actions[1] == "REQUIRED: Obtain missing information - Missing C"
    assert actions[2] == "ADVISORY: Verify and mitigate risk - Risk A"

def test_opportunity_intelligence_service_success():
    service = get_opportunity_intelligence_service()
    
    snapshot = create_test_snapshot(
        context_id="c3",
        provenance=["CandidateProfilerService", "DeterministicEnrichmentService"],
        raw_text="python senior backend engineer",
        seniority="Senior",
        normalized_technologies=["python"],
        timezone_str="UTC+1"
    )
    
    res = service.assess(context_snapshot=snapshot)
    assert isinstance(res, OpportunityIntelligenceResult)
    assert res.status == "success"
    assert res.assessment.assessment_type == AssessmentType.CANDIDATE
    assert res.assessment.opportunity_score == 0.5
    assert len(res.assessment.strengths) > 0

def test_mcp_assess_opportunity():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    snapshot_dict = {
        "metadata": {
            "context_id": "c4",
            "session_id": "s4",
            "timestamp_utc": "2026-07-27T12:00:00Z",
            "provenance": ["CandidateProfilerService", "DeterministicEnrichmentService"],
            "overall_confidence": 1.0
        },
        "inputs": {
            "document_references": [],
            "raw_text": "python backend dev"
        },
        "facts": {
            "role_type": "Backend",
            "seniority": "Senior",
            "normalized_technologies": ["python"],
            "timezone": "UTC+1"
        },
        "evidence": {
            "profile_evidence": [],
            "scoring_evidence": {}
        },
        "reasoning": {
            "scoring_reasoning": {},
            "summary_reasoning": None,
            "weaknesses_or_risks": None
        },
        "outputs": {
            "qualification_scores": None,
            "recruiter_summary": None
        }
    }
    
    req = {
        "jsonrpc": "2.0",
        "id": 991,
        "method": "tools/call",
        "params": {
            "name": "assess_opportunity",
            "arguments": {
                "context_snapshot": snapshot_dict,
                "assessment_type": "candidate"
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
    assert content["assessment"]["assessment_type"] == "candidate"
    assert content["assessment"]["confidence"] > 0.0
