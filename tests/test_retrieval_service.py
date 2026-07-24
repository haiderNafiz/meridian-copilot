import pytest
import json
from src.intelligence.platform.test_utils import run_mcp_session
from src.intelligence.tools.knowledge_service.schema import ChunkingConfig, ChunkMetadata
from src.intelligence.tools.knowledge_service.indexing.chunking import chunk_text
from src.intelligence.tools.knowledge_service.ranking.cosine import compute_cosine_similarity, CosineSimilarityRanker
from src.intelligence.tools.knowledge_service.store.base import VectorRecord

def test_character_chunker_basic():
    config = ChunkingConfig(chunk_size=10, overlap=2, strategy="character")
    text = "abcdefghijklmnop"
    # Overlap step: size - overlap = 10 - 2 = 8
    # Chunk 0: text[0:10] = "abcdefghij"
    # Chunk 1: text[8:18] = "ijklmnop"
    chunks = chunk_text(text, config)
    assert len(chunks) == 2
    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "ijklmnop"

def test_cosine_similarity_calculation():
    # Identical vectors -> similarity = 1.0
    v1 = [1.0, 2.0, 3.0]
    v2 = [1.0, 2.0, 3.0]
    assert pytest.approx(compute_cosine_similarity(v1, v2), 0.0001) == 1.0
    
    # Orthogonal vectors -> similarity = 0.0
    v3 = [1.0, 0.0]
    v4 = [0.0, 1.0]
    assert compute_cosine_similarity(v3, v4) == 0.0

def test_cosine_similarity_ranker():
    ranker = CosineSimilarityRanker()
    query = [1.0, 0.0]
    
    rec1 = VectorRecord(
        text="Orthogonal text",
        vector=[0.0, 1.0],
        metadata=ChunkMetadata(document_id="doc1", chunk_id="c1", source="s1", chunk_index=0)
    )
    rec2 = VectorRecord(
        text="Matching text",
        vector=[1.0, 0.0],
        metadata=ChunkMetadata(document_id="doc2", chunk_id="c2", source="s2", chunk_index=0)
    )
    
    results = ranker.rank(query, [rec1, rec2])
    assert len(results) == 2
    # Matching text should be ranked first
    assert results[0].text == "Matching text"
    assert results[0].score == 1.0
    assert results[1].text == "Orthogonal text"
    assert results[1].score == 0.0

def test_mock_vector_store_query_and_upsert():
    from src.intelligence.tools.knowledge_service.store.mock_store import MockVectorStore
    from src.intelligence.tools.knowledge_service.store.base import VectorRecord
    from src.intelligence.tools.knowledge_service.schema import ChunkMetadata
    
    store = MockVectorStore()
    
    # Query prepopulated records
    results = store.query(query_vector=[1.0, 0.0, 0.0, 0.0], collection="default", limit=5)
    assert len(results) == 3 # Returns all records in collection
    
    # Upsert a new record
    new_meta = ChunkMetadata(document_id="doc_new", chunk_id="chunk_new_0", source="test.txt", chunk_index=0)
    new_rec = VectorRecord(text="Newly indexed info", vector=[0.5, 0.5, 0.5, 0.5], metadata=new_meta)
    
    success = store.upsert("default", [new_rec])
    assert success is True
    
    # Test collection listing
    collections = store.list_collections()
    assert "default" in collections
    
    # Test filters
    filtered_results = store.query(
        query_vector=[1.0, 0.0, 0.0, 0.0],
        collection="default",
        limit=5,
        filters={"document_id": "doc_new"}
    )
    assert len(filtered_results) == 1
    assert filtered_results[0].text == "Newly indexed info"

def test_mock_embedding_provider():
    from src.intelligence.tools.knowledge_service.embedding.mock_embed import MockEmbeddingProvider
    
    embedder = MockEmbeddingProvider()
    
    q_vec = embedder.embed_query("Looking for a Docker specialist")
    assert q_vec == [1.0, 0.0, 0.0, 0.0]
    
    docs_vecs = embedder.embed_documents(["AWS and kubernetes", "React UI"])
    assert len(docs_vecs) == 2
    assert docs_vecs[0] == [0.0, 0.0, 1.0, 0.0]
    assert docs_vecs[1] == [0.0, 1.0, 0.0, 0.0]

