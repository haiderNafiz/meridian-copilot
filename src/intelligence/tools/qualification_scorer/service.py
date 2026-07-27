from typing import List, Optional, Any
from .schema import QualificationInput, QualificationOutput
from .strategy.base import QualificationStrategy
from .strategy.candidate import CandidateQualificationStrategy

class QualificationScorerService:
    def __init__(self, *args, **kwargs):
        # Handle overloaded constructor signature:
        # Legacy signature: (self, profiler_service, enrichment_service, retrieval_service, scorer_provider)
        if len(args) == 4 or ("profiler_service" in kwargs and "scorer_provider" in kwargs):
            profiler_service = args[0] if len(args) > 0 else kwargs.get("profiler_service")
            enrichment_service = args[1] if len(args) > 1 else kwargs.get("enrichment_service")
            retrieval_service = args[2] if len(args) > 2 else kwargs.get("retrieval_service")
            scorer_provider = args[3] if len(args) > 3 else kwargs.get("scorer_provider")
            
            self.strategy = CandidateQualificationStrategy(
                profiler_service=profiler_service,
                enrichment_service=enrichment_service,
                retrieval_service=retrieval_service,
                scorer_provider=scorer_provider
            )
        else:
            strategy = kwargs.get("strategy") or (args[0] if len(args) > 0 else None)
            self.strategy = strategy if strategy is not None else CandidateQualificationStrategy()

    @property
    def scorer_provider(self):
        return getattr(self.strategy, "scorer_provider", None)

    @property
    def profiler_service(self):
        return getattr(self.strategy, "profiler_service", None)

    @property
    def enrichment_service(self):
        return getattr(self.strategy, "enrichment_service", None)

    @property
    def retrieval_service(self):
        return getattr(self.strategy, "retrieval_service", None)

    def process(self, request: QualificationInput) -> QualificationOutput:
        """
        Qualifies the opportunity using the configured strategy.
        """
        return self.strategy.qualify(request)

_service_instance = None

def get_qualification_scorer_service(strategy: QualificationStrategy = None) -> QualificationScorerService:
    global _service_instance
    if _service_instance is None:
        if strategy is None:
            strategy = CandidateQualificationStrategy()
        _service_instance = QualificationScorerService(strategy=strategy)
    return _service_instance
