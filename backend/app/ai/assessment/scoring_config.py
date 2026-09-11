from typing import Dict

# Centralized Weighted Learning Performance Model Configuration
# Project Weights:
# - Gesture Accuracy: 40%
# - Assessment Performance: 25%
# - Lesson Completion: 15%
# - Practice Consistency: 10%
# - Skill Improvement Rate: 10%

WEIGHTED_PERFORMANCE_CONFIG: Dict[str, float] = {
    "gesture_accuracy_weight": 0.40,
    "assessment_performance_weight": 0.25,
    "lesson_completion_weight": 0.15,
    "practice_consistency_weight": 0.10,
    "skill_improvement_weight": 0.10
}

def calculate_overall_learning_score(
    gesture_accuracy: float,
    assessment_performance: float,
    lesson_completion: float,
    practice_consistency: float,
    skill_improvement_rate: float,
    config: Dict[str, float] = None
) -> float:
    """
    Backend calculation of overall weighted learning performance score [0.0, 100.0].
    Never hardcode the final score on the frontend.
    """
    cfg = config or WEIGHTED_PERFORMANCE_CONFIG
    
    score = (
        gesture_accuracy * cfg["gesture_accuracy_weight"] +
        assessment_performance * cfg["assessment_performance_weight"] +
        lesson_completion * cfg["lesson_completion_weight"] +
        practice_consistency * cfg["practice_consistency_weight"] +
        skill_improvement_rate * cfg["skill_improvement_weight"]
    )
    
    return round(float(score), 2)
