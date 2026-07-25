from src.intelligence.platform.contracts import ResponseStatus
from src.intelligence.platform.metadata import ResponseMetadata
from .schema import ContextBuilderInput, ContextBuilderOutput

class ContextBuilderService:
    def __init__(self, context_provider):
        self.context_provider = context_provider

    def process(self, request: ContextBuilderInput) -> ContextBuilderOutput:
        # Pure composition merge (no internal pipelines execution)
        payload = self.context_provider.compose(request)
        
        metadata = ResponseMetadata(
            provider="context_builder",
            model="n/a",
            prompt_version="n/a",
            confidence=payload.metadata.overall_confidence,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        return ContextBuilderOutput(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            payload=payload,
            provider_chain=payload.metadata.provenance + ["ContextBuilderService"]
        )

_context_builder_service = None

def get_context_builder_service() -> ContextBuilderService:
    global _context_builder_service
    if _context_builder_service is None:
        from .provider import ContextBuilderProvider
        provider = ContextBuilderProvider()
        _context_builder_service = ContextBuilderService(context_provider=provider)
    return _context_builder_service
