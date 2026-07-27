from abc import ABC, abstractmethod
from typing import Tuple, Any
from ..schema import EntityProfile

class ProfileExtractionStrategy(ABC):
    @abstractmethod
    def extract(self, input_data: Any) -> Tuple[EntityProfile, float]:
        """Extract profile information from input_data using the strategy."""
        pass
