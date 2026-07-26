from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from ..schema import ToolMetadata

class ToolRegistry(ABC):
    @abstractmethod
    def register_tool(self, metadata: ToolMetadata, func: Callable) -> None:
        """Register an executable callable function along with its metadata."""
        pass

    @abstractmethod
    def get_tool(self, name: str) -> Optional[Callable]:
        """Fetch callable executor mapping matching name."""
        pass

    @abstractmethod
    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Fetch metadata for registered tool."""
        pass

    @abstractmethod
    def get_all_tools(self) -> List[ToolMetadata]:
        """Return list of all registered tools."""
        pass
