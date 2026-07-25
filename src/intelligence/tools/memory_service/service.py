from datetime import datetime, timezone
from typing import Optional, List
from src.intelligence.platform.contracts import ResponseStatus
from src.intelligence.platform.metadata import ResponseMetadata
from .schema import (
    MemoryStoreRequest, MemoryStoreResponse,
    MemoryRetrieveRequest, MemoryRetrieveResponse,
    MemoryQuery, MemorySearchResponse, RetrievalMetadata
)

class MemoryService:
    def __init__(self, provider, store, index):
        self.provider = provider
        self.store = store
        self.index = index

    def save_memory(self, request: MemoryStoreRequest) -> MemoryStoreResponse:
        context_id = request.snapshot.metadata.context_id
        
        # Retrieve all previous versions of this context_id (append-only log)
        existing_versions = self.store.get_by_context_id(context_id)
        
        memory_record = self.provider.build_memory(
            existing_logs=existing_versions,
            incoming=request.snapshot,
            session_id=request.session_id,
            tags=request.tags,
            importance=request.importance
        )
        
        # Save to store and write to search indexes
        self.store.save(memory_record)
        self.index.index(memory_record)
        
        metadata = ResponseMetadata(
            provider="memory_service",
            model="n/a",
            prompt_version="n/a",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        return MemoryStoreResponse(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            memory_id=memory_record.metadata.memory_id,
            context_id=memory_record.metadata.context_id,
            session_id=memory_record.metadata.session_id
        )

    def retrieve_memory(self, request: MemoryRetrieveRequest) -> MemoryRetrieveResponse:
        results = []
        method = "direct_lookup"
        
        if request.memory_id:
            record = self.store.get_by_memory_id(request.memory_id)
            if record:
                results.append(record)
        elif request.context_id:
            records = self.store.get_by_context_id(request.context_id)
            results.extend(records)
            method = "context_log_lookup"
        elif request.session_id:
            records = self.store.get_by_session_id(request.session_id)
            results.extend(records)
            method = "session_log_lookup"
            
        # Update access count
        for record in results:
            record.metadata.access_count += 1
            self.store.save(record)
            
        metadata = ResponseMetadata(
            provider="memory_service",
            model="n/a",
            prompt_version="n/a",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        retrieval_info = RetrievalMetadata(
            retrieved_at=datetime.now(timezone.utc),
            retrieval_method=method,
            relevance_score=1.0,
            matched_fields=["memory_id" if request.memory_id else ("context_id" if request.context_id else "session_id")]
        )
        
        return MemoryRetrieveResponse(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            memories=results,
            retrieval_info=retrieval_info
        )

    def search_memory(self, request: MemoryQuery) -> MemorySearchResponse:
        results = self.index.search(request)
        
        metadata = ResponseMetadata(
            provider="memory_service",
            model="n/a",
            prompt_version="n/a",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        return MemorySearchResponse(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            results=results
        )

_memory_service = None

def get_memory_service() -> MemoryService:
    global _memory_service
    if _memory_service is None:
        from .provider import MemoryProvider
        from .policy.merge import MergeSnapshotPolicy
        from .policy.retention import DefaultNoOpRetentionPolicy
        from .store.local_file import LocalFileMemoryStore
        
        policy = MergeSnapshotPolicy()
        retention = DefaultNoOpRetentionPolicy()
        provider = MemoryProvider(policy=policy, retention_policy=retention)
        
        # LocalFileMemoryStore implements both Store and Index interfaces
        store_impl = LocalFileMemoryStore()
        
        _memory_service = MemoryService(
            provider=provider,
            store=store_impl,
            index=store_impl
        )
    return _memory_service
