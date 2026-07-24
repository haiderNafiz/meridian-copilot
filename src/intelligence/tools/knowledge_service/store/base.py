from typing import Protocol, List, Dict, Any, Optional
from pydantic import BaseModel
from ..schema import ChunkMetadata

class VectorRecord(BaseModel):
    text: str
    vector: List[float]
    metadata: ChunkMetadata

class VectorStoreProtocol(Protocol):
    def query(
        self,
        query_vector: List[float],
        collection: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorRecord]:
        """Queries the vector database returning matching record vectors."""
        ...

    def upsert(self, collection: str, records: List[VectorRecord]) -> bool:
        """Inserts or updates vector records in the specified collection."""
        ...

    def delete(self, collection: str, filters: Dict[str, Any]) -> bool:
        """Deletes vector records in the specified collection matching filters."""
        ...

    def list_collections(self) -> List[str]:
        """Lists names of all active collections in the database."""
        ...
