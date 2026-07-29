from typing import List
from .base_retrieval import RetrievalStrategy
from .dense import DenseRetrievalStrategy
from .sparse import SparseRetrievalStrategy
from ..schema import KnowledgeQuery, KnowledgeChunk
from ..ranking import RankingEngine

class HybridRetrievalStrategy(RetrievalStrategy):
    def __init__(self, dense_strategy: DenseRetrievalStrategy, sparse_strategy: SparseRetrievalStrategy, ranking_engine: RankingEngine):
        self.dense_strategy = dense_strategy
        self.sparse_strategy = sparse_strategy
        self.ranking_engine = ranking_engine

    def retrieve(self, query: KnowledgeQuery, chunks: List[KnowledgeChunk]) -> List[KnowledgeChunk]:
        dense_hits = self.dense_strategy.retrieve(query, chunks)
        sparse_hits = self.sparse_strategy.retrieve(query, chunks)
        
        merged = self.ranking_engine.reciprocal_rank_fusion(dense_hits, sparse_hits)
        return merged[:query.limit]
