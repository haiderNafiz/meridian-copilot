from typing import Dict, List, Optional
from .schema import CapabilityMetadata, PluginDefinition
from .strategy.base import ValidationStrategy

class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, CapabilityMetadata] = {}

    def register(self, name: str, meta: CapabilityMetadata) -> None:
        self._capabilities[name] = meta

    def get_capability(self, name: str) -> Optional[CapabilityMetadata]:
        return self._capabilities.get(name)

    def list_capabilities(self) -> List[str]:
        return list(self._capabilities.keys())

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, PluginDefinition] = {}

    def register_plugin(self, plugin: PluginDefinition) -> None:
        self._plugins[plugin.plugin_name] = plugin

    def get_plugin(self, name: str) -> Optional[PluginDefinition]:
        return self._plugins.get(name)

    def list_plugins(self) -> List[PluginDefinition]:
        return list(self._plugins.values())

class ValidationRegistry:
    def __init__(self):
        self._validators: Dict[str, ValidationStrategy] = {}

    def register(self, validator: ValidationStrategy) -> None:
        self._validators[validator.name] = validator

    def get_validator(self, name: str) -> Optional[ValidationStrategy]:
        return self._validators.get(name)

    def list_validators(self) -> List[ValidationStrategy]:
        return list(self._validators.values())
