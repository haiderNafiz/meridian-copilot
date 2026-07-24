from .base import CandidateProfilerProvider
from ..schema import CandidateInput, CandidateOutput
from typing import Tuple

class GeminiProvider(CandidateProfilerProvider):
    def profile(self, input_data: CandidateInput) -> Tuple[CandidateOutput, float]:
        raise NotImplementedError("GeminiProvider is not implemented yet.")
