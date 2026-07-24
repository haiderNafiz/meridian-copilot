from .schema import CandidateInput, CandidateOutput
from .providers.base import CandidateProfilerProvider
from .providers.groq_provider import GroqProvider
from typing import Tuple

class CandidateProfilerService:
    def __init__(self, provider: CandidateProfilerProvider = None):
        # Default to GroqProvider if not supplied (standard dependency injection)
        self.provider = provider if provider is not None else GroqProvider()

    def profile(self, input_data: CandidateInput) -> Tuple[CandidateOutput, float]:
        """
        Profiles the candidate profile using the configured provider.
        Returns a tuple of (CandidateOutput, provider_latency_ms).
        """
        return self.provider.profile(input_data)

def get_candidate_profiler_service(provider: CandidateProfilerProvider = None) -> CandidateProfilerService:
    return CandidateProfilerService(provider)
