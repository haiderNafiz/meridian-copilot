import os
import tempfile
import json
import pytest
from src.intelligence.tools.evaluation_framework.schema import DatasetType
from src.intelligence.tools.evaluation_framework.dataset.registry import DatasetRegistry

def test_dataset_registry_discovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Setup mock folder structure: datasets/intent/golden/
        intent_dir = os.path.join(tmpdir, "intent", "golden")
        os.makedirs(intent_dir)
        
        sample_dataset = {
            "dataset_id": "intent_golden",
            "version": "v1",
            "dataset_type": "golden",
            "items": [
                {
                    "id": "item1",
                    "input_payload": {"raw_text": "hello"},
                    "expected_output": "greeting",
                    "tags": ["test"],
                    "metadata": {}
                }
            ]
        }
        
        file_path = os.path.join(intent_dir, "v1.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sample_dataset, f)
            
        # 2. Assert registry discovery loads correctly
        registry = DatasetRegistry(base_dir=tmpdir)
        dataset = registry.get_dataset(domain="intent", dataset_type="golden", version="v1")
        
        assert dataset.dataset_id == "intent_golden"
        assert dataset.version == "v1"
        assert dataset.dataset_type == DatasetType.GOLDEN
        assert len(dataset.items) == 1
        assert dataset.items[0].id == "item1"
        assert dataset.items[0].expected_output == "greeting"
        
        list_res = registry.list_datasets()
        assert len(list_res) == 1
        assert list_res[0]["domain"] == "intent"
        assert list_res[0]["version"] == "v1"

def test_runner_target_execution():
    from src.intelligence.tools.evaluation_framework.target import ToolTarget
    from src.intelligence.tools.evaluation_framework.runner import EvaluationRunner
    from src.intelligence.tools.evaluation_framework.schema import EvaluationItem
    
    # 1. Custom mock logic executor
    def mock_executor(payload):
        return {"processed": payload["value"] * 2}
        
    target = ToolTarget("double_value_tool", executor=mock_executor)
    runner = EvaluationRunner(target=target)
    
    items = [
        EvaluationItem(
            id="item1",
            input_payload={"value": 10},
            expected_output=20
        ),
        EvaluationItem(
            id="item2",
            input_payload={"value": 5},
            expected_output=10
        )
    ]
    
    results = runner.run_batch(items)
    
    assert len(results) == 2
    assert results[0].item_id == "item1"
    assert results[0].actual_output == {"processed": 20}
    assert results[0].resource.cpu_percent == 1.5
    assert results[0].cost.estimated_cost == 0.001
    assert results[1].actual_output == {"processed": 10}

def test_metrics_registry_and_classification():
    from src.intelligence.tools.evaluation_framework.metric.definition import MetricDefinition
    from src.intelligence.tools.evaluation_framework.metric.registry import get_metric_registry
    from src.intelligence.tools.evaluation_framework.strategy.classification import ClassificationStrategy
    from src.intelligence.tools.evaluation_framework.metric.aggregator import MetricAggregator
    
    # 1. Register accuracy metric definition
    def_accuracy = MetricDefinition(
        name="accuracy",
        description="Measures exact equality match rate.",
        category="classification",
        target_threshold=0.8
    )
    
    registry = get_metric_registry()
    registry.register_metric(def_accuracy, lambda: ClassificationStrategy(metric_name="accuracy", threshold=0.8))
    
    # 2. Verify metric definition details
    retrieved_def = registry.get_definition("accuracy")
    assert retrieved_def.name == "accuracy"
    assert retrieved_def.target_threshold == 0.8
    
    # 3. Verify strategy creation & execution
    strategy = registry.create_strategy("accuracy")
    assert isinstance(strategy, ClassificationStrategy)
    
    res1 = strategy.evaluate(prediction="candidate", target="candidate")
    assert res1.score == 1.0
    assert res1.passed is True
    
    res2 = strategy.evaluate(prediction="lead", target="candidate")
    assert res2.score == 0.0
    assert res2.passed is False
    
    # 4. Verify metric aggregator
    avg = MetricAggregator.aggregate([res1.score, res2.score], method="macro")
    assert avg == 0.5

def test_regression_and_report_storage():
    from src.intelligence.tools.evaluation_framework.regression.analyzer import RegressionAnalyzer
    from src.intelligence.tools.evaluation_framework.report.store import ReportStore
    from src.intelligence.tools.evaluation_framework.schema import (
        EvaluationReport, EvaluationRunResult, ResourceMetrics, CostMetrics, ReproducibleConfig
    )
    
    # 1. Verify Regression Detection
    current = {"accuracy": 0.85, "latency": 500}
    baseline = {"accuracy": 0.90, "latency": 450}
    
    analysis = RegressionAnalyzer.analyze(current, baseline, thresholds={"accuracy": 0.02})
    assert analysis.regressed is True # accuracy dropped by 0.05 which is > threshold delta 0.02
    assert analysis.deltas[0].metric_name == "accuracy"
    assert analysis.deltas[0].delta == -0.05
    
    # 2. Verify Report Store Operations
    with tempfile.TemporaryDirectory() as tmpdir:
        store = ReportStore(base_dir=tmpdir)
        
        resource = ResourceMetrics(
            cpu_percent=1.0, peak_ram_mb=100.0, average_ram_mb=95.0, duration_ms=10.0, throughput_items_per_sec=100.0
        )
        cost = CostMetrics(provider="mock")
        repro = ReproducibleConfig()
        
        report = EvaluationReport(
            report_id="rep1",
            run_id="run1",
            experiment_id="exp1",
            dataset_id="ds1",
            target_tool="tool1",
            overall_score=0.95,
            run_results=[],
            passed=True,
            created_at="2026-07-29T12:00:00Z",
            reproducibility=repro,
            cost_summary=cost,
            resource_summary=resource
        )
        
        json_path = store.save_report(report, format="json")
        md_path = store.save_report(report, format="markdown")
        
        assert os.path.exists(json_path)
        assert os.path.exists(md_path)
        
        loaded = store.load_report("run1")
        assert loaded.report_id == "rep1"
        assert loaded.overall_score == 0.95

def test_expanded_evaluation_strategies():
    from src.intelligence.tools.evaluation_framework.strategy.ranking import RankingStrategy
    from src.intelligence.tools.evaluation_framework.strategy.generation import GenerationStrategy
    from src.intelligence.tools.evaluation_framework.strategy.cost import CostStrategy
    from src.intelligence.tools.evaluation_framework.strategy.resource import ResourceStrategy
    from src.intelligence.tools.evaluation_framework.strategy.robustness import RobustnessStrategy
    from src.intelligence.tools.evaluation_framework.strategy.fairness import FairnessStrategy
    from src.intelligence.tools.evaluation_framework.strategy.explainability import ExplainabilityStrategy
    from src.intelligence.tools.evaluation_framework.strategy.calibration import CalibrationStrategy
    from src.intelligence.tools.evaluation_framework.schema import CostMetrics, ResourceMetrics
    
    # 1. Ranking Check
    assert RankingStrategy().evaluate(["A", "B", "C"], ["B", "D"]).score == 0.5
    
    # 2. Generation Containment Check
    assert GenerationStrategy().evaluate("Hello world, I am Meridian", "Meridian").score == 1.0
    
    # 3. Cost Strategy Check
    cost = CostMetrics(estimated_cost=0.01, provider="groq")
    assert CostStrategy().evaluate(None, None, context={"cost": cost}).score == 0.01
    
    # 4. Resource Strategy Check
    res = ResourceMetrics(
        cpu_percent=1.0, peak_ram_mb=10.0, average_ram_mb=9.0, duration_ms=450.0, throughput_items_per_sec=2.0
    )
    assert ResourceStrategy().evaluate(None, None, context={"resource": res}).score == 450.0
    
    # 5. Robustness Stability check
    assert RobustnessStrategy().evaluate("Output JSON processed successfully.", None).score == 1.0
    assert RobustnessStrategy().evaluate("Traceback error: division by zero", None).score == 0.0
    
    # 6. Fairness demographic check
    assert FairnessStrategy().evaluate(None, None, context={"fairness_delta": 0.95}).score == 0.95
    
    # 7. Explainability coverage check
    exp_payload = {"explanation": "Candidate is selected based on Python skills.", "evidence": ["Python"]}
    assert ExplainabilityStrategy().evaluate(exp_payload, None).score == 1.0
    
    # 8. Calibration Strategy check
    cal_payload = {"value": "selected", "confidence": 0.85}
    assert CalibrationStrategy().evaluate(cal_payload, "selected").score == 0.85

def test_evaluation_service_orchestration():
    from src.intelligence.tools.evaluation_framework.service import EvaluationService
    from src.intelligence.tools.evaluation_framework.runner import EvaluationRunner
    from src.intelligence.tools.evaluation_framework.target import ToolTarget
    from src.intelligence.tools.evaluation_framework.report.store import ReportStore
    from src.intelligence.tools.evaluation_framework.hook.base import EvaluationHook
    from src.intelligence.tools.evaluation_framework.schema import (
        EvaluationDataset, EvaluationItem, EvaluationConfig, DatasetType, MetricType
    )
    
    # 1. Custom mock targets & runner
    def mock_double(payload):
        return payload["val"] * 2
    target = ToolTarget("double", executor=mock_double)
    runner = EvaluationRunner(target=target)
    
    # 2. Mock hooks
    class MockHook(EvaluationHook):
        def __init__(self):
            self.started = False
            self.finished = False
        def on_start(self, context):
            self.started = True
        def on_finish(self, results, context):
            self.finished = True
            
    hook = MockHook()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        store = ReportStore(base_dir=tmpdir)
        service = EvaluationService(runner=runner, report_store=store, hooks=[hook])
        
        dataset = EvaluationDataset(
            dataset_id="double_ds",
            version="v1",
            dataset_type=DatasetType.CURATED,
            items=[EvaluationItem(id="i1", input_payload={"val": 5}, expected_output=10)]
        )
        
        config = EvaluationConfig(
            target_id="double_tool",
            metrics=[MetricType.CLASSIFICATION],
            thresholds={"classification": 0.8}
        )
        
        report = service.run_evaluation(dataset, config)
        
        assert report.passed is True
        assert report.overall_score == 1.0
        assert hook.started is True
        assert hook.finished is True
        
        loaded = store.load_report(report.run_id)
        assert loaded.report_id == report.report_id

def test_mcp_run_evaluation():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    # Save a valid mock dataset to the workspace's default datasets folder
    import os
    os.makedirs("datasets/intent/golden", exist_ok=True)
    sample_dataset = {
        "dataset_id": "intent_golden",
        "version": "v1",
        "dataset_type": "golden",
        "items": [
            {
                "id": "item1",
                "input_payload": {"raw_text": "hello"},
                "expected_output": {"result": "mocked", "tool": "evaluation_default", "input": {"raw_text": "hello"}},
                "tags": ["test"],
                "metadata": {}
            }
        ]
    }
    with open("datasets/intent/golden/v1.json", "w", encoding="utf-8") as f:
        json.dump(sample_dataset, f)
        
    config_dict = {
        "target_id": "evaluation_default",
        "metrics": ["classification"],
        "thresholds": {"classification": 0.8}
    }
    
    req = {
        "jsonrpc": "2.0",
        "id": 998,
        "method": "tools/call",
        "params": {
            "name": "run_evaluation",
            "arguments": {
                "domain": "intent",
                "dataset_type": "golden",
                "version": "v1",
                "config": config_dict
            }
        }
    }
    
    responses, _ = run_mcp_session([req])
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert "content" in resp["result"]
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "success"
    assert content["report"]["overall_score"] == 1.0
    
    # Cleanup datasets path
    try:
        os.remove("datasets/intent/golden/v1.json")
    except Exception:
        pass
