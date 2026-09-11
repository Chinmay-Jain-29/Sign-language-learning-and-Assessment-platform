# Master Implementation Plan (`docs/IMPLEMENTATION_PLAN.md`)

This document defines the step-by-step master plan for implementing all missing and refactored components of the **AI Sign Language Learning & Assessment Platform** strictly following the 36-Phase execution order in the Master Specification.

---

## 🏗️ Master Architectural Target

```
Frontend (React + Vite + Tailwind CSS v4)
  └─ UI/UX Design System (Tokens, ARIA, Skeletons, Toasts)
  └─ 44 Pages across 4 Role Portals (Learner, Instructor, Trainer, Admin)
       │
       ▼ REST APIs (v1) [/api/v1/...]
       │ (Standard Envelope: { success, message, data, error, meta })
       │
FastAPI Application Layer (Router -> Service -> Repository -> Database)
  ├─ AuthService (JWT, Refresh Tokens, Password Reset, RBAC)
  ├─ PracticeService & AssessmentService
  ├─ AnalyticsService & RecommendationService
  └─ AIService Layer
       └─ HandTrackingModule (MediaPipe)
       └─ Normalizer (Wrist Origin Scale Normalization)
       └─ GestureClassifier (Versioned Model: models/asl_rf_v001/)
       └─ TemporalBuffer & StableGestureDetector
       └─ FeedbackEngine & AssessmentEvaluator
       │
       ▼
PostgreSQL Relational Database (23 Normalized Entities, UUIDs, Foreign Keys)
```

---

## 📌 Detailed Phase-by-Phase Plan

### PHASE 1: UI/UX Design System
- **Objective**: Build design system tokens, typography, colors, shadows, radius, and reusable UI components in `frontend/src/components/common/` (Buttons, Inputs, Cards, Modals, Toasts, Tables, Charts, Progress indicators, Badges, Empty states, Loading states, Skeleton loaders) and accessibility ARIA utilities.
- **Files**:
  - `frontend/src/index.css` (Expand design system tokens & variables)
  - `frontend/src/components/common/Button.jsx`
  - `frontend/src/components/common/Card.jsx`
  - `frontend/src/components/common/Modal.jsx`
  - `frontend/src/components/common/Toast.jsx`
  - `frontend/src/components/common/Skeleton.jsx`
  - `frontend/src/components/common/Badge.jsx`

### PHASE 2: Authentication, Refresh Tokens & RBAC Security
- **Objective**: Implement refresh token rotation, password reset endpoints (`/auth/forgot-password`, `/auth/reset-password`), session expiration handling, and enforce strict backend role authorization.
- **Files**:
  - `backend/app/models/domain.py` (Add RefreshToken, UserRole tables)
  - `backend/app/core/security.py` (Add refresh token logic)
  - `backend/app/api/v1/auth.py` (Add refresh & reset password routes)
  - `frontend/src/context/AuthContext.jsx` (Add token refresh interceptor)

### PHASE 3: Database Schema Normalization & Content Models
- **Objective**: Upgrade database models in `backend/app/models/domain.py` to support all 23 PostgreSQL entities specified in Section 14, including `AssessmentAttempt` with 18 detailed metrics fields, `practice_sessions`, `learner_alphabet_states`, `audit_logs`, and course modules.
- **Files**:
  - `backend/app/models/domain.py`
  - `backend/app/database/init_db.py`

### PHASE 4: Dataset Explorer & Inspection Scripts
- **Objective**: Create `scripts/dataset_explorer.py`, `scripts/image_loader.py`, and `scripts/camera_test.py` to inspect local datasets (`datasets/asl_alphabet`, `sign_mnist`, `wlasl`), count classes/samples, check image balance and dimensions, inspect WLASL annotations, and output `dataset_report.json` and `dataset_report.csv`.
- **Files**:
  - `scripts/dataset_explorer.py`
  - `scripts/image_loader.py`
  - `scripts/camera_test.py`

### PHASE 5: Isolated Hand Tracking Module
- **Objective**: Create `backend/app/ai/hand_tracking/detector.py` isolating MediaPipe hand detection, 21 landmark coordinate extraction, and multi-hand/visibility validation away from FastAPI routers.
- **Files**:
  - `backend/app/ai/hand_tracking/detector.py`
  - `backend/app/ai/hand_tracking/__init__.py`

