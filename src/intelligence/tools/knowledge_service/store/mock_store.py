from typing import List, Dict, Any, Optional
from .base import VectorRecord, VectorStoreProtocol
from ..schema import ChunkMetadata

class MockVectorStore:
    def __init__(self):
        # Memory dict storing collections of VectorRecord objects
        self._store: Dict[str, List[VectorRecord]] = {}
        
        # Prepopulate with dummy candidates data in "default" collection
        self._prepopulate_default_data()

    def _prepopulate_default_data(self):
        self._store["default"] = [
            VectorRecord(
                text="Mei is a senior backend developer specialized in Docker, Python, and Go pipelines.",
                vector=[1.0, 0.0, 0.0, 0.0],
                metadata=ChunkMetadata(
                    document_id="doc_mei_1",
                    chunk_id="doc_mei_1_chunk_0",
                    source="mei_resume.pdf",
                    chunk_index=0,
                    custom_tags={"role": "Backend", "experience": "senior"}
                )
            ),
            VectorRecord(
                text="John is a frontend architect working with React.js, JavaScript, and Tailwind CSS.",
                vector=[0.0, 1.0, 0.0, 0.0],
                metadata=ChunkMetadata(
                    document_id="doc_john_frontend",
                    chunk_id="doc_john_frontend_chunk_0",
                    source="john_cv.pdf",
                    chunk_index=0,
                    custom_tags={"role": "Frontend", "experience": "expert"}
                )
            ),
            VectorRecord(
                text="Alice is a cloud engineering specialist focusing on AWS, Kubernetes, and Terraform templates.",
                vector=[0.0, 0.0, 1.0, 0.0],
                metadata=ChunkMetadata(
                    document_id="doc_alice_cloud",
                    chunk_id="doc_alice_cloud_chunk_0",
                    source="alice_linkedin.txt",
                    chunk_index=0,
                    custom_tags={"role": "Cloud", "experience": "senior"}
                )
            )
        ]
        self._store["job_descriptions"] = [
            VectorRecord(
                text="Require a senior software engineer specialized in distributed systems and Go.",
                vector=[1.0, 0.0, 0.0, 0.0],
                metadata=ChunkMetadata(
                    document_id="doc_jd_go_dev",
                    chunk_id="doc_jd_go_dev_chunk_0",
                    source="jd_go.pdf",
                    chunk_index=0,
                    custom_tags={}
                )
            )
        ]

    def query(
        self,
        query_vector: List[float],
        collection: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorRecord]:
        records = self._store.get(collection, [])
        filtered_records = []
        
        for rec in records:
            if filters:
                match = True
                for k, v in filters.items():
                    val = getattr(rec.metadata, k, None)
                    if val is None:
                        val = rec.metadata.custom_tags.get(k)
                    if val != v:
                        match = False
                        break
                if not match:
                    continue
            filtered_records.append(rec)
            
        return filtered_records

    def upsert(self, collection: str, records: List[VectorRecord]) -> bool:
        if collection not in self._store:
            self._store[collection] = []
        current = self._store[collection]
        
        for record in records:
            existing_idx = next(
                (i for i, r in enumerate(current) if r.metadata.chunk_id == record.metadata.chunk_id),
                None
            )
            if existing_idx is not None:
                current[existing_idx] = record
            else:
                current.append(record)
        return True

    def delete(self, collection: str, filters: Dict[str, Any]) -> bool:
        if collection not in self._store:
            return False
        current = self._store[collection]
        
        # Keep records that DO NOT match filters
        new_records = []
        for rec in current:
            match = True
            for k, v in filters.items():
                val = getattr(rec.metadata, k, None)
                if val is None:
                    val = rec.metadata.custom_tags.get(k)
                if val != v:
                    match = False
                    break
            if not match:
                new_records.append(rec)
                
        self._store[collection] = new_records
        return True

    def list_collections(self) -> List[str]:
        return list(self._store.keys())
