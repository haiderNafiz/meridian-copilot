import pytest
import os
import json
from datetime import datetime, timezone
from src.intelligence.tools.memory_service.schema import (
    MemoryMetadata,
    MemorySnapshot,
    RetrievalMetadata,
    MemorySearchResult
)
from src.intelligence.tools.context_builder.schema import (
    ContextSnapshot,
    ContextMetadata,
    ContextInputs,
    ContextFacts,
    ContextEvidence,
    ContextReasoning,
    ContextOutputs
)

def test_memory_snapshot_schema_validation():
    meta = ContextMetadata(
        context_id="ctx_111",
        session_id="sess_222",
        timestamp_utc=datetime.now(timezone.utc),
        provenance=["CandidateProfilerService"],
        overall_confidence=0.9
    )
    
    ctx = ContextSnapshot(
        metadata=meta,
        inputs=ContextInputs(),
        facts=ContextFacts(),
        evidence=ContextEvidence(),
        reasoning=ContextReasoning(),
        outputs=ContextOutputs()
    )
    
    mem_meta = MemoryMetadata(
        memory_id="mem_uuid_000",
        context_id="ctx_111",
        session_id="sess_222",
        created_at=datetime.now(timezone.utc),
        last_accessed_at=datetime.now(timezone.utc),
        tags=["go", "backend"],
        importance=0.8
    )
    
    mem_snap = MemorySnapshot(metadata=mem_meta, snapshot=ctx)
    
    assert mem_snap.metadata.memory_id == "mem_uuid_000"
    assert mem_snap.snapshot.metadata.context_id == "ctx_111"
    assert mem_snap.metadata.tags == ["go", "backend"]
    assert mem_snap.metadata.is_pinned is False

def test_merge_snapshot_policy_success():
    from src.intelligence.tools.memory_service.policy.merge import MergeSnapshotPolicy
    
    meta1 = ContextMetadata(context_id="ctx_merge_1", timestamp_utc=datetime.now(timezone.utc), provenance=["P1"])
    ctx1 = ContextSnapshot(
        metadata=meta1,
        inputs=ContextInputs(),
        facts=ContextFacts(role_type="Backend", technical_domains=["Go"]),
        evidence=ContextEvidence(profile_evidence=["Ref 1"]),
        reasoning=ContextReasoning(scoring_reasoning={"skill": "Good"}),
        outputs=ContextOutputs()
    )
    
    meta2 = ContextMetadata(context_id="ctx_merge_1", timestamp_utc=datetime.now(timezone.utc), provenance=["P1", "P2"])
    ctx2 = ContextSnapshot(
        metadata=meta2,
        inputs=ContextInputs(),
        facts=ContextFacts(role_type=None, technical_domains=["Cloud"], normalized_technologies=["aws"]),
        evidence=ContextEvidence(profile_evidence=["Ref 2"]),
        reasoning=ContextReasoning(scoring_reasoning={"qual": "Okay"}, summary_reasoning="Summary 2"),
        outputs=ContextOutputs()
    )
    
    policy = MergeSnapshotPolicy()
    merged = policy.apply(ctx1, ctx2)
    
    assert merged.facts.role_type == "Backend"
    assert set(merged.facts.technical_domains) == {"Go", "Cloud"}
    assert set(merged.facts.normalized_technologies) == {"aws"}
    assert set(merged.evidence.profile_evidence) == {"Ref 1", "Ref 2"}
    assert merged.reasoning.scoring_reasoning == {"skill": "Good", "qual": "Okay"}
    assert merged.reasoning.summary_reasoning == "Summary 2"

