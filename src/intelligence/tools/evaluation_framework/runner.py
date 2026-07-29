from typing import List, Dict, Any
from .schema import EvaluationItem, EvaluationRunResult
from .target import EvaluationTarget

class EvaluationRunner:
    def __init__(self, target: EvaluationTarget):
        self.target = target

    def run_batch(self, items: List[EvaluationItem], context: Dict[str, Any] = None) -> List[EvaluationRunResult]:
        """Execute a batch of dataset items against the evaluation target."""
        run_context = context or {}
        results = []
        
        for item in items:
            exec_res = self.target.execute(item.input_payload, run_context)
            results.append(EvaluationRunResult(
                item_id=item.id,
                actual_output=exec_res.actual_output,
                metrics=[],  # computed downstream
                resource=exec_res.resource,
                cost=exec_res.cost,
                artifacts=exec_res.artifacts
            ))
            
        return results
