from sqlalchemy.orm import Session
from app.database.session import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.domain import (
    User, Role, UserRole, LearnerProfile, LearningLevelEnum, RoleEnum,
    Course, CourseModule, Lesson, Sign, LessonSign, LearnerAlphabetState, StateEnum
)

def init_db(db: Session):
    target_bind = db.get_bind() if hasattr(db, 'get_bind') and db.get_bind() is not None else engine
    Base.metadata.create_all(bind=target_bind)
    
    # Ensure profile columns exist in users table
    from sqlalchemy import text, inspect
    try:
        inspector = inspect(target_bind)
        existing_cols = [c["name"] for c in inspector.get_columns("users")] if "users" in inspector.get_table_names() else []
        profile_columns = [
            ("first_name", "VARCHAR"),
            ("last_name", "VARCHAR"),
            ("phone", "VARCHAR"),
            ("bio", "TEXT"),
            ("profile_photo_url", "VARCHAR"),
            ("preferred_language", "VARCHAR DEFAULT 'English'"),
            ("title", "VARCHAR"),
            ("specialization", "VARCHAR"),
            ("qualification", "VARCHAR"),
            ("experience_years", "INTEGER"),
            ("department", "VARCHAR"),
            ("designation", "VARCHAR"),
        ]
        for col_name, col_type in profile_columns:
            if col_name not in existing_cols:
                try:
                    db.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"))
                    db.commit()
                except Exception:
                    db.rollback()
    except Exception:
        pass
    
    # Check if database is already fully initialized
    admin_exists = db.query(User).filter(User.email == "admin@example.com").first()
    if admin_exists:
        return

    # 1. Seed Roles
    roles = [RoleEnum.LEARNER, RoleEnum.INSTRUCTOR, RoleEnum.ACCESSIBILITY_TRAINER, RoleEnum.ADMINISTRATOR]
    role_objs = {}
    for r_name in roles:
        r = db.query(Role).filter(Role.name == r_name.value).first()
        if not r:
            r = Role(name=r_name.value, description=f"{r_name.value} system role")
            db.add(r)
        role_objs[r_name.value] = r
    db.commit()

    for r_name in roles:
        r = db.query(Role).filter(Role.name == r_name.value).first()
        if r:
            role_objs[r_name.value] = r

    # 2. Seed Default Demo Users
    roles_users = [
        ("learner@example.com", "Alex Learner", RoleEnum.LEARNER, LearningLevelEnum.BEGINNER),
        ("instructor@example.com", "Prof. Sarah Jenkins", RoleEnum.INSTRUCTOR, LearningLevelEnum.EXPERT),
        ("trainer@example.com", "Marcus Trainer", RoleEnum.ACCESSIBILITY_TRAINER, LearningLevelEnum.EXPERT),
        ("admin@example.com", "Admin System", RoleEnum.ADMINISTRATOR, LearningLevelEnum.EXPERT),
    ]

    for email, name, role_enum, level in roles_users:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name=name,
                hashed_password=get_password_hash("password123"),
                role=role_enum,
                is_active=True
            )
            db.add(user)
            db.flush()

        r_obj = role_objs.get(role_enum.value)
        if r_obj:
            ur = db.query(UserRole).filter(UserRole.user_id == user.id, UserRole.role_id == r_obj.id).first()
            if not ur:
                ur = UserRole(user_id=user.id, role_id=r_obj.id)
                db.add(ur)

        profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user.id).first()
        if not profile:
            profile = LearnerProfile(
                user_id=user.id,
                learning_level=level,
                preferred_language="English",
                overall_performance_score=85.5 if role_enum == RoleEnum.LEARNER else 95.0,
                practice_streak_days=5 if role_enum == RoleEnum.LEARNER else 12,
                total_practice_time_mins=120 if role_enum == RoleEnum.LEARNER else 450
            )
            db.add(profile)

        if role_enum == RoleEnum.LEARNER:
            alphabet = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
            for char in alphabet:
                st = db.query(LearnerAlphabetState).filter(
                    LearnerAlphabetState.learner_id == user.id,
                    LearnerAlphabetState.sign_character == char
                ).first()
                if not st:
                    state_val = StateEnum.MASTERED if char in ['A', 'B', 'C'] else (StateEnum.LEARNING if char in ['D', 'E'] else StateEnum.NOT_ATTEMPTED)
                    acc_val = 92.0 if state_val == StateEnum.MASTERED else (65.0 if state_val == StateEnum.LEARNING else 0.0)
                    st = LearnerAlphabetState(
                        learner_id=user.id,
                        sign_character=char,
                        current_state=state_val,
                        total_attempts=5 if acc_val > 0 else 0,
                        successful_attempts=4 if acc_val > 80 else (1 if acc_val > 0 else 0),
                        average_accuracy=acc_val,
                        mastery_percentage=acc_val
                    )
                    db.add(st)
    db.commit()

    # 3. Seed Course, Course Module & Lessons A-Z
    asl_course = db.query(Course).filter(Course.title == "ASL Manual Alphabet").first()
    if not asl_course:
        asl_course = Course(
            title="ASL Manual Alphabet",
            category="Beginner Sign Language",
            description="Master all 26 letters of the American Sign Language manual alphabet through interactive webcam practice and real-time AI feedback.",
            level=LearningLevelEnum.BEGINNER
        )
        db.add(asl_course)
        db.flush()

        module = CourseModule(
            course_id=asl_course.id,
            title="Module 1: Alphabet Fundamentals (A - Z)",
            order_index=1
        )
        db.add(module)
        db.flush()

        alphabet = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        for idx, char in enumerate(alphabet, start=1):
            sign_obj = db.query(Sign).filter(Sign.character == char).first()
            if not sign_obj:
                sign_obj = Sign(
                    character=char,
                    description=f"ASL manual sign for letter '{char}'",
                    difficulty="Easy" if idx <= 10 else "Medium"
                )
                db.add(sign_obj)
                db.flush()

            lesson = db.query(Lesson).filter(Lesson.sign_character == char).first()
            if not lesson:
                lesson = Lesson(
                    module_id=module.id,
                    title=f"Sign '{char}' - ASL Letter",
                    sign_character=char,
                    description=f"Learn how to form and hold the ASL sign for letter '{char}'.",
                    tips=f"Keep palm facing forward towards the camera. Position thumb correctly for '{char}'.",
                    reference_image_url=f"/assets/asl/{char.lower()}.png",
                    order_index=idx
                )
                db.add(lesson)
                db.flush()

                ls = LessonSign(lesson_id=lesson.id, sign_id=sign_obj.id)
                db.add(ls)
        db.commit()

    # 4. Seed 26 Global Alphabet Achievements (A - Z)
    from app.models.domain import AchievementDefinition
    alphabet = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    for idx, char in enumerate(alphabet, start=1):
        ach = db.query(AchievementDefinition).filter(AchievementDefinition.sign == char).first()
        if not ach:
            ach = AchievementDefinition(
                sign=char,
                title=f"Master of {char}",
                description=f"Mastered the ASL manual sign for letter '{char}'.",
                icon="🏆",
                display_order=idx
            )
            db.add(ach)
    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    print("Database entities initialized and seeded successfully!")
