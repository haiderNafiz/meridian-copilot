from typing import Tuple, Any
from .schema import CandidateInput, CandidateProfile, EntityProfile
from .strategy.base import ProfileExtractionStrategy
from .strategy.candidate import CandidateProfileStrategy

class CandidateProfilerService:
    def __init__(self, strategy: ProfileExtractionStrategy = None):
        # Default to CandidateProfileStrategy if not supplied
        self.strategy = strategy if strategy is not None else CandidateProfileStrategy()

    @property
    def provider(self):
        return getattr(self.strategy, "provider", None)

    def profile(self, input_data: Any) -> Tuple[EntityProfile, float]:
        """
        Profiles the candidate/entity using the configured strategy.
        Returns a tuple of (EntityProfile, provider_latency_ms).
        """
        return self.strategy.extract(input_data)

def get_candidate_profiler_service(strategy_or_provider: Any = None) -> CandidateProfilerService:
    if strategy_or_provider is not None:
        if isinstance(strategy_or_provider, ProfileExtractionStrategy):
            return CandidateProfilerService(strategy=strategy_or_provider)
        else:
            # Treat as legacy provider and wrap in CandidateProfileStrategy
            strategy = CandidateProfileStrategy(provider=strategy_or_provider)
            return CandidateProfilerService(strategy=strategy)
    return CandidateProfilerService()
