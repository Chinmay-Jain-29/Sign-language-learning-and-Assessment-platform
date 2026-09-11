import collections
from typing import Optional, Dict, Any, Tuple

class GestureStabilizer:
    """
    Real-Time Gesture Stabilizer:
    Requires N consecutive identical frame predictions (e.g., N=3)
    within a sliding window before marking a gesture prediction as 'stable'.
    Filters out single-frame classification jitter.
    """
    def __init__(self, required_consecutive_agreement: int = 3, window_size: int = 10):
        self.required_agreement = required_consecutive_agreement
        self.window_size = window_size
        self.history = collections.deque(maxlen=window_size)
        self.last_stable_gesture = None

    def update(self, new_prediction: str, confidence: float = 1.0) -> Tuple[str, bool]:
        """
        Pushes a new prediction string into recent history.
        Returns: (stable_gesture, is_stable)
        """
        self.history.append(new_prediction)

        # Check majority voting / consecutive confirmation
        if len(self.history) >= self.required_agreement:
            recent_k = list(self.history)[-self.required_agreement:]
            if len(set(recent_k)) == 1 and recent_k[0] not in [None, "NONE", "UNCERTAIN"]:
                self.last_stable_gesture = recent_k[0]
                return (self.last_stable_gesture, True)

        # If recent history is not yet unanimous, return last stable gesture or current prediction
        active = self.last_stable_gesture if self.last_stable_gesture else new_prediction
        return (active, False)

    def update_detailed(self, new_prediction: str) -> Dict[str, Any]:
        """Detailed status dictionary for analytics reporting."""
        stable, is_stable = self.update(new_prediction)
        return {
            "is_stable": is_stable,
            "stable_gesture": stable,
            "current_prediction": new_prediction,
            "status": "stable" if is_stable else "unstable",
            "reason": f"Prediction stabilized across {self.required_agreement} frames." if is_stable else "Predictions fluctuating between frames."
        }

    def reset(self):
        """Resets recent prediction history."""
        self.history.clear()
        self.last_stable_gesture = None

# Global singleton instance for real-time recognition pipeline
gesture_stabilizer = GestureStabilizer(required_consecutive_agreement=3, window_size=10)
