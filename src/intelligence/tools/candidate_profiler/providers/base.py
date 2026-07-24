from abc import ABC, abstractmethod
from ..schema import CandidateInput, CandidateOutput
from typing import Tuple

class CandidateProfilerProvider(ABC):
    @abstractmethod
    def profile(self, input_data: CandidateInput) -> Tuple[CandidateOutput, float]:
        """
        Profiles the candidate and returns a tuple of (CandidateOutput, provider_latency_ms).
        """
        pass