def test_document_indexer_basic():
    from src.intelligence.tools.knowledge_service.indexing.ingest import DocumentIndexer
    from src.intelligence.tools.knowledge_service.store.mock_store import MockVectorStore
    from src.intelligence.tools.knowledge_service.embedding.mock_embed import MockEmbeddingProvider
    from src.intelligence.tools.knowledge_service.schema import DocumentInput, ChunkingConfig
    
    store = MockVectorStore()
    embedder = MockEmbeddingProvider()
    indexer = DocumentIndexer(store=store, embedding=embedder)
    
    doc = DocumentInput(
        document_id="doc_test_indexing",
        text_content="Docker is amazing. Kubernetes is hard.",
        source="doc_test.txt",
        chunking_config=ChunkingConfig(chunk_size=18, overlap=0, strategy="character")
    )
    
    success = indexer.index_document("default", doc)
    assert success is True
    
    indexed_records = store.query(query_vector=[1.0, 0.0, 0.0, 0.0], collection="default", limit=10)
    assert len(indexed_records) == 6
    
    chunk_docs = [r for r in indexed_records if r.metadata.document_id == "doc_test_indexing"]
    assert len(chunk_docs) == 3
    assert chunk_docs[0].metadata.chunk_id == "doc_test_indexing_chunk_0"
    assert chunk_docs[0].metadata.chunk_index == 0

def test_retrieval_service_orchestration():
    from src.intelligence.tools.knowledge_service.service import RetrievalService
    from src.intelligence.tools.knowledge_service.provider import RetrievalProvider
    from src.intelligence.tools.knowledge_service.store.mock_store import MockVectorStore
    from src.intelligence.tools.knowledge_service.embedding.mock_embed import MockEmbeddingProvider
    from src.intelligence.tools.knowledge_service.ranking.cosine import CosineSimilarityRanker
    from src.intelligence.tools.knowledge_service.schema import RetrievalInput
    
    store = MockVectorStore()
    embedder = MockEmbeddingProvider()
    ranker = CosineSimilarityRanker()
    provider = RetrievalProvider(store=store, embedding=embedder, ranker=ranker)
    service = RetrievalService(provider=provider)
    
    # Query matching John (frontend vector [0, 1, 0, 0])
    req = RetrievalInput(query="React frontend developer", limit=2, threshold=0.5)
    output = service.process(req)
    
    assert output.status.value == "success"
    assert output.metadata.provider == "mock_store"
    assert output.metadata.model == "mock-embed"
    
    # Matching John should be first with similarity score 1.0
    results = output.payload.results
    assert len(results) >= 1
    assert results[0].text == "John is a frontend architect working with React.js, JavaScript, and Tailwind CSS."
    assert results[0].score == 1.0
    
    # Query with strict threshold that should filter out everything
    req_strict = RetrievalInput(query="React frontend developer", limit=2, threshold=0.99)
    output_strict = service.process(req_strict)
    assert len(output_strict.payload.results) == 1
    assert output_strict.payload.results[0].score == 1.0

def test_mcp_retrieve_knowledge_success():
    call_req = {
        "jsonrpc": "2.0",
        "id": 501,
        "method": "tools/call",
        "params": {
            "name": "retrieve_knowledge",
            "arguments": {
                "query": "React frontend developer",
                "limit": 2,
                "threshold": 0.5
            }
        }
    }
    
    responses, stderr_lines = run_mcp_session([call_req])
    
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert "content" in resp["result"]
    
    content_raw = resp["result"]["content"][0]["text"]
    content_data = json.loads(content_raw)
    
    assert content_data["status"] == "success"
    payload = content_data["payload"]
    results = payload["results"]
    assert len(results) >= 1
    assert results[0]["text"] == "John is a frontend architect working with React.js, JavaScript, and Tailwind CSS."
    assert results[0]["score"] == 1.0
    
    json_logs = []
    for line in stderr_lines:
        try:
            parsed = json.loads(line)
            if "request_id" in parsed:
                json_logs.append(parsed)
        except json.JSONDecodeError:
            continue
            
    assert len(json_logs) == 1
    log = json_logs[0]
    assert log["tool_name"] == "retrieve_knowledge"
    assert log["provider"] == "mock_store"
    assert log["model"] == "mock-embed"
    assert log["status"] == "success"
