from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import User, AssessmentAttempt, LearnerAlphabetState, LearnerProfile, PracticeSession
from app.schemas.dto import AttemptCreate
from app.api.deps import get_current_user
from app.services.practice_analytics_service import PracticeAnalyticsService
from app.services.adaptive_learning_service import process_adaptive_assessment_attempt

router = APIRouter(prefix="/practice", tags=["Practice & Adaptive Assessment"])

@router.post("/sessions/start")
def start_practice_session(
    selected_signs: List[str] = ["A", "B", "C"],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sess = PracticeSession(
        learner_id=current_user.id,
        selected_signs=selected_signs,
        start_time=datetime.utcnow(),
        status="active"
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return {
        "session_id": sess.id,
        "selected_signs": sess.selected_signs,
        "status": sess.status,
        "start_time": sess.start_time.isoformat() if sess.start_time else None
    }

@router.post("/sessions/{session_id}/end")
def end_practice_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sess = db.query(PracticeSession).filter(
        PracticeSession.id == session_id,
        PracticeSession.learner_id == current_user.id
    ).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Practice session not found.")
        
    sess.end_time = datetime.utcnow()
    sess.status = "completed"
    db.commit()
    db.refresh(sess)
    return {
        "session_id": sess.id,
        "total_attempts": sess.total_attempts,
        "correct_count": sess.correct_count,
        "incorrect_count": sess.incorrect_count,
        "average_accuracy": sess.average_accuracy,
        "average_confidence": sess.average_confidence,
        "status": sess.status
    }

@router.post("/attempt")
def submit_practice_attempt(
    attempt_in: AttemptCreate,
    session_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits and authoritatively persists a practice attempt result.
    If predicted_sign is provided by the live ML evaluation, records it directly
    without running a second inference pass.
    """
    # 1. Direct authoritative recording from live ML evaluation
    if attempt_in.predicted_sign is not None and attempt_in.predicted_sign not in ["None", "Uncertain", ""]:
        return PracticeAnalyticsService.record_attempt(
            db=db,
            learner=current_user,
            expected_sign=attempt_in.expected_sign,
            predicted_sign=attempt_in.predicted_sign,
            confidence=attempt_in.confidence if attempt_in.confidence is not None else 0.0,
            is_correct=attempt_in.is_correct,
            gesture_accuracy=attempt_in.gesture_accuracy,
            feedback_text=attempt_in.feedback,
            session_id=session_id
        )

    # 2. Fallback: If raw landmarks provided without a prediction
    if attempt_in.landmarks and len(attempt_in.landmarks) == 21:
        landmarks_dicts = [{'x': pt.x, 'y': pt.y, 'z': pt.z} for pt in attempt_in.landmarks]
        return process_adaptive_assessment_attempt(
            db=db,
            learner=current_user,
            expected_sign=attempt_in.expected_sign,
            landmarks=landmarks_dicts,
            session_id=session_id
        )

    raise HTTPException(
        status_code=422,
        detail="Invalid practice attempt. Please provide a valid predicted_sign or 21 spatial landmarks."
    )

@router.get("/history")
def get_practice_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.learner_id == current_user.id
    ).order_by(AssessmentAttempt.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "expected_sign": a.expected_sign,
            "predicted_sign": a.predicted_sign,
            "is_correct": a.is_correct,
            "confidence": a.confidence,
            "confidence_percentage": round(a.confidence * 100.0, 1) if a.confidence <= 1.0 else round(a.confidence, 1),
            "accuracy": 100.0 if a.is_correct else 0.0,
            "gesture_accuracy": a.gesture_accuracy,
            "feedback": a.feedback_obj.feedback_text if a.feedback_obj else (
                f"Correct! You performed sign {a.expected_sign}." if a.is_correct else f"Detected sign {a.predicted_sign}. Please perform sign {a.expected_sign}."
            ),
            "timestamp": a.timestamp.isoformat() if a.timestamp else None
        }
        for a in attempts
    ]

@router.get("/mastery")
def get_mastery_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    summary = PracticeAnalyticsService.get_dashboard_summary(db, current_user)
    return summary["sign_classification"]

