from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class MemoryMetadata(BaseModel):
    memory_id: str = Field(description="Unique identifier for this specific version entry (UUID)")
    context_id: str = Field(description="Immutable source ContextSnapshot identifier")
    session_id: Optional[str] = Field(default=None, description="Conversational session code grouping memories")
    parent_memory_id: Optional[str] = Field(default=None, description="Lineage reference to preceding version (Snapshot V1 -> V2)")
    created_at: datetime = Field(description="UTC timestamp of snapshot entry insertion")
    last_accessed_at: datetime = Field(description="UTC timestamp of last retrieval or search match")
    access_count: int = Field(default=1, description="Number of times this memory record has been accessed")
    tags: List[str] = Field(default_factory=list, description="Keywords or structural classification tags")
    importance: float = Field(default=1.0, ge=0.0, le=1.0, description="Significance score for retrieval priority")
    version: str = Field(default="1.0.0", description="Memory system schema version")
    
    # Retention markers
    is_pinned: bool = Field(default=False, description="Explicit pin to prevent eviction")
    is_archived: bool = Field(default=False, description="Flagged for long-term archiving")

class MemorySnapshot(BaseModel):
    metadata: MemoryMetadata = Field(description="Memory tracking and indexing metadata")
    snapshot: ContextSnapshot = Field(description="The underlying immutable canonical ContextSnapshot")

class MemoryStoreRequest(BaseRequest):
    snapshot: ContextSnapshot = Field(description="The canonical ContextSnapshot to persist")
    session_id: Optional[str] = Field(default=None, description="Conversational session identifier")
    tags: List[str] = Field(default_factory=list, description="Keywords for indexing and retrieval")
    importance: float = Field(default=1.0, description="Significance score")

class MemoryStoreResponse(BaseResponse):
    memory_id: str = Field(description="Assigned memory record UUID")
    context_id: str = Field(description="Persisted ContextSnapshot ID")
    session_id: Optional[str] = Field(default=None, description="Conversational session code")

class MemoryRetrieveRequest(BaseRequest):
    context_id: Optional[str] = Field(default=None, description="Retrieve snapshot by Context ID")
    session_id: Optional[str] = Field(default=None, description="Retrieve snapshots by Session ID")
    memory_id: Optional[str] = Field(default=None, description="Retrieve snapshot by Memory ID")

class RetrievalMetadata(BaseModel):
    retrieved_at: datetime = Field(description="UTC timestamp of retrieval execution")
    retrieval_method: str = Field(description="Search strategy matched (e.g. 'direct_lookup', 'tag_filter', 'text_scan')")
    relevance_score: float = Field(default=1.0, description="Match score indicator (1.0 = direct match)")
    matched_fields: List[str] = Field(default_factory=list, description="List of structural paths matching terms")

class MemoryRetrieveResponse(BaseResponse):
    memories: List[MemorySnapshot] = Field(default_factory=list, description="Matched memory snapshots list")
    retrieval_info: Optional[RetrievalMetadata] = Field(default=None, description="Direct retrieval meta logs")

class MemoryQuery(BaseRequest):
    query_text: Optional[str] = Field(default=None, description="Optional text query to scan facts/reasoning fields")
    session_id: Optional[str] = Field(default=None, description="Optional session filter")
    tags: List[str] = Field(default_factory=list, description="Optional tags filter")
    importance_threshold: float = Field(default=0.0, description="Minimum importance rating")
    limit: int = Field(default=10, description="Max results count")

class MemorySearchResult(BaseModel):
    memory: MemorySnapshot = Field(description="Matching memory snapshot")
    retrieval_info: RetrievalMetadata = Field(description="Search trace match details")

class MemorySearchResponse(BaseResponse):
    results: List[MemorySearchResult] = Field(default_factory=list, description="Ordered search matches")
