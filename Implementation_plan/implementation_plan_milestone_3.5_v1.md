# Implementation Plan: Shared Platform Infrastructure

Design and extract reusable platform components shared by all intelligence services in `meridian-copilot`, establishing an MCP-first, composition-focused, and modality-agnostic infrastructure.

---

## 1. Directory Structure

We will introduce a dedicated platform package under `src/intelligence/platform/`:

```text
src/intelligence/platform/
├── __init__.py
├── config.py          # Centralized configuration (lazy-loaded)
├── errors.py          # Extensible custom exception hierarchy
├── metadata.py        # RequestMetadata and ResponseMetadata models
├── contracts.py       # BaseRequest (modality-agnostic), BaseResponse, and ResponseStatus Enum
├── interfaces.py      # typing.Protocol interface definitions
├── prompts.py         # Path-decoupled prompt template and version loader (pathlib-based)
├── telemetry.py       # Telemetry context manager utilizing typed TelemetryCollector
├── clients.py         # Centralized LLM client factory (SDK lifecycle only)
└── test_utils.py      # Standardized pytest subprocess runner harness
```

---

## 2. Platform Components Design

### A. Lazy Configuration Module (`config.py`)
Loads environment configurations lazily only when requested:
```python
import os

class PlatformConfig:
    def __init__(self):
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self.groq_model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    _instance = None

    @classmethod
    def load(cls) -> "PlatformConfig":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### B. Custom Exception Tree (`errors.py`)
Provides detailed custom error contexts:
```python
class MeridianError(Exception):
    """Base exception for all copilot errors."""
    pass

class ConfigurationError(MeridianError):
    """Raised when environment variables or configurations are missing/invalid."""
    pass

class LLMProviderError(MeridianError):
    """Base provider exception."""
    pass

class ProviderTimeoutError(LLMProviderError):
    """Raised when LLM model inference times out."""
    pass

class InferenceError(LLMProviderError):
    """Raised when an LLM provider request fails or returns invalid response."""
    pass

class PromptLoadError(MeridianError):
    """Raised when prompt text or version files fail to load."""
    pass

class PlatformValidationError(MeridianError):
    """Raised when inputs or outputs violate schema boundaries."""
    pass

class TransportError(MeridianError):
    """Raised when communication over the MCP transport layer drops."""
    pass
```

### C. Metadata Models (`metadata.py`)
```python
from pydantic import BaseModel, Field
from typing import Optional

class RequestMetadata(BaseModel):
    event_id: Optional[str] = None
    job_id: Optional[str] = None
    trace_id: Optional[str] = None

class ResponseMetadata(BaseModel):
    provider: str
    model: str
    prompt_version: str
    confidence: float
    fallback_used: bool = False
    provider_latency_ms: float = 0.0
```

### D. Modality-Agnostic Contracts (`contracts.py`)
```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from .metadata import RequestMetadata, ResponseMetadata

class ResponseStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    FALLBACK = "FALLBACK"

class BaseRequest(BaseModel):
    # Modality-agnostic: contains only request tracing metadata
    metadata: Optional[RequestMetadata] = None

class BaseResponse(BaseModel):
    status: ResponseStatus = Field(description="Operational outcome status")
    metadata: ResponseMetadata
```

### E. typing.Protocol Interfaces (`interfaces.py`)
```python
from typing import Protocol, TypeVar
from .contracts import BaseRequest, BaseResponse

TRequest = TypeVar("TRequest", bound=BaseRequest, contravariant=True)
TResponse = TypeVar("TResponse", bound=BaseResponse, covariant=True)

class ProviderProtocol(Protocol[TRequest, TResponse]):
    def infer(self, request: TRequest) -> TResponse:
        """Executes the provider-specific semantic inference or lookup."""
        ...

class ServiceProtocol(Protocol[TRequest, TResponse]):
    def process(self, request: TRequest) -> TResponse:
        """Coordinates execution through provider strategies."""
        ...
```

### F. Path-Decoupled Prompt Loader (`prompts.py`)
Decoupled from tool conventions, utilizing modern `pathlib.Path`:
```python
from pathlib import Path
from pydantic import BaseModel
from .errors import PromptLoadError

class Prompt(BaseModel):
    text: str
    version: str

class PromptLoader:
    @staticmethod
    def load(directory_path: str) -> Prompt:
        """
        Dynamically loads the prompt.txt and accompanying version.txt from the specified directory path.
        """
        dir_path = Path(directory_path)
        prompt_path = dir_path / "prompt.txt"
        version_path = dir_path / "version.txt"
        
        if not prompt_path.exists():
            raise PromptLoadError(f"Prompt template file not found at: {prompt_path}")
            
        try:
            prompt_text = prompt_path.read_text(encoding="utf-8")
                
            # Default to "1.0.0" if version.txt is missing
            version = "1.0.0"
            if version_path.exists():
                version = version_path.read_text(encoding="utf-8").strip()
                    
            return Prompt(text=prompt_text, version=version)
        except Exception as exc:
            raise PromptLoadError(f"Failed to load prompt from directory '{directory_path}': {str(exc)}")
