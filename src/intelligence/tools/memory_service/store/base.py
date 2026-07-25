from abc import ABC, abstractmethod
from typing import List, Optional
from ..schema import MemorySnapshot, MemoryQuery, MemorySearchResult

class MemoryStore(ABC):
    @abstractmethod
    def save(self, memory: MemorySnapshot) -> None:
        """Persist memory snapshot to storage (append-only log)."""
        pass

    @abstractmethod
    def get_by_memory_id(self, memory_id: str) -> Optional[MemorySnapshot]:
        """Fetch memory record by primary key memory_id."""
        pass

    @abstractmethod
    def get_by_context_id(self, context_id: str) -> List[MemorySnapshot]:
        """Fetch all snapshot versions associated with a context_id."""
        pass

    @abstractmethod
    def get_by_session_id(self, session_id: str) -> List[MemorySnapshot]:
        """Fetch all memory snapshots associated with a session_id."""
        pass

class MemoryIndex(ABC):
    @abstractmethod
    def index(self, memory: MemorySnapshot) -> None:
        """Index a memory record for retrieval lookup scan."""
        pass

    @abstractmethod
    def search(self, query: MemoryQuery) -> List[MemorySearchResult]:
        """Search memories applying filters and scanning fields."""
        pass
