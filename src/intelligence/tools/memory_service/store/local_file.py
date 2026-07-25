import os
import json
from datetime import datetime, timezone
from typing import List, Optional
from ..schema import MemorySnapshot, MemoryQuery, MemorySearchResult, RetrievalMetadata
from .base import MemoryStore, MemoryIndex

class LocalFileMemoryStore(MemoryStore, MemoryIndex):
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Locate file relative to workspace
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            storage_dir = os.path.join(base_dir, "storage")
            os.makedirs(storage_dir, exist_ok=True)
            db_path = os.path.join(storage_dir, "memory_db.json")
        self.db_path = db_path

    def _load_all(self) -> List[MemorySnapshot]:
        if not os.path.exists(self.db_path):
            return []
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                return [MemorySnapshot.model_validate(item) for item in raw_data]
        except (json.JSONDecodeError, ValueError):
            return []

    def _write_all(self, memories: List[MemorySnapshot]) -> None:
        serialized = [json.loads(mem.model_dump_json()) for mem in memories]
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)

    def save(self, memory: MemorySnapshot) -> None:
        memories = self._load_all()
        updated = False
        for idx, item in enumerate(memories):
            if item.metadata.memory_id == memory.metadata.memory_id:
                memories[idx] = memory
                updated = True
                break
        if not updated:
            memories.append(memory)
        self._write_all(memories)

    def get_by_memory_id(self, memory_id: str) -> Optional[MemorySnapshot]:
        memories = self._load_all()
        for item in memories:
            if item.metadata.memory_id == memory_id:
                return item
        return None

    def get_by_context_id(self, context_id: str) -> List[MemorySnapshot]:
        memories = self._load_all()
        return [item for item in memories if item.metadata.context_id == context_id]

    def get_by_session_id(self, session_id: str) -> List[MemorySnapshot]:
        memories = self._load_all()
        return [item for item in memories if item.metadata.session_id == session_id]

    def index(self, memory: MemorySnapshot) -> None:
        # File-based store acts as its own index, so indexing is handled inside save()
        pass

    def search(self, query: MemoryQuery) -> List[MemorySearchResult]:
        memories = self._load_all()
        results = []
        
        for item in memories:
            # 1. Session ID filter
            if query.session_id and item.metadata.session_id != query.session_id:
                continue
                
            # 2. Importance threshold
            if item.metadata.importance < query.importance_threshold:
                continue
                
            # 3. Tag intersection filter
            if query.tags:
                matched_tags = set(query.tags).intersection(set(item.metadata.tags))
                if not matched_tags:
                    continue
                    
            # 4. Text query scanning facts and reasoning
            relevance = 1.0
            matched_fields = []
            if query.query_text:
                q = query.query_text.lower()
                # Scan facts
                if item.snapshot.facts.role_type and q in item.snapshot.facts.role_type.lower():
                    matched_fields.append("facts.role_type")
                if item.snapshot.facts.seniority and q in item.snapshot.facts.seniority.lower():
                    matched_fields.append("facts.seniority")
                for domain in item.snapshot.facts.technical_domains:
                    if q in domain.lower():
                        matched_fields.append("facts.technical_domains")
                for tech in item.snapshot.facts.normalized_technologies:
                    if q in tech.lower():
                        matched_fields.append("facts.normalized_technologies")
                # Scan reasoning
                for r_key, r_val in item.snapshot.reasoning.scoring_reasoning.items():
                    if q in r_val.lower():
                        matched_fields.append(f"reasoning.scoring_reasoning.{r_key}")
                if item.snapshot.reasoning.summary_reasoning and q in item.snapshot.reasoning.summary_reasoning.lower():
                    matched_fields.append("reasoning.summary_reasoning")
                if item.snapshot.reasoning.weaknesses_or_risks and q in item.snapshot.reasoning.weaknesses_or_risks.lower():
                    matched_fields.append("reasoning.weaknesses_or_risks")
                if item.snapshot.reasoning.recruiter_recommendation and q in item.snapshot.reasoning.recruiter_recommendation.lower():
                    matched_fields.append("reasoning.recruiter_recommendation")
                # Scan raw text input if it exists
                if item.snapshot.inputs.raw_text and q in item.snapshot.inputs.raw_text.lower():
                    matched_fields.append("inputs.raw_text")
                    
                if not matched_fields:
                    continue
                relevance = min(1.0, 0.5 + (len(matched_fields) * 0.1))
                
            retrieval_info = RetrievalMetadata(
                retrieved_at=datetime.now(timezone.utc),
                retrieval_method="text_scan" if query.query_text else "filter_match",
                relevance_score=relevance,
                matched_fields=matched_fields
            )
            
            results.append(MemorySearchResult(memory=item, retrieval_info=retrieval_info))
            
        results.sort(key=lambda r: (r.retrieval_info.relevance_score, r.memory.metadata.importance), reverse=True)
        return results[:query.limit]
