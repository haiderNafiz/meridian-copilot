from enum import Enum
from pydantic import BaseModel, Field

class FailureAction(str, Enum):
    ABORT = "abort"
    CONTINUE_WITH_FALLBACK = "continue_with_fallback"

class FailurePolicy(BaseModel):
    action: FailureAction = Field(default=FailureAction.ABORT, description="Workflow policy routing action on error")

    def should_abort(self) -> bool:
        return self.action == FailureAction.ABORT
