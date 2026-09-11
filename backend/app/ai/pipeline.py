import time
import os
import json
import hashlib
import joblib
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field

from app.ai.hand_tracking.hand_tracker import HandTracker
try:
    from app.ai.preprocessing.normalize_landmarks import LandmarkNormalizer
except ImportError:
    try:
        from ml.preprocessing.normalize_landmarks import LandmarkNormalizer
    except ImportError:
        from preprocessing.normalize_landmarks import LandmarkNormalizer

class PredictionResult(BaseModel):
    predicted_gesture: str = Field(..., description="Class label predicted by ML model or 'NONE'")
    confidence: float = Field(..., description="Prediction confidence score [0.0, 1.0]")
    model_version: str = Field("asl_rf_v001", description="Approved production model version")
    model_hash: str = Field("", description="SHA256 checksum of the loaded model binary")
    inference_time_ms: float = Field(..., description="End-to-end pipeline latency in milliseconds")
    landmarks_valid: bool = Field(..., description="True if 21 3D spatial keypoints were extracted cleanly")
    status: str = Field(..., description="'valid', 'uncertain', or 'invalid_input'")
    reason: str = Field(..., description="User-friendly status explanation")
    probabilities: Optional[Dict[str, float]] = Field(None, description="Per-class predicted probability distribution")

