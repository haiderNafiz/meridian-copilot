import pytest
from pydantic import ValidationError
from unittest.mock import MagicMock, patch
import json
import subprocess
import time
import os

from src.intelligence.tools.candidate_profiler.schema import CandidateInput, CandidateOutput
from src.intelligence.tools.candidate_profiler.profiler import CandidateProfilerService, get_candidate_profiler_service
from src.intelligence.tools.candidate_profiler.providers.base import CandidateProfilerProvider
from src.intelligence.tools.candidate_profiler.providers.groq_provider import GroqProvider
from src.intelligence.tools.candidate_profiler.providers.gemini_provider import GeminiProvider
from src.intelligence.platform.test_utils import run_mcp_session

# 1. Schema Unit Tests
def test_candidate_input_optional_fields():
    # Only raw_text is required
    inp = CandidateInput(raw_text="Some unstructured biography text.")
    assert inp.raw_text == "Some unstructured biography text."
    assert inp.current_title is None
    assert inp.skills is None
    assert inp.years_experience is None
    assert inp.job_context is None

def test_candidate_input_invalid_types():
    with pytest.raises(ValidationError):
        # years_experience should be int, skills should be list
        CandidateInput(raw_text="Biography", years_experience="invalid_int", skills="not_a_list")

def test_candidate_output_validation():
    # Valid output payload dictionary matching schema literals
    payload = {
        "role_type": "Backend",
        "seniority": "Senior",
        "urgency": "immediate",
        "open_to_negotiation": True,
        "predicted_functions": ["API Development", "Database Optimization"],
        "technical_domains": ["Cloud Infrastructure", "Backend Engineering"],
        "management_level": "IC",
        "evidence": ["10 years backend experience"],
        "confidence": 0.95,
        "reasoning": "Candidate demonstrates senior backend developer traits."
    }
    output = CandidateOutput(**payload)
    assert output.role_type == "Backend"
    assert output.seniority == "Senior"
    assert output.urgency == "immediate"
    assert output.management_level == "IC"
    assert output.confidence == 0.95

def test_candidate_output_invalid_taxonomy():
    # Invalid role_type or management_level taxonomy raises ValidationError
    payload = {
        "role_type": "InvalidRole",  # Not in Backend|Frontend etc.
        "seniority": "Senior",
        "urgency": "immediate",
        "open_to_negotiation": True,
        "predicted_functions": ["API Development"],
        "technical_domains": ["Cloud Infrastructure"],
        "management_level": "InvalidManagement",  # Not in IC|Lead etc.
        "evidence": ["10 years experience"],
        "confidence": 0.95,
        "reasoning": "Wrong taxonomies."
    }
    with pytest.raises(ValidationError):
        CandidateOutput(**payload)

# 2. Service Unit & Mock Provider Tests
class MockCandidateProvider(CandidateProfilerProvider):
    def __init__(self, stubbed_output: CandidateOutput):
        self.stubbed_output = stubbed_output

    def profile(self, input_data: CandidateInput) -> tuple:
        return self.stubbed_output, 45.2

def test_profiler_service_with_mock_provider():
    stubbed = CandidateOutput(
        role_type="ML",
        seniority="Lead",
        urgency="actively_interviewing",
        open_to_negotiation=False,
        predicted_functions=["Model training", "MLOps pipeline construction"],
        technical_domains=["Machine Learning Engineering", "NLP"],
        management_level="Lead",
        evidence=["Lead ML engineer since 2022"],
        confidence=0.98,
        reasoning="Qualified machine learning lead."
    )
    
    provider = MockCandidateProvider(stubbed)
    service = get_candidate_profiler_service(provider)
    
    inp = CandidateInput(raw_text="Lead ML engineer since 2022")
    output, latency = service.profile(inp)
    
    assert output.role_type == "ML"
    assert output.seniority == "Lead"
    assert output.urgency == "actively_interviewing"
    assert latency == 45.2

def test_gemini_provider_not_implemented():
    gemini = GeminiProvider()
    inp = CandidateInput(raw_text="Resume text")
    with pytest.raises(NotImplementedError):
        gemini.profile(inp)

# 3. Subprocess Transport Integration Tests

def test_mcp_profile_candidate_validation_failure():
    # Pass negative years_experience to trigger ValidationError inside tool handler
    call_req = {
        "jsonrpc": "2.0",
        "id": 201,
        "method": "tools/call",
        "params": {
            "name": "profile_candidate",
            "arguments": {
                "raw_text": "Software developer candidate resume text.",
                "years_experience": -5
            }
        }
    }
    
    responses, stderr_lines = run_mcp_session([call_req])
    
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert resp["result"].get("isError") is True
    
    # Extract our structured JSON logs from stderr
    json_logs = []
    for line in stderr_lines:
        try:
            parsed = json.loads(line)
            if "request_id" in parsed and parsed.get("tool_name") == "profile_candidate":
                json_logs.append(parsed)
        except json.JSONDecodeError:
            continue
            
    assert len(json_logs) == 1
    failure_log = json_logs[0]
    
    assert failure_log["tool_name"] == "profile_candidate"
    assert failure_log["status"] == "failure"
    assert "error" in failure_log
    assert "Validation Error" in failure_log["error"]
    assert "model" in failure_log
    assert "prompt_version" == "prompt_version" or "prompt_version" in failure_log
