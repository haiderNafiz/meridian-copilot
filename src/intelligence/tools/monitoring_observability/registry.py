from typing import Dict, List, Optional
from .schema import MonitoredComponent, ComponentHealth

class MonitoringRegistry:
    def __init__(self):
        self._components: Dict[str, MonitoredComponent] = {}

    def register_component(self, component: MonitoredComponent) -> None:
        self._components[component.component_id] = component

    def get_component(self, component_id: str) -> Optional[MonitoredComponent]:
        return self._components.get(component_id)

    def list_components(self) -> List[MonitoredComponent]:
        return list(self._components.values())

    def update_health(self, component_id: str, status: ComponentHealth) -> None:
        if component_id in self._components:
            self._components[component_id].health_status = status
