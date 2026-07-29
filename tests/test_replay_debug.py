import pytest
from src.intelligence.tools.replay_debug.schema import ReplayRecord, ReplayExecutionResult, ReplayDiff, ReplayResponse

def test_replay_record_validation():
    rec = ReplayRecord(
        run_id="run_1",
        target_id="intent_classifier",
        timestamp="2026-07-29T12:00:00Z",
        version="v1",
        input_payload={"text": "hello"},
        output_payload={"intent": "greeting"},
        parent_replay_id="parent_123"
    )
    assert rec.run_id == "run_1"
    assert rec.parent_replay_id == "parent_123"
    assert rec.replay_id.startswith("rep_")

def test_replay_execution_result():
    res = ReplayExecutionResult(
        replay_id="rep_1",
        replayed_at="2026-07-29T12:05:00Z",
        output_payload={"intent": "greeting"}
    )
    assert res.replay_id == "rep_1"
    assert res.config_overridden is False

def test_replay_diff():
    diff = ReplayDiff(
        replay_id="rep_1",
        outputs_match=True,
        output_diff={},
        cost_delta=0.0,
        duration_delta_ms=5.0,
        confidence_delta=0.0
    )
    assert diff.outputs_match is True

def test_replay_storage_and_registry():
    import tempfile
    import os
    from src.intelligence.tools.replay_debug.storage.file import LocalFilesystemStorage
    from src.intelligence.tools.replay_debug.registry import ReplayRegistry
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalFilesystemStorage(base_dir=tmpdir)
        registry = ReplayRegistry(storage=storage)
        
        rec = ReplayRecord(
            run_id="run_abc",
            target_id="tool_abc",
            timestamp="2026-07-29T12:00:00Z",
            version="v1",
            input_payload={"val": 123},
            output_payload={"res": 456}
        )
        
        path = registry.register_replay(rec)
        assert os.path.exists(path)
        
        loaded = registry.get_replay(rec.replay_id)
        assert loaded.run_id == "run_abc"
        assert loaded.input_payload == {"val": 123}
        
        replays = registry.find_replays(target_id="tool_abc", run_id="run_abc")
        assert len(replays) == 1
        assert replays[0].replay_id == rec.replay_id

def test_automatic_replay_capture_decorator():
    import tempfile
    from src.intelligence.tools.replay_debug.storage.file import LocalFilesystemStorage
    from src.intelligence.tools.replay_debug.registry import ReplayRegistry
    from src.intelligence.tools.replay_debug.capture import replay_capture
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalFilesystemStorage(base_dir=tmpdir)
        registry = ReplayRegistry(storage=storage)
        
        @replay_capture(target_id="math_add", registry=registry)
        def add(a, b, context=None):
            return a + b
            
        res = add(a=10, b=20, context={"run_id": "run_add_123"})
        assert res == 30
        
        replays = registry.find_replays(target_id="math_add", run_id="run_add_123")
        assert len(replays) == 1
        assert replays[0].output_payload == 30
        assert replays[0].input_payload == {"kwargs": {"a": 10, "b": 20}}

def test_runner_and_analyzer_replays():
    from src.intelligence.tools.replay_debug.runner import ReplayRunner
    from src.intelligence.tools.replay_debug.analyzer import DifferenceAnalyzer
    from src.intelligence.tools.evaluation_framework.target import ToolTarget
    
    # Setup mock executor
    def double_executor(payload):
        return {"value": payload["val"] * 2, "confidence": 0.9}
        
    target = ToolTarget("math_double", executor=double_executor)
    runner = ReplayRunner()
    runner.register_target("math_double", target)
    
    record = ReplayRecord(
        run_id="run_double_777",
        target_id="math_double",
        timestamp="2026-07-29T12:00:00Z",
        version="v1",
        input_payload={"val": 5},
        output_payload={"value": 10, "confidence": 0.85},
        cost={"estimated_cost": 0.005},
        resource={"duration_ms": 100.0}
    )
    
    repl_res = runner.replay(record)
    assert repl_res.output_payload == {"value": 10, "confidence": 0.9}
    
    diff = DifferenceAnalyzer.analyze(record, repl_res)
    assert diff.outputs_match is False
    assert diff.confidence_delta == 0.05
    assert diff.cost_delta < 0.0

def test_debug_reporter():
    import tempfile
    import os
    from src.intelligence.tools.replay_debug.runner import ReplayRunner
    from src.intelligence.tools.replay_debug.analyzer import DifferenceAnalyzer
    from src.intelligence.tools.replay_debug.reporter import DebugReporter
    
    record = ReplayRecord(
        run_id="run_rep_1",
        target_id="math_square",
        timestamp="2026-07-29T12:00:00Z",
        version="v1",
        input_payload={"val": 4},
        output_payload=16
    )
    
    repl_res = ReplayExecutionResult(
        replay_id=record.replay_id,
        replayed_at="2026-07-29T12:05:00Z",
        output_payload=16
    )
    
    diff = DifferenceAnalyzer.analyze(record, repl_res)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        reporter = DebugReporter(base_dir=tmpdir)
        json_path = reporter.generate_report(record, repl_res, diff, format="json")
        md_path = reporter.generate_report(record, repl_res, diff, format="markdown")
        
        assert os.path.exists(json_path)
        assert os.path.exists(md_path)

def test_mcp_create_and_replay():
    from src.intelligence.platform.test_utils import run_mcp_session
    import os
    import json
    
    create_req = {
        "jsonrpc": "2.0",
        "id": 100,
        "method": "tools/call",
        "params": {
            "name": "create_replay",
            "arguments": {
                "target_id": "math_cube",
                "input_payload": {"val": 3},
                "output_payload": 27,
                "parent_replay_id": "ancestor_abc"
            }
        }
    }
    
    responses, _ = run_mcp_session([create_req])
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "success"
    
    replay_id = content["replay_record"]["replay_id"]
    assert replay_id.startswith("rep_")
    assert content["replay_record"]["parent_replay_id"] == "ancestor_abc"
    
    replay_req = {
        "jsonrpc": "2.0",
        "id": 101,
        "method": "tools/call",
        "params": {
            "name": "replay_execution",
            "arguments": {
                "replay_id": replay_id
            }
        }
    }
    
    responses, _ = run_mcp_session([replay_req])
    assert len(responses) == 1
    resp2 = json.loads(responses[0])
    assert "result" in resp2
    content2 = json.loads(resp2["result"]["content"][0]["text"])
    assert content2["status"] == "success"
    assert content2["execution_result"]["output_payload"] == {"result": "mocked", "tool": "math_cube", "input": {"val": 3}}
    
    from src.intelligence.tools.replay_debug.service import get_replay_service
    service = get_replay_service()
    path = os.path.join(service.registry.storage.base_dir, f"{replay_id}.json")
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass
