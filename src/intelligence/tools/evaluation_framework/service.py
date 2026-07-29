import datetime
import uuid
from typing import List, Dict, Any, Optional
from .schema import (
    EvaluationDataset, EvaluationConfig, EvaluationReport, EvaluationRunResult, 
    MetricResult, ResourceMetrics, CostMetrics
)
from .runner import EvaluationRunner
from .target import EvaluationTarget, ToolTarget
from .metric.registry import get_metric_registry
from .metric.aggregator import MetricAggregator
from .report.store import ReportStore
from .hook.base import EvaluationHook

class EvaluationService:
    def __init__(
        self,
        runner: EvaluationRunner,
        report_store: Optional[ReportStore] = None,
        hooks: Optional[List[EvaluationHook]] = None
    ):
        self.runner = runner
        self.report_store = report_store or ReportStore()
        self.hooks = hooks or []

    def run_evaluation(
        self,
        dataset: EvaluationDataset,
        config: EvaluationConfig,
        experiment_id: str = "exp_default"
    ) -> EvaluationReport:
        run_id = f"run_{uuid.uuid4().hex[:10]}"
        created_at = datetime.datetime.utcnow().isoformat() + "Z"
        
        # 1. Trigger Hooks Start
        context = {
            "run_id": run_id,
            "experiment_id": experiment_id,
            "dataset": dataset,
            "config": config
        }
        for hook in self.hooks:
            try:
                hook.on_start(context)
            except Exception:
                pass
                
        # 2. Run Batch Inference
        run_results = self.runner.run_batch(dataset.items, context)
        
        # 3. Score Metrics via Strategies
        registry = get_metric_registry()
        overall_scores = []
        
        for run_res in run_results:
            # Match item expected output with actual output
            item = next(x for x in dataset.items if x.id == run_res.item_id)
            
            # Map metrics using config selection
            item_metrics = []
            for metric_type in config.metrics:
                metric_name = metric_type.value
                strategy = registry.create_strategy(metric_name)
                
                # Fallback to classification accuracy if not explicitly registered
                if not strategy:
                    from .strategy.classification import ClassificationStrategy
                    strategy = ClassificationStrategy(metric_name=metric_name)
                    
                eval_context = {
                    "resource": run_res.resource,
                    "cost": run_res.cost,
                    "artifacts": run_res.artifacts
                }
                
                res = strategy.evaluate(
                    prediction=run_res.actual_output,
                    target=item.expected_output,
                    context=eval_context
                )
                item_metrics.append(res)
                overall_scores.append(res.score)
                
            run_res.metrics = item_metrics
            
            # Trigger Hooks complete
            for hook in self.hooks:
                try:
                    hook.on_item_complete(item, run_res, context)
                except Exception:
                    pass
                    
        # 4. Aggregations & Verdicts
        overall_score = MetricAggregator.aggregate(overall_scores, method="macro")
        passed = all(m.passed for r in run_results for m in r.metrics)
        
        # 5. Populate Summaries
        resource_sum = ResourceMetrics(
            cpu_percent=sum(r.resource.cpu_percent for r in run_results) / (len(run_results) or 1),
            peak_ram_mb=max((r.resource.peak_ram_mb for r in run_results), default=0.0),
            average_ram_mb=sum(r.resource.average_ram_mb for r in run_results) / (len(run_results) or 1),
            duration_ms=sum(r.resource.duration_ms for r in run_results),
            throughput_items_per_sec=len(run_results) / ((sum(r.resource.duration_ms for r in run_results) / 1000.0) or 1.0)
        )
        
        cost_sum = CostMetrics(
            prompt_tokens=sum(r.cost.prompt_tokens for r in run_results),
            completion_tokens=sum(r.cost.completion_tokens for r in run_results),
            estimated_cost=sum(r.cost.estimated_cost for r in run_results),
            provider=config.reproducibility.provider
        )
        
        report = EvaluationReport(
            report_id=f"rep_{uuid.uuid4().hex[:10]}",
            run_id=run_id,
            experiment_id=experiment_id,
            dataset_id=dataset.dataset_id,
            target_tool=config.target_id,
            overall_score=overall_score,
            run_results=run_results,
            passed=passed,
            created_at=created_at,
            reproducibility=config.reproducibility,
            cost_summary=cost_sum,
            resource_summary=resource_sum
        )
        
        # Trigger Hooks finish
        for hook in self.hooks:
            try:
                hook.on_finish(run_results, context)
            except Exception:
                pass
                
        # Save JSON & Markdown reports
        self.report_store.save_report(report, format="json")
        self.report_store.save_report(report, format="markdown")
        
        return report

_service_instance = None

def get_evaluation_service() -> EvaluationService:
    global _service_instance
    if _service_instance is None:
        # Default fallback binding
        target = ToolTarget("evaluation_default")
        runner = EvaluationRunner(target=target)
        store = ReportStore()
        _service_instance = EvaluationService(runner=runner, report_store=store)
    return _service_instance
