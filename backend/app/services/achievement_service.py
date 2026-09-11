from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.domain import (
    User, AchievementDefinition, AchievementUnlock,
    Notification, StateEnum
)
from app.services.practice_analytics_service import PracticeAnalyticsService

ALL_ALPHABET_SIGNS = [chr(i) for i in range(ord('A'), ord('Z') + 1)]

class AchievementService:
    """
    Authoritative Achievement Service for ASL Alphabet Mastery.
    Directly consumes canonical sign analytics from PracticeAnalyticsService.
    Guarantees:
    - 26 static alphabet achievement definitions (A to Z).
    - Event-driven and query-time synchronization with canonical mastery.
    - Permanent unlock persistence (Mastered -> Revision maintains unlocked status).
    - Strict user data isolation.
    """

    @staticmethod
    def ensure_achievement_definitions(db: Session) -> List[AchievementDefinition]:
        """Ensures all 26 alphabet achievement definitions exist in the database."""
        existing = db.query(AchievementDefinition).order_by(AchievementDefinition.display_order.asc()).all()
        if len(existing) == 26:
            return existing

        existing_signs = {a.sign for a in existing}
        for idx, char in enumerate(ALL_ALPHABET_SIGNS, start=1):
            if char not in existing_signs:
                new_def = AchievementDefinition(
                    sign=char,
                    title=f"Master of {char}",
                    description=f"You mastered the ASL sign for letter '{char}'.",
                    icon="🏆",
                    display_order=idx
                )
                db.add(new_def)
        db.commit()
        return db.query(AchievementDefinition).order_by(AchievementDefinition.display_order.asc()).all()

    @staticmethod
    def get_user_achievements(db: Session, current_user: User) -> Dict[str, Any]:
        """
        Retrieves the 26 alphabet achievements for the authenticated user.
        Consumes canonical PracticeAnalyticsService summary to synchronize mastery.
        """
        definitions = AchievementService.ensure_achievement_definitions(db)
        def_by_sign = {d.sign: d for d in definitions}

        # 1. Fetch user's existing unlock records
        unlock_rows = db.query(AchievementUnlock).filter(
            AchievementUnlock.user_id == current_user.id
        ).all()
        unlock_map = {u.sign: u for u in unlock_rows}

        # 2. Fetch canonical dashboard summary from PracticeAnalyticsService
        canonical_summary = PracticeAnalyticsService.get_dashboard_summary(db=db, current_user=current_user)
        sign_class_map = {s["sign"]: s for s in canonical_summary["sign_classification"]}

        # 3. Synchronize new Mastered signs to unlocks
        new_unlocks_added = False
        for char in ALL_ALPHABET_SIGNS:
            stat = sign_class_map.get(char, {})
            is_mastered = stat.get("category") == "Mastered"

            if is_mastered and char not in unlock_map and char in def_by_sign:
                def_obj = def_by_sign[char]
                try:
                    new_unlock = AchievementUnlock(
                        user_id=current_user.id,
                        achievement_id=def_obj.id,
                        sign=char,
                        unlocked_at=datetime.utcnow()
                    )
                    db.add(new_unlock)
                    
                    # Private learner notification
                    notif = Notification(
                        user_id=current_user.id,
                        title="🏆 Achievement Unlocked!",
                        message=f"Congratulations! You mastered the ASL sign for letter '{char}' and unlocked the 'Master of {char}' achievement.",
                        type="achievement"
                    )
                    db.add(notif)
                    db.commit()
                    db.refresh(new_unlock)
                    unlock_map[char] = new_unlock
                    new_unlocks_added = True
                except IntegrityError:
                    db.rollback()
                    existing_unlock = db.query(AchievementUnlock).filter(
                        AchievementUnlock.user_id == current_user.id,
                        AchievementUnlock.achievement_id == def_obj.id
                    ).first()
                    if existing_unlock:
                        unlock_map[char] = existing_unlock

        # 4. Construct response with 26 achievements
        achievements_list = []
        for def_obj in definitions:
            char = def_obj.sign
            unlock_record = unlock_map.get(char)
            stat = sign_class_map.get(char, {})
            is_unlocked = unlock_record is not None
            current_category = stat.get("category", "Not Attempted")

            achievements_list.append({
                "id": def_obj.id,
                "sign": char,
                "title": def_obj.title,
                "description": def_obj.description,
                "icon": def_obj.icon,
                "display_order": def_obj.display_order,
                "is_unlocked": is_unlocked,
                "unlocked_at": unlock_record.unlocked_at.isoformat() if unlock_record else None,
                "current_category": current_category,
                "accuracy": stat.get("accuracy", 0.0),
                "total_attempts": stat.get("total_attempts", 0),
                "average_confidence": stat.get("average_confidence", 0.0)
            })

        unlocked_count = len(unlock_map)
        locked_count = 26 - unlocked_count
        mastered_current_count = len([
            s for s in canonical_summary["sign_classification"] 
            if s["sign"] in ALL_ALPHABET_SIGNS and s["category"] == "Mastered"
        ])
        completion_percentage = round((unlocked_count / 26.0) * 100.0, 2)

        return {
            "total": 26,
            "unlocked_count": unlocked_count,
            "locked_count": locked_count,
            "mastered_signs_count": mastered_current_count,
            "completion_percentage": completion_percentage,
            "achievements": achievements_list
        }

    @staticmethod
    def check_and_unlock_for_attempt(db: Session, learner_id: int, expected_sign: str) -> Optional[Dict[str, Any]]:
        """
        Event-driven trigger called immediately upon practice attempt completion.
        If the sign is now Mastered and not yet unlocked, persists AchievementUnlock.
        """
        clean_sign = (expected_sign or "").strip().upper()
        if clean_sign not in ALL_ALPHABET_SIGNS:
            return None

        learner = db.query(User).filter(User.id == learner_id).first()
        if not learner:
            return None

        def_obj = db.query(AchievementDefinition).filter(AchievementDefinition.sign == clean_sign).first()
        if not def_obj:
            AchievementService.ensure_achievement_definitions(db)
            def_obj = db.query(AchievementDefinition).filter(AchievementDefinition.sign == clean_sign).first()

        if not def_obj:
            return None

        # Check if already unlocked
        existing = db.query(AchievementUnlock).filter(
            AchievementUnlock.user_id == learner_id,
            AchievementUnlock.achievement_id == def_obj.id
        ).first()
        if existing:
            return None

        # Check canonical mastery
        canonical_summary = PracticeAnalyticsService.get_dashboard_summary(db=db, current_user=learner)
        sign_stat = next((s for s in canonical_summary["sign_classification"] if s["sign"] == clean_sign), None)
        if sign_stat and sign_stat["category"] == "Mastered":
            try:
                new_unlock = AchievementUnlock(
                    user_id=learner_id,
                    achievement_id=def_obj.id,
                    sign=clean_sign,
                    unlocked_at=datetime.utcnow()
                )
                db.add(new_unlock)

                # Add private notification
                notif = Notification(
                    user_id=learner_id,
                    title="🏆 Achievement Unlocked!",
                    message=f"Congratulations! You mastered the ASL sign for letter '{clean_sign}' and unlocked the 'Master of {clean_sign}' achievement.",
                    type="achievement"
                )
                db.add(notif)
                db.commit()
                db.refresh(new_unlock)
                return {
                    "unlocked": True,
                    "sign": clean_sign,
                    "title": def_obj.title,
                    "unlocked_at": new_unlock.unlocked_at.isoformat()
                }
            except IntegrityError:
                db.rollback()
                return None

        return None
