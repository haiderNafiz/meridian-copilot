from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.intelligence.platform.contracts import BaseRequest, BaseResponse

class ChunkingConfig(BaseModel):
    chunk_size: int = Field(default=500, description="Target character or token length of each chunk")
    overlap: int = Field(default=100, description="Overlapping character or token count between adjacent chunks")
    strategy: str = Field(default="character", description="Chunking strategy: 'character', 'recursive', or 'token'")

class DocumentInput(BaseModel):
    document_id: str = Field(description="Unique parent document identifier")
    text_content: str = Field(description="Raw string content of the document")
    source: str = Field(description="Source origin of the chunk (file path, URL, etc.)")
    chunking_config: ChunkingConfig = Field(default_factory=ChunkingConfig, description="Parameters for chunk splitting")
    custom_tags: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata key-value tags")

class RetrievalInput(BaseRequest):
    query: str = Field(description="Semantic search query string")
    collection: str = Field(default="default", description="Document collection name target")
    limit: int = Field(default=5, description="Maximum number of context chunks to return")
    threshold: float = Field(default=0.0, description="Minimum relevance/confidence similarity score threshold")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filtering key-value limits")

class ChunkMetadata(BaseModel):
    document_id: str = Field(description="Unique parent document identifier")
    chunk_id: str = Field(description="Unique positional chunk identifier (for replay/debug support)")
    source: str = Field(description="Source origin of the chunk")
    chunk_index: int = Field(description="Positional index of the chunk in the document")
    custom_tags: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata key-value tags")

class RetrievalResult(BaseModel):
    text: str = Field(description="Context segment text content")
    score: float = Field(description="Cosine similarity relevance score between 0.0 and 1.0")
    metadata: ChunkMetadata

class RetrievalPayload(BaseModel):
    results: List[RetrievalResult] = Field(default_factory=list, description="Ranked retrieved results list")
    total_retrieved: int = Field(default=0, description="Total number of hits found")

class RetrievalOutput(BaseResponse):
    payload: RetrievalPayload
