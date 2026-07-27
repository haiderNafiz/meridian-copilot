from typing import List, Any
from src.intelligence.tools.memory_service.schema import MemoryQuery, MemoryRetrieveRequest
from src.intelligence.tools.memory_service.service import get_memory_service

class MemoryRetriever:
    def retrieve_history(
        self,
        session_id: str,
        query_text: str = None
    ) -> List[Any]:
        """Pulls previous context snapshots from persistent MemoryService."""
        service = get_memory_service()
        
        # 1. Direct session retrieval
        req = MemoryRetrieveRequest(session_id=session_id)
        res = service.retrieve_memory(req)
        
        memories = getattr(res, "memories", [])
        
        # 2. Keyword/semantic retrieval if query_text is present
        if query_text:
            query = MemoryQuery(
                query_text=query_text,
                session_id=session_id,
                limit=5
            )
            search_res = service.search_memory(query)
            # Add unique search memories if they are not already in direct memories list
            existing_ids = {getattr(m, "memory_id", None) for m in memories}
            for m in getattr(search_res, "memories", []):
                m_id = getattr(m, "memory_id", None)
                if m_id not in existing_ids:
                    memories.append(m)
                    
        return memories