def test_local_file_memory_store_operations(tmp_path):
    from src.intelligence.tools.memory_service.store.local_file import LocalFileMemoryStore
    from src.intelligence.tools.memory_service.schema import MemoryQuery
    
    db_file = tmp_path / "memory_test_db.json"
    store = LocalFileMemoryStore(db_path=str(db_file))
    
    meta = ContextMetadata(context_id="ctx_store_1", timestamp_utc=datetime.now(timezone.utc), provenance=["P1"])
    ctx = ContextSnapshot(
        metadata=meta,
        inputs=ContextInputs(raw_text="Larry is a python developer"),
        facts=ContextFacts(role_type="Backend", technical_domains=["Python"]),
        evidence=ContextEvidence(),
        reasoning=ContextReasoning(summary_reasoning="Great developer"),
        outputs=ContextOutputs()
    )
    
    mem_meta = MemoryMetadata(
        memory_id="mem_uuid_111",
        context_id="ctx_store_1",
        session_id="sess_100",
        created_at=datetime.now(timezone.utc),
        last_accessed_at=datetime.now(timezone.utc),
        tags=["python", "junior"],
        importance=0.7
    )
    
    record = MemorySnapshot(metadata=mem_meta, snapshot=ctx)
    store.save(record)
    
    res = store.get_by_memory_id("mem_uuid_111")
    assert res is not None
    assert res.metadata.session_id == "sess_100"
    
    versions = store.get_by_context_id("ctx_store_1")
    assert len(versions) == 1
    assert versions[0].metadata.memory_id == "mem_uuid_111"
    
    sess_list = store.get_by_session_id("sess_100")
    assert len(sess_list) == 1
    
    query = MemoryQuery(query_text="python")
    matches = store.search(query)
    assert len(matches) == 1
    assert matches[0].memory.metadata.memory_id == "mem_uuid_111"
    assert "facts.technical_domains" in matches[0].retrieval_info.matched_fields
    
    query_no = MemoryQuery(query_text="java")
    matches_no = store.search(query_no)
    assert len(matches_no) == 0

def test_memory_service_singleton():
    from src.intelligence.tools.memory_service.service import get_memory_service
    s1 = get_memory_service()
    s2 = get_memory_service()
    assert s1 is s2

def test_memory_service_append_only_lineage_and_search(tmp_path):
    from src.intelligence.tools.memory_service.service import MemoryService
    from src.intelligence.tools.memory_service.provider import MemoryProvider
    from src.intelligence.tools.memory_service.policy.merge import MergeSnapshotPolicy
    from src.intelligence.tools.memory_service.policy.retention import DefaultNoOpRetentionPolicy
    from src.intelligence.tools.memory_service.store.local_file import LocalFileMemoryStore
    from src.intelligence.tools.memory_service.schema import MemoryStoreRequest, MemoryRetrieveRequest, MemoryQuery
    
    db_file = tmp_path / "memory_srv_db.json"
    store = LocalFileMemoryStore(db_path=str(db_file))
    policy = MergeSnapshotPolicy()
    retention = DefaultNoOpRetentionPolicy()
    provider = MemoryProvider(policy=policy, retention_policy=retention)
    service = MemoryService(provider=provider, store=store, index=store)
    
    # 1. Store initial snapshot (V1)
    meta1 = ContextMetadata(context_id="ctx_srv_1", timestamp_utc=datetime.now(timezone.utc), provenance=["P1"])
    ctx1 = ContextSnapshot(
        metadata=meta1,
        inputs=ContextInputs(raw_text="Initial developer resume"),
        facts=ContextFacts(role_type="Backend", technical_domains=["Go"]),
        evidence=ContextEvidence(),
        reasoning=ContextReasoning(),
        outputs=ContextOutputs()
    )
    
    req1 = MemoryStoreRequest(snapshot=ctx1, session_id="sess_srv_1", tags=["golang"], importance=0.8)
    res1 = service.save_memory(req1)
    
    assert res1.status.value == "success"
    mem_id_v1 = res1.memory_id
    
    # 2. Store updated snapshot (V2) - append-only test
    meta2 = ContextMetadata(context_id="ctx_srv_1", timestamp_utc=datetime.now(timezone.utc), provenance=["P2"])
    ctx2 = ContextSnapshot(
        metadata=meta2,
        inputs=ContextInputs(),
        facts=ContextFacts(technical_domains=["Cloud"]),
        evidence=ContextEvidence(profile_evidence=["Cloud Ref"]),
        reasoning=ContextReasoning(summary_reasoning="Cloud architect"),
        outputs=ContextOutputs()
    )
    
    req2 = MemoryStoreRequest(snapshot=ctx2, session_id="sess_srv_1", tags=["aws"], importance=0.9)
    res2 = service.save_memory(req2)
    
    assert res2.status.value == "success"
    mem_id_v2 = res2.memory_id
    assert mem_id_v1 != mem_id_v2
    
    # Check lineage (get all versions by context_id)
    versions = store.get_by_context_id("ctx_srv_1")
    assert len(versions) == 2
    assert versions[0].metadata.memory_id == mem_id_v1
    assert versions[0].metadata.parent_memory_id is None
    
    assert versions[1].metadata.memory_id == mem_id_v2
    assert versions[1].metadata.parent_memory_id == mem_id_v1
    
    # Validate the merged fields on V2
    assert versions[1].snapshot.facts.role_type == "Backend"
    assert set(versions[1].snapshot.facts.technical_domains) == {"Go", "Cloud"}
    assert set(versions[1].metadata.tags) == {"golang", "aws"}
    
    # 3. Retrieve
    ret_req = MemoryRetrieveRequest(context_id="ctx_srv_1")
    ret_res = service.retrieve_memory(ret_req)
    assert ret_res.status.value == "success"
    assert len(ret_res.memories) == 2
    assert ret_res.retrieval_info.retrieval_method == "context_log_lookup"
    
    # 4. Search
    query = MemoryQuery(query_text="architect")
    search_res = service.search_memory(query)
    assert search_res.status.value == "success"
    assert len(search_res.results) == 1
    assert search_res.results[0].memory.metadata.memory_id == mem_id_v2
    assert "reasoning.summary_reasoning" in search_res.results[0].retrieval_info.matched_fields

