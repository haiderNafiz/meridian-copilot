import datetime
from typing import Any, Dict, List, Optional
from .schema import KnowledgeAsset, KnowledgeChunk, KnowledgeQuery, AssetType
from .registry import KnowledgeRegistry
from .pipeline import IngestionPipeline
from .provider.base import KnowledgeProvider
from .provider.file import LocalFilesystemKnowledgeProvider
from .embedding import EmbeddingRegistry
from .index import IndexRegistry
from .ranking import RankingEngine
from .strategy.dense import DenseRetrievalStrategy
from .strategy.sparse import SparseRetrievalStrategy
from .strategy.hybrid import HybridRetrievalStrategy
from .strategy.filter.attribute import AttributeFilterStrategy

class KnowledgeService:
    def __init__(self, provider: Optional[KnowledgeProvider] = None, registry: Optional[KnowledgeRegistry] = None, embedding_registry: Optional[EmbeddingRegistry] = None, index_registry: Optional[IndexRegistry] = None, pipeline: Optional[IngestionPipeline] = None):
        self.provider = provider or LocalFilesystemKnowledgeProvider()
        self.registry = registry or KnowledgeRegistry()
        self.embedding_registry = embedding_registry or EmbeddingRegistry()
        self.index_registry = index_registry or IndexRegistry()
        
        self.pipeline = pipeline or IngestionPipeline(
            embedding_registry=self.embedding_registry,
            index_registry=self.index_registry
        )
        
        self.ranking_engine = RankingEngine()
        self.dense_strategy = DenseRetrievalStrategy(self.embedding_registry)
        self.sparse_strategy = SparseRetrievalStrategy()
        self.hybrid_strategy = HybridRetrievalStrategy(
            self.dense_strategy, self.sparse_strategy, self.ranking_engine
        )
        self.filter_strategy = AttributeFilterStrategy()

    def ingest_knowledge(self, namespace: str, content: str, asset_type: AssetType, asset_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, version: str = "v1", parent_version_id: Optional[str] = None, derived_from_asset_id: Optional[str] = None) -> KnowledgeAsset:
        asset = KnowledgeAsset(
            asset_id=asset_id or f"ast_{uuid_factory_str()}",
            namespace=namespace,
            asset_type=asset_type,
            content=content,
            metadata=metadata or {},
            version=version,
            parent_version_id=parent_version_id,
            derived_from_asset_id=derived_from_asset_id,
            created_at=datetime.datetime.utcnow().isoformat() + "Z"
        )
        
        self.registry.register_asset(asset)
        self.provider.save_asset(asset)
        self.pipeline.process(asset)
        
        return asset

    def retrieve_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeChunk]:
        ns = query.namespace or "default"
        candidates = self.index_registry.get_chunks(ns)
        
        filtered_candidates = self.filter_strategy.evaluate(candidates, query.filters)
        if not filtered_candidates:
            return []
            
        if query.strategy == "dense":
            results = self.dense_strategy.retrieve(query, filtered_candidates)
        elif query.strategy == "sparse":
            results = self.sparse_strategy.retrieve(query, filtered_candidates)
        else:
            results = self.hybrid_strategy.retrieve(query, filtered_candidates)
            
        if query.min_score is not None:
            results = [r for r in results if r.score is not None and r.score >= query.min_score]
            
        return results[:query.limit]

    def list_knowledge(self, namespace: Optional[str] = None) -> List[KnowledgeAsset]:
        if namespace:
            return self.registry.list_assets_in_namespace(namespace)
        results = []
        for ns in self.registry.list_namespaces():
            results.extend(self.registry.list_assets_in_namespace(ns))
        return results

    def rebuild_embeddings(self, namespace: str) -> None:
        """Reload all assets in a namespace and regenerate chunk embeddings."""
        assets = self.list_knowledge(namespace)
        for asset in assets:
            self.pipeline.process(asset)

def uuid_factory_str() -> str:
    import uuid
    return uuid.uuid4().hex[:10]

_service_instance = None

def get_knowledge_service() -> KnowledgeService:
    global _service_instance
    if _service_instance is None:
        _service_instance = KnowledgeService()
    return _service_instance
