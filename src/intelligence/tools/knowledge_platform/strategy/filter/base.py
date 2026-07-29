from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...schema import KnowledgeChunk

class MetadataFilterStrategy(ABC):
    @abstractmethod
    def evaluate(self, chunks: List[KnowledgeChunk], query_filters: Dict[str, Any]) -> List[KnowledgeChunk]:
        """Filter chunks based on query criteria metadata matching."""
        pass
