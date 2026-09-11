import numpy as np
from typing import List, Tuple, Union
from app.ai.hand_tracking.schemas import LandmarkPoint

class LandmarkNormalizer:
    """
    Provides translation-invariant (wrist-centered) and scale-invariant landmark normalization.
    Anchors wrist joint 0 to (0, 0, 0) and scales all 63 coordinates relative to maximum hand span.
    """

    @staticmethod
    def normalize_points(landmarks: List[LandmarkPoint]) -> List[LandmarkPoint]:
        """
        Normalizes a list of 21 3D LandmarkPoint objects.
        Returns a list of 21 zero-centered, scale-invariant LandmarkPoint objects.
        """
        if not landmarks or len(landmarks) != 21:
            return landmarks

        # Wrist reference point (Landmark 0)
        base_x = landmarks[0].x
        base_y = landmarks[0].y
        base_z = landmarks[0].z

        # 1. Translate (Zero-center relative to wrist)
        rel_coords = []
        max_dist = 0.0

        for lm in landmarks:
            rx = lm.x - base_x
            ry = lm.y - base_y
            rz = lm.z - base_z
            
            # Compute Euclidean distance from wrist
            dist = np.sqrt(rx**2 + ry**2 + rz**2)
            if dist > max_dist:
                max_dist = dist
                
            rel_coords.append((rx, ry, rz))

        # Avoid division by zero
        if max_dist < 1e-6:
            max_dist = 1.0

        # 2. Scale normalize relative to max span
        normalized_points: List[LandmarkPoint] = []
        for rx, ry, rz in rel_coords:
            normalized_points.append(
                LandmarkPoint(
                    x=round(float(rx / max_dist), 6),
                    y=round(float(ry / max_dist), 6),
                    z=round(float(rz / max_dist), 6)
                )
            )

        return normalized_points

    @staticmethod
    def normalize_array(flat_coords: np.ndarray) -> np.ndarray:
        """
        Normalizes a 1D (63,) or 2D (N, 63) NumPy array of landmarks.
        """
        return LandmarkNormalizer.normalize_array(flat_coords)

    def normalize(self, flat_coords: Union[List[float], np.ndarray]) -> np.ndarray:
        """
        Normalizes a 63-element flattened array. Compatible with standalone scripts.
        """
        return self.normalize_array(np.array(flat_coords, dtype=np.float32))

    @staticmethod
    def normalize_array(flat_coords: np.ndarray) -> np.ndarray:
        """
        Normalizes a 1D (63,) or 2D (N, 63) NumPy array of landmarks.
        """
        arr = np.array(flat_coords, dtype=np.float32)

        if arr.ndim == 1:
            if arr.shape[0] != 63:
                return arr
            
            # Reshape to (21, 3)
            pts = arr.reshape(21, 3)
            wrist = pts[0, :].copy()
            
            # Translate relative to wrist
            rel_pts = pts - wrist
            
            # Max Euclidean distance
            distances = np.linalg.norm(rel_pts, axis=1)
            max_d = np.max(distances)
            if max_d < 1e-6:
                max_d = 1.0
                
            norm_pts = rel_pts / max_d
            return norm_pts.flatten()

        elif arr.ndim == 2:
            if arr.shape[1] != 63:
                return arr
            
            N = arr.shape[0]
            norm_batch = np.zeros_like(arr)

            for i in range(N):
                pts = arr[i].reshape(21, 3)
                wrist = pts[0, :].copy()
                rel_pts = pts - wrist
                distances = np.linalg.norm(rel_pts, axis=1)
                max_d = np.max(distances)
                if max_d < 1e-6:
                    max_d = 1.0
                norm_batch[i] = (rel_pts / max_d).flatten()

            return norm_batch

        return arr
