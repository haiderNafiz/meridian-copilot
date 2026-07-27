import time
import uuid
from typing import Union
from .schema import (
    ConversationRequest, ConversationResult, ConversationFailure,
    ConversationContext, ConversationWindow
)
from .state_manager import ConversationStateManager
from .retriever import MemoryRetriever
from .selector.base import MemorySelectionStrategy

class ConversationMemoryProvider:
    def __init__(
        self,
        state_manager: ConversationStateManager,
        retriever: MemoryRetriever,
        selector: MemorySelectionStrategy
    ):
        self.state_manager = state_manager
        self.retriever = retriever
        self.selector = selector

    def process_turn(
        self,
        request: ConversationRequest
    ) -> Union[ConversationResult, ConversationFailure]:
        start_time = time.perf_counter()
        trace_id = f"con_{uuid.uuid4().hex[:8]}"
        
        try:
            # 1. Post new turn if text info is present
            if request.role and request.content:
                self.state_manager.add_message_turn(
                    session_id=request.session_id,
                    role=request.role,
                    content=request.content,
                    active_goal=request.active_goal
                )
                
            # 2. Get active session state
            state, wm = self.state_manager.get_or_create_session(request.session_id)
            
            # 3. Retrieve historical persistence memory snapshot records
            retrieved = []
            window = ConversationWindow()
            if window.include_memories:
                retrieved = self.retriever.retrieve_history(
                    session_id=request.session_id,
                    query_text=request.query_text
                )
                
            # 4. Filter and select relevant memories
            context_payload = self.selector.select_memories(
                session_id=request.session_id,
                working_memory=wm,
                retrieved_memories=retrieved,
                window=window,
                active_goal=request.active_goal
            )
            
            # 5. Populate response metadata
            latency = (time.perf_counter() - start_time) * 1000
            from src.intelligence.platform.metadata import ResponseMetadata
            res_metadata = ResponseMetadata(
                provider="conversation_memory",
                model="n/a",
                prompt_version="1.0.0",
                confidence=1.0,
                fallback_used=False,
                provider_latency_ms=latency
            )
            
            return ConversationResult(
                session_id=request.session_id,
                context=context_payload,
                status="success",
                metadata=res_metadata
            )
            
        except Exception as e:
            return ConversationFailure(
                error_code="InternalConversationMemoryError",
                message=f"Conversation memory execution encountered exception: {str(e)}",
                trace_id=trace_id
            )
