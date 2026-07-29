import uuid
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from src.intelligence.platform.contracts import BaseResponse

class AssetType(str, Enum):
    DOCUMENT = "document"
    DATASET = "dataset"
    SNAPSHOT = "snapshot"
    REPLAY = "replay"
    BENCHMARK = "benchmark"
    FEEDBACK = "feedback"
    MULTIMODAL = "multimodal"

class KnowledgeAsset(BaseModel):
    asset_id: str = Field(default_factory=lambda: f"ast_{uuid.uuid4().hex[:10]}")
    namespace: str
    asset_type: AssetType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: str = "v1"
    parent_version_id: Optional[str] = None
    derived_from_asset_id: Optional[str] = None
    created_at: str

class KnowledgeChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:10]}")
    asset_id: str
    namespace: str
    text_content: str
    vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: Optional[float] = None

class KnowledgeQuery(BaseModel):
    query: str
    namespace: Optional[str] = None
    strategy: str = "hybrid"
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = 5
    min_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EmbeddingModelConfig(BaseModel):
    embedding_id: str
    provider: str
    model_name: str
    dimension: int
    version: str
    date_created: str

class KnowledgeResponse(BaseResponse):
    asset: Optional[KnowledgeAsset] = None
    assets: Optional[List[KnowledgeAsset]] = None
    chunks: Optional[List[KnowledgeChunk]] = None
    analytics_summary: Optional[Dict[str, Any]] = None
