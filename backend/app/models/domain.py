import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON, Table, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class RoleEnum(str, enum.Enum):
    LEARNER = "Learner"
    INSTRUCTOR = "Instructor"
    ACCESSIBILITY_TRAINER = "Accessibility Trainer"
    ADMINISTRATOR = "Administrator"

class LearningLevelEnum(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"
    ADVANCED = "Expert"
    PROFESSIONAL = "Expert"

class StateEnum(str, enum.Enum):
    NOT_ATTEMPTED = "Not Attempted"
    LEARNING = "Learning"
    IMPROVING = "Improving"
    MASTERED = "Mastered"
    NEEDS_REVISION = "Needs Revision"

# 1. User Entity
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.LEARNER, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Personal Profile Attributes
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    profile_photo_url = Column(String, nullable=True)
    preferred_language = Column(String, default="English", nullable=True)
    
    # Role-Specific Professional Attributes
    title = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    qualification = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)

    profile = relationship("LearnerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeSession", back_populates="learner", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="learner", cascade="all, delete-orphan")
    alphabet_states = relationship("LearnerAlphabetState", back_populates="learner", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="learner", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    sent_instructions = relationship("InstructorInstruction", foreign_keys="[InstructorInstruction.instructor_id]", back_populates="instructor", cascade="all, delete-orphan")
    received_instructions = relationship("InstructorInstruction", foreign_keys="[InstructorInstruction.learner_id]", back_populates="learner", cascade="all, delete-orphan")
    achievement_unlocks = relationship("AchievementUnlock", back_populates="user", cascade="all, delete-orphan")
    level_audits = relationship("LearningLevelAudit", foreign_keys="[LearningLevelAudit.learner_id]", back_populates="learner", cascade="all, delete-orphan")

# RefreshToken Entity
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

# PasswordResetToken Entity
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reset_tokens")

# 2. Role Entity
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    user_roles = relationship("UserRole", back_populates="role")

# 3. UserRole Entity
class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

# 4. LearnerProfile Entity
class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    learning_level = Column(SQLEnum(LearningLevelEnum), nullable=True, default=None)
    preferred_language = Column(String, default="English")
    overall_performance_score = Column(Float, default=0.0)
    practice_streak_days = Column(Integer, default=0)
    total_practice_time_mins = Column(Integer, default=0)
    last_practice_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")
    goals = relationship("LearningGoal", back_populates="profile", cascade="all, delete-orphan")

# LearningLevelAudit Entity
class LearningLevelAudit(Base):
    __tablename__ = "learning_level_audits"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    changed_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    old_level = Column(String, nullable=True)
    new_level = Column(String, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    learner = relationship("User", foreign_keys=[learner_id], back_populates="level_audits")
    admin = relationship("User", foreign_keys=[changed_by_admin_id])

# 5. LearningGoal Entity
class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("learner_profiles.id"), nullable=False, index=True)
    goal_description = Column(Text, nullable=False)
    target_date = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)

    profile = relationship("LearnerProfile", back_populates="goals")

# 6. Course Entity
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    level = Column(SQLEnum(LearningLevelEnum), default=LearningLevelEnum.BEGINNER)
    created_at = Column(DateTime, default=datetime.utcnow)

    modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan")

# 7. CourseModule Entity
class CourseModule(Base):
    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    order_index = Column(Integer, default=1)

    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

# 8. Lesson Entity
class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("course_modules.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    sign_character = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    tips = Column(Text, nullable=True)
    reference_image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    order_index = Column(Integer, default=1)

    module = relationship("CourseModule", back_populates="lessons")
    lesson_signs = relationship("LessonSign", back_populates="lesson", cascade="all, delete-orphan")

# 9. Sign Entity
class Sign(Base):
    __tablename__ = "signs"

    id = Column(Integer, primary_key=True, index=True)
    character = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, default="Easy")
    landmark_template = Column(JSON, nullable=True)

    lesson_signs = relationship("LessonSign", back_populates="sign")

# 10. LessonSign Entity
class LessonSign(Base):
    __tablename__ = "lesson_signs"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    sign_id = Column(Integer, ForeignKey("signs.id"), nullable=False, index=True)

    lesson = relationship("Lesson", back_populates="lesson_signs")
    sign = relationship("Sign", back_populates="lesson_signs")

# 11. PracticeSession Entity
class PracticeSession(Base):
    __tablename__ = "practice_sessions"
    __table_args__ = (
        Index("ix_practice_sessions_learner_start", "learner_id", "start_time"),
    )

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, default=generate_uuid, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    selected_signs = Column(JSON, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, index=True)
    end_time = Column(DateTime, nullable=True)
    total_attempts = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    average_accuracy = Column(Float, default=0.0)
    average_confidence = Column(Float, default=0.0)
    status = Column(String, default="active")

    learner = relationship("User", back_populates="practice_sessions")
    attempts = relationship("AssessmentAttempt", back_populates="session", cascade="all, delete-orphan")

