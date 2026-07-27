from typing import Tuple, Any
from .base import ProfileExtractionStrategy
from ..schema import EntityProfile, CandidateInput, CandidateProfile, EntityType
from ..providers.base import CandidateProfilerProvider
from ..providers.groq_provider import GroqProvider

class CandidateProfileStrategy(ProfileExtractionStrategy):
    def __init__(self, provider: CandidateProfilerProvider = None):
        # Default to GroqProvider if not supplied (dependency injection)
        self.provider = provider if provider is not None else GroqProvider()

    def extract(self, input_data: CandidateInput) -> Tuple[CandidateProfile, float]:
        output, latency = self.provider.profile(input_data)
        
        # Ensure EntityProfile fields are initialized/propagated
        output.entity_type = EntityType.CANDIDATE
        if input_data.skills:
            output.technologies = list(set(output.technologies + input_data.skills))
            
        # Map location if present, else None
        output.location = getattr(output, "location", None)
        
        # Inject generic signals dictionary
        output.signals = {
            "strategy": "CandidateProfileStrategy",
            "provider": self.provider.__class__.__name__,
            "confidence": getattr(output, "confidence", 1.0)
        }
        
        return output, latency
