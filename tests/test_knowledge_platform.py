import pytest
from src.intelligence.tools.knowledge_platform.schema import (
    AssetType, KnowledgeAsset, KnowledgeChunk, KnowledgeQuery
)
from src.intelligence.tools.knowledge_platform.registry import KnowledgeRegistry

def test_knowledge_asset_and_lineage():
    registry = KnowledgeRegistry()
    
    ast1 = KnowledgeAsset(
        asset_id="doc_1",
        namespace="sales",
        asset_type=AssetType.DOCUMENT,
        content="hello v1",
        version="v1",
        created_at="2026-07-29T12:00:00Z"
    )
    
    ast2 = KnowledgeAsset(
        asset_id="doc_1",
        namespace="sales",
        asset_type=AssetType.DOCUMENT,
        content="hello v2",
        version="v2",
        parent_version_id="v1",
        derived_from_asset_id="src_pdf_123",
        created_at="2026-07-29T12:05:00Z"
    )
    
    registry.register_asset(ast1)
    registry.register_asset(ast2)
    
    latest = registry.get_asset("doc_1", version="latest")
    assert latest is not None
    assert latest.version == "v2"
    assert latest.derived_from_asset_id == "src_pdf_123"
    
    lineage = registry.get_lineage("doc_1")
    assert len(lineage) == 2
    assert lineage[0].version == "v1"
    assert lineage[1].version == "v2"

def test_chunk_strategies():
    from src.intelligence.tools.knowledge_platform.strategy.chunk import ParagraphChunker, SlidingWindowChunker
    
    para_chunker = ParagraphChunker()
    text = "First paragraph.\n\nSecond paragraph."
    chunks = para_chunker.chunk(text)
    assert len(chunks) == 2
    assert chunks[0] == "First paragraph."
    assert chunks[1] == "Second paragraph."
    
    sliding = SlidingWindowChunker(window_size=10, overlap=3)
    chunks_s = sliding.chunk("abcdefghijkl")
    assert len(chunks_s) >= 2

def test_embedding_registry_and_indexing():
    from src.intelligence.tools.knowledge_platform.embedding import EmbeddingRegistry
    from src.intelligence.tools.knowledge_platform.index import IndexRegistry
    from src.intelligence.tools.knowledge_platform.schema import KnowledgeChunk
    
    embed_reg = EmbeddingRegistry()
    config = embed_reg.get_model_config("default_text_embed")
    assert config is not None
    assert config.dimension == 1536
    
    vectors = embed_reg.generate_embeddings("default_text_embed", ["hello"])
    assert len(vectors) == 1
    assert len(vectors[0]) == 1536
    
    index_reg = IndexRegistry()
    chunk = KnowledgeChunk(asset_id="asset_1", namespace="finance", text_content="income statement")
    index_reg.index_chunks("finance", [chunk])
    
    retrieved = index_reg.get_chunks("finance")
    assert len(retrieved) == 1
    assert retrieved[0].text_content == "income statement"

def test_ingestion_pipeline_hooks():
    from src.intelligence.tools.knowledge_platform.pipeline import IngestionPipeline, IngestionHook
    from src.intelligence.tools.knowledge_platform.schema import KnowledgeAsset, AssetType
    
    class MockIngestionHook(IngestionHook):
        def __init__(self):
            self.triggered_before = False
            self.triggered_after = False
        def before_ingestion(self, asset, context):
            self.triggered_before = True
        def after_index(self, chunks, context):
            self.triggered_after = True
            
    hook = MockIngestionHook()
    pipeline = IngestionPipeline(hooks=[hook])
    
    asset = KnowledgeAsset(
        asset_id="doc_x",
        namespace="tech",
        asset_type=AssetType.DOCUMENT,
        content="line 1\n\nline 2",
        created_at="2026-07-29"
    )
    
    chunks = pipeline.process(asset)
    assert len(chunks) == 2
    assert hook.triggered_before is True
    assert hook.triggered_after is True
    assert chunks[0].vector is not None
    assert len(chunks[0].vector) == 1536

