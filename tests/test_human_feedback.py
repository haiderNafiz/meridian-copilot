import pytest
from src.intelligence.tools.human_feedback.schema import (
    TargetType, FeedbackType, FeedbackTarget, FeedbackRecord, FeedbackEvent, AuditRecord
)

def test_feedback_record_validation():
    target = FeedbackTarget(target_id="math_add", target_type=TargetType.TOOL, version="v1")
    rec = FeedbackRecord(
        run_id="run_1",
        target=target,
        reviewer_id="rev_1",
        timestamp="2026-07-29T12:00:00Z",
        feedback_type=FeedbackType.RATING,
        feedback_payload={"score": 5}
    )
    assert rec.run_id == "run_1"
    assert rec.target.target_id == "math_add"
    assert rec.feedback_id.startswith("fb_")

def test_audit_record_validation():
    aud = AuditRecord(
        entity_id="fb_123",
        actor_id="admin_1",
        action="approve",
        timestamp="2026-07-29T12:01:00Z",
        changes={"status": "approved"}
    )
    assert aud.entity_id == "fb_123"
    assert aud.changes == {"status": "approved"}

def test_feedback_strategies_and_consensus():
    from src.intelligence.tools.human_feedback.strategy import StrategyRegistry
    from src.intelligence.tools.human_feedback.consensus import ConsensusRegistry
    from src.intelligence.tools.human_feedback.schema import FeedbackTarget, TargetType
    
    registry = StrategyRegistry()
    rating_strategy = registry.get_strategy(FeedbackType.RATING)
    assert rating_strategy.validate({"score": 4.5}) is True
    assert rating_strategy.validate({"invalid": "data"}) is False
    assert rating_strategy.normalize({"score": 6.0}) == {"score": 5.0}
    
    consensus_reg = ConsensusRegistry()
    target = FeedbackTarget(target_id="math_add", target_type=TargetType.TOOL)
    
    fb1 = FeedbackRecord(
        run_id="run_1", target=target, feedback_type=FeedbackType.RATING, feedback_payload={"score": 4.0}, timestamp="2026"
    )
    fb2 = FeedbackRecord(
        run_id="run_1", target=target, feedback_type=FeedbackType.RATING, feedback_payload={"score": 4.5}, timestamp="2026"
    )
    fb3 = FeedbackRecord(
        run_id="run_1", target=target, feedback_type=FeedbackType.RATING, feedback_payload={"score": 5.0}, timestamp="2026"
    )
    
    res = consensus_reg.resolve(FeedbackType.RATING, [fb1, fb2, fb3])
    assert res["consensus"] is True
    assert res["average_score"] == 4.5
    assert res["agreement_rate"] == 1.0
    
    out1 = FeedbackRecord(
        run_id="run_1", target=target, feedback_type=FeedbackType.OUTCOME, feedback_payload={"verified": True}, timestamp="2026"
    )
    out2 = FeedbackRecord(
        run_id="run_1", target=target, feedback_type=FeedbackType.OUTCOME, feedback_payload={"verified": False}, timestamp="2026"
    )
    
    res_out = consensus_reg.resolve(FeedbackType.OUTCOME, [out1, out2])
    assert res_out["consensus"] is False
    assert res_out["verified_ratio"] == 0.5

def test_feedback_storage_and_service():
    import tempfile
    import os
    from src.intelligence.tools.human_feedback.provider.file import LocalFilesystemFeedbackProvider
    from src.intelligence.tools.human_feedback.service import FeedbackService
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemFeedbackProvider(base_dir=tmpdir)
        service = FeedbackService(provider=provider)
        
        rec = service.submit_feedback(
            target_id="math_add",
            target_type=TargetType.TOOL,
            run_id="run_xyz",
            feedback_type=FeedbackType.RATING,
            feedback_payload={"score": 4.0},
            reviewer_id="reviewer_bob"
        )
        
        loaded = service.get_feedback(rec.feedback_id)
        assert loaded is not None
        assert loaded.feedback_payload == {"score": 4.0}
        
        audits = service.get_audits(rec.feedback_id)
        assert len(audits) == 1
        assert audits[0].action == "create_feedback"
        assert audits[0].actor_id == "reviewer_bob"
        
        list_rec = service.list_feedback(target_id="math_add", run_id="run_xyz")
        assert len(list_rec) == 1
        assert list_rec[0].feedback_id == rec.feedback_id

def test_feedback_pipeline_dispatches():
    from src.intelligence.tools.human_feedback.pipeline import FeedbackPipeline, FeedbackPipelineHook
    from src.intelligence.tools.human_feedback.schema import FeedbackRecord, FeedbackTarget, TargetType, FeedbackType
    
    class MockPipelineHook(FeedbackPipelineHook):
        def __init__(self):
            self.triggered = False
            self.snapshot = None
        def on_event(self, event, context):
            self.triggered = True
            self.snapshot = event.payload_snapshot
            
    hook = MockPipelineHook()
    pipeline = FeedbackPipeline(hooks=[hook])
    
    target = FeedbackTarget(target_id="tool_x", target_type=TargetType.TOOL)
    record = FeedbackRecord(
        run_id="run_123",
        target=target,
        timestamp="2026",
        feedback_type=FeedbackType.RATING,
        feedback_payload={"score": 5}
    )
    
    event = pipeline.dispatch(record, payload_snapshot={"text": "hello"})
    assert event.feedback_id == record.feedback_id
    assert hook.triggered is True
    assert hook.snapshot == {"text": "hello"}

