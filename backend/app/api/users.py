import os
import time
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import User, LearnerProfile, LearningGoal, RoleEnum
from app.schemas.dto import (
    UserProfileResponse, UserProfileUpdate,
    GoalCreate, GoalUpdate, GoalResponse
)
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/users", tags=["Users & Profiles"])

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "avatars")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def calculate_profile_completeness(user: User, learner_profile: Optional[LearnerProfile] = None) -> int:
    fields_checked = []
    
    # Common personal fields (8 points)
    fields_checked.append(bool(user.email))
    fields_checked.append(bool(user.full_name))
    fields_checked.append(bool(user.first_name))
    fields_checked.append(bool(user.last_name))
    fields_checked.append(bool(user.phone))
    fields_checked.append(bool(user.bio))
    fields_checked.append(bool(user.profile_photo_url))
    fields_checked.append(bool(user.preferred_language))
    
    # Role-specific fields
    if user.role == RoleEnum.LEARNER:
        fields_checked.append(bool(learner_profile and learner_profile.learning_level))
    elif user.role == RoleEnum.ACCESSIBILITY_TRAINER:
        fields_checked.append(bool(user.title))
        fields_checked.append(bool(user.specialization))
        fields_checked.append(bool(user.qualification))
        fields_checked.append(bool(user.experience_years))
    elif user.role == RoleEnum.INSTRUCTOR:
        fields_checked.append(bool(user.title))
        fields_checked.append(bool(user.department))
        fields_checked.append(bool(user.specialization))
        fields_checked.append(bool(user.qualification))
        fields_checked.append(bool(user.experience_years))
    elif user.role == RoleEnum.ADMINISTRATOR:
        fields_checked.append(bool(user.department))
        fields_checked.append(bool(user.designation))
        
    filled = sum(1 for f in fields_checked if f)
    total = len(fields_checked)
    if total == 0:
        return 100
    return int((filled / total) * 100)

def validate_image_file(file_bytes: bytes) -> str:
    """Validates file magic bytes and returns the confirmed extension."""
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed limit of 5MB."
        )
    if len(file_bytes) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted image file."
        )
    
    # Magic bytes check
    if file_bytes.startswith(b'\xff\xd8\xff'):
        return "jpg"
    elif file_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return "png"
    elif file_bytes[:4] == b'RIFF' and file_bytes[8:12] == b'WEBP':
        return "webp"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Allowed formats: JPG/JPEG, PNG, WebP."
        )

def build_profile_response(user: User, db: Session) -> UserProfileResponse:
    learner_profile = None
    learning_level = None
    if user.role == RoleEnum.LEARNER:
        learner_profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user.id).first()
        if not learner_profile:
            learner_profile = LearnerProfile(user_id=user.id)
            db.add(learner_profile)
            db.commit()
            db.refresh(learner_profile)
        learning_level = learner_profile.learning_level

    completeness = calculate_profile_completeness(user, learner_profile)

    return UserProfileResponse(
        id=user.id,
        uuid=user.uuid,
        email=user.email,
        full_name=user.full_name,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        bio=user.bio,
        profile_photo_url=user.profile_photo_url,
        preferred_language=user.preferred_language or "English",
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        learning_level=learning_level,
        title=user.title,
        specialization=user.specialization,
        qualification=user.qualification,
        experience_years=user.experience_years,
        department=user.department,
        designation=user.designation,
        completeness_percentage=completeness
    )

@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_profile_response(current_user, db)

