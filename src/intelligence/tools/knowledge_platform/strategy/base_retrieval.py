from abc import ABC, abstractmethod
from typing import List
from ..schema import KnowledgeQuery, KnowledgeChunk

class RetrievalStrategy(ABC):
    @abstractmethod
    def retrieve(self, query: KnowledgeQuery, chunks: List[KnowledgeChunk]) -> List[KnowledgeChunk]:
        """Perform search query matches over candidate chunks."""
        pass