### PHASE 6: Batch Landmark Extraction Pipeline
- **Objective**: Create `extract_landmarks.py` to iterate through images, extract 21 keypoints (63 features + label), handle invalid frames gracefully, and output `landmarks.csv`.
- **Files**:
  - `scripts/extract_landmarks.py`

### PHASE 7: Invalid Sample Handling & Quality Reporting
- **Objective**: Implement corrupt image detection, no-hand logging, NaN/Inf checks, and generate `dataset_report.json` with sample processing statistics.
- **Files**:
  - `scripts/extract_landmarks.py`

### PHASE 8: Landmark Normalization Module
- **Objective**: Create `preprocessing/normalize_landmarks.py` implementing wrist origin subtraction and scale normalization, producing `normalized_landmarks.csv`.
- **Files**:
  - `backend/app/ai/preprocessing/normalize_landmarks.py`

### PHASE 9: Stratified Dataset Splitting
- **Objective**: Create `split_dataset.py` to split `normalized_landmarks.csv` into `train.csv`, `validation.csv`, and `test.csv` using stratified and group-aware splitting.
- **Files**:
  - `scripts/split_dataset.py`

### PHASE 10: Classifier Experiments (RF vs. Decision Tree vs. SVM)
- **Objective**: Train Random Forest, Decision Tree, and SVM models on the exact same dataset splits and output performance comparison metrics (`comparison_report.csv`).
- **Files**:
  - `backend/app/ai/ml/experiments.py`

### PHASE 11: Random Forest Hyperparameter Study
- **Objective**: Experiment with 50, 100, and 200 trees, tuning `max_depth` and `min_samples_leaf` to determine optimal model size vs. accuracy vs. inference latency.
- **Files**:
  - `backend/app/ai/ml/hyperparameter_study.py`

### PHASE 12: Error Analysis & Confusion Matrix
- **Objective**: Generate confusion matrix and top 5 confused gesture pairs report (`error_analysis.md`).
- **Files**:
  - `reports/error_analysis.md`

### PHASE 13: Real-Time AI Inference Latency Benchmarking
- **Objective**: Measure P50/P95 latency, model size, memory, FPS, and generate `benchmark_report.md`.
- **Files**:
  - `reports/benchmark_report.md`

### PHASE 14: Production AI Service & Versioned Model Packaging
- **Objective**: Package approved model into `models/asl_rf_v001/` with `model.pkl`, `metadata.json`, `preprocessing.json`, and `labels.json`. Build clean `AIService.predict(image) -> PredictionResult` interface with `MODEL_CONFIDENCE_THRESHOLD` and mock mode (`AI_MODE=mock`).
- **Files**:
  - `models/asl_rf_v001/*`
  - `backend/app/services/ai_service.py`

### PHASE 15: Real-Time Webcam Recognition & 15 Webcam States UI
- **Objective**: Implement 15 camera states in the frontend practice page and integrate n-consecutive frame gesture stabilization.
- **Files**:
  - `frontend/src/pages/learner/Practice.jsx`
  - `backend/app/ai/temporal/buffer.py`

### PHASES 16–22: Practice Sessions, Assessment Engine, Feedback, Analytics, States & Recommendations
- **Objective**: Build PracticeSession persistence, detailed `AssessmentAttempt` logging, modular feedback rules, 5-stage learner state machine, and adaptive personalized recommendations.
- **Files**:
  - `backend/app/services/practice_service.py`
  - `backend/app/services/assessment_service.py`
  - `backend/app/services/recommendation_service.py`
  - `backend/app/ai/feedback/rules.py`

### PHASES 23–26: Complete 44 Frontend Pages Across 4 Role Portals
- **Objective**: Complete all required sub-pages for Public (Landing, About, Features, How It Works, Accessibility Info), Learner (18 pages), Instructor (9 pages), Accessibility Trainer (6 pages), and Admin (10 pages).
- **Files**:
  - `frontend/src/pages/*`

### PHASES 27–35: Reports, Certification, Notifications, Testing, Optimization, Docker & CI/CD
- **Objective**: Build PDF/Excel reports, skill level certification exams, event-driven notifications, pytest test suite, Docker containerization, and GitHub Actions CI/CD.
- **Files**:
  - `backend/app/api/v1/reports.py`
  - `backend/app/api/v1/certification.py`
  - `backend/app/api/v1/notifications.py`
  - `.github/workflows/ci.yml`
