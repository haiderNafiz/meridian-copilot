from typing import Dict, List, Any, Optional
from .schema import KnowledgeChunk

class IndexRegistry:
    def __init__(self):
        self._namespaces: Dict[str, List[KnowledgeChunk]] = {}

    def index_chunks(self, namespace: str, chunks: List[KnowledgeChunk]) -> None:
        if namespace not in self._namespaces:
            self._namespaces[namespace] = []
        self._namespaces[namespace].extend(chunks)

    def get_chunks(self, namespace: str) -> List[KnowledgeChunk]:
        return self._namespaces.get(namespace, [])

    def rebuild_index(self, namespace: str) -> None:
        """Trigger index consolidation."""
        pass
