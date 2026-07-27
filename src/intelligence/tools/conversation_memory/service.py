from typing import Union, Optional
from .schema import ConversationRequest, ConversationResult, ConversationFailure
from .provider import ConversationMemoryProvider

class ConversationMemoryService:
    def __init__(self, provider: ConversationMemoryProvider):
        self.provider = provider

    def post_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        active_goal: Optional[str] = None
    ) -> Union[ConversationResult, ConversationFailure]:
        req = ConversationRequest(
            session_id=session_id,
            role=role,
            content=content,
            active_goal=active_goal
        )
        return self.provider.process_turn(req)

    def get_context(
        self,
        session_id: str,
        query_text: Optional[str] = None,
        active_goal: Optional[str] = None
    ) -> Union[ConversationResult, ConversationFailure]:
        req = ConversationRequest(
            session_id=session_id,
            query_text=query_text,
            active_goal=active_goal
        )
        return self.provider.process_turn(req)

_conversation_memory_service = None

def get_conversation_memory_service() -> ConversationMemoryService:
    global _conversation_memory_service
    if _conversation_memory_service is None:
        from .state_manager import ConversationStateManager
        from .retriever import MemoryRetriever
        from .selector.default import DefaultMemorySelector
        
        state_mgr = ConversationStateManager()
        retriever = MemoryRetriever()
        selector = DefaultMemorySelector()
        
        provider = ConversationMemoryProvider(
            state_manager=state_mgr,
            retriever=retriever,
            selector=selector
        )
        _conversation_memory_service = ConversationMemoryService(provider=provider)
    return _conversation_memory_service
