from typing import Protocol, List

class EmbeddingProviderProtocol(Protocol):
    def embed_query(self, query: str) -> List[float]:
        """Generates vector embedding representing the query string."""
        ...

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates vector embeddings for a list of document chunks (batch)."""
        ...
