from typing import Dict, List, Optional
from .schema import EmbeddingModelConfig

class EmbeddingRegistry:
    def __init__(self):
        self._models: Dict[str, EmbeddingModelConfig] = {}
        self.register_model(EmbeddingModelConfig(
            embedding_id="default_text_embed",
            provider="mock",
            model_name="mock-embedding-model-001",
            dimension=1536,
            version="v1",
            date_created="2026-07-29"
        ))

    def register_model(self, config: EmbeddingModelConfig) -> None:
        self._models[config.embedding_id] = config

    def get_model_config(self, embedding_id: str) -> Optional[EmbeddingModelConfig]:
        return self._models.get(embedding_id)

    def generate_embeddings(self, embedding_id: str, texts: List[str]) -> List[List[float]]:
        config = self.get_model_config(embedding_id)
        if not config:
            raise ValueError(f"Embedding model config not found: {embedding_id}")
        
        results = []
        for text in texts:
            dim = config.dimension
            val = float(len(text) % 100) / 100.0
            vector = [val] * dim
            results.append(vector)
        return results
