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

        # Default success or general adjustment advice
        if expected_sign.upper() == predicted_sign.upper():
            return f"Great execution of sign '{expected_sign.upper()}'. Maintain thumb alignment for optimal joint contrast."
        
        return f"Sign '{expected_sign.upper()}' misclassified as '{predicted_sign.upper()}'. Try adjusting your finger position and hold steady."

# Global Feedback Engine Singleton
feedback_engine = FeedbackEngine()
