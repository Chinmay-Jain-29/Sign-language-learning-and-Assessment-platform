from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.domain import LearnerAlphabetState, LearnerStateHistory, StateEnum

def evaluate_and_update_state(
    db: Session,
    state_obj: LearnerAlphabetState,
    latest_accuracy: float,
    is_correct: bool,
    latest_confidence: Optional[float] = None
) -> StateEnum:
    """
    Authoritative Sign Mastery State Machine Transition Rules:
    
    1. NOT_ATTEMPTED: total_attempts == 0
    2. MASTERED:
       - total_attempts >= 5
       - average_accuracy >= 85.0%
       - average_confidence >= 85.0%
    3. PRACTICING (IMPROVING):
       - total_attempts >= 2
       - average_accuracy >= 50.0%
       - (mastery criteria not yet fully met)
    4. LEARNING:
       - total_attempts > 0
       - (insufficient practice evidence, e.g. < 2 attempts or accuracy < 50%)
    5. NEEDS_REVISION:
       - previously MASTERED or IMPROVING but:
         consecutive_incorrect >= 2 OR average_accuracy < 60.0% OR neglected > 7 days
    """
    previous_state = state_obj.current_state
    
    # 1. Update streak counters
    if is_correct:
        state_obj.consecutive_correct = (state_obj.consecutive_correct or 0) + 1
        state_obj.consecutive_incorrect = 0
    else:
        state_obj.consecutive_incorrect = (state_obj.consecutive_incorrect or 0) + 1
        state_obj.consecutive_correct = 0

    attempts = state_obj.total_attempts or 0
    avg_acc = state_obj.average_accuracy or 0.0
    avg_conf = state_obj.average_confidence or 0.0
    days_since_practice = (datetime.utcnow() - state_obj.last_updated).days if state_obj.last_updated else 0

    # 2. Determine new state based on authoritative criteria
    if attempts == 0:
        new_state = StateEnum.NOT_ATTEMPTED
    elif previous_state in [StateEnum.MASTERED, StateEnum.IMPROVING] and (
        state_obj.consecutive_incorrect >= 2 or avg_acc < 60.0 or days_since_practice > 7
    ):
        new_state = StateEnum.NEEDS_REVISION
    elif attempts >= 5 and avg_acc >= 85.0 and avg_conf >= 85.0:
        new_state = StateEnum.MASTERED
    elif attempts >= 2 and avg_acc >= 50.0:
        new_state = StateEnum.IMPROVING
    else:
        new_state = StateEnum.LEARNING

    state_obj.current_state = new_state
    state_obj.last_updated = datetime.utcnow()

    # 3. Log history if state transitioned
    if previous_state != new_state:
        db.flush()
        if state_obj.id:
            history_entry = LearnerStateHistory(
                state_id=state_obj.id,
                previous_state=previous_state,
                new_state=new_state,
                accuracy_score=latest_accuracy,
                changed_at=datetime.utcnow()
            )
            db.add(history_entry)

    db.flush()
    return new_state
