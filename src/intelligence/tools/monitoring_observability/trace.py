import uuid
import datetime
import inspect
import functools
from typing import Dict, Optional, Any, Callable
from contextlib import contextmanager
from .schema import TraceSpan

class TraceContext:
    def __init__(self, on_span_end: Optional[Callable[[TraceSpan], None]] = None):
        self._active_spans: Dict[str, TraceSpan] = {}
        self.on_span_end = on_span_end

    def start_span(self, operation_name: str, parent_span_id: Optional[str] = None, trace_id: Optional[str] = None) -> TraceSpan:
        span_id = f"spn_{uuid.uuid4().hex[:10]}"
        t_id = trace_id or f"trc_{uuid.uuid4().hex[:10]}"
        span = TraceSpan(
            span_id=span_id,
            trace_id=t_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.datetime.now(datetime.UTC).isoformat()
        )
        self._active_spans[span_id] = span
        return span

    def end_span(self, span_id: str, status: str = "success") -> Optional[TraceSpan]:
        if span_id in self._active_spans:
            span = self._active_spans[span_id]
            span.end_time = datetime.datetime.now(datetime.UTC).isoformat()
            span.status = status
            
            t1 = datetime.datetime.fromisoformat(span.start_time)
            t2 = datetime.datetime.fromisoformat(span.end_time)
            span.duration_ms = (t2 - t1).total_seconds() * 1000.0
            
            if self.on_span_end:
                self.on_span_end(span)
            return span
        return None

    @contextmanager
    def trace(self, operation_name: str, parent_span_id: Optional[str] = None, trace_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        span = self.start_span(operation_name, parent_span_id, trace_id)
        if tags:
            span.tags.update(tags)
        try:
            yield span
        except Exception as e:
            span.status = "error"
            span.tags["error"] = str(e)
            raise
        finally:
            self.end_span(span.span_id, span.status)

def trace_operation(operation_name: str, tags: Optional[Dict[str, str]] = None):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            from .service import get_monitoring_service
            service = get_monitoring_service()
            span = service.tracing.start_span(operation_name)
            if tags:
                span.tags.update(tags)
            try:
                result = await func(*args, **kwargs)
                service.metrics.counter(f"{operation_name}_success", 1.0)
                span.status = "success"
                return result
            except Exception as e:
                service.metrics.counter(f"{operation_name}_failure", 1.0)
                span.status = "error"
                span.tags["error"] = str(e)
                raise
            finally:
                service.tracing.end_span(span.span_id, span.status)
                if span.duration_ms is not None:
                    service.metrics.timer(f"{operation_name}_duration", span.duration_ms)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            from .service import get_monitoring_service
            service = get_monitoring_service()
            span = service.tracing.start_span(operation_name)
            if tags:
                span.tags.update(tags)
            try:
                result = func(*args, **kwargs)
                service.metrics.counter(f"{operation_name}_success", 1.0)
                span.status = "success"
                return result
            except Exception as e:
                service.metrics.counter(f"{operation_name}_failure", 1.0)
                span.status = "error"
                span.tags["error"] = str(e)
                raise
            finally:
                service.tracing.end_span(span.span_id, span.status)
                if span.duration_ms is not None:
                    service.metrics.timer(f"{operation_name}_duration", span.duration_ms)

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
