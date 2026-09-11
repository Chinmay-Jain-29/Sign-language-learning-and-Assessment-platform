import time
import base64
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.models.domain import User
from app.api.deps import get_optional_current_user
from app.ai.pipeline import ai_pipeline
from app.ai.temporal.stabilizer import gesture_stabilizer

router = APIRouter(prefix="/recognition", tags=["Real-Time Recognition"])

class LandmarkPointItem(BaseModel):
    x: float
    y: float
    z: float

class PredictLandmarksRequest(BaseModel):
    landmarks: List[LandmarkPointItem]
    target_sign: Optional[str] = None
    session_id: Optional[int] = None

class FramePredictRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded JPEG/PNG camera frame")
    target_sign: Optional[str] = None

class ResetStabilizerRequest(BaseModel):
    session_id: Optional[int] = None
    target_sign: Optional[str] = None

class RecognitionResponse(BaseModel):
    target_sign: Optional[str] = None
    predicted_sign: str
    predicted_class: str
    predicted_index: int
    confidence: float
    correct: Optional[bool] = None
    is_correct: Optional[bool] = None
    status: str
    message: str
    reason: str
    model_version: str
    model_hash: Optional[str] = None
    feature_dimension: Optional[int] = 63
    preprocessing_version: Optional[str] = None
    class_mapping_version: Optional[str] = None
    inference_time_ms: float
    is_valid_hand: bool

def compute_generic_assessment(target_sign: Optional[str], predicted_class: str, confidence: float, min_confidence: float = 0.70) -> Dict[str, Any]:
    """
    Completely generic, class-agnostic comparison engine for all 26 ASL classes (A-Z).
    Never hardcodes any specific sign letter.
    """
    norm_pred = predicted_class.strip().upper() if predicted_class else "NONE"
    norm_target = target_sign.strip().upper() if target_sign else None

    if norm_pred in ["NONE", "NO_HAND"]:
        return {
            "correct": False,
            "status": "NO_HAND",
            "message": "No hand detected. Position your hand clearly in front of the camera."
        }

    if confidence < min_confidence or norm_pred == "UNCERTAIN":
        return {
            "correct": False,
            "status": "UNCERTAIN",
            "message": "I couldn't confidently recognize the sign. Please position your hand clearly and try again."
        }

    if not norm_target:
        return {
            "correct": None,
            "status": "DETECTED",
            "message": f"Detected sign {norm_pred} with {confidence*100:.1f}% confidence."
        }

    # Pure generic equality comparison
    is_match = (norm_target == norm_pred)
    if is_match:
        return {
            "correct": True,
            "status": "CORRECT",
            "message": f"Correct! You performed sign {norm_target}."
        }
    else:
        return {
            "correct": False,
            "status": "INCORRECT",
            "message": f"Detected sign {norm_pred}. Please perform sign {norm_target}."
        }

