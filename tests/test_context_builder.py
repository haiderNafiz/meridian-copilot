import pytest
import json
from datetime import datetime, timezone
from src.intelligence.tools.context_builder.schema import (
    ContextMetadata,
    ContextInputs,
    ContextFacts,
    ContextEvidence,
    ContextReasoning,
    ContextOutputs,
    ContextSnapshot
)

def test_context_snapshot_schema_parsing():
    meta = ContextMetadata(
        context_id="ctx_123",
        session_id="sess_456",
        timestamp_utc=datetime.now(timezone.utc),
        provenance=["CandidateProfilerService"],
        overall_confidence=0.95
    )
    
    inputs = ContextInputs(
        document_references=["doc_jd_1"],
        raw_text="Transient raw text"
    )
    
    facts = ContextFacts(
        role_type="Backend",
        seniority="Senior",
        technical_domains=["Distributed Systems"]
    )
    
    evidence = ContextEvidence(
        profile_evidence=["Worked on distributed database"]
    )
    
    reasoning = ContextReasoning(
        scoring_reasoning={"skill_match": "Strong background matches"}
    )
    
    outputs = ContextOutputs()
    
    snapshot = ContextSnapshot(
        metadata=meta,
        inputs=inputs,
        facts=facts,
        evidence=evidence,
        reasoning=reasoning,
        outputs=outputs
    )
    
    assert snapshot.metadata.context_id == "ctx_123"
    assert snapshot.facts.role_type == "Backend"
    assert snapshot.evidence.profile_evidence == ["Worked on distributed database"]
    assert "skill_match" in snapshot.reasoning.scoring_reasoning

def test_provider_partial_context_composition():
    from src.intelligence.tools.context_builder.schema import ContextBuilderInput
    from src.intelligence.tools.context_builder.provider import ContextBuilderProvider
    from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
    
    profile_out = CandidateOutput(
        role_type="Backend",
        seniority="Senior",
        urgency="passive_looker",
        open_to_negotiation=True,
        management_level="IC",
        predicted_functions=["API Design"],
        technical_domains=["Go", "Distributed Systems"],
        confidence=0.9,
        evidence=["Senior software engineer with Go experience"],
        reasoning="Good match"
    )
    
    req = ContextBuilderInput(
        context_id="ctx_partial_123",
        document_references=["doc_resume_1"],
        candidate_profile=profile_out
    )
    
    provider = ContextBuilderProvider()
    snapshot = provider.compose(req)
    
    assert snapshot.metadata.context_id == "ctx_partial_123"
    assert snapshot.metadata.provenance == ["CandidateProfilerService"]
    assert snapshot.metadata.overall_confidence == 0.9
    
    assert snapshot.facts.role_type == "Backend"
    assert snapshot.facts.timezone is None
    assert snapshot.facts.country is None
    
    assert snapshot.outputs.qualification_scores is None
    assert snapshot.outputs.recruiter_summary is None

