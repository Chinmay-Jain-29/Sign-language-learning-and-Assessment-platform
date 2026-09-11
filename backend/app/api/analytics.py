from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from app.database.session import get_db
from app.models.domain import (
    User, LearnerProfile, LearnerAlphabetState, AssessmentAttempt,
    PracticeSession, Certification, RoleEnum, Course, StateEnum
)
from app.schemas.dto import ProfileResponse
from app.api.deps import get_current_user, require_roles
from app.services.practice_analytics_service import PracticeAnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Multi-Role Dashboards"])

@router.get("/dashboard")
@router.get("/progress")
@router.get("/learner")
def get_learner_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    100% Data-Driven Learner Dashboard API
    Directly delegates to PracticeAnalyticsService as the single authoritative source of truth.
    """
    return PracticeAnalyticsService.get_dashboard_summary(db=db, current_user=current_user)

@router.get("/instructor/learners")
def get_instructor_learners_list(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Returns list of all registered learners with real aggregated metrics via single-pass batch SQL queries.
    """
    learners = db.query(User).options(joinedload(User.profile)).filter(User.role == RoleEnum.LEARNER).order_by(User.id.asc()).all()
    if not learners:
        return []

    learner_ids = [l.id for l in learners]

    attempt_aggregates = db.query(
        AssessmentAttempt.learner_id,
        func.count(AssessmentAttempt.id).label("total_attempts"),
        func.sum(case((AssessmentAttempt.is_correct == True, 1), else_=0)).label("correct_attempts"),
        func.max(AssessmentAttempt.timestamp).label("last_practice_at")
    ).filter(
        AssessmentAttempt.learner_id.in_(learner_ids)
    ).group_by(
        AssessmentAttempt.learner_id
    ).all()
    attempts_map = {r.learner_id: r for r in attempt_aggregates}

    session_counts = db.query(
        PracticeSession.learner_id,
        func.count(PracticeSession.id).label("total_sessions")
    ).filter(
        PracticeSession.learner_id.in_(learner_ids)
    ).group_by(
        PracticeSession.learner_id
    ).all()
    sessions_map = {r.learner_id: r.total_sessions for r in session_counts}

    results = []
    for l in learners:
        prof = l.profile
        att = attempts_map.get(l.id)
        total_attempts = int(att.total_attempts) if att else 0
        correct_attempts = int(att.correct_attempts) if (att and att.correct_attempts is not None) else 0
        avg_acc = round((correct_attempts / total_attempts * 100.0), 1) if total_attempts > 0 else None
        last_at = att.last_practice_at.isoformat() if (att and att.last_practice_at) else None
        sessions_count = sessions_map.get(l.id, 0)

        results.append({
            "id": l.id,
            "full_name": l.full_name,
            "email": l.email,
            "learning_level": prof.learning_level.value if (prof and hasattr(prof.learning_level, 'value')) else (prof.learning_level if prof else "Beginner"),
            "overall_score": prof.overall_performance_score if prof else 0.0,
            "practice_streak_days": prof.practice_streak_days if prof else 0,
            "total_attempts": total_attempts,
            "total_sessions": sessions_count,
            "overall_accuracy": avg_acc,
            "last_practice_at": last_at,
            "status": "Active" if l.is_active else "Inactive"
        })

    return results

@router.get("/learners/{learner_id}")
def get_learner_drilldown_analytics(
    learner_id: int,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Detailed, canonical analytics drill-down for a specific learner.
    Enforces strict consistency with the learner's own dashboard by using PracticeAnalyticsService.
    """
    target_learner = db.query(User).filter(User.id == learner_id, User.role == RoleEnum.LEARNER).first()
    if not target_learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID {learner_id} not found."
        )

    # Returns the exact canonical analytics as the learner's own dashboard
    return PracticeAnalyticsService.get_dashboard_summary(db=db, current_user=target_learner)

@router.get("/instructor")
def get_instructor_dashboard(
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    total_students = db.query(User).filter(User.role == RoleEnum.LEARNER).count()
    avg_accuracy = db.query(func.avg(AssessmentAttempt.gesture_accuracy)).scalar()
    
    masteries = db.query(LearnerAlphabetState.sign_character, func.avg(LearnerAlphabetState.mastery_percentage)).group_by(LearnerAlphabetState.sign_character).all()
    mastery_summary = {char: round(float(avg_m), 1) for char, avg_m in masteries} if masteries else {}
    
    total_submissions = db.query(AssessmentAttempt).count()

    return {
        "total_students": total_students,
        "active_students_count": total_students,
        "average_class_accuracy": round(float(avg_accuracy), 1) if avg_accuracy is not None else None,
        "total_practice_submissions": total_submissions,
        "student_mastery_summary": mastery_summary
    }

@router.get("/trainer")
def get_trainer_dashboard(
    current_user: User = Depends(require_roles([RoleEnum.ACCESSIBILITY_TRAINER, RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    total_learners = db.query(User).filter(User.role == RoleEnum.LEARNER).count()
    struggling = db.query(LearnerProfile).filter(LearnerProfile.overall_performance_score < 60.0).count()
    
    weak_signs = db.query(
        LearnerAlphabetState.sign_character,
        func.avg(LearnerAlphabetState.mastery_percentage).label("avg_mastery")
    ).group_by(LearnerAlphabetState.sign_character).order_by(func.avg(LearnerAlphabetState.mastery_percentage).asc()).limit(5).all()
    
    weak_list = [{"sign": char, "average_mastery": round(float(m), 1)} for char, m in weak_signs] if weak_signs else []
    
    return {
        "total_learners": total_learners,
        "struggling_learners_count": struggling,
        "common_weak_signs": weak_list,
        "engagement_rate": round(float((total_learners - struggling) / max(1, total_learners) * 100.0), 1) if total_learners > 0 else None
    }

@router.get("/admin")
def get_admin_dashboard(
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    learner_count = db.query(User).filter(User.role == RoleEnum.LEARNER).count()
    trainer_count = db.query(User).filter(User.role == RoleEnum.ACCESSIBILITY_TRAINER).count()
    instructor_count = db.query(User).filter(User.role == RoleEnum.INSTRUCTOR).count()
    total_attempts = db.query(AssessmentAttempt).count()
    total_courses = db.query(Course).count()
    
    return {
        "learner_count": learner_count,
        "trainer_count": trainer_count,
        "instructor_count": instructor_count,
        "total_users": learner_count + trainer_count + instructor_count,
        "total_attempts": total_attempts,
        "total_courses": total_courses,
        "system_status": "Operational"
    }
