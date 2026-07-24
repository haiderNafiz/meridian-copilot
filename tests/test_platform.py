import pytest
import os
import json
from pathlib import Path
from src.intelligence.platform.config import PlatformConfig
from src.intelligence.platform.errors import PromptLoadError, ConfigurationError
from src.intelligence.platform.prompts import PromptLoader
from src.intelligence.platform.contracts import BaseRequest, BaseResponse, ResponseStatus
from src.intelligence.platform.metadata import RequestMetadata, ResponseMetadata
from src.intelligence.platform.telemetry import mcp_telemetry, TelemetryCollector

# 1. Config Unit Test
def test_platform_config_lazy_loading(monkeypatch):
    # Setup mock env vars
    monkeypatch.setenv("GROQ_API_KEY", "mock_key")
    monkeypatch.setenv("GROQ_MODEL", "mock_model")
    
    # Reload/load instance
    PlatformConfig._instance = None
    config = PlatformConfig.load()
    assert config.groq_api_key == "mock_key"
    assert config.groq_model == "mock_model"

# 2. Prompt Loader Unit Test
def test_prompt_loader_pathlib(tmp_path):
    # Setup temp prompt.txt and version.txt
    prompt_file = tmp_path / "prompt.txt"
    version_file = tmp_path / "version.txt"
    
    prompt_file.write_text("Hello {{name}}", encoding="utf-8")
    version_file.write_text("2.1.0", encoding="utf-8")
    
    prompt = PromptLoader.load(str(tmp_path))
    assert prompt.text == "Hello {{name}}"
    assert prompt.version == "2.1.0"

def test_prompt_loader_default_version(tmp_path):
    # prompt.txt exists but version.txt does not
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Hello", encoding="utf-8")
    
    prompt = PromptLoader.load(str(tmp_path))
    assert prompt.text == "Hello"
    assert prompt.version == "1.0.0"  # default fallback

def test_prompt_loader_missing_file():
    with pytest.raises(PromptLoadError):
        PromptLoader.load("./non_existent_folder_path")

# 3. Base Request / Response validation
def test_contracts_schema_validation():
    # BaseRequest with optional metadata
    req = BaseRequest()
    assert req.metadata is None
    
    req_meta = BaseRequest(metadata=RequestMetadata(event_id="e1", job_id="j1", trace_id="t1"))
    assert req_meta.metadata.trace_id == "t1"
    
    # BaseResponse validation
    resp_meta = ResponseMetadata(
        provider="groq",
        model="llama3",
        prompt_version="1.0.0",
        confidence=0.8,
        provider_latency_ms=120.5
    )
    resp = BaseResponse(status=ResponseStatus.SUCCESS, metadata=resp_meta)
    assert resp.status == ResponseStatus.SUCCESS
    assert resp.metadata.provider_latency_ms == 120.5

# 4. Telemetry Context Manager validation
def test_mcp_telemetry_success(capsys):
    context = {"event_id": "evt_t", "job_id": "job_t", "trace_id": "trace_t"}
    
    with mcp_telemetry("test_tool", context) as collector:
        collector.metadata = ResponseMetadata(
            provider="groq",
            model="llama-3.1",
            prompt_version="1.0.0",
            confidence=0.95,
            provider_latency_ms=50.25
        )
        
    captured = capsys.readouterr()
    log_line = captured.err.strip()
    parsed = json.loads(log_line)
    
    assert parsed["tool_name"] == "test_tool"
    assert parsed["status"] == "success"
    assert parsed["provider_latency_ms"] == 50.25
    assert parsed["trace_id"] == "trace_t"
