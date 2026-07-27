from typing import List, Any
from .base import MemorySelectionStrategy
from ..schema import ConversationContext, WorkingMemory, ConversationWindow

class DefaultMemorySelector(MemorySelectionStrategy):
    def select_memories(
        self,
        session_id: str,
        working_memory: WorkingMemory,
        retrieved_memories: List[Any],
        window: ConversationWindow,
        active_goal: str = None
    ) -> ConversationContext:
        # Deduplicate and sort memories by recency if possible
        # For simplicity, we prioritize the most recent 3 ContextSnapshots
        selected_memories = []
        for mem in retrieved_memories[:3]:
            # Convert snapshots to clean dict representations if needed
            if hasattr(mem, "snapshot"):
                snapshot = mem.snapshot
                if hasattr(snapshot, "model_dump"):
                    selected_memories.append(snapshot.model_dump())
                else:
                    selected_memories.append(snapshot)
            elif isinstance(mem, dict):
                selected_memories.append(mem)
                
        return ConversationContext(
            session_id=session_id,
            recent_turns=working_memory.turns,
            active_entities=working_memory.active_entities,
            unresolved_questions=working_memory.unresolved_questions,
            pending_actions=working_memory.pending_actions,
            active_goal=active_goal or working_memory.current_topic,
            relevant_memories=selected_memories
        )
