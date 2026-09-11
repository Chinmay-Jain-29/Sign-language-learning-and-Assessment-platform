import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import User, AssessmentAttempt, Certification, CertificationAttempt, LearningLevelEnum
from app.api.deps import get_current_user

router = APIRouter(prefix="/assessment", tags=["Assessment & Quizzes"])

# Question bank with canonical target signs and correct answers
ASSESSMENT_CATALOG = [
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
                "correct_option": "A",
                "hint": "The thumb rests on the side of the fist, not over the fingers."
            },
            {
                "id": 2,
                "question_text": "Which sign requires all four fingers extended straight upwards with the thumb tucked across the palm?",
                "target_sign": "B",
                "options_json": ["A", "B", "D", "F"],
                "correct_option": "B",
                "hint": "Fingers are flat together pointing straight up."
            },
            {
                "id": 3,
                "question_text": "Which sign forms a curved 'C' shape with all four fingers and thumb open facing each other?",
                "target_sign": "C",
                "options_json": ["C", "O", "E", "G"],
                "correct_option": "C",
                "hint": "Hand forms the curved profile of the letter C."
            }
        ]
    }
]

@router.get("/list")
def list_assessments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [
        {
            "id": a["id"],
            "title": a["title"],
            "description": a["description"],
            "level": a["level"],
            "time_limit_mins": a["time_limit_mins"],
            "passing_score": a["passing_score"],
            "questions": [
                {
                    "id": q["id"],
                    "question_text": q["question_text"],
                    "target_sign": q["target_sign"],
                    "options_json": q["options_json"],
                    "hint": q["hint"]
                }
                for q in a["questions"]
            ]
        }
        for a in ASSESSMENT_CATALOG
    ]

@router.post("/submit")
def submit_assessment(
    submission_in: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment_id = submission_in.get("assessment_id", 1)
    assessment = next((a for a in ASSESSMENT_CATALOG if a["id"] == assessment_id), None)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")
        
    question_map = {q["id"]: q for q in assessment["questions"]}
    answers = submission_in.get("answers", [])
    correct_count = 0
    total = max(1, len(assessment["questions"]))
    
    question_results = []
    for ans in answers:
        q_id = ans.get("question_id")
        selected = (ans.get("selected_option") or "").strip().upper()
        q_item = question_map.get(q_id)
        
        is_corr = False
        if q_item and selected == q_item["correct_option"].upper():
            is_corr = True
            correct_count += 1
            
        question_results.append({
            "question_id": q_id,
            "selected_option": selected,
            "correct_option": q_item["correct_option"] if q_item else None,
            "is_correct": is_corr
        })
            
    score = round((correct_count / total) * 100.0, 2)
    passed = score >= assessment["passing_score"]
    
    cert_code = None
    if passed:
        cert_code = f"CERT-ASL-{uuid.uuid4().hex[:8].upper()}"
        certification = Certification(
            user_id=current_user.id,
            level=assessment["level"],
            title=f"Certificate of Completion: {assessment['title']}",
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
        "assessment_id": assessment_id,
        "score": score,
        "passed": passed,
        "total_questions": total,
        "correct_answers": correct_count,
        "certificate_code": cert_code,
        "results": question_results,
        "completed_at": datetime.utcnow()
    }
