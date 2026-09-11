from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.domain import LearnerAlphabetState, Recommendation, StateEnum, Lesson

def generate_adaptive_recommendation(db: Session, learner_id: int) -> Dict[str, Any]:
    """
    Data-driven adaptive recommendation engine:
    1. Highest Priority: Signs in NEEDS_REVISION state.
    2. High Priority: Signs with consecutive_incorrect >= 1 (frequent mistakes).
    3. Medium Priority: Active signs (LEARNING / IMPROVING) with lowest mastery percentage.
    4. Unattempted Priority: Next unattempted alphabet letter.
    5. Maintenance Priority: Mastered signs review.
    """
    states = db.query(LearnerAlphabetState).filter(LearnerAlphabetState.learner_id == learner_id).all()

    if not states:
        first_lesson = db.query(Lesson).order_by(Lesson.order_index.asc()).first()
        rec_sign = first_lesson.sign_character if first_lesson else "A"
        reason = "Welcome! Start your sign language journey with the foundational letter 'A'."
        return _persist_recommendation(db, learner_id, rec_sign, reason, priority=1, mastery=0.0)

    # 1. Check for NEEDS_REVISION signs
    revision_signs = [s for s in states if s.current_state == StateEnum.NEEDS_REVISION]
    if revision_signs:
        target = sorted(revision_signs, key=lambda x: x.mastery_percentage)[0]
        reason = f"Sign '{target.sign_character}' needs revision because recent accuracy dropped to {target.average_accuracy:.1f}%. Practice to restore mastery!"
        return _persist_recommendation(db, learner_id, target.sign_character, reason, priority=1, mastery=target.mastery_percentage)

    # 2. Check for signs with consecutive errors (>= 1)
    error_signs = [s for s in states if s.consecutive_incorrect >= 1]
    if error_signs:
        target = sorted(error_signs, key=lambda x: (x.consecutive_incorrect, -x.mastery_percentage), reverse=True)[0]
        reason = f"Sign '{target.sign_character}' has {target.consecutive_incorrect} consecutive incorrect attempts (mastery: {target.mastery_percentage:.1f}%). Focused practice will resolve confusion!"
        return _persist_recommendation(db, learner_id, target.sign_character, reason, priority=2, mastery=target.mastery_percentage)

    # 3. Check for LEARNING or IMPROVING signs with lowest mastery
    active_signs = [s for s in states if s.current_state in [StateEnum.LEARNING, StateEnum.IMPROVING]]
    if active_signs:
        target = sorted(active_signs, key=lambda x: x.mastery_percentage)[0]
        reason = f"Your mastery for sign '{target.sign_character}' is currently {target.mastery_percentage:.1f}%. Practice to advance to Mastered status!"
        return _persist_recommendation(db, learner_id, target.sign_character, reason, priority=3, mastery=target.mastery_percentage)

    # 4. Check for UNATTEMPTED signs
    unattempted = [s for s in states if s.current_state == StateEnum.NOT_ATTEMPTED]
    if unattempted:
        target = sorted(unattempted, key=lambda x: x.sign_character)[0]
        reason = f"Sign '{target.sign_character}' has not been attempted yet. Expand your ASL alphabet vocabulary!"
        return _persist_recommendation(db, learner_id, target.sign_character, reason, priority=4, mastery=0.0)

    # 5. Review Mastered signs
    mastered = [s for s in states if s.current_state == StateEnum.MASTERED]
    if mastered:
        target = sorted(mastered, key=lambda x: x.last_updated)[0]
        reason = f"Great progress! Review sign '{target.sign_character}' to maintain your {target.mastery_percentage:.1f}% mastery streak."
        return _persist_recommendation(db, learner_id, target.sign_character, reason, priority=5, mastery=target.mastery_percentage)

    return _persist_recommendation(db, learner_id, "A", "Start practicing ASL alphabet letters.", priority=5, mastery=0.0)

def _persist_recommendation(
    db: Session,
    learner_id: int,
    sign: str,
    reason: str,
    priority: int,
    mastery: float
) -> Dict[str, Any]:
    target_lesson = db.query(Lesson).filter(Lesson.sign_character == sign).first()
    
    rec_obj = Recommendation(
        learner_id=learner_id,
        recommended_sign=sign,
        reason=reason,
        priority=priority,
        current_mastery=mastery,
        created_at=datetime.utcnow()
    )
    db.add(rec_obj)
    db.commit()
    
    return {
        "recommended_sign": sign,
        "reason": reason,
        "priority": priority,
        "current_mastery": mastery,
        "target_lesson_id": target_lesson.id if target_lesson else 1
    }
