import time
import sys
import uuid
from contextlib import contextmanager
from pydantic import BaseModel, ValidationError
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
    except ValidationError as val_err:
        collector.status = ResponseStatus.FAILED
        error_msg = f"Validation Error: {str(val_err)}"
        raise val_err
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
