from typing import Dict, Any, List
from pydantic import BaseModel, Field

class RegressionDelta(BaseModel):
    metric_name: str
    current_score: float
    previous_score: float
    delta: float
    regression: bool = False

class RegressionReport(BaseModel):
    baseline_run_id: str
    current_run_id: str
    deltas: List[RegressionDelta] = Field(default_factory=list)
    regressed: bool = False

class RegressionAnalyzer:
    @staticmethod
    def analyze(current_metrics: Dict[str, float], baseline_metrics: Dict[str, float], thresholds: Dict[str, float] = None) -> RegressionReport:
        deltas = []
        regressed = False
        limit_thresholds = thresholds or {}
        
        for name, current in current_metrics.items():
            if name in baseline_metrics:
                previous = baseline_metrics[name]
                delta = round(current - previous, 4)
                # Let's say if delta is negative and exceeds threshold delta or defaults to < 0
                is_regressed = (delta < 0)
                if name in limit_thresholds:
                    # e.g., if we accept up to -2% drop: delta < -limit_thresholds[name]
                    is_regressed = (delta < -abs(limit_thresholds[name]))
                    
                if is_regressed:
                    regressed = True
                deltas.append(RegressionDelta(
                    metric_name=name,
                    current_score=current,
                    previous_score=previous,
                    delta=delta,
                    regression=is_regressed
                ))
                
        return RegressionReport(
            baseline_run_id="baseline_run",
            current_run_id="current_run",
            deltas=deltas,
            regressed=regressed
        )
