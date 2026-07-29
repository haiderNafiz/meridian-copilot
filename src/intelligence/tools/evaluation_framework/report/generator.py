import json
from typing import Dict, Any
from ..schema import EvaluationReport

class ReportGenerator:
    @staticmethod
    def generate_json(report: EvaluationReport) -> str:
        """Serialize evaluation report directly to a raw JSON string."""
        return report.model_dump_json(indent=2)

    @staticmethod
    def generate_markdown(report: EvaluationReport) -> str:
        """Produce a clean human-readable Markdown summary report."""
        md = []
        md.append(f"# Evaluation Report — {report.report_id}")
        md.append(f"- **Target Tool/Component**: {report.target_tool}")
        md.append(f"- **Dataset**: {report.dataset_id}")
        md.append(f"- **Outcome**: {'PASSED' if report.passed else 'FAILED'}")
        md.append(f"- **Overall Score**: {report.overall_score * 100:.1f}%")
        md.append(f"- **Timestamp**: {report.created_at}")
        md.append("")
        
        md.append("## Resource & Cost Summary")
        md.append(f"- Latency: {report.resource_summary.duration_ms:.2f} ms")
        md.append(f"- Peak Memory: {report.resource_summary.peak_ram_mb:.1f} MB")
        md.append(f"- Estimated Run Cost: {report.cost_summary.estimated_cost:.5f} {report.cost_summary.currency}")
        md.append("")
        
        md.append("## Individual Check Scenarios")
        md.append("| Item ID | Mapped Metrics Scores | Passed? |")
        md.append("|---|---|---|")
        for item in report.run_results:
            metric_strs = []
            item_passed = True
            for m in item.metrics:
                metric_strs.append(f"{m.metric_name}: {m.score * 100:.1f}%")
                if not m.passed:
                    item_passed = False
            md.append(f"| {item.item_id} | {', '.join(metric_strs)} | {'Yes' if item_passed else 'No'} |")
            
        return "\n".join(md)
