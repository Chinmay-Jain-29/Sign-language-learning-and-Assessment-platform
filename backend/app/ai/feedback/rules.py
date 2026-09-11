import numpy as np
from typing import Optional, List

class BaseFeedbackRule:
    """Abstract Base Class for Modular Feedback Rules."""
    def evaluate(self, landmarks_63: List[float], expected_sign: str, predicted_sign: str, confidence: float, invalid_frames: int) -> Optional[str]:
        raise NotImplementedError

class ConfidenceThresholdRule(BaseFeedbackRule):
    def evaluate(self, landmarks_63: List[float], expected_sign: str, predicted_sign: str, confidence: float, invalid_frames: int) -> Optional[str]:
        if confidence < 0.75:
            return "Your confidence is too low; repeat the gesture with firm finger posture."
        return None

class WristPositionRule(BaseFeedbackRule):
    def evaluate(self, landmarks_63: List[float], expected_sign: str, predicted_sign: str, confidence: float, invalid_frames: int) -> Optional[str]:
        if not landmarks_63 or len(landmarks_63) < 63:
            return "Keep your hand visible inside the camera frame."
        pts = np.array(landmarks_63, dtype=np.float32).reshape(21, 3)
        wrist_x, wrist_y = pts[0, 0], pts[0, 1]
        if wrist_x < 0.2 or wrist_x > 0.8 or wrist_y < 0.2 or wrist_y > 0.8:
            return "Move your hand closer to the center of the screen."
        return None

class HandScaleRule(BaseFeedbackRule):
    def evaluate(self, landmarks_63: List[float], expected_sign: str, predicted_sign: str, confidence: float, invalid_frames: int) -> Optional[str]:
        if not landmarks_63 or len(landmarks_63) < 63:
            return None
        pts = np.array(landmarks_63, dtype=np.float32).reshape(21, 3)
        dists = np.linalg.norm(pts - pts[0], axis=1)
        scale = np.max(dists)
        if scale < 0.15:
            return "Move your hand closer to the camera."
        elif scale > 0.60:
            return "Move your hand back slightly so wrist and all fingers remain visible."
        return None

class ThumbPositionRule(BaseFeedbackRule):
    def evaluate(self, landmarks_63: List[float], expected_sign: str, predicted_sign: str, confidence: float, invalid_frames: int) -> Optional[str]:
        exp = expected_sign.upper()
        pred = predicted_sign.upper()
        if exp == 'A' and pred in ['S', 'E', 'M', 'N']:
            return "Keep your thumb upright along the side of your index finger instead of tucking it underneath."
        if exp == 'B' and pred in ['4', 'PALM']:
            return "Cross your thumb horizontally across your palm while extending four fingers straight."
        if exp in ['M', 'N'] and pred in ['M', 'N']:
            return "Check thumb placement: 'N' tucks thumb under 2 fingers, while 'M' tucks under 3 fingers."
        return None

class StabilityRule(BaseFeedbackRule):
    def evaluate(self, landmarks_63: List[float], expected_sign: str, predicted_sign: str, confidence: float, invalid_frames: int) -> Optional[str]:
        if invalid_frames > 2:
            return "Your prediction is unstable. Hold the gesture steady for 3 seconds."
        return None