@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Personal info
    if profile_in.first_name is not None:
        current_user.first_name = profile_in.first_name.strip()
    if profile_in.last_name is not None:
        current_user.last_name = profile_in.last_name.strip()
    if profile_in.full_name is not None and profile_in.full_name.strip():
        current_user.full_name = profile_in.full_name.strip()
    elif current_user.first_name or current_user.last_name:
        parts = [p for p in [current_user.first_name, current_user.last_name] if p]
        if parts:
            current_user.full_name = " ".join(parts)
            
    if profile_in.phone is not None:
        current_user.phone = profile_in.phone.strip()
    if profile_in.bio is not None:
        current_user.bio = profile_in.bio.strip()
    if profile_in.preferred_language is not None:
        current_user.preferred_language = profile_in.preferred_language.strip()

    # Role-specific fields
    if current_user.role == RoleEnum.LEARNER:
        learner_profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
        if not learner_profile:
            learner_profile = LearnerProfile(user_id=current_user.id)
            db.add(learner_profile)
        if profile_in.learning_level is not None:
            # Check if learning_level is already set
            if learner_profile.learning_level is not None and learner_profile.learning_level != profile_in.learning_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Learning level cannot be modified once set. Only an administrator can update your learning level."
                )
            learner_profile.learning_level = profile_in.learning_level
        if profile_in.preferred_language is not None:
            learner_profile.preferred_language = profile_in.preferred_language.strip()
    elif current_user.role in [RoleEnum.ACCESSIBILITY_TRAINER, RoleEnum.INSTRUCTOR]:
        if profile_in.title is not None:
            current_user.title = profile_in.title.strip()
        if profile_in.specialization is not None:
            current_user.specialization = profile_in.specialization.strip()
        if profile_in.qualification is not None:
            current_user.qualification = profile_in.qualification.strip()
        if profile_in.experience_years is not None:
            current_user.experience_years = profile_in.experience_years
        if current_user.role == RoleEnum.INSTRUCTOR and profile_in.department is not None:
            current_user.department = profile_in.department.strip()
    elif current_user.role == RoleEnum.ADMINISTRATOR:
        if profile_in.department is not None:
            current_user.department = profile_in.department.strip()
        if profile_in.designation is not None:
            current_user.designation = profile_in.designation.strip()

    db.commit()
    db.refresh(current_user)
    return build_profile_response(current_user, db)

@router.post("/profile/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    ext = validate_image_file(contents)

    # Clean up existing photo if present
    if current_user.profile_photo_url and current_user.profile_photo_url.startswith("/uploads/avatars/"):
        old_filename = os.path.basename(current_user.profile_photo_url)
        old_path = os.path.join(UPLOAD_DIR, old_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    # Save new photo
    filename = f"user_{current_user.id}_{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    photo_url = f"/uploads/avatars/{filename}"
    current_user.profile_photo_url = photo_url
    db.commit()
    db.refresh(current_user)

    return {
        "profile_photo_url": photo_url,
        "message": "Profile photo uploaded successfully."
    }

@router.delete("/profile/photo")
def delete_profile_photo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.profile_photo_url and current_user.profile_photo_url.startswith("/uploads/avatars/"):
        old_filename = os.path.basename(current_user.profile_photo_url)
        old_path = os.path.join(UPLOAD_DIR, old_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    current_user.profile_photo_url = None
    db.commit()
    db.refresh(current_user)

    return {
        "profile_photo_url": None,
        "message": "Profile photo removed successfully."
    }

@router.get("/goals", response_model=List[GoalResponse])
def get_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_profile(current_user=current_user, db=db)
    return db.query(LearningGoal).filter(LearningGoal.profile_id == profile.id).all()

@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = get_profile(current_user=current_user, db=db)
    goal = LearningGoal(
        profile_id=profile.id,
        goal_description=goal_in.goal_description,
        target_date=goal_in.target_date,
        is_completed=False
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_in: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = get_profile(current_user=current_user, db=db)
    goal = db.query(LearningGoal).filter(
        LearningGoal.id == goal_id,
        LearningGoal.profile_id == profile.id
    ).first()
    if not goal:
        raise NotFoundException(message="Learning goal not found.")
        
    if goal_in.goal_description is not None:
        goal.goal_description = goal_in.goal_description
    if goal_in.target_date is not None:
        goal.target_date = goal_in.target_date
    if goal_in.is_completed is not None:
        goal.is_completed = goal_in.is_completed
        
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = get_profile(current_user=current_user, db=db)
    goal = db.query(LearningGoal).filter(
        LearningGoal.id == goal_id,
        LearningGoal.profile_id == profile.id
    ).first()
    if not goal:
        raise NotFoundException(message="Learning goal not found.")
        
    db.delete(goal)
    db.commit()
    return None
