import math
from typing import List
from ..schema import RetrievalResult
from ..store.base import VectorRecord

def compute_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Computes the cosine similarity score between two float vectors.
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
        
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

class CosineSimilarityRanker:
    def rank(self, query_vector: List[float], records: List[VectorRecord]) -> List[RetrievalResult]:
        results = []
        for rec in records:
            score = compute_cosine_similarity(query_vector, rec.vector)
            results.append(RetrievalResult(
                text=rec.text,
                score=round(score, 4),
                metadata=rec.metadata
            ))
            
        # Sort by similarity score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results
