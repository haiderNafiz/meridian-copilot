from typing import List, Dict
from .schema import KnowledgeChunk

class RankingEngine:
    def reciprocal_rank_fusion(self, dense_results: List[KnowledgeChunk], sparse_results: List[KnowledgeChunk], k: int = 60) -> List[KnowledgeChunk]:
        """Combine dense and sparse result lists using Reciprocal Rank Fusion (RRF)."""
        rrf_scores: Dict[str, float] = {}
        chunks_map: Dict[str, KnowledgeChunk] = {}

        for rank, chunk in enumerate(dense_results):
            chunks_map[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + (1.0 / (rank + 1 + k))

        for rank, chunk in enumerate(sparse_results):
            chunks_map[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + (1.0 / (rank + 1 + k))

        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        merged_results = []
        for cid in sorted_ids:
            chunk = chunks_map[cid]
            chunk.score = rrf_scores[cid]
            merged_results.append(chunk)
            
        return merged_results
