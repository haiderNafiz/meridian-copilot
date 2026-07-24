from typing import Optional
from src.intelligence.platform.interfaces import ServiceProtocol
from src.intelligence.platform.contracts import ResponseStatus
from src.intelligence.platform.metadata import ResponseMetadata
from .schema import RetrievalInput, RetrievalOutput
from .provider import RetrievalProvider

class RetrievalService:
    def __init__(self, provider: RetrievalProvider):
        self.provider = provider

    def process(self, request: RetrievalInput) -> RetrievalOutput:
        # Delegate RAG retrieval process orchestration to provider
        payload = self.provider.infer(request)
        
        metadata = ResponseMetadata(
            provider="mock_store",
            model="mock-embed",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        return RetrievalOutput(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            payload=payload
        )
