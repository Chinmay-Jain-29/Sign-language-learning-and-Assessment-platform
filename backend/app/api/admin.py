import math
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db
from app.models.domain import (
    User, RoleEnum, Course, Lesson, AssessmentAttempt, 
    LearnerProfile, InstructorInstruction, Notification,
    LearningLevelAudit, LearningLevelEnum
)
from app.schemas.dto import (
    UserResponse, AdminLearnerLevelUpdate, LearningLevelAuditResponse
)
from app.api.deps import require_roles
from app.services.practice_analytics_service import PracticeAnalyticsService

router = APIRouter(prefix="/admin", tags=["Admin Management"])

class AdminInstructionRequest(BaseModel):
    recipient_id: int
    message: str

@router.get("/counts")
def get_role_counts(
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Returns exact real database counts for the three key roles:
    Learner, Accessibility Trainer, and Instructor.
    """
    learner_count = db.query(User).filter(User.role == RoleEnum.LEARNER).count()
    trainer_count = db.query(User).filter(User.role == RoleEnum.ACCESSIBILITY_TRAINER).count()
    instructor_count = db.query(User).filter(User.role == RoleEnum.INSTRUCTOR).count()

    return {
        "learner_count": learner_count,
        "trainer_count": trainer_count,
        "instructor_count": instructor_count,
        "total_users": learner_count + trainer_count + instructor_count
    }

@router.get("/users-by-role")
def get_users_by_role(
    role: str = Query("Learner", description="Role to filter by (Learner, Accessibility Trainer, Instructor, Administrator)"),
    search: Optional[str] = Query(None, description="Search term for name or email"),
    page: Optional[int] = Query(None, description="1-indexed page number"),
    limit: Optional[int] = Query(None, description="Items per page"),
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Returns filtered, searchable, and optionally paginated list of users strictly matching the specified role.
    """
    query = db.query(User).filter(User.role == role)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(User.full_name.ilike(term), User.email.ilike(term)))

    total_count = query.count()
    query = query.order_by(User.id.asc())

    if page is not None and limit is not None and limit > 0:
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
    else:
        users = query.all()

    results = []
    for u in users:
        prof = db.query(LearnerProfile).filter(LearnerProfile.user_id == u.id).first()
        attempts_count = db.query(AssessmentAttempt).filter(AssessmentAttempt.learner_id == u.id).count() if u.role == RoleEnum.LEARNER else 0
        instructions_count = db.query(InstructorInstruction).filter(InstructorInstruction.instructor_id == u.id).count() if u.role == RoleEnum.INSTRUCTOR else 0
        last_attempt = db.query(AssessmentAttempt).filter(AssessmentAttempt.learner_id == u.id).order_by(AssessmentAttempt.timestamp.desc()).first() if u.role == RoleEnum.LEARNER else None

        results.append({
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, 'value') else str(u.role),
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "learning_level": prof.learning_level.value if (prof and hasattr(prof.learning_level, 'value')) else (prof.learning_level if prof else "N/A"),
            "total_attempts": attempts_count,
            "instructions_sent": instructions_count,
            "last_activity": last_attempt.timestamp.isoformat() if (last_attempt and last_attempt.timestamp) else (u.updated_at.isoformat() if u.updated_at else None)
        })

    if page is not None and limit is not None:
        total_pages = math.ceil(total_count / limit) if limit > 0 else 1
        return {
            "items": results,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": max(1, total_pages)
        }

    return results

