from typing import List
from .base_retrieval import RetrievalStrategy
from ..schema import KnowledgeQuery, KnowledgeChunk
from ..embedding import EmbeddingRegistry

class DenseRetrievalStrategy(RetrievalStrategy):
    def __init__(self, embedding_registry: EmbeddingRegistry):
        self.embedding_registry = embedding_registry

    def retrieve(self, query: KnowledgeQuery, chunks: List[KnowledgeChunk]) -> List[KnowledgeChunk]:
        model_id = query.metadata.get("embedding_id", "default_text_embed")
        query_vectors = self.embedding_registry.generate_embeddings(model_id, [query.query])
        if not query_vectors or not chunks:
            return []
            
        q_val = query_vectors[0][0]
        scored_chunks = []
        for chunk in chunks:
            if chunk.vector:
                c_val = chunk.vector[0]
                score = 1.0 - abs(q_val - c_val)
                chunk.score = float(score)
                scored_chunks.append(chunk)
                
        scored_chunks.sort(key=lambda x: x.score or 0.0, reverse=True)
        return scored_chunks[:query.limit]