# 12. AssessmentAttempt Entity
class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"
    __table_args__ = (
        Index("ix_attempts_learner_timestamp", "learner_id", "timestamp"),
        Index("ix_attempts_learner_expected", "learner_id", "expected_sign"),
        Index("ix_attempts_session_id", "session_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=True, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    expected_sign = Column(String, nullable=False, index=True)
    predicted_sign = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    gesture_accuracy = Column(Float, nullable=False)
    hand_shape_accuracy = Column(Float, nullable=False)
    motion_accuracy = Column(Float, nullable=False)
    position_accuracy = Column(Float, nullable=False)
    timing_score = Column(Float, default=100.0)
    stability_score = Column(Float, default=100.0)
    invalid_frame_count = Column(Integer, default=0)
    inference_time = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    model_version = Column(String, default="v1.0.0")
    feedback_id = Column(Integer, ForeignKey("feedback.id"), nullable=True)

    learner = relationship("User", back_populates="assessment_attempts")
    session = relationship("PracticeSession", back_populates="attempts")
    feedback_obj = relationship("Feedback", back_populates="attempts")
    predictions = relationship("Prediction", back_populates="attempt", cascade="all, delete-orphan")

# 13. Prediction Entity
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("assessment_attempts.id"), nullable=False, index=True)
    predicted_gesture = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    raw_probabilities = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    attempt = relationship("AssessmentAttempt", back_populates="predictions")

# 14. Feedback Entity
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    feedback_text = Column(Text, nullable=False)
    correction_suggestion = Column(Text, nullable=False)
    error_category = Column(String, default="Hand Shape")

    attempts = relationship("AssessmentAttempt", back_populates="feedback_obj")

# 15. LearnerAlphabetState Entity
class LearnerAlphabetState(Base):
    __tablename__ = "learner_alphabet_states"
    __table_args__ = (
        Index("ix_alphabet_learner_sign", "learner_id", "sign_character"),
    )

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sign_character = Column(String, nullable=False, index=True)
    current_state = Column(SQLEnum(StateEnum), default=StateEnum.NOT_ATTEMPTED)
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    consecutive_correct = Column(Integer, default=0)
    consecutive_incorrect = Column(Integer, default=0)
    average_accuracy = Column(Float, default=0.0)
    average_confidence = Column(Float, default=0.0)
    mastery_percentage = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    learner = relationship("User", back_populates="alphabet_states")
    history = relationship("LearnerStateHistory", back_populates="state_obj", cascade="all, delete-orphan")

# 16. LearnerStateHistory Entity
class LearnerStateHistory(Base):
    __tablename__ = "learner_state_history"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("learner_alphabet_states.id"), nullable=False)
    previous_state = Column(SQLEnum(StateEnum), nullable=False)
    new_state = Column(SQLEnum(StateEnum), nullable=False)
    accuracy_score = Column(Float, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)

    state_obj = relationship("LearnerAlphabetState", back_populates="history")

# 17. Recommendation Entity
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommended_sign = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    priority = Column(Integer, default=1)
    current_mastery = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    learner = relationship("User", back_populates="recommendations")

# 18. AnalyticsSnapshot Entity
class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    total_users = Column(Integer, default=0)
    active_users_count = Column(Integer, default=0)
    total_practice_sessions = Column(Integer, default=0)
    average_platform_accuracy = Column(Float, default=0.0)

# 19. ProgressRecord Entity
class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_number = Column(Integer, nullable=False)
    accuracy_percentage = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

# 20. Certification Entity
class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level = Column(SQLEnum(LearningLevelEnum), default=LearningLevelEnum.BEGINNER)
    title = Column(String, nullable=False)
    certificate_code = Column(String, unique=True, index=True, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="certifications")
    attempts = relationship("CertificationAttempt", back_populates="certification", cascade="all, delete-orphan")

# 21. CertificationAttempt Entity
class CertificationAttempt(Base):
    __tablename__ = "certification_attempts"

    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)

    certification = relationship("Certification", back_populates="attempts")

# 22. Notification Entity
class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, default="info")
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="notifications")

# 23. AuditLog Entity
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")

# 24. InstructorInstruction Entity
class InstructorInstruction(Base):
    __tablename__ = "instructor_instructions"
    __table_args__ = (
        Index("ix_instruction_learner_read", "learner_id", "is_read"),
    )

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False, index=True)

    instructor = relationship("User", foreign_keys=[instructor_id], back_populates="sent_instructions")
    learner = relationship("User", foreign_keys=[learner_id], back_populates="received_instructions")

# 25. AchievementDefinition Entity
class AchievementDefinition(Base):
    __tablename__ = "achievement_definitions"

    id = Column(Integer, primary_key=True, index=True)
    sign = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, default="🏆")
    display_order = Column(Integer, default=1, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    unlocks = relationship("AchievementUnlock", back_populates="achievement", cascade="all, delete-orphan")

# 26. AchievementUnlock Entity
class AchievementUnlock(Base):
    __tablename__ = "achievement_unlocks"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
        Index("ix_achievement_user_sign", "user_id", "sign"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievement_definitions.id"), nullable=False, index=True)
    sign = Column(String, nullable=False, index=True)
    unlocked_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="achievement_unlocks")
    achievement = relationship("AchievementDefinition", back_populates="unlocks")
