import os
import json
from typing import Optional
from ..schema import EvaluationReport

class ReportStore:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../../reports")
            )
        else:
            self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def save_report(self, report: EvaluationReport, format: str = "json") -> str:
        """Save report serialized representation to disk and return filename."""
        filename = f"{report.run_id}.{format}"
        file_path = os.path.join(self.base_dir, filename)
        
        if format == "markdown":
            from .generator import ReportGenerator
            content = ReportGenerator.generate_markdown(report)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        else: # default json
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))
                
        return file_path

    def load_report(self, run_id: str) -> Optional[EvaluationReport]:
        """Load report object back from saved file paths."""
        file_path = os.path.join(self.base_dir, f"{run_id}.json")
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return EvaluationReport.model_validate(raw)