def test_analytics_registry():
    from src.intelligence.tools.human_feedback.analytics import AnalyticsRegistry, FeedbackMetric
    from src.intelligence.tools.human_feedback.schema import FeedbackRecord, FeedbackTarget, TargetType, FeedbackType
    from typing import List
    
    registry = AnalyticsRegistry()
    target = FeedbackTarget(target_id="tool_y", target_type=TargetType.TOOL)
    
    class ReviewerCountMetric(FeedbackMetric):
        def calculate(self, records: List[FeedbackRecord]) -> int:
            return len(set(r.reviewer_id for r in records if r.reviewer_id))
            
    registry.register_metric("reviewers_count", ReviewerCountMetric())
    
    fb1 = FeedbackRecord(
        run_id="run_1", target=target, reviewer_id="user_a", feedback_type=FeedbackType.RATING, feedback_payload={"score": 4}, timestamp="2026"
    )
    fb2 = FeedbackRecord(
        run_id="run_2", target=target, reviewer_id="user_b", feedback_type=FeedbackType.CORRECTION, feedback_payload={"corrected_output": {}}, timestamp="2026"
    )
    
    results = registry.compute_all([fb1, fb2])
    assert results["reviewers_count"] == 2
    assert results["correction_frequency"] == 0.5

def test_promotion_workflow():
    import tempfile
    import os
    from src.intelligence.tools.human_feedback.provider.file import LocalFilesystemFeedbackProvider
    from src.intelligence.tools.human_feedback.promotion import DatasetPromotionWorkflow
    from src.intelligence.tools.evaluation_framework.dataset.registry import DatasetRegistry
    from src.intelligence.tools.human_feedback.schema import FeedbackRecord, FeedbackTarget, TargetType, FeedbackType, PromotionStatus
    
    with tempfile.TemporaryDirectory() as tmpdir:
        datasets_base = os.path.join(tmpdir, "datasets")
        os.makedirs(datasets_base, exist_ok=True)
        
        provider = LocalFilesystemFeedbackProvider(base_dir=tmpdir)
        dataset_reg = DatasetRegistry(base_dir=datasets_base)
        
        workflow = DatasetPromotionWorkflow(feedback_provider=provider, dataset_registry=dataset_reg)
        
        req = workflow.request_promotion(
            replay_id="rep_999",
            target_domain="intent",
            target_dataset_type="golden",
            target_version="v1",
            actor="admin_alice"
        )
        assert req.status == PromotionStatus.PENDING
        
        fb = FeedbackRecord(
            run_id="run_xyz",
            target=FeedbackTarget(target_id="math_add", target_type=TargetType.TOOL),
            feedback_type=FeedbackType.RATING,
            feedback_payload={"score": 5.0},
            timestamp="2026"
        )
        
        updated = workflow.evaluate_and_promote(req.promotion_id, [fb], actor="admin_alice")
        assert updated.status == PromotionStatus.APPROVED
        
        versioned_file = os.path.join(datasets_base, "intent", "golden", "v1_rev1.json")
        assert os.path.exists(versioned_file)
        
        audits = provider.list_audits(req.promotion_id)
        assert len(audits) == 2

@pytest.mark.anyio
async def test_mcp_feedback_tools():
    import json
    import tempfile
    import os
    from src.intelligence.mcp.server import submit_feedback, list_feedback, get_feedback, feedback_summary, promote_dataset_item
    from src.intelligence.tools.human_feedback.service import get_feedback_service
    from src.intelligence.tools.human_feedback.provider.file import LocalFilesystemFeedbackProvider
    
    with tempfile.TemporaryDirectory() as tmpdir:
        datasets_base = os.path.join(tmpdir, "datasets")
        os.makedirs(datasets_base, exist_ok=True)
        
        provider = LocalFilesystemFeedbackProvider(base_dir=tmpdir)
        service = get_feedback_service()
        service.provider = provider
        service.provider.base_dir = tmpdir
        service.provider.feedback_dir = os.path.join(tmpdir, "records")
        service.provider.audit_dir = os.path.join(tmpdir, "audits")
        service.provider.promotion_dir = os.path.join(tmpdir, "promotions")
        os.makedirs(service.provider.feedback_dir, exist_ok=True)
        os.makedirs(service.provider.audit_dir, exist_ok=True)
        os.makedirs(service.provider.promotion_dir, exist_ok=True)
        
        res = await submit_feedback(
            target_id="tool_z",
            target_type="tool",
            run_id="run_1",
            feedback_type="rating",
            feedback_payload={"score": 4.5},
            reviewer_id="reviewer_1"
        )
        data = json.loads(res)
        assert data["status"] == "success"
        fb_id = data["feedback_record"]["feedback_id"]
        
        res_get = await get_feedback(feedback_id=fb_id)
        data_get = json.loads(res_get)
        assert data_get["feedback_record"]["feedback_payload"] == {"score": 4.5}
        
        res_list = await list_feedback(target_id="tool_z")
        data_list = json.loads(res_list)
        assert len(data_list["feedback_records"]) == 1
        
        res_sum = await feedback_summary(target_id="tool_z")
        data_sum = json.loads(res_sum)
        assert data_sum["analytics_summary"]["agreement_rate"] == 1.0
        
        from src.intelligence.tools.evaluation_framework.dataset.registry import DatasetRegistry
        
        res_prom = await promote_dataset_item(
            replay_id="rep_mcp",
            target_domain="intent",
            target_dataset_type="curated",
            target_version="v1",
            actor="admin_1"
        )
        # Verify result structure
        data_prom = json.loads(res_prom)
        assert data_prom["status"] == "success"
        assert data_prom["promotion_request"]["status"] == "approved"
