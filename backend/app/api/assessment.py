import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import User, AssessmentAttempt, Certification, CertificationAttempt, LearningLevelEnum
from app.api.deps import get_current_user

router = APIRouter(prefix="/assessment", tags=["Assessment & Quizzes"])

@router.get("/list")
def list_assessments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [
        {
            "id": 1,
            "title": "ASL Alphabet Foundation Quiz",
            "description": "Evaluate your mastery of basic ASL hand shapes and letters.",
            "level": LearningLevelEnum.BEGINNER,
            "time_limit_mins": 10,
            "passing_score": 70.0,
            "questions": [
                {
                    "id": 1,
                    "question_text": "Which sign requires curling all four fingers into a fist with the thumb resting against the side of the index finger?",
                    "target_sign": "A",
                    "options_json": ["A", "B", "C", "S"],
                    "hint": "The thumb rests on the side of the fist, not over the fingers."
                },
                {
                    "id": 2,
                    "question_text": "Which sign requires all four fingers extended straight upwards with the thumb tucked across the palm?",
                    "target_sign": "B",
                    "options_json": ["A", "B", "D", "F"],
                    "hint": "Fingers are flat together pointing straight up."
                }
            ]
        }
    ]

@router.post("/submit")
def submit_assessment(
    submission_in: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    answers = submission_in.get("answers", [])
    correct_count = 0
    total = max(1, len(answers))
    
    for ans in answers:
        if ans.get("selected_option") in ["A", "B"]:
            correct_count += 1
            
    score = round((correct_count / total) * 100.0, 2)
    passed = score >= 70.0
    
    cert_code = None
    if passed:
        cert_code = f"CERT-ASL-{uuid.uuid4().hex[:8].upper()}"
        certification = Certification(
            user_id=current_user.id,
            level=LearningLevelEnum.BEGINNER,
            title="Certificate of Completion: ASL Foundation",
            certificate_code=cert_code
        )
        db.add(certification)
        db.commit()
        db.refresh(certification)
        
        ca = CertificationAttempt(
            certification_id=certification.id,
            score=score,
            passed=passed
        )
        db.add(ca)
        db.commit()
        
    return {
        "id": 1,
        "assessment_id": submission_in.get("assessment_id", 1),
        "score": score,
        "passed": passed,
        "certificate_code": cert_code,
        "completed_at": datetime.utcnow()
    }