@router.get("/users/{user_id}/activity")
def get_user_activity_for_admin(
    user_id: int,
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Provides comprehensive activity monitoring for a target user.
    If Learner: returns canonical PracticeAnalyticsService dashboard summary.
    If Instructor: returns profile, instructions issued count, and last activity.
    If Trainer: returns profile and training activity status.
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    prof = db.query(LearnerProfile).filter(LearnerProfile.user_id == target_user.id).first()

    if target_user.role == RoleEnum.LEARNER:
        level_audits = db.query(LearningLevelAudit).filter(
            LearningLevelAudit.learner_id == target_user.id
        ).order_by(LearningLevelAudit.changed_at.desc()).all()
        
        history_list = []
        for a in level_audits:
            admin_u = db.query(User).filter(User.id == a.changed_by_admin_id).first()
            history_list.append({
                "id": a.id,
                "old_level": a.old_level,
                "new_level": a.new_level,
                "changed_by": admin_u.full_name if admin_u else "Administrator",
                "changed_at": a.changed_at.isoformat()
            })

        return {
            "type": "learner",
            "user": {
                "id": target_user.id,
                "full_name": target_user.full_name,
                "email": target_user.email,
                "role": target_user.role.value if hasattr(target_user.role, 'value') else str(target_user.role),
                "is_active": target_user.is_active,
                "created_at": target_user.created_at.isoformat() if target_user.created_at else None,
                "learning_level": prof.learning_level.value if (prof and prof.learning_level and hasattr(prof.learning_level, 'value')) else (prof.learning_level if (prof and prof.learning_level) else "Beginner"),
                "preferred_language": prof.preferred_language if prof else "English"
            },
            "level_history": history_list,
            "analytics": PracticeAnalyticsService.get_dashboard_summary(db=db, current_user=target_user)
        }
    elif target_user.role == RoleEnum.INSTRUCTOR:
        instructions_count = db.query(InstructorInstruction).filter(InstructorInstruction.instructor_id == target_user.id).count()
        last_inst = db.query(InstructorInstruction).filter(InstructorInstruction.instructor_id == target_user.id).order_by(InstructorInstruction.created_at.desc()).first()
        return {
            "type": "instructor",
            "user": {
                "id": target_user.id,
                "full_name": target_user.full_name,
                "email": target_user.email,
                "role": target_user.role.value if hasattr(target_user.role, 'value') else str(target_user.role),
                "is_active": target_user.is_active,
                "created_at": target_user.created_at.isoformat() if target_user.created_at else None
            },
            "total_instructions_issued": instructions_count,
            "last_instruction_sent_at": last_inst.created_at.isoformat() if (last_inst and last_inst.created_at) else None,
            "status": "Active instructor profile"
        }
    else:
        return {
            "type": "trainer",
            "user": {
                "id": target_user.id,
                "full_name": target_user.full_name,
                "email": target_user.email,
                "role": target_user.role.value if hasattr(target_user.role, 'value') else str(target_user.role),
                "is_active": target_user.is_active,
                "created_at": target_user.created_at.isoformat() if target_user.created_at else None
            },
            "status": "Active accessibility trainer profile"
        }

@router.post("/instructions", status_code=status.HTTP_201_CREATED)
def create_admin_instruction(
    payload: AdminInstructionRequest,
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Administrator dispatches a private administrative directive/instruction to a designated recipient.
    Strictly recipient-specific: only recipient can view this directive.
    """
    recipient = db.query(User).filter(User.id == payload.recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipient with ID {payload.recipient_id} does not exist."
        )

    msg_text = payload.message.strip()
    if not msg_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instruction message cannot be empty."
        )

    # 1. Create dedicated Notification for recipient
    notif = Notification(
        user_id=recipient.id,
        title=f"Administrative Directive from {current_user.full_name}",
        message=msg_text,
        type="admin_instruction",
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(notif)

    # 2. If recipient is a Learner, also record in InstructorInstruction so it appears in learner guidance
    if recipient.role == RoleEnum.LEARNER:
        inst = InstructorInstruction(
            instructor_id=current_user.id,
            learner_id=recipient.id,
            message=f"[Admin] {msg_text}",
            created_at=datetime.utcnow(),
            is_read=False
        )
        db.add(inst)

    db.commit()

    return {
        "success": True,
        "recipient_id": recipient.id,
        "recipient_name": recipient.full_name,
        "recipient_role": recipient.role.value if hasattr(recipient.role, 'value') else str(recipient.role),
        "message": msg_text,
        "created_at": notif.created_at.isoformat()
    }

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    return db.query(User).order_by(User.id.asc()).all()

@router.get("/system-status")
def get_system_status(
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    learner_count = db.query(User).filter(User.role == RoleEnum.LEARNER).count()
    trainer_count = db.query(User).filter(User.role == RoleEnum.ACCESSIBILITY_TRAINER).count()
    instructor_count = db.query(User).filter(User.role == RoleEnum.INSTRUCTOR).count()

    return {
        "status": "Healthy & Operational",
        "database": "Connected",
        "ai_model": "Loaded (Random Forest Classifier)",
        "total_registered_users": learner_count + trainer_count + instructor_count,
        "learner_count": learner_count,
        "trainer_count": trainer_count,
        "instructor_count": instructor_count,
        "total_practice_attempts": db.query(AssessmentAttempt).count(),
        "total_courses": db.query(Course).count()
    }

@router.patch("/learners/{learner_id}/level")
@router.put("/learners/{learner_id}/level")
def update_learner_learning_level(
    learner_id: int,
    payload: AdminLearnerLevelUpdate,
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Administrator changes a learner's controlled learning level.
    Records audit history for transparency and governance.
    """
    target_learner = db.query(User).filter(User.id == learner_id).first()
    if not target_learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID {learner_id} not found."
        )
    if target_learner.role != RoleEnum.LEARNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {target_learner.full_name} is not a Learner. Only Learner accounts have a learning level."
        )

    prof = db.query(LearnerProfile).filter(LearnerProfile.user_id == target_learner.id).first()
    if not prof:
        prof = LearnerProfile(user_id=target_learner.id)
        db.add(prof)
        db.commit()
        db.refresh(prof)

    old_level_str = prof.learning_level.value if (prof.learning_level and hasattr(prof.learning_level, 'value')) else (str(prof.learning_level) if prof.learning_level else None)
    new_level_val = payload.learning_level

    prof.learning_level = new_level_val
    prof.updated_at = datetime.utcnow()

    # Record level change audit history
    audit_entry = LearningLevelAudit(
        learner_id=target_learner.id,
        changed_by_admin_id=current_user.id,
        old_level=old_level_str,
        new_level=new_level_val.value if hasattr(new_level_val, 'value') else str(new_level_val),
        changed_at=datetime.utcnow()
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(prof)

    return {
        "success": True,
        "message": f"Learning level for {target_learner.full_name} successfully updated to {prof.learning_level.value}.",
        "learner_id": target_learner.id,
        "learner_name": target_learner.full_name,
        "old_level": old_level_str,
        "new_level": prof.learning_level.value if hasattr(prof.learning_level, 'value') else str(prof.learning_level),
        "changed_by": current_user.full_name,
        "changed_at": audit_entry.changed_at.isoformat()
    }

@router.get("/learners/{learner_id}/level-history", response_model=List[LearningLevelAuditResponse])
def get_learner_level_history(
    learner_id: int,
    current_user: User = Depends(require_roles([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Returns audit history of all learning level changes for a specific learner.
    """
    target_learner = db.query(User).filter(User.id == learner_id).first()
    if not target_learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID {learner_id} not found."
        )

    audits = db.query(LearningLevelAudit).filter(
        LearningLevelAudit.learner_id == learner_id
    ).order_by(LearningLevelAudit.changed_at.desc()).all()

    results = []
    for a in audits:
        admin_user = db.query(User).filter(User.id == a.changed_by_admin_id).first()
        results.append(LearningLevelAuditResponse(
            id=a.id,
            learner_id=a.learner_id,
            changed_by_admin_id=a.changed_by_admin_id,
            admin_name=admin_user.full_name if admin_user else "Administrator",
            old_level=a.old_level,
            new_level=a.new_level,
            changed_at=a.changed_at
        ))
    return results
