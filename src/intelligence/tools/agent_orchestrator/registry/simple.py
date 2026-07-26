from typing import List, Optional, Callable, Dict
from .base import ToolRegistry
from ..schema import ToolMetadata

class SimpleToolRegistry(ToolRegistry):
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, ToolMetadata] = {}

    def register_tool(self, metadata: ToolMetadata, func: Callable) -> None:
        self._tools[metadata.name] = func
        self._metadata[metadata.name] = metadata

    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        return self._metadata.get(name)

    def get_all_tools(self) -> List[ToolMetadata]:
        return list(self._metadata.values())
