import cv2
import numpy as np
import mediapipe as mp
from typing import List, Tuple, Optional, Dict, Any

mp_hands = mp.solutions.hands

def normalize_landmarks(raw_landmarks: List[Dict[str, float]]) -> np.ndarray:
    """
    Takes 21 raw (x, y, z) MediaPipe landmarks and normalizes them:
    1. Zero-centers relative to wrist (landmark 0).
    2. Scales by maximum distance from wrist to make position & size invariant.
    Returns 1D numpy array of length 63.
    """
    if len(raw_landmarks) != 21:
        raise ValueError(f"Expected 21 hand landmarks, got {len(raw_landmarks)}")

    coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in raw_landmarks], dtype=np.float32)
    
    # 1. Zero-center relative to wrist (index 0)
    wrist = coords[0]
    centered = coords - wrist
    
    # 2. Compute max Euclidean distance from wrist to normalize scale
    distances = np.linalg.norm(centered, axis=1)
    max_dist = np.max(distances)
    if max_dist > 1e-6:
        normalized = centered / max_dist
    else:
        normalized = centered
        
    return normalized.flatten()

def extract_landmarks_from_image(image_path: str) -> Optional[np.ndarray]:
    """
    Runs MediaPipe Hands on an image path and returns 63-dim normalized landmark array.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
        
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    with mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5) as hands:
        results = hands.process(img_rgb)
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            raw = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in hand_landmarks.landmark]
            return normalize_landmarks(raw)
    return None