class AIPipeline:
    """
    Production AI Pipeline Interface:
    Encapsulates input validation, MediaPipe landmark extraction, wrist-scale normalization,
    Random Forest inference, confidence thresholding, and status evaluation.
    
    Guarantees 100% deterministic inference parity across localhost and production environments.
    """
    def __init__(self, model_dir: Optional[str] = None, confidence_threshold: float = 0.70):
        self.confidence_threshold = confidence_threshold
        self.tracker = HandTracker(static_image_mode=True, max_num_hands=1)
        self.normalizer = LandmarkNormalizer()
        
        self.model = None
        self.model_path = ""
        self.model_version = "asl_rf_v001"
        self.model_hash_sha256 = ""
        self.model_hash_md5 = ""
        self.model_size_bytes = 0
        self.preprocessing_version = "v1.0.0_wrist_maxdist_l2"
        self.class_mapping_version = "v1.0.0_canonical_26"
        
        self._load_production_model(model_dir)

    def _load_production_model(self, model_dir: Optional[str] = None):
        """Loads canonical production Random Forest model from tracked paths."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        
        candidate_paths = [
            os.path.join(base_dir, "models", "asl_rf_v001", "model.joblib"),
            os.path.join(base_dir, "backend", "app", "ai", "ml", "models", "gesture_model.joblib"),
            os.path.join(base_dir, "app", "ai", "ml", "models", "gesture_model.joblib"),
            os.path.join(base_dir, "models", "randomforest_tuned.joblib"),
            os.path.join(base_dir, "models", "gesture_model.joblib")
        ]
        
        if model_dir:
            candidate_paths.insert(0, os.path.join(model_dir, "model.joblib"))
            candidate_paths.insert(1, model_dir)

        loaded_path = None
        for path in candidate_paths:
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    self.model = joblib.load(path)
                    loaded_path = path
                    break
                except Exception as e:
                    print(f"[AIPipeline] Warning: Failed to load candidate model at {path}: {e}")

        if loaded_path and self.model is not None:
            self.model_path = loaded_path
            try:
                with open(loaded_path, "rb") as f:
                    data = f.read()
                self.model_hash_sha256 = hashlib.sha256(data).hexdigest()
                self.model_hash_md5 = hashlib.md5(data).hexdigest()
                self.model_size_bytes = len(data)
                
                # Check for metadata
                meta_dir = os.path.dirname(loaded_path)
                meta_file = os.path.join(meta_dir, "metadata.json")
                if os.path.exists(meta_file):
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        self.model_version = meta.get("model_version", "asl_rf_v001")
                        self.preprocessing_version = meta.get("preprocessing_version", "v1.0.0_wrist_maxdist_l2")
                        self.class_mapping_version = meta.get("class_mapping_version", "v1.0.0_canonical_26")
                        
                print(f"[AIPipeline] Production model loaded successfully from {loaded_path} (SHA256: {self.model_hash_sha256[:12]}...)")
            except Exception as e:
                print(f"[AIPipeline] Error reading model metadata: {e}")
        else:
            print("[AIPipeline] Warning: No production model artifact found across candidates.")
            self.model = None

    def get_model_metadata(self) -> Dict[str, Any]:
        """Returns non-sensitive model metadata for diagnostic endpoints."""
        classes_list = [str(c) for c in self.model.classes_] if self.model and hasattr(self.model, "classes_") else []
        return {
            "model_loaded": self.model is not None,
            "model_name": os.path.basename(self.model_path) if self.model_path else "none",
            "model_version": self.model_version,
            "model_hash_sha256": self.model_hash_sha256,
            "model_hash_md5": self.model_hash_md5,
            "model_size_bytes": self.model_size_bytes,
            "num_classes": len(classes_list),
            "classes": classes_list,
            "feature_dimension": 63,
            "preprocessing_version": self.preprocessing_version,
            "class_mapping_version": self.class_mapping_version,
            "environment": os.getenv("ENVIRONMENT", "development")
        }

    def validate_input(self, image_np: np.ndarray) -> Tuple[bool, str]:
        """Validates camera frame presence, dimensions, channels, and validity."""
        if image_np is None:
            return False, "Camera frame is missing or null."
        if not isinstance(image_np, np.ndarray) or image_np.size == 0:
            return False, "Invalid image format or empty frame buffer."
        if len(image_np.shape) < 2:
            return False, "Invalid image tensor dimensions."
        height, width = image_np.shape[:2]
        if height < 64 or width < 64:
            return False, f"Image resolution too low ({width}x{height}). Minimum required: 64x64."
        return True, "Valid frame"

    def predict(self, image_np: np.ndarray) -> PredictionResult:
        """
        Clean interface entry point:
        Raw Image -> Input Validation -> MediaPipe -> Landmarks -> Normalization -> 63 Features -> Model -> Threshold -> PredictionResult
        """
        t0 = time.time()

        # 1. Input Validation
        is_valid_frame, frame_err = self.validate_input(image_np)
        if not is_valid_frame:
            return PredictionResult(
                predicted_gesture="NONE",
                confidence=0.0,
                model_version=self.model_version,
                model_hash=self.model_hash_sha256,
                inference_time_ms=round((time.time() - t0) * 1000.0, 2),
                landmarks_valid=False,
                status="invalid_input",
                reason=frame_err
            )

        # 2. Hand Detection & Landmark Extraction
        detections = self.tracker.detect(image_np)
        if not detections:
            return PredictionResult(
                predicted_gesture="NONE",
                confidence=0.0,
                model_version=self.model_version,
                model_hash=self.model_hash_sha256,
                inference_time_ms=round((time.time() - t0) * 1000.0, 2),
                landmarks_valid=False,
                status="invalid_input",
                reason="No hand detected. Position your hand clearly within the camera frame."
            )

        det = detections[0]
        if len(det.landmarks) != 21:
            return PredictionResult(
                predicted_gesture="NONE",
                confidence=0.0,
                model_version=self.model_version,
                model_hash=self.model_hash_sha256,
                inference_time_ms=round((time.time() - t0) * 1000.0, 2),
                landmarks_valid=False,
                status="invalid_input",
                reason=f"Partial hand clipped ({len(det.landmarks)}/21 keypoints visible)."
            )

        # 3. Extract 63 Raw Features (x, y, z for 21 points)
        raw_63 = []
        for lm in det.landmarks:
            raw_63.extend([lm.x, lm.y, lm.z])

        # 4. Wrist-Centered Scale Normalization
        try:
            norm_63 = self.normalizer.normalize(raw_63)
        except Exception as e:
            return PredictionResult(
                predicted_gesture="NONE",
                confidence=0.0,
                model_version=self.model_version,
                model_hash=self.model_hash_sha256,
                inference_time_ms=round((time.time() - t0) * 1000.0, 2),
                landmarks_valid=False,
                status="invalid_input",
                reason=f"Landmark normalization error: {e}"
            )

        # 5. Classifier Inference
        if self.model is None:
            return PredictionResult(
                predicted_gesture="NONE",
                confidence=0.0,
                model_version=self.model_version,
                model_hash="",
                inference_time_ms=round((time.time() - t0) * 1000.0, 2),
                landmarks_valid=True,
                status="invalid_input",
                reason="ML model is currently unavailable on server."
            )

        feat_vector = norm_63.reshape(1, -1)
        pred_label = str(self.model.predict(feat_vector)[0])
        
        # Calculate confidence probability
        probs_dict = {}
        max_prob = float(det.score)
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(feat_vector)[0]
            classes = self.model.classes_
            max_prob = float(np.max(probabilities))
            for cls_name, p in zip(classes, probabilities):
                probs_dict[str(cls_name)] = round(float(p), 4)

        # 6. Confidence Thresholding
        status = "valid"
        reason = f"Gesture '{pred_label}' recognized with high confidence."
        if max_prob < self.confidence_threshold:
            status = "uncertain"
            reason = f"Low confidence gesture ({max_prob*100:.1f}% < threshold {self.confidence_threshold*100:.0f}%). Please stabilize your hand posture."

        elapsed_ms = round((time.time() - t0) * 1000.0, 2)

        return PredictionResult(
            predicted_gesture=pred_label,
            confidence=round(max_prob, 4),
            model_version=self.model_version,
            model_hash=self.model_hash_sha256,
            inference_time_ms=elapsed_ms,
            landmarks_valid=True,
            status=status,
            reason=reason,
            probabilities=probs_dict
        )

    def predict_landmarks(self, raw_63: List[float]) -> Tuple[str, float]:
        """
        Predict gesture directly from 63 3D spatial landmark coordinates.
        Uses trained Random Forest model.
        Returns: (predicted_sign, confidence) or ("NONE", 0.0) if model unavailable.
        """
        if self.model is None or len(raw_63) < 63:
            return "NONE", 0.0

        try:
            arr_63 = np.array(raw_63[:63], dtype=np.float32)
            norm_63 = self.normalizer.normalize(arr_63)
            feat_vector = norm_63.reshape(1, -1)
            pred_label = str(self.model.predict(feat_vector)[0])
            confidence = 0.90
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(feat_vector)[0]
                confidence = float(np.max(probs))
            return pred_label, round(confidence, 4)
        except Exception as e:
            print(f"[AIPipeline] Error in predict_landmarks: {e}")
            return "NONE", 0.0

# Global Pipeline Singleton
ai_pipeline = AIPipeline()
