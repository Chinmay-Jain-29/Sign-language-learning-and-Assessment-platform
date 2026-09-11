import numpy as np
from typing import Union, List, Tuple

class LandmarkNormalizer:
    """
    Production Landmark Normalization Engine:
    Translates hand keypoints so wrist landmark (index 0) is at origin (0, 0, 0),
    and scales keypoints by the maximum Euclidean distance from wrist across all 21 points.
    
    Formula:
      1. P_centered[i] = P[i] - P[0]  for i = 0..20
      2. scale = max_i ( sqrt( x_centered[i]^2 + y_centered[i]^2 + z_centered[i]^2 ) )
      3. P_normalized[i] = P_centered[i] / max(scale, 1e-6)
    
    Guarantees spatial scale invariance while preserving relative joint angles.
    """
    def __init__(self, eps: float = 1e-6):
        self.eps = eps

    def normalize(self, landmarks_flat: Union[List[float], np.ndarray]) -> np.ndarray:
        """
        Normalizes a 63-element flattened array (x0, y0, z0, ..., x20, y20, z20).
        Returns a 63-element normalized float32 NumPy array.
        """
        arr = np.array(landmarks_flat, dtype=np.float32)
        if arr.shape[0] != 63:
            raise ValueError(f"Expected 63 landmark values, got {arr.shape[0]}")

        # Reshape to (21, 3)
        pts = arr.reshape(21, 3)

        # 1. Translate wrist (index 0) to origin
        wrist = pts[0].copy()
        centered = pts - wrist

        # 2. Calculate hand scale (max Euclidean distance from wrist)
        distances = np.linalg.norm(centered, axis=1)
        scale = np.max(distances)

        # Handle zero or near-zero scale safely
        if scale < self.eps:
            scale = 1.0

        # 3. Divide coordinates by hand scale
        normalized = centered / scale

        # Flatten back to 63 features
        return normalized.flatten()

def normalize_feature_row(row_63: List[float]) -> List[float]:
    normalizer = LandmarkNormalizer()
    return normalizer.normalize(row_63).tolist()
