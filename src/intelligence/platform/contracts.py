from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from .metadata import RequestMetadata, ResponseMetadata

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failure"
    FALLBACK = "fallback"

class BaseRequest(BaseModel):
    # Modality-agnostic: contains only request tracing metadata
    metadata: Optional[RequestMetadata] = None

class BaseResponse(BaseModel):
    status: ResponseStatus = Field(description="Operational outcome status")
    metadata: ResponseMetadata
