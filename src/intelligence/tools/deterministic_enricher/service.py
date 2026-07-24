from typing import Optional
from src.intelligence.platform.interfaces import ServiceProtocol
from src.intelligence.platform.contracts import ResponseStatus
from src.intelligence.platform.metadata import ResponseMetadata
from .schema import EnrichmentInput, EnrichmentOutput
from .provider import DeterministicEnrichmentProvider

class DeterministicEnrichmentService:
    def __init__(self, provider: Optional[DeterministicEnrichmentProvider] = None):
        self.provider = provider or DeterministicEnrichmentProvider()

    def process(self, request: EnrichmentInput) -> EnrichmentOutput:
        payload = self.provider.infer(request)
        
        metadata = ResponseMetadata(
            provider="deterministic",
            model="rule-engine-v1",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        return EnrichmentOutput(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            payload=payload
        )
