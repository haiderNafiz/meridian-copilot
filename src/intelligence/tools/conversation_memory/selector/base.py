from abc import ABC, abstractmethod
from typing import List, Any
from ..schema import ConversationContext, WorkingMemory, ConversationWindow

class MemorySelectionStrategy(ABC):
    @abstractmethod
    def select_memories(
        self,
        session_id: str,
        working_memory: WorkingMemory,
        retrieved_memories: List[Any],
        window: ConversationWindow,
        active_goal: str = None
    ) -> ConversationContext:
        """Filter retrieved historical memories and construct consolidated ConversationContext."""
        pass