```

### G. Telemetry Context Manager (`telemetry.py`)
A context manager that maps trace correlation IDs and parses logging metrics using a typed collector:
```python
import time
import sys
import json
import uuid
from contextlib import contextmanager
from pydantic import BaseModel, Field
from typing import Optional
from .metadata import ResponseMetadata
from .contracts import ResponseStatus

class TelemetryCollector:
    def __init__(self):
        self.metadata: Optional[ResponseMetadata] = None
        self.status: ResponseStatus = ResponseStatus.SUCCESS

class TelemetryLogModel(BaseModel):
    request_id: str
    tool_name: str
    provider: str
    model: str
    prompt_version: str
    fallback_used: bool
    confidence: float
    duration_ms: float
    provider_latency_ms: float
    status: ResponseStatus
    event_id: Optional[str] = None
    job_id: Optional[str] = None
    trace_id: Optional[str] = None
    error: Optional[str] = None

@contextmanager
def mcp_telemetry(tool_name: str, context: dict = None):
    context = context or {}
    trace_id = context.get("trace_id") or str(uuid.uuid4())
    event_id = context.get("event_id")
    job_id = context.get("job_id")
    request_id = str(uuid.uuid4())
    
    start_time = time.perf_counter()
    collector = TelemetryCollector()
    error_msg = None
    
    try:
        yield collector
    except Exception as exc:
        collector.status = ResponseStatus.FAILED
        error_msg = str(exc)
        raise exc
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        meta = collector.metadata
        
        log_payload = TelemetryLogModel(
            request_id=request_id,
            tool_name=tool_name,
            provider=meta.provider if meta else "unknown",
            model=meta.model if meta else "unknown",
            prompt_version=meta.prompt_version if meta else "unknown",
            fallback_used=meta.fallback_used if meta else False,
            confidence=meta.confidence if meta else 0.0,
            duration_ms=round(duration_ms, 2),
            provider_latency_ms=round(meta.provider_latency_ms if meta else 0.0, 2),
            status=collector.status,
            event_id=event_id,
            job_id=job_id,
            trace_id=trace_id,
            error=error_msg
        )
        # Print JSON log to stderr to ensure stdio stdout stays clean
        print(log_payload.model_dump_json(), file=sys.stderr, flush=True)
```

### H. LLM Client Factory (`clients.py`)
Responsible strictly for SDK lifecycles and authentication. Do not let it evolve into provider selection:
```python
from groq import Groq
from .config import PlatformConfig
from .errors import ConfigurationError

class LLMClientFactory:
    _groq_client = None

    @classmethod
    def get_groq_client(cls) -> Groq:
        if cls._groq_client is None:
            config = PlatformConfig.load()
            api_key = config.groq_api_key
            if not api_key:
                raise ConfigurationError("GROQ_API_KEY environment variable is not set")
            cls._groq_client = Groq(api_key=api_key)
        return cls._groq_client
```

---

## 3. Backwards Compatibility & Public API Freeze

We freeze the following interfaces; **NO** changes will be made to:
*   Public MCP tool names (`classify_intent`, `profile_candidate`).
*   Request schemas, function signatures, and Node.js gateway parameter mapping.
*   Response JSON schema values, BullMQ worker early exits, and DB insertion stages.

---

## 4. Implementation Steps & Verification Plan

### Step 1: Create Platform Package & Tests
*   Create all files in `src/intelligence/platform/` containing config, contracts, metadata, interfaces, clients, errors, prompts, telemetry, and test utilities.
*   Write unit tests specifically verifying configuration lazy-loading, Pydantic metadata validations, and path-based prompt files loading.
*   **Verification**: Run `python -m pytest tests/test_platform.py` and ensure the existing suites `test_mcp_server.py` and `test_candidate_profiler.py` pass without regression.

### Step 2: Refactor IntentClassifierService
*   Refactor `IntentClassifier` to utilize the configuration, prompts, and factory clients from `src/intelligence/platform/`.
*   **Verification**: Run `python -m pytest tests/test_mcp_server.py`.

### Step 3: Refactor CandidateProfilerService
*   Refactor `CandidateProfilerService` and providers to adopt the new platform loader, errors, config, and client factor classes.
*   **Verification**: Run `python -m pytest tests/test_candidate_profiler.py`.

### Step 4: Refactor server.py
*   Replace manual telemetry try-finally blocks with the `mcp_telemetry` context manager.
*   **Verification**: Run both Python test suites and E2E Node.js verification script (`node tests/verifyCandidateClient.js`).

### Step 5: Clean Up Dead Code
*   Remove unused duplicated loaders, constants, and client setup references.
*   **Verification**: Run all tests and node verification to certify Milestone 3.5 completion.
