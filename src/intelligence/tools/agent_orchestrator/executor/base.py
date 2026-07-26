from abc import ABC, abstractmethod
from typing import Any, Callable
from ..schema import ExecutionContext, ExecutionNode, ToolMetadata
from ..policy.retry import RetryPolicy
from ..policy.failure import FailurePolicy

class ToolExecutor(ABC):
    @abstractmethod
    def execute(
        self, 
        node: ExecutionNode, 
        metadata: ToolMetadata,
        func: Callable,
        context: ExecutionContext,
        retry_policy: RetryPolicy,
        failure_policy: FailurePolicy
    ) -> Any:
        """
        Execute tool node, resolving mapping variables, validating dependencies,
        tracking telemetry, handling retries, and dispatching function calls.
        """
        pass
