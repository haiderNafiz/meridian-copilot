from typing import List
from ..schema import DocumentInput, ChunkMetadata
from ..store.base import VectorStoreProtocol, VectorRecord
from ..embedding.base import EmbeddingProviderProtocol
from .chunking import chunk_text

class DocumentIndexer:
    def __init__(
        self,
        store: VectorStoreProtocol,
        embedding: EmbeddingProviderProtocol
    ):
        self.store = store
        self.embedding = embedding

    def index_document(self, collection: str, doc: DocumentInput) -> bool:
        # Step 1: Chunk the text content using config guidelines
        chunks = chunk_text(doc.text_content, doc.chunking_config)
        if not chunks:
            return False
            
        # Step 2: Batch embed chunk strings
        embeddings = self.embedding.embed_documents(chunks)
        
        # Step 3: Compile VectorRecords
        records = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{doc.document_id}_chunk_{i}"
            meta = ChunkMetadata(
                document_id=doc.document_id,
                chunk_id=chunk_id,
                source=doc.source,
                chunk_index=i,
                custom_tags=doc.custom_tags
            )
            records.append(VectorRecord(text=chunk, vector=vector, metadata=meta))
            
        # Step 4: Index records in Vector Store
        return self.store.upsert(collection, records)
