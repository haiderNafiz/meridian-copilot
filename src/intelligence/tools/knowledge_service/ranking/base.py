from typing import Protocol, List
from ..schema import RetrievalResult
from ..store.base import VectorRecord

class RankerProtocol(Protocol):
    def rank(self, query_vector: List[float], records: List[VectorRecord]) -> List[RetrievalResult]:
        """Ranks list of VectorRecord matches against the query vector."""
        ...
