from pydantic import BaseModel
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
