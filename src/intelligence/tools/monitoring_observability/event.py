from typing import List, Callable
from .schema import MonitoringEvent

class EventDispatcher:
    def __init__(self):
        self._listeners: List[Callable[[MonitoringEvent], None]] = []

    def register_listener(self, listener: Callable[[MonitoringEvent], None]) -> None:
        self._listeners.append(listener)

    def dispatch(self, event: MonitoringEvent) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass
