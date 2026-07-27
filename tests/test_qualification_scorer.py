import pytest
import json
from src.intelligence.tools.qualification_scorer.schema import (
    ScoringDimension,
    DimensionScore,
    QualificationPayload
)

def test_scoring_dimension_enum():
    assert ScoringDimension.SKILL_MATCH == "skill_match"
    assert ScoringDimension.OVERALL_QUALIFICATION == "overall_qualification"

def test_dimension_score_parsing():
    score = DimensionScore(
        score=0.85,
        confidence=0.9,
        evidence=["Worked with React for 5 years", "Mentored junior devs"],
        reasoning="Strong frontend experience matches JD well."
    )
    assert score.score == 0.85
    assert score.confidence == 0.9
    assert "React" in score.evidence[0]
    
def test_qualification_payload_dictionary_mapping():
    scores_dict = {
        ScoringDimension.SKILL_MATCH: DimensionScore(score=0.9, confidence=1.0, evidence=[], reasoning=""),
        ScoringDimension.OVERALL_QUALIFICATION: DimensionScore(score=0.85, confidence=0.95, evidence=[], reasoning="")
    }
    
    payload = QualificationPayload(
        scores=scores_dict,
        reconciliation_notes="Overall high match based on skills."
    )
    
    assert payload.scores[ScoringDimension.SKILL_MATCH].score == 0.9
    assert payload.reconciliation_notes == "Overall high match based on skills."

def test_qualification_provider_evaluation():
    from unittest.mock import MagicMock
    from src.intelligence.tools.qualification_scorer.provider import QualificationProvider
    from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
    from src.intelligence.tools.deterministic_enricher.schema import EnrichmentOutput, EnrichmentPayload
    from src.intelligence.tools.deterministic_enricher.schema import FieldResult as EnrichFieldResult
    from src.intelligence.tools.knowledge_service.schema import RetrievalPayload, RetrievalResult, ChunkMetadata
    
    # Mock groq client
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    dummy_payload = {
        "scores": {
            "skill_match": {"score": 0.9, "confidence": 1.0, "evidence": ["React", "Python"], "reasoning": "Matching tech"},
            "experience_match": {"score": 0.8, "confidence": 0.9, "evidence": ["5 years"], "reasoning": "Experience matches"},
            "seniority_match": {"score": 0.8, "confidence": 0.9, "evidence": [], "reasoning": ""},
            "domain_match": {"score": 0.7, "confidence": 0.8, "evidence": [], "reasoning": ""},
            "location_compatibility": {"score": 0.9, "confidence": 0.9, "evidence": [], "reasoning": ""},
            "employment_type_compatibility": {"score": 0.9, "confidence": 0.9, "evidence": [], "reasoning": ""},
            "availability_urgency": {"score": 0.9, "confidence": 0.9, "evidence": [], "reasoning": ""},
            "overall_qualification": {"score": 0.85, "confidence": 0.9, "evidence": [], "reasoning": ""}
        },
        "reconciliation_notes": "Highly qualified frontend engineer."
    }
    
    mock_response.choices[0].message.content = json.dumps(dummy_payload)
    mock_client.chat.completions.create.return_value = mock_response
    
    provider = QualificationProvider(client=mock_client)
    
    profile = CandidateOutput(
        role_type="Backend",
        seniority="Senior",
        urgency="immediate",
        open_to_negotiation=True,
        management_level="IC",
        predicted_functions=["Backend Development"],
        technical_domains=["Distributed Systems"],
        evidence=[],
        confidence=0.9,
        reasoning="Good match"
    )
    
    from src.intelligence.platform.metadata import ResponseMetadata
    from src.intelligence.platform.contracts import ResponseStatus
    
    enrichment = EnrichmentOutput(
        status=ResponseStatus.SUCCESS,
        metadata=ResponseMetadata(
            provider="deterministic",
            model="rule-engine-v1",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        ),
        payload=EnrichmentPayload(
            technology_keywords=EnrichFieldResult(normalized_value=["React", "Python"], source="t", confidence=1.0, validation_status="valid", evidence=[])
        )
    )
    
    retrieval = RetrievalPayload(
        results=[
            RetrievalResult(
                text="Require senior developer with experience in React and Python.",
                score=0.9,
                metadata=ChunkMetadata(document_id="jd1", chunk_id="jd1_c0", source="jd.pdf", chunk_index=0)
            )
        ]
    )
    
    payload, version = provider.infer(profile, enrichment, retrieval)
    
    assert version == "1.0.0"
    assert payload.scores[ScoringDimension.SKILL_MATCH].score == 0.9
    assert payload.reconciliation_notes == "Highly qualified frontend engineer."
    mock_client.chat.completions.create.assert_called_once()

