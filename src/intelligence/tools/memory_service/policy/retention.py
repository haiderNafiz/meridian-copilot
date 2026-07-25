from .base import MemoryRetentionPolicy
from ..schema import MemorySnapshot

class DefaultNoOpRetentionPolicy(MemoryRetentionPolicy):
    def evaluate_retention(self, memory: MemorySnapshot) -> MemorySnapshot:
        # No-op return
        return memory
