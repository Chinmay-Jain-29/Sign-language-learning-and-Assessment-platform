from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain import (
    User, LearnerProfile, AssessmentAttempt, LearnerAlphabetState,
    PracticeSession, Feedback, StateEnum
)
from app.ai.assessment.evaluator import evaluate_gesture_attempt, assessment_evaluator
from app.ai.feedback.engine import feedback_engine
from app.services.learner_state_service import evaluate_and_update_state
from app.services.recommendation_service import generate_adaptive_recommendation

def process_adaptive_assessment_attempt(
    db: Session,
    learner: User,
    expected_sign: str,
    landmarks: List[Dict[str, float]],
    session_id: int = None
) -> Dict[str, Any]:
    """
    Executes the mandatory closed-loop adaptive learning flow:
    assessment → analytics → learner profile → learner state → feedback → recommendation → dashboard payload
    """
    # 1. AI Assessment & Evaluation
    eval_result = evaluate_gesture_attempt(
        expected_sign=expected_sign.upper(),
        landmarks=landmarks
    )
    
    is_corr = eval_result["predicted_sign"] == eval_result["expected_sign"]
    accuracy = eval_result["overall_accuracy"]
    confidence = eval_result["confidence"]

    # Flatten landmarks to 63 floats for feedback engine
    raw_63 = []
    for lm in landmarks:
        raw_63.extend([lm.get('x', 0.0), lm.get('y', 0.0), lm.get('z', 0.0)])

    # 2. Modular Rule-Based Feedback Engine
    feedback_text = feedback_engine.generate_feedback(
        landmarks_63=raw_63,
        expected_sign=expected_sign.upper(),
        predicted_sign=eval_result["predicted_sign"],
        confidence=confidence,
        invalid_frames=0
    )
    correction_suggestion = "Maintain finger extension." if is_corr else f"Check finger curl and thumb placement for sign '{expected_sign.upper()}'."

    feedback_obj = Feedback(
        feedback_text=feedback_text,
        correction_suggestion=correction_suggestion,
        error_category="Landmark Alignment" if not is_corr else "None"
    )
    db.add(feedback_obj)
    db.commit()
    db.refresh(feedback_obj)

    # 3. Log AssessmentAttempt
    attempt = AssessmentAttempt(
        session_id=session_id,
        learner_id=learner.id,
        expected_sign=eval_result["expected_sign"],
        predicted_sign=eval_result["predicted_sign"],
        is_correct=is_corr,
        confidence=confidence,
        gesture_accuracy=accuracy,
        hand_shape_accuracy=eval_result["hand_shape_accuracy"],
        position_accuracy=eval_result["position_accuracy"],
        motion_accuracy=eval_result["motion_accuracy"],
        timing_score=95.0,
        stability_score=90.0,
        invalid_frame_count=0,
        inference_time=12.5,
        timestamp=datetime.utcnow(),
        feedback_id=feedback_obj.id
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # 4. Update PracticeSession stats if session_id provided
    if session_id:
        sess = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
        if sess:
            sess.total_attempts += 1
            if is_corr:
                sess.correct_count += 1
            else:
                sess.incorrect_count += 1
            n = sess.total_attempts
            sess.average_accuracy = round(((sess.average_accuracy * (n - 1)) + accuracy) / n, 2)
            sess.average_confidence = round(((sess.average_confidence * (n - 1)) + confidence) / n, 2)
            db.commit()

    # 5. Get or Create LearnerAlphabetState
    sign_char = eval_result["expected_sign"]
    st = db.query(LearnerAlphabetState).filter(
        LearnerAlphabetState.learner_id == learner.id,
        LearnerAlphabetState.sign_character == sign_char
    ).first()

    if not st:
        st = LearnerAlphabetState(
            learner_id=learner.id,
            sign_character=sign_char,
            current_state=StateEnum.NOT_ATTEMPTED
        )
        db.add(st)
        db.commit()
        db.refresh(st)

    # Update alphabet performance metrics
    st.total_attempts += 1
    if is_corr:
        st.successful_attempts += 1

    n_st = st.total_attempts
    st.average_accuracy = round(((st.average_accuracy * (n_st - 1)) + accuracy) / n_st, 2)
    st.average_confidence = round(((st.average_confidence * (n_st - 1)) + confidence) / n_st, 2)
    
    # Calculate moving weighted mastery percentage
    success_ratio = (st.successful_attempts / n_st) * 100.0
    st.mastery_percentage = round(min(100.0, (success_ratio * 0.5) + (st.average_accuracy * 0.5)), 2)

    # 6. Run Measurable State Machine Transition Engine
    new_state = evaluate_and_update_state(
        db=db,
        state_obj=st,
        latest_accuracy=accuracy,
        is_correct=is_corr
    )

    # 7. Update LearnerProfile
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == learner.id).first()
    if profile:
        profile.total_practice_time_mins += 1
        profile.last_practice_at = datetime.utcnow()
        # Compute overall performance score across all alphabet states
        all_states = db.query(LearnerAlphabetState).filter(LearnerAlphabetState.learner_id == learner.id).all()
        if all_states:
            profile.overall_performance_score = round(sum(s.mastery_percentage for s in all_states) / len(all_states), 2)
        db.commit()

    # 8. Run Adaptive Recommendation Engine
    next_recommendation = generate_adaptive_recommendation(db, learner.id)

    # 9. Return Unified Closed-Loop Payload
    return {
        "assessment": {
            "attempt_id": attempt.id,
            "expected_sign": eval_result["expected_sign"],
            "predicted_sign": eval_result["predicted_sign"],
            "is_correct": is_corr,
            "confidence": confidence,
            "accuracy": accuracy,
            "hand_shape_accuracy": eval_result["hand_shape_accuracy"],
            "position_accuracy": eval_result["position_accuracy"],
            "motion_accuracy": eval_result["motion_accuracy"]
        },
        "feedback": {
            "text": feedback_text,
            "suggestion": correction_suggestion
        },
        "learner_state": {
            "sign_character": st.sign_character,
            "current_state": new_state.value,
            "total_attempts": st.total_attempts,
            "successful_attempts": st.successful_attempts,
            "consecutive_correct": st.consecutive_correct,
            "consecutive_incorrect": st.consecutive_incorrect,
            "mastery_percentage": st.mastery_percentage,
            "average_accuracy": st.average_accuracy
        },
        "recommendation": next_recommendation,
        "profile": {
            "overall_performance_score": profile.overall_performance_score if profile else 0.0,
            "total_practice_time_mins": profile.total_practice_time_mins if profile else 0,
            "last_practice_at": profile.last_practice_at if profile else None
        }
    }
