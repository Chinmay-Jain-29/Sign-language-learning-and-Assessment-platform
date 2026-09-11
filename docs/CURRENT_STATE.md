# Technical Audit & Current Repository State (`docs/CURRENT_STATE.md`)

This document provides a technical classification and architectural audit of every module in the repository against the **Master Project Specification**.

---

## 1. Module Classification Matrix

| Category | Module / File | Current Status | Description & Audit Notes |
|---|---|---|---|
| **Database** | `backend/app/models/domain.py` | `NEEDS REFACTOR` | Implements basic SQLAlchemy models (User, Profile, Course, Lesson, Attempt, Mastery, Assessment, Certification, Notification). Missing PostgreSQL normalized schema entities (Roles, UserRoles, CourseModules, LessonSigns, Signs, PracticeSessions, Predictions, Feedback, LearnerAlphabetStates, StateHistory, AnalyticsSnapshots, ProgressRecords, AuditLogs, UUID keys). |
| **Database** | `backend/app/database/session.py` | `WORKING` | SQLAlchemy engine with dual SQLite/PostgreSQL connection handling and session management. |
| **Database** | `backend/app/database/init_db.py` | `WORKING` | Seeds default demo users (4 roles) and ASL alphabet courses/lessons A–Z. |
| **Auth** | `backend/app/core/security.py` | `PARTIALLY WORKING` | Implements JWT token generation and PBKDF2 password hashing. Missing refresh token strategy and password reset tokens. |
| **Auth** | `backend/app/api/auth.py` | `PARTIALLY WORKING` | Handles `/auth/login`, `/auth/register`, `/auth/me`. Missing `/auth/refresh`, `/auth/logout`, `/auth/forgot-password`, `/auth/reset-password`. |
| **Auth** | `backend/app/api/deps.py` | `WORKING` | Enforces JWT validation and backend role-based access control (`require_roles`). |
| **ML Engine** | `backend/app/ai/preprocessing/extract_landmarks.py` | `PARTIALLY WORKING` | MediaPipe 21-landmark extraction and wrist-relative scale normalization. Missing CLI pipeline for batch dataset extraction saving to `landmarks.csv`. |
| **ML Engine** | `backend/app/ai/ml/train.py` | `PARTIALLY WORKING` | Random Forest classifier training script. Missing Decision Tree & SVM comparison, hyperparameter grid search, and experiment tracking. |
| **ML Engine** | `backend/app/ai/gesture_recognition/classifier.py` | `PARTIALLY WORKING` | Loads model and predicts gesture class. Missing prediction thresholding (`MODEL_CONFIDENCE_THRESHOLD`), `PredictionResult` DTO, and Mock mode (`AI_MODE=mock`). |
| **ML Engine** | `backend/app/ai/assessment/evaluator.py` | `WORKING` | Integrates classification and feedback evaluation. |
| **ML Engine** | `backend/app/ai/feedback/feedback_engine.py` | `WORKING` | Calculates hand shape, position, motion accuracy, and finger joint mistake guidance. |
| **ML Scripts** | `scripts/dataset_explorer.py` | `MISSING` | Required dataset inspection script analyzing class balance, image dimensions, corrupt files, generating `dataset_report.json`. |
| **ML Scripts** | `scripts/image_loader.py` | `MISSING` | Required low-level image loading verification script. |
| **ML Scripts** | `scripts/camera_test.py` | `MISSING` | Required standalone camera verification utility. |
| **ML Scripts** | `preprocessing/normalize_landmarks.py` | `MISSING` | Required standalone landmark normalization module producing `normalized_landmarks.csv`. |
| **ML Scripts** | `split_dataset.py` | `MISSING` | Required dataset splitting script producing `train.csv`, `validation.csv`, `test.csv` with stratified split. |
| **ML Models** | `models/asl_rf_v001/` | `NEEDS REFACTOR` | Currently saves single `gesture_model.joblib`. Must be structured with `model.pkl`, `metadata.json`, `preprocessing.json`, `labels.json`. |
| **ML Experiments**| `experiments/` | `MISSING` | Required experiment tracking directory (`experiment_001/` with configs, results, notes). |
| **ML Temporal** | `backend/app/ai/temporal/` | `MISSING` | Required temporal sequence buffer storing latest 20–30 landmark vectors for future sequence models. |
| **ML Tracking** | `backend/app/ai/hand_tracking/` | `MISSING` | Reusable MediaPipe hand tracking module isolated from FastAPI. |
| **APIs** | `backend/app/api/*.py` | `NEEDS REFACTOR` | Currently uses `/api/` prefix instead of versioned `/api/v1/`. Responses do not conform to standardized `{ success, message, data, error, meta }` format. |
| **Frontend UI** | `frontend/src/App.jsx` & Design System | `PARTIALLY WORKING` | Basic Tailwind CSS setup and role router. Missing comprehensive component library (Modals, Toasts, Skeletons, Badges) and accessibility ARIA features. |
| **Frontend Pages**| Public Pages | `MISSING` | Missing Landing Page, About, Features, How It Works, Accessibility Info, Forgot Password, Reset Password. Login & Register are working. |
| **Frontend Pages**| Learner Pages | `PARTIALLY WORKING` | Dashboard, Webcam Practice, Lessons, Assessments present. Missing 14 detailed sub-pages (Course Details, Practice Review, Skill Mastery, History, Progress trends, Settings). |
| **Frontend Pages**| Instructor Pages | `PARTIALLY WORKING` | Instructor Dashboard present. Missing 8 detailed sub-pages (Students, Student Details, Class Progress, Assessment Analytics, Weak Areas, Course/Lesson Management, Reports). |
| **Frontend Pages**| Trainer Pages | `PARTIALLY WORKING` | Trainer Dashboard present. Missing 5 detailed sub-pages (Learner Engagement, Skill Development, Assessment Analytics, Certification Monitoring, Reports). |
| **Frontend Pages**| Admin Pages | `PARTIALLY WORKING` | Admin Dashboard present. Missing 9 detailed sub-pages (Role Management, Content Management, System Monitoring, Model Monitoring, Audit Logs). |
| **DevOps** | `docker-compose.yml`, `Dockerfile` | `WORKING` | Docker configuration for PostgreSQL, FastAPI backend, and Nginx frontend. |

