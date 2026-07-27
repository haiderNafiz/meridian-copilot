from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse
from src.intelligence.platform.metadata import ResponseMetadata

class ConversationTurn(BaseModel):
    role: str = Field(description="Speaker role: user, assistant, system")
    content: str = Field(description="Text content of the turn")
    timestamp_utc: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of the turn")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted turn entities")
    unresolved_questions: List[str] = Field(default_factory=list, description="Questions asked in this turn still awaiting response")
    pending_actions: List[str] = Field(default_factory=list, description="Tasks committed to be performed")

class WorkingMemory(BaseModel):
    turns: List[ConversationTurn] = Field(default_factory=list, description="Recent turns window log")
    active_entities: Dict[str, Any] = Field(default_factory=dict, description="Consolidated active session entities")
    unresolved_questions: List[str] = Field(default_factory=list, description="Consolidated session questions")
    pending_actions: List[str] = Field(default_factory=list, description="Consolidated session actions")
    current_topic: Optional[str] = Field(default=None, description="Current discussion subject")
    active_workflow: Optional[str] = Field(default=None, description="Active executing workflow identifier")
    current_assumptions: List[str] = Field(default_factory=list, description="Active conversational assertions")

class ConversationState(BaseModel):
    session_id: str = Field(description="Unique session grouping code")
    current_turn_index: int = Field(default=0, description="Total turns count track")
    active_workflow: Optional[str] = Field(default=None, description="Currently matching workflow code")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class ConversationWindow(BaseModel):
    max_turns: int = Field(default=10, description="Sliding window depth cut")
    include_memories: bool = Field(default=True, description="Retrieve persistent records flag")

class ConversationContext(BaseModel):
    session_id: str = Field(description="Target session tracking reference")
    recent_turns: List[ConversationTurn] = Field(default_factory=list, description="Recent conversation turns window")
    active_entities: Dict[str, Any] = Field(default_factory=dict, description="Consolidated active entities")
    unresolved_questions: List[str] = Field(default_factory=list, description="Consolidated unresolved questions")
    pending_actions: List[str] = Field(default_factory=list, description="Consolidated pending actions")
    active_goal: Optional[str] = Field(default=None, description="Current active session target goal")
    relevant_memories: List[Any] = Field(default_factory=list, description="ContextSnapshots loaded from persistent store")

class ConversationRequest(BaseRequest):
    session_id: str = Field(description="Session grouping code")
    role: Optional[str] = Field(default=None, description="Role of speaker if posting a message")
    content: Optional[str] = Field(default=None, description="Text content of the message if posting")
    query_text: Optional[str] = Field(default=None, description="Query keywords if requesting context search")
    active_goal: Optional[str] = Field(default=None, description="Updated session target goal if specified")

class ConversationResult(BaseResponse):
    session_id: str = Field(description="Session grouping code")
    context: Optional[ConversationContext] = Field(default=None, description="Consolidated conversation context object")
    status: str = Field(default="success", description="Success code")

class ConversationFailure(BaseModel):
    status: str = Field(default="failure", description="Outcome status code")
    error_code: str = Field(description="Designated error class identifier")
    message: str = Field(description="Descriptive explanation of the failure")
    trace_id: str = Field(description="Unique tracking reference code")