@router.post("/reset-stabilizer")
def reset_stabilizer_endpoint(
    req: Optional[ResetStabilizerRequest] = None,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Resets temporal stabilizer history on target change or session reset."""
    gesture_stabilizer.reset()
    return {
        "success": True,
        "message": "Temporal prediction stabilizer reset successfully.",
        "data": {
            "status": "RESET",
            "target_sign": req.target_sign if req else None
        }
    }

@router.post("/predict-landmarks", response_model=RecognitionResponse)
def predict_landmarks_endpoint(
    req: PredictLandmarksRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Real-Time Landmark Recognition:
    Takes 21 3D spatial keypoints (x, y, z) from hand tracking,
    normalizes them (wrist-origin + Euclidean max scale),
    evaluates through trained Random Forest model (asl_rf_v001),
    and performs a generic class-agnostic target comparison.
    """
    t0 = time.time()
    
    if not req.landmarks or len(req.landmarks) != 21:
        return RecognitionResponse(
            target_sign=req.target_sign.upper() if req.target_sign else None,
            predicted_sign="NONE",
            predicted_class="NONE",
            predicted_index=-1,
            confidence=0.0,
            correct=False,
            is_correct=False,
            status="INVALID_INPUT",
            message="Invalid landmark count (expected 21 keypoints).",
            reason="Landmark count mismatch.",
            model_version=ai_pipeline.model_version,
            inference_time_ms=0.0,
            is_valid_hand=False
        )

    # 1. Extract 63 raw floats in exact XYZ order: x0,y0,z0,...,x20,y20,z20
    raw_63 = []
    for lm in req.landmarks:
        raw_63.extend([lm.x, lm.y, lm.z])

    # 2. Predict with production trained model
    pred_label, conf = ai_pipeline.predict_landmarks(raw_63)
    
    # 3. Apply temporal stabilization
    stable_label, is_stable = gesture_stabilizer.update(pred_label, conf)
    active_pred = stable_label if is_stable else pred_label

    # 4. Generic assessment evaluation
    assessment = compute_generic_assessment(req.target_sign, active_pred, conf, min_confidence=0.70)

    # 5. Class index lookup
    class_idx = -1
    if ai_pipeline.model is not None and hasattr(ai_pipeline.model, "classes_"):
        classes_list = list(ai_pipeline.model.classes_)
        if active_pred in classes_list:
            class_idx = classes_list.index(active_pred)

    elapsed_ms = round((time.time() - t0) * 1000.0, 2)

    return RecognitionResponse(
        target_sign=req.target_sign.upper() if req.target_sign else None,
        predicted_sign=active_pred,
        predicted_class=active_pred,
        predicted_index=class_idx,
        confidence=round(conf, 4),
        correct=assessment["correct"],
        is_correct=assessment["correct"],
        status=assessment["status"],
        message=assessment["message"],
        reason=f"Sign '{active_pred}' recognized with {conf*100:.1f}% confidence.",
        model_version=ai_pipeline.model_version,
        model_hash=ai_pipeline.model_hash_sha256,
        feature_dimension=63,
        preprocessing_version=ai_pipeline.preprocessing_version,
        class_mapping_version=ai_pipeline.class_mapping_version,
        inference_time_ms=elapsed_ms,
        is_valid_hand=True
    )

@router.post("/predict-frame", response_model=RecognitionResponse)
def predict_frame_endpoint(
    req: FramePredictRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Real-Time Camera Frame Recognition:
    Decodes base64 image frame, runs MediaPipe HandTracker, normalizes landmarks,
    evaluates Random Forest model, and performs generic target comparison.
    """
    t0 = time.time()
    try:
        header, encoded = req.image_base64.split(",", 1) if "," in req.image_base64 else ("", req.image_base64)
        image_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError("Failed to decode image buffer")
    except Exception as e:
        return RecognitionResponse(
            target_sign=req.target_sign.upper() if req.target_sign else None,
            predicted_sign="NONE",
            predicted_class="NONE",
            predicted_index=-1,
            confidence=0.0,
            correct=False,
            is_correct=False,
            status="INVALID_INPUT",
            message="Invalid image buffer.",
            reason=f"Image decoding failed: {e}",
            model_version=ai_pipeline.model_version,
            model_hash=ai_pipeline.model_hash_sha256,
            feature_dimension=63,
            preprocessing_version=ai_pipeline.preprocessing_version,
            class_mapping_version=ai_pipeline.class_mapping_version,
            inference_time_ms=round((time.time() - t0) * 1000.0, 2),
            is_valid_hand=False
        )

    res = ai_pipeline.predict(img_bgr)
    active_pred = res.predicted_gesture if res.landmarks_valid else "NONE"
    
    # Generic assessment
    assessment = compute_generic_assessment(req.target_sign, active_pred, res.confidence, min_confidence=0.70)

    # Class index
    class_idx = -1
    if ai_pipeline.model is not None and hasattr(ai_pipeline.model, "classes_"):
        classes_list = list(ai_pipeline.model.classes_)
        if active_pred in classes_list:
            class_idx = classes_list.index(active_pred)

    elapsed_ms = round((time.time() - t0) * 1000.0, 2)

    return RecognitionResponse(
        target_sign=req.target_sign.upper() if req.target_sign else None,
        predicted_sign=active_pred,
        predicted_class=active_pred,
        predicted_index=class_idx,
        confidence=res.confidence,
        correct=assessment["correct"],
        is_correct=assessment["correct"],
        status=assessment["status"],
        message=assessment["message"],
        reason=res.reason,
        model_version=res.model_version,
        model_hash=res.model_hash,
        feature_dimension=63,
        preprocessing_version=ai_pipeline.preprocessing_version,
        class_mapping_version=ai_pipeline.class_mapping_version,
        inference_time_ms=elapsed_ms,
        is_valid_hand=res.landmarks_valid
    )