def test_provider_full_context_composition():
    from src.intelligence.tools.context_builder.schema import ContextBuilderInput
    from src.intelligence.tools.context_builder.provider import ContextBuilderProvider
    from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
    from src.intelligence.tools.deterministic_enricher.schema import EnrichmentOutput, EnrichmentPayload, FieldResult
    from src.intelligence.tools.qualification_scorer.schema import QualificationPayload, DimensionScore, ScoringDimension
    from src.intelligence.tools.summarizer.schema import SummarizationPayload, FactualSection
    from src.intelligence.platform.contracts import ResponseStatus
    from src.intelligence.platform.metadata import ResponseMetadata
    
    profile_out = CandidateOutput(
        role_type="Backend",
        seniority="Senior",
        urgency="passive_looker",
        open_to_negotiation=True,
        management_level="IC",
        predicted_functions=["API Design"],
        technical_domains=["Go"],
        confidence=0.9,
        evidence=["Resume matching Go"],
        reasoning="Match"
    )
    
    enrich_out = EnrichmentOutput(
        status=ResponseStatus.SUCCESS,
        metadata=ResponseMetadata(provider="enricher", model="n/a", prompt_version="1.0.0", confidence=1.0, fallback_used=False, provider_latency_ms=0.0),
        payload=EnrichmentPayload(
            technology_keywords=FieldResult(normalized_value=["go"], source="t", confidence=1.0, validation_status="valid", evidence=["Go"]),
            timezone=FieldResult(normalized_value="PST", source="t", confidence=1.0, validation_status="valid", evidence=["US/Pacific"]),
            country=FieldResult(normalized_value="US", source="t", confidence=1.0, validation_status="valid", evidence=["United States"])
        )
    )
    
    scores_out = QualificationPayload(
        scores={
            ScoringDimension.OVERALL_QUALIFICATION: DimensionScore(score=0.85, reasoning="Good alignment", evidence=["Matching requirements"], confidence=0.85)
        },
        reconciliation_notes="Match found."
    )
    
    summary_out = SummarizationPayload(
        summary_type="candidate",
        executive_summary="Excellent fit.",
        strengths=FactualSection(evidence=["Strong Go"], reasoning="Highly experienced"),
        weaknesses_or_risks=FactualSection(evidence=["N/A"], reasoning="None identified"),
        recruiter_recommendation="Hire",
        interview_focus=["Go concurrency"],
        follow_up_questions=["Explain channels"]
    )
    
    req = ContextBuilderInput(
        context_id="ctx_full_123",
        document_references=["doc_resume_1", "doc_jd_1"],
        candidate_profile=profile_out,
        candidate_enrichment=enrich_out,
        qualification_scores=scores_out,
        recruiter_summary=summary_out
    )
    
    provider = ContextBuilderProvider()
    snapshot = provider.compose(req)
    
    assert snapshot.metadata.context_id == "ctx_full_123"
    assert "CandidateProfilerService" in snapshot.metadata.provenance
    assert "DeterministicEnrichmentService" in snapshot.metadata.provenance
    assert "QualificationScorerService" in snapshot.metadata.provenance
    assert "SummarizationService" in snapshot.metadata.provenance
    
    assert abs(snapshot.metadata.overall_confidence - 0.916666666) < 1e-5
    
    assert snapshot.facts.role_type == "Backend"
    assert snapshot.facts.timezone == "PST"
    assert snapshot.facts.country == "US"
    assert snapshot.facts.normalized_technologies == ["go"]
    
    assert snapshot.evidence.profile_evidence == ["Resume matching Go"]
    assert snapshot.evidence.scoring_evidence["overall_qualification"] == ["Matching requirements"]
    
    assert snapshot.reasoning.summary_reasoning == "Excellent fit."

def test_context_builder_service_singleton():
    from src.intelligence.tools.context_builder.service import get_context_builder_service
    s1 = get_context_builder_service()
    s2 = get_context_builder_service()
    assert s1 is s2

def test_context_builder_service_processing():
    from src.intelligence.tools.context_builder.schema import ContextBuilderInput
    from src.intelligence.tools.context_builder.service import get_context_builder_service
    from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
    
    profile_out = CandidateOutput(
        role_type="Backend",
        seniority="Senior",
        urgency="passive_looker",
        open_to_negotiation=True,
        management_level="IC",
        predicted_functions=["API Design"],
        technical_domains=["Go", "Distributed Systems"],
        confidence=0.9,
        evidence=["Senior Go developer"],
        reasoning="Okay match"
    )
    
    req = ContextBuilderInput(
        context_id="ctx_srv_test_789",
        document_references=["doc_jd_3"],
        candidate_profile=profile_out
    )
    
    service = get_context_builder_service()
    output = service.process(req)
    
    assert output.status.value == "success"
    assert output.payload.metadata.context_id == "ctx_srv_test_789"
    assert output.provider_chain == ["CandidateProfilerService", "ContextBuilderService"]

def test_mcp_build_context_success():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    call_req = {
        "jsonrpc": "2.0",
        "id": 801,
        "method": "tools/call",
        "params": {
            "name": "build_context",
            "arguments": {
                "context_id": "ctx_mcp_test_999",
                "document_references": ["doc_mcp_ref_1"],
                "candidate_profile": {
                    "role_type": "Backend",
                    "seniority": "Senior",
                    "urgency": "passive_looker",
                    "open_to_negotiation": True,
                    "management_level": "IC",
                    "predicted_functions": ["API Design"],
                    "technical_domains": ["Go"],
                    "confidence": 0.9,
                    "evidence": ["Evidence 1"],
                    "reasoning": "Reason 1"
                }
            }
        }
    }
    
    responses, stderr_lines = run_mcp_session([call_req])
    
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert "content" in resp["result"]
    
    content_raw = resp["result"]["content"][0]["text"]
    content_data = json.loads(content_raw)
    
    assert content_data["status"] == "success"
    assert content_data["payload"]["metadata"]["context_id"] == "ctx_mcp_test_999"
    assert content_data["payload"]["facts"]["role_type"] == "Backend"
    assert content_data["provider_chain"] == ["CandidateProfilerService", "ContextBuilderService"]


