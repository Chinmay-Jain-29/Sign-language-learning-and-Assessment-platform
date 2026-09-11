# Database Schema & Entity Specification (`docs/database.md`)

## 1. Relational Database Overview
The platform uses a normalized PostgreSQL relational database (`backend/app/models/domain.py`) containing 24 domain entities supporting multi-role authorization, practice sessions, granular assessment attempts, alphabet mastery state machines, recommendations, certification, and audit logs.

---

## 2. Core Entities & Tables

### 1. `User` & `LearnerProfile`
- **User**: `id`, `email`, `hashed_password`, `full_name`, `role` (`Learner`, `Instructor`, `AccessibilityTrainer`, `Administrator`), `is_active`, `created_at`.
- **LearnerProfile**: `id`, `user_id`, `learning_level`, `overall_performance_score`, `practice_streak_days`, `total_practice_time_mins`, `preferred_language`.

### 2. `PracticeSession` & `AssessmentAttempt`
- **PracticeSession**: `id`, `uuid`, `learner_id`, `selected_signs`, `start_time`, `end_time`, `total_attempts`, `correct_count`, `incorrect_count`, `average_accuracy`, `average_confidence`, `status`.
- **AssessmentAttempt**: `id`, `session_id`, `learner_id`, `expected_sign`, `predicted_sign`, `is_correct`, `confidence`, `gesture_accuracy`, `hand_shape_accuracy`, `position_accuracy`, `motion_accuracy`, `timing_score`, `stability_score`, `invalid_frame_count`, `inference_time`, `timestamp`, `feedback_id`.

### 3. `LearnerAlphabetState` & `LearnerStateHistory`
- **LearnerAlphabetState**: `id`, `learner_id`, `sign_character`, `current_state` (`Not Attempted`, `Learning`, `Improving`, `Mastered`, `Needs Revision`), `total_attempts`, `successful_attempts`, `consecutive_correct`, `consecutive_incorrect`, `average_accuracy`, `mastery_percentage`, `last_updated`.

### 4. `Certification` & `Notification`
- **Certification**: `id`, `user_id`, `title`, `certificate_code`, `issued_at`.
- **Notification**: `id`, `user_id`, `title`, `message`, `type`, `is_read`, `created_at`.