def test_filters_and_retrieval_strategies():
    from src.intelligence.tools.knowledge_platform.strategy.filter.attribute import AttributeFilterStrategy
    from src.intelligence.tools.knowledge_platform.strategy.dense import DenseRetrievalStrategy
    from src.intelligence.tools.knowledge_platform.strategy.sparse import SparseRetrievalStrategy
    from src.intelligence.tools.knowledge_platform.strategy.hybrid import HybridRetrievalStrategy
    from src.intelligence.tools.knowledge_platform.ranking import RankingEngine
    from src.intelligence.tools.knowledge_platform.embedding import EmbeddingRegistry
    from src.intelligence.tools.knowledge_platform.schema import KnowledgeChunk, KnowledgeQuery
    
    chunk1 = KnowledgeChunk(asset_id="a1", namespace="hr", text_content="resumes", metadata={"visibility": "internal"})
    chunk2 = KnowledgeChunk(asset_id="a2", namespace="hr", text_content="salaries", metadata={"visibility": "restricted"})
    
    filter_strat = AttributeFilterStrategy()
    res_f = filter_strat.evaluate([chunk1, chunk2], {"visibility": "restricted"})
    assert len(res_f) == 1
    assert res_f[0].asset_id == "a2"
    
    embed_reg = EmbeddingRegistry()
    ranking_engine = RankingEngine()
    dense_strat = DenseRetrievalStrategy(embed_reg)
    sparse_strat = SparseRetrievalStrategy()
    hybrid_strat = HybridRetrievalStrategy(dense_strat, sparse_strat, ranking_engine)
    
    chunk_dense1 = KnowledgeChunk(asset_id="d1", namespace="hr", text_content="benefits options policy", vector=[0.1]*1536)
    chunk_dense2 = KnowledgeChunk(asset_id="d2", namespace="hr", text_content="salaries bonus structures", vector=[0.8]*1536)
    
    query = KnowledgeQuery(query="salaries structures", namespace="hr", limit=2)
    
    dense_hits = dense_strat.retrieve(query, [chunk_dense1, chunk_dense2])
    assert len(dense_hits) > 0
    
    sparse_hits = sparse_strat.retrieve(query, [chunk_dense1, chunk_dense2])
    assert sparse_hits[0].asset_id == "d2"
    
    hybrid_hits = hybrid_strat.retrieve(query, [chunk_dense1, chunk_dense2])
    assert len(hybrid_hits) > 0

def test_knowledge_service_facade():
    import tempfile
    from src.intelligence.tools.knowledge_platform.provider.file import LocalFilesystemKnowledgeProvider
    from src.intelligence.tools.knowledge_platform.service import KnowledgeService
    from src.intelligence.tools.knowledge_platform.schema import AssetType, KnowledgeQuery
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemKnowledgeProvider(base_dir=tmpdir)
        service = KnowledgeService(provider=provider)
        
        asset = service.ingest_knowledge(
            namespace="sales",
            content="quarterly revenue projections.\n\nannual partner contracts.",
            asset_type=AssetType.DOCUMENT,
            asset_id="projections_1",
            metadata={"visibility": "internal"}
        )
        assert asset.asset_id == "projections_1"
        
        loaded = provider.get_asset("projections_1", "v1")
        assert loaded is not None
        assert "quarterly revenue" in loaded.content
        
        query = KnowledgeQuery(
            query="revenue projections",
            namespace="sales",
            strategy="sparse",
            filters={"visibility": "internal"},
            limit=1
        )
        hits = service.retrieve_knowledge(query)
        assert len(hits) == 1
        assert "quarterly revenue" in hits[0].text_content

def test_knowledge_analytics_registry():
    from src.intelligence.tools.knowledge_platform.analytics import KnowledgeAnalyticsRegistry, KnowledgeMetric
    from src.intelligence.tools.knowledge_platform.schema import KnowledgeAsset, KnowledgeChunk, AssetType
    
    registry = KnowledgeAnalyticsRegistry()
    
    class MockChunkCountMetric(KnowledgeMetric):
        def calculate(self, assets, chunks):
            return len(chunks)
            
    registry.register_metric("chunk_count", MockChunkCountMetric())
    
    ast = KnowledgeAsset(
        asset_id="a1", namespace="hr", asset_type=AssetType.DOCUMENT, content="hello", created_at="2026"
    )
    chunk = KnowledgeChunk(asset_id="a1", namespace="hr", text_content="hello")
    
    metrics = registry.compute_all([ast], [chunk])
    assert metrics["chunk_count"] == 1
    assert metrics["storage_growth"] == 5
    assert metrics["namespace_growth"] == {"hr": 1}

@pytest.mark.anyio
async def test_mcp_knowledge_platform_tools():
    import json
    import tempfile
    import os
    from src.intelligence.mcp.server import ingest_knowledge, list_knowledge, retrieve_knowledge_platform, rebuild_embeddings, knowledge_statistics
    from src.intelligence.tools.knowledge_platform.service import get_knowledge_service
    from src.intelligence.tools.knowledge_platform.provider.file import LocalFilesystemKnowledgeProvider
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemKnowledgeProvider(base_dir=tmpdir)
        service = get_knowledge_service()
        service.provider = provider
        service.provider.base_dir = tmpdir
        service.provider.assets_dir = os.path.join(tmpdir, "assets")
        service.provider.indices_dir = os.path.join(tmpdir, "indices")
        os.makedirs(service.provider.assets_dir, exist_ok=True)
        os.makedirs(service.provider.indices_dir, exist_ok=True)
        
        res_ing = await ingest_knowledge(
            namespace="legal",
            content="nondisclosure agreements templates.",
            asset_type="document",
            asset_id="legal_1"
        )
        data_ing = json.loads(res_ing)
        assert data_ing["status"] == "success"
        
        res_list = await list_knowledge(namespace="legal")
        data_list = json.loads(res_list)
        assert len(data_list["assets"]) == 1
        
        res_ret = await retrieve_knowledge_platform(
            query="nondisclosure templates",
            namespace="legal",
            strategy="sparse"
        )
        data_ret = json.loads(res_ret)
        assert len(data_ret["chunks"]) == 1
        assert "nondisclosure" in data_ret["chunks"][0]["text_content"]
        
        res_stats = await knowledge_statistics()
        data_stats = json.loads(res_stats)
        assert data_stats["analytics_summary"]["storage_growth"] > 0
