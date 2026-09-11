import os
import json
import numpy as np
from typing import Dict, List

_CANONICAL_CACHE = None

def get_canonical_landmarks() -> Dict[str, List[float]]:
    global _CANONICAL_CACHE
    if _CANONICAL_CACHE is not None:
        return _CANONICAL_CACHE

    json_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "datasets", "canonical_landmarks.json"
    ))

    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                _CANONICAL_CACHE = json.load(f)
                return _CANONICAL_CACHE
        except Exception as e:
            print(f"[CanonicalLandmarks] Error reading json: {e}")

    _CANONICAL_CACHE = {}
    return _CANONICAL_CACHE

def get_canonical_landmarks_for_sign(sign_char: str) -> List[Dict[str, float]]:
    """
    Returns 21 landmark dictionary objects [{'x': x, 'y': y, 'z': z}, ...]
    for specified sign character ('A' - 'Z').
    """
    sign_char = sign_char.upper()
    data = get_canonical_landmarks()
    raw_63 = data.get(sign_char)

    if not raw_63 or len(raw_63) < 63:
        # Fallback wrist-centered pose
        return [{'x': 0.0, 'y': 0.0, 'z': 0.0} for _ in range(21)]

    # Denormalize coordinates to (x, y, z) range [0, 1] centered at (0.5, 0.5) for display & MediaPipe compatibility
    pts = np.array(raw_63[:63], dtype=np.float32).reshape(21, 3)
    
    # Scale & shift for camera display (centered around x=0.5, y=0.5)
    display_pts = (pts * 0.25) + np.array([0.5, 0.5, 0.0])

    return [{'x': float(p[0]), 'y': float(p[1]), 'z': float(p[2])} for p in display_pts]
