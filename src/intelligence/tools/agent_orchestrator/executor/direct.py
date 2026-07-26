import time
import logging
from typing import Any, Callable, Dict
from .base import ToolExecutor
from ..schema import ExecutionContext, ExecutionNode, ToolMetadata
from ..policy.retry import RetryPolicy
from ..policy.failure import FailurePolicy

logger = logging.getLogger("meridian.orchestrator.executor")

class DirectToolExecutor(ToolExecutor):
    def execute(
        self, 
        node: ExecutionNode, 
        metadata: ToolMetadata,
        func: Callable,
        context: ExecutionContext,
        retry_policy: RetryPolicy,
        failure_policy: FailurePolicy
    ) -> Any:
        # 1. Dependency Validation
        for dep in metadata.dependencies:
            if dep not in context.outputs:
                raise ValueError(f"Dependency error: Tool {node.tool_name} requires {dep} to be completed.")

        # 2. Argument Resolution
        resolved_args = self._resolve_arguments(node.arguments_mapping, context)

        # 3. Telemetry Hooks & Retry Loop Invocation
        attempts = 0
        last_error = None
        
        while attempts <= retry_policy.max_retries:
            start_time = time.perf_counter()
            logger.info(f"[{context.trace_id}] Executing tool={node.tool_name} (Attempt {attempts + 1})")
            
            try:
                # Add context tracing trace_id into argument list if accepted
                if hasattr(func, "__code__") and "context" in func.__code__.co_varnames:
                    resolved_args["context"] = {"trace_id": context.trace_id}
                
                # Invocation
                result = func(**resolved_args)
                latency = (time.perf_counter() - start_time) * 1000
                logger.info(f"[{context.trace_id}] Tool {node.tool_name} success. Latency: {latency:.2f}ms")
                return result
            except Exception as e:
                latency = (time.perf_counter() - start_time) * 1000
                logger.error(f"[{context.trace_id}] Tool {node.tool_name} failed. Latency: {latency:.2f}ms. Error: {str(e)}")
                last_error = e
                attempts += 1
                if attempts <= retry_policy.max_retries:
                    delay = retry_policy.initial_delay * (retry_policy.backoff ** (attempts - 1))
                    if delay > 0:
                        time.sleep(delay)
                    
        raise last_error

    def _resolve_arguments(self, mapping: Dict[str, str], context: ExecutionContext) -> Dict[str, Any]:
        resolved = {}
        for target_arg, source_path in mapping.items():
            if "." in source_path:
                parts = source_path.split(".", 1)
                tool_output = context.outputs.get(parts[0])
                if tool_output:
                    resolved[target_arg] = self._extract_nested_value(tool_output, parts[1])
            else:
                resolved[target_arg] = context.outputs.get(source_path)
        return resolved

    def _extract_nested_value(self, obj: Any, path: str) -> Any:
        current = obj
        for step in path.split("."):
            if hasattr(current, step):
                current = getattr(current, step)
            elif isinstance(current, dict) and step in current:
                current = current[step]
            else:
                return None
        return current
