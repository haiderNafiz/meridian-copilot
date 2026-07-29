from .base import FeedbackStrategy
from .rating import RatingStrategy
from .correction import CorrectionStrategy
from .annotation import AnnotationStrategy
from .outcome import OutcomeStrategy
from .preference import PreferenceStrategy
from typing import Dict, Optional
from ..schema import FeedbackType

class StrategyRegistry:
    def __init__(self):
        self._strategies: Dict[FeedbackType, FeedbackStrategy] = {
            FeedbackType.RATING: RatingStrategy(),
            FeedbackType.CORRECTION: CorrectionStrategy(),
            FeedbackType.ANNOTATION: AnnotationStrategy(),
            FeedbackType.OUTCOME: OutcomeStrategy(),
            FeedbackType.PREFERENCE: PreferenceStrategy()
        }

    def get_strategy(self, feedback_type: FeedbackType) -> Optional[FeedbackStrategy]:
        return self._strategies.get(feedback_type)