def test_mcp_save_and_search_memory_success():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    # Clean database file if it exists so we test fresh E2E
    from src.intelligence.tools.memory_service.store.local_file import LocalFileMemoryStore
    store = LocalFileMemoryStore()
    if os.path.exists(store.db_path):
        try:
            os.remove(store.db_path)
        except OSError:
            pass

    snapshot_dict = {
        "metadata": {
            "context_id": "ctx_mcp_save_1",
            "timestamp_utc": "2026-07-25T12:00:00Z",
            "provenance": ["P1"],
            "overall_confidence": 0.88
        },
        "inputs": {
            "document_references": ["doc_ref_99"],
            "raw_text": "Larry Go Developer"
        },
        "facts": {
            "role_type": "Backend",
            "technical_domains": ["Go"]
        },
        "evidence": {},
        "reasoning": {},
        "outputs": {}
    }
    
    save_req = {
        "jsonrpc": "2.0",
        "id": 901,
        "method": "tools/call",
        "params": {
            "name": "save_memory",
            "arguments": {
                "snapshot": snapshot_dict,
                "session_id": "session_mcp_99",
                "tags": ["go_lang"],
                "importance": 0.75
            }
        }
    }
    
    responses, stderr_lines = run_mcp_session([save_req])
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert "content" in resp["result"]
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "success"
    mem_id = content["memory_id"]
    
    # Query Search
    search_req = {
        "jsonrpc": "2.0",
        "id": 902,
        "method": "tools/call",
        "params": {
            "name": "search_memory",
            "arguments": {
                "query_text": "Larry",
                "session_id": "session_mcp_99"
            }
        }
    }
    
    responses_s, stderr_lines_s = run_mcp_session([search_req])
    assert len(responses_s) == 1
    resp_s = json.loads(responses_s[0])
    content_s = json.loads(resp_s["result"]["content"][0]["text"])
    assert content_s["status"] == "success"
    assert len(content_s["results"]) == 1
    assert content_s["results"][0]["memory"]["metadata"]["memory_id"] == mem_id