---

## 2. Identified Architectural Problems & Duplication

1. **API Router & AI Logic Coupling**: In some handlers, AI prediction calls are invoked directly without passing through an explicit `AIService` / `AssessmentService` layer.
2. **Missing Standard API Envelope**: APIs return direct Pydantic models instead of the standard `{ success, message, data, error, meta }` response wrapper required by Section 60.
3. **Database Schema Normalization Gaps**: Missing separate `roles`, `user_roles`, `course_modules`, `lesson_signs`, `signs`, `practice_sessions`, `predictions`, `feedback`, `learner_alphabet_states`, `learner_state_history`, and `audit_logs` tables as specified in Section 14.
4. **Lack of Machine Learning Artifact Management**: Trained model artifacts are not versioned in `models/asl_rf_v001/` with full training metadata, hyperparameters, metrics, and preprocessing parameters.

---

## 3. Dataset Audit Status

- **ASL Alphabet Dataset (`datasets/asl_alphabet`)**: Available locally with A–Z, del, nothing, space directories. Requires `scripts/dataset_explorer.py` integration.
- **Sign Language MNIST (`datasets/sign_mnist`)**: Available locally (`sign_mnist_train.csv`, `sign_mnist_test.csv`).
- **WLASL (`datasets/wlasl`)**: Available locally (`WLASL_v0.3.json`, videos).
- **RWTH-PHOENIX (`datasets/rwth_phoenix`)**: Directory present, currently empty.
