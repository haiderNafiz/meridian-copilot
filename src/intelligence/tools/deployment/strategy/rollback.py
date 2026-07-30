from .base import RollbackStrategy

class DefaultRollbackStrategy(RollbackStrategy):
    def __init__(self):
        self.rollback_executed = False

    def execute_rollback(self) -> bool:
        self.rollback_executed = True
        return True
