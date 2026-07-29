from abc import ABC
from typing import Any, Dict
from ..schema import EvaluationItem, EvaluationRunResult

class EvaluationHook(ABC):
    def on_start(self, context: Dict[str, Any]):
        pass

    def on_item_complete(self, item: EvaluationItem, result: EvaluationRunResult, context: Dict[str, Any]):
        pass

    def on_finish(self, results: list, context: Dict[str, Any]):
        pass

    def on_failure(self, error: Exception, context: Dict[str, Any]):
        pass
