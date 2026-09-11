import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.domain import User, Certification, LearnerProfile
from app.api.deps import get_current_user

router = APIRouter(prefix="/certification", tags=["Certification Exam System"])

class ExamSubmitRequest(BaseModel):
    exam_score: float = Field(..., ge=0.0, le=100.0, description="Submitted exam score [0.0, 100.0]")
    level_requested: str = Field("Beginner", description="'Beginner', 'Intermediate', 'Advanced', or 'Professional'")

@router.post("/start")
def start_certification_exam(
    level: str = "Beginner",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiates a timed skill evaluation exam session for a target certification level."""
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
    overall_score = profile.overall_performance_score if profile else 0.0

    return {
        "exam_session_id": f"EXAM-{uuid.uuid4().hex[:8].upper()}",
        "learner_name": current_user.full_name,
        "target_level": level,
        "overall_performance_score": overall_score,
        "total_questions": 10,
        "time_limit_mins": 15,
        "status": "in_progress",
        "started_at": datetime.utcnow()
    }

@router.post("/submit")
def submit_certification_exam(
    exam_in: ExamSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evaluates exam submission and awards official certificate if passing threshold (75%) is met."""
    pass_threshold = 75.0
    passed = (exam_in.exam_score >= pass_threshold)

    level_name = exam_in.level_requested.capitalize()
    cert_title = f"Certified ASL {level_name} Signer"

    cert_obj = None
    if passed:
        cert_code = f"CERT-{level_name.upper()}-{uuid.uuid4().hex[:6].upper()}"
        cert_obj = Certification(
            user_id=current_user.id,
            title=cert_title,
            certificate_code=cert_code,
            issued_at=datetime.utcnow()
        )
        db.add(cert_obj)
        db.commit()
        db.refresh(cert_obj)

    return {
        "passed": passed,
        "exam_score": exam_in.exam_score,
        "pass_threshold": pass_threshold,
        "certification_level": level_name if passed else "Not Eligible",
        "title": cert_title if passed else "N/A",
        "certificate_code": cert_obj.certificate_code if cert_obj else None,
        "issued_at": cert_obj.issued_at if cert_obj else None,
        "message": f"Congratulations! You passed the {cert_title} exam." if passed else f"Exam score ({exam_in.exam_score:.1f}%) below passing threshold ({pass_threshold:.0f}%). Practice to re-take."
    }

@router.get("/history")
@router.get("/list")
def get_user_certifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns list of all certificates earned by the current user."""
    certs = db.query(Certification).filter(Certification.user_id == current_user.id).order_by(Certification.issued_at.desc()).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "certificate_code": c.certificate_code,
            "issued_at": c.issued_at
        }
        for c in certs
    ]

@router.get("/{cert_code}")
def verify_certificate(cert_code: str, db: Session = Depends(get_db)):
    """Public verification endpoint for certificate code validity."""
    cert = db.query(Certification).filter(Certification.certificate_code == cert_code).first()
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate code is invalid or not found.")
    return {
        "id": cert.id,
        "title": cert.title,
        "certificate_code": cert.certificate_code,
        "issued_at": cert.issued_at,
        "valid": True
    }
