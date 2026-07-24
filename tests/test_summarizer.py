import pytest
import json
from unittest.mock import MagicMock
from src.intelligence.tools.summarizer.schema import (
    SummaryType,
    FactualSection,
    SummarizationPayload,
    SummarizationInput
)
from src.intelligence.tools.summarizer.provider import SummarizationProvider

def test_summarizer_schemas():
    assert SummaryType.CANDIDATE == "candidate"
    
    fact = FactualSection(
        evidence=["Has 5 years Go experience"],
        reasoning="Go match is strong."
    )
    assert fact.evidence == ["Has 5 years Go experience"]
    assert fact.reasoning == "Go match is strong."

def test_summarization_provider_inference():
    # Mock client completion response
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    dummy_payload = {
        "summary_type": "candidate",
        "executive_summary": "Highly qualified backend engineer.",
        "strengths": {
            "evidence": ["React", "Python"],
            "reasoning": "Matching stack"
        },
        "weaknesses_or_risks": {
            "evidence": ["None"],
            "reasoning": "Low risk"
        },
        "recruiter_recommendation": "Interview immediately.",
        "interview_focus": ["API Design"],
        "follow_up_questions": ["Explain ASGI vs WSGI."]
    }
    
    mock_response.choices[0].message.content = json.dumps(dummy_payload)
    mock_client.chat.completions.create.return_value = mock_response
    
    provider = SummarizationProvider(client=mock_client)
    
    payload, version = provider.infer(
        summary_type=SummaryType.CANDIDATE,
        context_json='{"dummy": true}'
    )
    
    assert version == "1.0.0"
    assert payload.summary_type == SummaryType.CANDIDATE
    assert payload.executive_summary == "Highly qualified backend engineer."
    assert payload.strengths.evidence == ["React", "Python"]
    assert payload.follow_up_questions == ["Explain ASGI vs WSGI."]
    mock_client.chat.completions.create.assert_called_once()

def test_summarization_service_orchestration():
    from unittest.mock import MagicMock
    from src.intelligence.tools.summarizer.service import SummarizationService
    from src.intelligence.tools.summarizer.schema import SummarizationInput, SummarizationOutput, SummarizationPayload, SummaryType
    from src.intelligence.tools.qualification_scorer.schema import QualificationOutput, QualificationPayload, ScoringDimension, DimensionScore
    from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
    from src.intelligence.tools.deterministic_enricher.schema import EnrichmentOutput, EnrichmentPayload
    from src.intelligence.tools.deterministic_enricher.schema import FieldResult as EnrichFieldResult
    from src.intelligence.tools.knowledge_service.schema import RetrievalResult, ChunkMetadata
    from src.intelligence.platform.metadata import ResponseMetadata
    from src.intelligence.platform.contracts import ResponseStatus

    mock_scorer = MagicMock()
    
    profile = CandidateOutput(
        role_type="Backend", seniority="Senior", urgency="immediate", open_to_negotiation=True, management_level="IC", predicted_functions=[], technical_domains=[], evidence=[], confidence=1.0, reasoning=""
    )
    
    enrichment = EnrichmentOutput(
        status=ResponseStatus.SUCCESS,
        metadata=ResponseMetadata(provider="d", model="m", prompt_version="1", confidence=1.0, fallback_used=False, provider_latency_ms=0),
        payload=EnrichmentPayload(technology_keywords=EnrichFieldResult(normalized_value=[], source="t", confidence=1.0, validation_status="valid", evidence=[]))
    )
    
    retrieval_chunks = [
        RetrievalResult(
            text="Require senior developer.", score=0.9, metadata=ChunkMetadata(document_id="jd1", chunk_id="jd1_chunk_0", source="jd.pdf", chunk_index=0)
        )
    ]
    
    scores = {
        ScoringDimension.SKILL_MATCH: DimensionScore(score=0.9, confidence=1.0, evidence=[], reasoning=""),
        ScoringDimension.OVERALL_QUALIFICATION: DimensionScore(score=0.85, confidence=0.9, evidence=[], reasoning="")
    }
    
    mock_scorer.process.return_value = QualificationOutput(
        status=ResponseStatus.SUCCESS,
        metadata=ResponseMetadata(provider="g", model="l", prompt_version="1", confidence=1.0, fallback_used=False, provider_latency_ms=0),
        payload=QualificationPayload(scores=scores, reconciliation_notes="Match found."),
        retrieved_chunks=["jd1_chunk_0"],
        provider_chain=["CandidateProfilerService", "DeterministicEnrichmentService", "RetrievalService", "QualificationProvider"],
        candidate_profile=profile,
        candidate_enrichment=enrichment,
        retrieved_context=retrieval_chunks
    )
    
    mock_provider = MagicMock()
    dummy_payload = SummarizationPayload(
        summary_type=SummaryType.CANDIDATE,
        executive_summary="Highly qualified backend engineer.",
        strengths={"evidence": ["skills"], "reasoning": "strong"},
        weaknesses_or_risks={"evidence": [], "reasoning": ""},
        recruiter_recommendation="Hire",
        interview_focus=[],
        follow_up_questions=[]
    )
    mock_provider.infer.return_value = (dummy_payload, "1.0.0")
    
    service = SummarizationService(
        qualification_scorer_service=mock_scorer,
        summarizer_provider=mock_provider
    )
    
    req = SummarizationInput(
        raw_text="Resume",
        job_description_id="jd1"
    )
    
    output = service.process(req)
    
    assert output.status.value == "success"
    assert output.payload.executive_summary == "Highly qualified backend engineer."
    assert output.provider_chain == [
        "CandidateProfilerService",
        "DeterministicEnrichmentService",
        "RetrievalService",
        "QualificationProvider",
        "MagicMock"
    ]

def test_mcp_summarize_candidate_success():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    call_req = {
        "jsonrpc": "2.0",
        "id": 701,
        "method": "tools/call",
        "params": {
            "name": "summarize_candidate",
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
    assert "strengths" in payload
    assert "weaknesses_or_risks" in payload
    
    # Assert dynamic execution chain
    assert content_data["provider_chain"] == [
        "CandidateProfilerService",
        "DeterministicEnrichmentService",
        "RetrievalService",
        "QualificationProvider",
        "SummarizationProvider"
    ]
    
    # Assert telemetry logs in stderr
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
    assert log["tool_name"] == "summarize_candidate"
    assert log["provider"] == "groq"
    assert log["model"] == "llama-3.3-70b-versatile"
    assert log["status"] == "success"
