from abc import ABC
from typing import Any, Dict, List, Optional
from .schema import KnowledgeAsset, KnowledgeChunk
from .strategy.chunk.base import ChunkStrategy
from .strategy.chunk.paragraph import ParagraphChunker
from .embedding import EmbeddingRegistry
from .index import IndexRegistry

class IngestionHook(ABC):
    def before_ingestion(self, asset: KnowledgeAsset, context: Dict[str, Any]) -> None:
        pass
    def after_chunking(self, chunks: List[KnowledgeChunk], context: Dict[str, Any]) -> None:
        pass
    def before_embedding(self, chunks: List[KnowledgeChunk], context: Dict[str, Any]) -> None:
        pass
    def after_embedding(self, chunks: List[KnowledgeChunk], context: Dict[str, Any]) -> None:
        pass
    def before_index(self, chunks: List[KnowledgeChunk], context: Dict[str, Any]) -> None:
        pass
    def after_index(self, chunks: List[KnowledgeChunk], context: Dict[str, Any]) -> None:
        pass

class IngestionPipeline:
    def __init__(self, chunk_strategy: Optional[ChunkStrategy] = None, embedding_registry: Optional[EmbeddingRegistry] = None, index_registry: Optional[IndexRegistry] = None, hooks: Optional[List[IngestionHook]] = None):
        self.chunk_strategy = chunk_strategy or ParagraphChunker()
        self.embedding_registry = embedding_registry or EmbeddingRegistry()
        self.index_registry = index_registry or IndexRegistry()
        self.hooks = hooks or []

    def register_hook(self, hook: IngestionHook) -> None:
        self.hooks.append(hook)

    def process(self, asset: KnowledgeAsset, context: Optional[Dict[str, Any]] = None) -> List[KnowledgeChunk]:
        run_context = context or {}

        for hook in self.hooks:
            try:
                hook.before_ingestion(asset, run_context)
            except Exception:
                pass

        raw_chunks = self.chunk_strategy.chunk(asset.content)
        chunks = []
        for i, text in enumerate(raw_chunks):
            chunk_metadata = {"index": i}
            if asset.metadata:
                chunk_metadata.update(asset.metadata)
            chunk = KnowledgeChunk(
                chunk_id=f"chk_{asset.asset_id}_{i}",
                asset_id=asset.asset_id,
                namespace=asset.namespace,
                text_content=text,
                metadata=chunk_metadata
            )
            chunks.append(chunk)

        for hook in self.hooks:
            try:
                hook.after_chunking(chunks, run_context)
            except Exception:
                pass

        for hook in self.hooks:
            try:
                hook.before_embedding(chunks, run_context)
            except Exception:
                pass

        embedding_model_id = run_context.get("embedding_id", "default_text_embed")
        texts_to_embed = [c.text_content for c in chunks]
        if texts_to_embed:
            vectors = self.embedding_registry.generate_embeddings(embedding_model_id, texts_to_embed)
            for chunk, vector in zip(chunks, vectors):
                chunk.vector = vector

        for hook in self.hooks:
            try:
                hook.after_embedding(chunks, run_context)
            except Exception:
                pass

        for hook in self.hooks:
            try:
                hook.before_index(chunks, run_context)
            except Exception:
                pass

        self.index_registry.index_chunks(asset.namespace, chunks)

        for hook in self.hooks:
            try:
                hook.after_index(chunks, run_context)
            except Exception:
                pass

        return chunks
