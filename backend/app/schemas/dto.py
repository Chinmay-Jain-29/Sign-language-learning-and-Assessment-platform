from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr
from app.models.domain import RoleEnum, LearningLevelEnum

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Optional[RoleEnum] = RoleEnum.LEARNER
    preferred_language: Optional[str] = "English"
    learning_level: Optional[LearningLevelEnum] = LearningLevelEnum.BEGINNER

class UserLogin(BaseModel):
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str
    role: Optional[RoleEnum] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    role: RoleEnum

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    uuid: str
    email: str
    full_name: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class GoalCreate(BaseModel):
    goal_description: str
    target_date: Optional[datetime] = None

class GoalUpdate(BaseModel):
    goal_description: Optional[str] = None
    target_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

class GoalResponse(BaseModel):
    id: int
    profile_id: int
    goal_description: str
    target_date: Optional[datetime] = None
    is_completed: bool

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    learning_level: Optional[LearningLevelEnum] = None
    preferred_language: Optional[str] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    learning_level: Optional[LearningLevelEnum] = None
    preferred_language: str
    overall_performance_score: float
    practice_streak_days: int
    total_practice_time_mins: int
    last_practice_at: Optional[datetime] = None
    goals: List[GoalResponse] = []

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    preferred_language: Optional[str] = None
    
    # Role-specific fields
    learning_level: Optional[LearningLevelEnum] = None
    title: Optional[str] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    department: Optional[str] = None
    designation: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    uuid: str
    email: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    preferred_language: Optional[str] = "English"
    role: RoleEnum
    is_active: bool
    created_at: datetime
    
    # Role-specific fields
    learning_level: Optional[LearningLevelEnum] = None
    title: Optional[str] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    
    completeness_percentage: int = 100

    class Config:
        from_attributes = True

class LessonCreate(BaseModel):
    module_id: Optional[int] = None
    title: str
    sign_character: str
    description: str
    tips: Optional[str] = None
    reference_image_url: Optional[str] = None
    video_url: Optional[str] = None
    order_index: Optional[int] = 1

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    sign_character: Optional[str] = None
    description: Optional[str] = None
    tips: Optional[str] = None
    reference_image_url: Optional[str] = None
    video_url: Optional[str] = None
    order_index: Optional[int] = None

class LessonResponse(BaseModel):
    id: int
    module_id: Optional[int] = None
    title: str
    sign_character: str
    description: str
    tips: Optional[str] = None
    reference_image_url: Optional[str] = None
    video_url: Optional[str] = None
    order_index: int

    class Config:
        from_attributes = True

class CourseModuleResponse(BaseModel):
    id: int
    course_id: int
    title: str
    order_index: int
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True

class CourseResponse(BaseModel):
    id: int
    title: str
    category: str
    description: str
    level: LearningLevelEnum
    modules: List[CourseModuleResponse] = []

    class Config:
        from_attributes = True

class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float

class AttemptCreate(BaseModel):
    expected_sign: str
    predicted_sign: Optional[str] = None
    confidence: Optional[float] = None
    is_correct: Optional[bool] = None
    gesture_accuracy: Optional[float] = None
    feedback: Optional[str] = None
    landmarks: Optional[List[LandmarkPoint]] = None

class AttemptResponse(BaseModel):
    id: int
    expected_sign: str
    predicted_sign: str
    confidence: float
    gesture_accuracy: float
    hand_shape_accuracy: float
    position_accuracy: float
    motion_accuracy: float
    timestamp: datetime

    class Config:
        from_attributes = True

class AdminLearnerLevelUpdate(BaseModel):
    learning_level: LearningLevelEnum

class LearningLevelAuditResponse(BaseModel):
    id: int
    learner_id: int
    changed_by_admin_id: int
    admin_name: Optional[str] = None
    old_level: Optional[str] = None
    new_level: str
    changed_at: datetime

    class Config:
        from_attributes = True
