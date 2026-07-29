from abc import ABC, abstractmethod
from typing import List

class ChunkStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """Split text content into chunked string segments."""
        pass
