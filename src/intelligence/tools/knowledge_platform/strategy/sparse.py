from typing import List
from .base_retrieval import RetrievalStrategy
from ..schema import KnowledgeQuery, KnowledgeChunk

class SparseRetrievalStrategy(RetrievalStrategy):
    def retrieve(self, query: KnowledgeQuery, chunks: List[KnowledgeChunk]) -> List[KnowledgeChunk]:
        if not chunks:
            return []
            
        query_words = set(query.query.lower().split())
        scored_chunks = []
        for chunk in chunks:
            chunk_words = set(chunk.text_content.lower().split())
            intersection = query_words.intersection(chunk_words)
            
            score = float(len(intersection)) / float(max(1, len(chunk_words)))
            chunk.score = score
            scored_chunks.append(chunk)
            
        scored_chunks.sort(key=lambda x: x.score or 0.0, reverse=True)
        return scored_chunks[:query.limit]
