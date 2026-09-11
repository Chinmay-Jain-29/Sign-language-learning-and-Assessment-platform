import cv2
import numpy as np
import mediapipe as mp
from typing import List, Optional
from app.ai.hand_tracking.schemas import LandmarkPoint, BoundingBox, HandDetectionResult

class HandTracker:
    def __init__(
        self,
        static_image_mode: bool = True,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.7
    ):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def detect(self, image_np: np.ndarray) -> List[HandDetectionResult]:
        """
        Processes a BGR or RGB image NumPy array, detects multi-hand landmarks via MediaPipe,
        and returns structured HandDetectionResult objects with 21 3D landmarks and visibility validation.
        """
        if image_np is None or image_np.size == 0:
            return []

        # Ensure image is RGB format
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image_np

        height, width = image_rgb.shape[:2]
        results = self.hands.process(image_rgb)

        detections: List[HandDetectionResult] = []

        if not results.multi_hand_landmarks or not results.multi_handedness:
            return detections

        for hand_landmarks, handedness_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness_info.classification[0].label
            score = float(handedness_info.classification[0].score)

            # Extract 21 landmark points & evaluate visibility
            landmarks: List[LandmarkPoint] = []
            x_coords = []
            y_coords = []
            all_visible = True

            for lm in hand_landmarks.landmark:
                vis = getattr(lm, 'visibility', 1.0)
                if vis < 0.3:
                    all_visible = False

                landmarks.append(LandmarkPoint(
                    x=float(lm.x),
                    y=float(lm.y),
                    z=float(lm.z),
                    visibility=round(float(vis), 4)
                ))
                x_coords.append(int(lm.x * width))
                y_coords.append(int(lm.y * height))

            # Compute Bounding Box
            xmin = max(0, min(x_coords) - 10)
            ymin = max(0, min(y_coords) - 10)
            xmax = min(width, max(x_coords) + 10)
            ymax = min(height, max(y_coords) + 10)
            bbox = BoundingBox(
                xmin=xmin,
                ymin=ymin,
                width=xmax - xmin,
                height=ymax - ymin
            )

            detections.append(HandDetectionResult(
                handedness=label,
                score=round(score, 4),
                landmarks=landmarks,
                bbox=bbox,
                visibility_valid=(len(landmarks) == 21 and all_visible)
            ))

        return detections

    def draw_landmarks(self, image_np: np.ndarray, detections: List[HandDetectionResult]) -> np.ndarray:
        """Annotates detected hand keypoints, landmark connections, and bounding boxes."""
        annotated = image_np.copy()
        height, width = annotated.shape[:2]

        for det in detections:
            # Draw bounding box
            cv2.rectangle(
                annotated,
                (det.bbox.xmin, det.bbox.ymin),
                (det.bbox.xmin + det.bbox.width, det.bbox.ymin + det.bbox.height),
                (0, 255, 128),
                2
            )
            # Label
            cv2.putText(
                annotated,
                f"{det.handedness} ({int(det.score * 100)}%)",
                (det.bbox.xmin, max(20, det.bbox.ymin - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 128),
                2
            )
            
            # Draw 21 points
            for lm in det.landmarks:
                cx, cy = int(lm.x * width), int(lm.y * height)
                cv2.circle(annotated, (cx, cy), 4, (255, 100, 0), -1)

        return annotated

    def close(self):
        self.hands.close()