def test_qualification_service_orchestration():
    from unittest.mock import MagicMock
    from src.intelligence.tools.qualification_scorer.service import QualificationScorerService
    from src.intelligence.tools.qualification_scorer.schema import QualificationInput, ScoringDimension, DimensionScore, QualificationPayload
    from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
    from src.intelligence.tools.deterministic_enricher.schema import EnrichmentOutput, EnrichmentPayload
    from src.intelligence.tools.deterministic_enricher.schema import FieldResult as EnrichFieldResult
    from src.intelligence.tools.knowledge_service.schema import RetrievalOutput, RetrievalPayload, RetrievalResult, ChunkMetadata
    from src.intelligence.platform.metadata import ResponseMetadata
    from src.intelligence.platform.contracts import ResponseStatus

    mock_profiler = MagicMock()
    mock_profiler.profile.return_value = (CandidateOutput(
        role_type="Backend", seniority="Senior", urgency="immediate", open_to_negotiation=True, management_level="IC", predicted_functions=[], technical_domains=[], evidence=[], confidence=1.0, reasoning=""
    ), 10.0)

    mock_enricher = MagicMock()
    mock_enricher.process.return_value = EnrichmentOutput(
        status=ResponseStatus.SUCCESS,
        metadata=ResponseMetadata(provider="d", model="m", prompt_version="1", confidence=1.0, fallback_used=False, provider_latency_ms=0),
        payload=EnrichmentPayload(technology_keywords=EnrichFieldResult(normalized_value=[], source="t", confidence=1.0, validation_status="valid", evidence=[]))
    )

    mock_retrieval = MagicMock()
    mock_retrieval.process.return_value = RetrievalOutput(
        status=ResponseStatus.SUCCESS,
        metadata=ResponseMetadata(provider="v", model="e", prompt_version="1", confidence=1.0, fallback_used=False, provider_latency_ms=0),
        payload=RetrievalPayload(results=[
            RetrievalResult(
                text="Require senior developer.", score=0.9, metadata=ChunkMetadata(document_id="jd1", chunk_id="jd1_chunk_0", source="jd.pdf", chunk_index=0)
            )
        ])
    )

    mock_provider = MagicMock()
    dummy_payload = QualificationPayload(
        scores={
            ScoringDimension.SKILL_MATCH: DimensionScore(score=0.9, confidence=1.0, evidence=["skills"], reasoning="match"),
            ScoringDimension.OVERALL_QUALIFICATION: DimensionScore(score=0.85, confidence=0.9, evidence=[], reasoning="")
        },
        reconciliation_notes="Match found."
    )
    mock_provider.infer.return_value = (dummy_payload, "1.0.0")

    service = QualificationScorerService(
        profiler_service=mock_profiler,
        enrichment_service=mock_enricher,
        retrieval_service=mock_retrieval,
        scorer_provider=mock_provider
    )

    req = QualificationInput(raw_text="Resume content", job_description_id="jd_123")
    output = service.process(req)

    assert output.status.value == "success"
    assert output.metadata.provider == "groq"
    assert output.metadata.model == "llama-3.3-70b-versatile"
    assert output.payload.reconciliation_notes == "Match found."
    assert output.retrieved_chunks == ["jd1_chunk_0"]
    assert output.provider_chain == ["MagicMock", "MagicMock", "MagicMock", "MagicMock"]

def test_mcp_score_qualification_success():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    call_req = {
        "jsonrpc": "2.0",
        "id": 601,
        "method": "tools/call",
        "params": {
            "name": "score_qualification",
            "arguments": {
                "raw_text": "Larry Page is a senior software engineer specialized in distributed systems and Go.",
                "job_description_id": "doc_jd_go_dev",
                "email": "larry@google.com",
                "location": "Palo Alto, CA",
                "technology_keywords": ["go", "distributed systems"]
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
    assert "payload" in content_data
    payload = content_data["payload"]
    assert "scores" in payload
    assert content_data["provider_chain"] == [
        "CandidateProfilerService",
        "DeterministicEnrichmentService",
        "RetrievalService",
        "QualificationProvider"
    ]
    
    json_logs = []
    for line in stderr_lines:
        try:
            parsed = json.loads(line)
            if "request_id" in parsed:
                json_logs.append(parsed)
        except json.JSONDecodeError:
            continue
            
    assert len(json_logs) == 1
    log = json_logs[0]
    assert log["tool_name"] == "score_qualification"
    assert log["provider"] == "groq"
    assert log["model"] == "llama-3.3-70b-versatile"
    assert log["status"] == "success"

def test_scorer_strategy_injection():
    from src.intelligence.tools.qualification_scorer.strategy.candidate import CandidateQualificationStrategy
    from src.intelligence.tools.qualification_scorer.strategy.base import QualificationStrategy
    from src.intelligence.tools.qualification_scorer.service import get_qualification_scorer_service, QualificationScorerService
    from src.intelligence.tools.qualification_scorer.schema import QualificationInput, QualificationOutput
    from src.intelligence.platform.contracts import ResponseStatus
    from src.intelligence.platform.metadata import ResponseMetadata

    # 1. Verify default strategy is Candidate
    # We clear the singleton instance if any, or just check the class of the default constructed one
    service_default = get_qualification_scorer_service()
    assert isinstance(service_default.strategy, CandidateQualificationStrategy)

    # 2. Test mock strategy injection
    class MockQualStrategy(QualificationStrategy):
        def qualify(self, request):
            meta = ResponseMetadata(
                provider="mock", model="m", prompt_version="1", confidence=1.0, fallback_used=False, provider_latency_ms=0.0
            )
            from src.intelligence.tools.qualification_scorer.schema import QualificationPayload
            dummy_payload = QualificationPayload(scores={}, reconciliation_notes="Mock notes")
            return QualificationOutput(
                status=ResponseStatus.SUCCESS,
                metadata=meta,
                payload=dummy_payload,
                retrieved_chunks=[],
                provider_chain=["MockStrategy"]
            )

    mock_strat = MockQualStrategy()
    service_custom = QualificationScorerService(strategy=mock_strat)
    assert service_custom.strategy is mock_strat

    res = service_custom.process(QualificationInput(raw_text="dummy", job_description_id="jd1"))
    assert res.status == ResponseStatus.SUCCESS
    assert res.provider_chain == ["MockStrategy"]
