import uuid
from datetime import datetime, timezone
from typing import Optional, List
from src.intelligence.tools.context_builder.schema import ContextSnapshot
from .schema import MemorySnapshot, MemoryMetadata

class MemoryProvider:
    def __init__(self, policy, retention_policy):
        self.policy = policy
        self.retention_policy = retention_policy

    def build_memory(
        self, 
        existing_logs: List[MemorySnapshot], 
        incoming: ContextSnapshot,
        session_id: Optional[str],
        tags: List[str],
        importance: float
    ) -> MemorySnapshot:
        # Enforce append-only state tracking (retrieve latest snapshot version if it exists)
        latest_version = existing_logs[-1] if existing_logs else None
        latest_snapshot = latest_version.snapshot if latest_version else None
        
        # Merge snapshots values
        final_snapshot = self.policy.apply(latest_snapshot, incoming)
        
        now = datetime.now(timezone.utc)
        
        if latest_version:
            # Create a brand new memory entry mapping lineage parent-child relation
            metadata = MemoryMetadata(
                memory_id=str(uuid.uuid4()),
                context_id=incoming.metadata.context_id,
                session_id=session_id or latest_version.metadata.session_id,
                parent_memory_id=latest_version.metadata.memory_id,
                created_at=now,
                last_accessed_at=now,
                access_count=1,
                tags=list(set(latest_version.metadata.tags + tags)),
                importance=importance,
                is_pinned=latest_version.metadata.is_pinned,
                is_archived=latest_version.metadata.is_archived
            )
        else:
            metadata = MemoryMetadata(
                memory_id=str(uuid.uuid4()),
                context_id=incoming.metadata.context_id,
                session_id=session_id or incoming.metadata.session_id,
                parent_memory_id=None,
                created_at=now,
                last_accessed_at=now,
                access_count=1,
                tags=tags,
                importance=importance
            )
            
        memory_record = MemorySnapshot(metadata=metadata, snapshot=final_snapshot)
        
        # Apply retention checks prior to saving
        return self.retention_policy.evaluate_retention(memory_record)
