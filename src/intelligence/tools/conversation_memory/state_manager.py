from datetime import datetime
from typing import Dict, Tuple
from .schema import ConversationState, WorkingMemory, ConversationTurn
from .working_memory import WorkingMemoryManager, parse_turn_metadata, extract_questions_and_actions

class ConversationStateManager:
    def __init__(self):
        self._sessions: Dict[str, Tuple[ConversationState, WorkingMemory]] = {}

    def get_or_create_session(self, session_id: str) -> Tuple[ConversationState, WorkingMemory]:
        if session_id not in self._sessions:
            state = ConversationState(session_id=session_id)
            wm = WorkingMemory()
            self._sessions[session_id] = (state, wm)
        return self._sessions[session_id]

    def add_message_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        active_goal: str = None
    ) -> ConversationTurn:
        state, wm = self.get_or_create_session(session_id)
        
        # Parse entities, questions, and actions from content
        entities = parse_turn_metadata(content)
        questions, actions = extract_questions_and_actions(content)
        
        turn = ConversationTurn(
            role=role,
            content=content,
            entities=entities,
            unresolved_questions=questions,
            pending_actions=actions
        )
        
        WorkingMemoryManager.update_working_memory(wm, turn)
        
        state.current_turn_index += 1
        state.updated_at = datetime.utcnow()
        if active_goal:
            wm.current_topic = active_goal
            
        self.prune_stale_turns(session_id)
        return turn

    def prune_stale_turns(self, session_id: str, max_turns: int = 10) -> None:
        if session_id in self._sessions:
            _, wm = self._sessions[session_id]
            if len(wm.turns) > max_turns:
                # Keep sliding window
                wm.turns = wm.turns[-max_turns:]
