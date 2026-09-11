import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from app.models.domain import User, RoleEnum
from app.api.deps import require_roles, get_current_user
from app.ai.dataset_service import get_dataset_summary, get_camera_status
from app.ai.hand_tracking.hand_tracker import HandTracker
from app.ai.hand_tracking.schemas import HandDetectionResult, LandmarkPoint
from app.ai.landmark_extraction_service import run_landmark_extraction
from app.ai.dataset_quality_service import audit_dataset_quality
from app.ai.preprocessing.normalize_landmarks import LandmarkNormalizer
from app.ai.dataset_split_service import run_dataset_split
from app.ai.classifier_service import run_classifier_experiments, get_classifier_report
from app.ai.rf_hyperparameter_service import run_rf_hyperparameter_study, get_rf_hyperparameter_report
from app.ai.error_analysis_service import run_error_analysis, get_error_analysis_report
from app.ai.benchmark_service import run_inference_benchmark, get_benchmark_report

router = APIRouter(prefix="/ai", tags=["AI & Hand Tracking"])
tracker = HandTracker(static_image_mode=True, max_num_hands=2)

class LandmarkNormalizeRequest(BaseModel):
    landmarks: List[LandmarkPoint]

@router.get("/dataset/audit", response_model=Dict[str, Any])
def dataset_audit_endpoint(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR, RoleEnum.ACCESSIBILITY_TRAINER]))
):
    try:
        return get_dataset_audit_report()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch dataset audit: {str(e)}")

@router.get("/dataset/summary", response_model=Dict[str, Any])
def dataset_summary(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR, RoleEnum.ACCESSIBILITY_TRAINER]))
):
    return get_dataset_summary()

@router.get("/dataset/quality-report", response_model=Dict[str, Any])
def dataset_quality_report(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR, RoleEnum.ACCESSIBILITY_TRAINER]))
):
    return audit_dataset_quality()

@router.post("/dataset/split", response_model=Dict[str, Any])
def split_dataset_endpoint(
    train_ratio: Optional[float] = 0.70,
    val_ratio: Optional[float] = 0.15,
    test_ratio: Optional[float] = 0.15,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    try:
        res = run_dataset_split(train_ratio=train_ratio, val_ratio=val_ratio, test_ratio=test_ratio)
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Dataset split failed: {str(e)}")

@router.get("/classifiers/report", response_model=Dict[str, Any])
def classifier_report_endpoint(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR, RoleEnum.ACCESSIBILITY_TRAINER]))
):
    try:
        return get_classifier_report()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch classifier report: {str(e)}")

@router.post("/classifiers/train", response_model=Dict[str, Any])
def train_classifiers_endpoint(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    try:
        res = run_classifier_experiments()
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Classifier training failed: {str(e)}")

@router.get("/rf/hyperparameters/report", response_model=Dict[str, Any])
def rf_hyperparameter_report_endpoint(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR, RoleEnum.ACCESSIBILITY_TRAINER]))
):
    try:
        return get_rf_hyperparameter_report()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch RF hyperparameter report: {str(e)}")

@router.post("/rf/hyperparameters/study", response_model=Dict[str, Any])
def study_rf_hyperparameters_endpoint(
    n_estimators_grid: Optional[List[int]] = None,
    max_depth_grid: Optional[List[Optional[int]]] = None,
    min_samples_leaf_grid: Optional[List[int]] = None,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    try:
        res = run_rf_hyperparameter_study(
            n_estimators_grid=n_estimators_grid,
            max_depth_grid=max_depth_grid,
            min_samples_leaf_grid=min_samples_leaf_grid
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"RF hyperparameter study failed: {str(e)}")

@router.get("/error-analysis/report", response_model=Dict[str, Any])
def error_analysis_report_endpoint(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR, RoleEnum.ACCESSIBILITY_TRAINER]))
):
    try:
        return get_error_analysis_report()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch error analysis report: {str(e)}")

@router.post("/error-analysis/run", response_model=Dict[str, Any])
def run_error_analysis_endpoint(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    try:
        res = run_error_analysis()
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error analysis execution failed: {str(e)}")

@router.get("/benchmark/report", response_model=Dict[str, Any])
def benchmark_report_endpoint(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR, RoleEnum.ACCESSIBILITY_TRAINER]))
):
    try:
        return get_benchmark_report()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch benchmark report: {str(e)}")

@router.post("/benchmark/run", response_model=Dict[str, Any])
def run_benchmark_endpoint(
    iterations: Optional[int] = 500,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    try:
        res = run_inference_benchmark(iterations=iterations)
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Inference benchmark execution failed: {str(e)}")

@router.get("/camera/status", response_model=Dict[str, Any])
def camera_status(
    current_user: User = Depends(get_current_user)
):
    return get_camera_status()

@router.post("/detect-landmarks", response_model=List[HandDetectionResult])
async def detect_landmarks(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_bgr is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file uploaded.")

        detections = tracker.detect(img_bgr)
        return detections
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Landmark detection failed: {str(e)}")

@router.post("/normalize-landmarks", response_model=List[LandmarkPoint])
def normalize_landmarks(
    req: LandmarkNormalizeRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        normalized = LandmarkNormalizer.normalize_points(req.landmarks)
        return normalized
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Normalization failed: {str(e)}")

@router.post("/extract-landmarks", response_model=Dict[str, Any])
def extract_landmarks(
    max_samples_per_class: Optional[int] = 50,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    try:
        stats = run_landmark_extraction(max_samples_per_class=max_samples_per_class)
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Batch extraction failed: {str(e)}")
