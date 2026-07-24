from typing import List

class MockEmbeddingProvider:
    def _get_keyword_vector(self, text: str) -> List[float]:
        text_lower = text.lower()
        if "docker" in text_lower or "python" in text_lower or "go" in text_lower or "backend" in text_lower:
            return [1.0, 0.0, 0.0, 0.0]
        elif "react" in text_lower or "javascript" in text_lower or "frontend" in text_lower:
            return [0.0, 1.0, 0.0, 0.0]
        elif "aws" in text_lower or "kubernetes" in text_lower or "cloud" in text_lower:
            return [0.0, 0.0, 1.0, 0.0]
        else:
            # Equal weight fallback
            return [0.5, 0.5, 0.5, 0.5]

    def embed_query(self, query: str) -> List[float]:
        return self._get_keyword_vector(query)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._get_keyword_vector(t) for t in texts]
