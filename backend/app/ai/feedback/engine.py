from typing import List, Optional
from app.ai.feedback.rules import (
    BaseFeedbackRule, ConfidenceThresholdRule, WristPositionRule,
    HandScaleRule, ThumbPositionRule, StabilityRule
)

class FeedbackEngine:
    """
    Modular Rule-Based Feedback Engine:
    Evaluates registered modular feedback rules sequentially against system state
    and landmark metrics to generate non-random, actionable guidance.
    """
    def __init__(self):
        self.rules: List[BaseFeedbackRule] = [
            WristPositionRule(),
            HandScaleRule(),
            StabilityRule(),
            ThumbPositionRule(),
            ConfidenceThresholdRule()
        ]

    def generate_feedback(
        self,
        landmarks_63: List[float],
        expected_sign: str,
        predicted_sign: str,
        confidence: float,
        invalid_frames: int = 0
    ) -> str:
        # Evaluate modular rules in priority order
        for rule in self.rules:
            msg = rule.evaluate(landmarks_63, expected_sign, predicted_sign, confidence, invalid_frames)
            if msg:
                return msg

        # Standardized genuine model comparison feedback
        if expected_sign.upper() == predicted_sign.upper():
            return f"Correct. The model detected {predicted_sign.upper()}, which matches the expected {expected_sign.upper()} sign."
        
        return f"Incorrect. The model detected {predicted_sign.upper()}, while the expected sign was {expected_sign.upper()}. Please adjust your hand position and try the {expected_sign.upper()} sign again."

# Global Feedback Engine Singleton
feedback_engine = FeedbackEngine()
