from typing import List, Dict, Any
from .base import MetadataFilterStrategy
from ...schema import KnowledgeChunk

class AttributeFilterStrategy(MetadataFilterStrategy):
    def evaluate(self, chunks: List[KnowledgeChunk], query_filters: Dict[str, Any]) -> List[KnowledgeChunk]:
        if not query_filters:
            return chunks
        results = []
        for chunk in chunks:
            match = True
            for key, val in query_filters.items():
                if key == "namespace":
                    if chunk.namespace != val:
                        match = False
                        break
                elif key == "min_score":
                    if chunk.score is not None and chunk.score < float(val):
                        match = False
                        break
                else:
                    if chunk.metadata.get(key) != val:
                        match = False
                        break
            if match:
                results.append(chunk)
        return results
