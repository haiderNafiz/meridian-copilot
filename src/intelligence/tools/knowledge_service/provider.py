from typing import Optional, List
from .schema import RetrievalInput, RetrievalPayload
from .store.base import VectorStoreProtocol
from .embedding.base import EmbeddingProviderProtocol
from .ranking.base import RankerProtocol

class RetrievalProvider:
    def __init__(
        self,
        store: VectorStoreProtocol,
        embedding: EmbeddingProviderProtocol,
        ranker: RankerProtocol
    ):
        self.store = store
        self.embedding = embedding
        self.ranker = ranker

    def infer(self, request: RetrievalInput) -> RetrievalPayload:
        # Step 1: Embed Query
        query_vector = self.embedding.embed_query(request.query)
        
        # Step 2: Query Store (Retrieving candidate vector records)
        records = self.store.query(
            query_vector=query_vector,
            collection=request.collection,
            limit=request.limit,
            filters=request.filters
        )
        
        # Step 3: Delegate Similarity Scoring & Ranking to Ranker Strategy
        ranked_results = self.ranker.rank(query_vector, records)
        
        # Step 4: Apply threshold filtering and limit boundaries
        filtered_results = [r for r in ranked_results if r.score >= request.threshold]
        filtered_results = filtered_results[:request.limit]
        
        return RetrievalPayload(results=filtered_results, total_retrieved=len(filtered_results))
