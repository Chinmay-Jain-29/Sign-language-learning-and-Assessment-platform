from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import User, LearnerAlphabetState, Lesson
from app.api.deps import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("")
@router.get("/")
@router.get("/next-sign")
def get_next_sign_recommendation(

    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    states = db.query(LearnerAlphabetState).filter(LearnerAlphabetState.learner_id == current_user.id).all()
    
    if not states:
        first_lesson = db.query(Lesson).order_by(Lesson.order_index.asc()).first()
        return {
            "recommended_sign": first_lesson.sign_character if first_lesson else "A",
            "reason": "Welcome! Start your sign language learning with letter 'A'.",
            "target_lesson_id": first_lesson.id if first_lesson else 1
        }
        
    sorted_s = sorted(states, key=lambda x: x.mastery_percentage)
    weakest = sorted_s[0]
    
    target_lesson = db.query(Lesson).filter(Lesson.sign_character == weakest.sign_character).first()
    
    return {
        "recommended_sign": weakest.sign_character,
        "current_mastery": weakest.mastery_percentage,
        "reason": f"Your mastery for '{weakest.sign_character}' is currently {weakest.mastery_percentage:.1f}%. Practice will improve your overall accuracy score.",
        "target_lesson_id": target_lesson.id if target_lesson else 1
    }
