from abc import ABC, abstractmethod
from typing import Optional
from src.intelligence.tools.context_builder.schema import ContextSnapshot
from ..schema import MemorySnapshot

class MemoryPolicy(ABC):
    @abstractmethod
    def apply(self, existing: Optional[ContextSnapshot], new_incoming: ContextSnapshot) -> ContextSnapshot:
        """Define how incoming snapshots resolve elements against existing states."""
        pass

class MemoryRetentionPolicy(ABC):
    @abstractmethod
    def evaluate_retention(self, memory: MemorySnapshot) -> MemorySnapshot:
        """
        Evaluate and update retention/archiving markers on snapshot.
        Acts as no-op by default to preserve the raw memory metadata.
        """
        pass
