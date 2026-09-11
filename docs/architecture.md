# System Architecture & Service Layer Design (`docs/architecture.md`)

## 1. Overview & Clean Architecture Principles

The platform follows clean architecture principles with explicit separation of concerns:

```text
HTTP Request
   ↓
FastAPI Router Layer (`backend/app/api/`)
   ↓
Business Service Layer (`backend/app/services/`)
   ↓
Repository & Persistence Layer (`backend/app/models/domain.py` + SQLAlchemy)
   ↓
PostgreSQL Database (Neon Cloud / Local)
```

FastAPI routers do **not** contain raw OpenCV, MediaPipe, ML model prediction, or scoring calculations. Routers delegate directly to service singletons.

---

## 2. AI Pipeline Architecture

```text
Raw Video Frame (BGR)
   ↓
Input Validation (`AIPipeline.validate_input`)
   ↓
MediaPipe Hand Detector (`HandTracker`)
   ↓
21 3D Spatial Keypoint Extractor ($21 \times 3 = 63$ features)
   ↓
Wrist-Centered Max Scale Normalizer (`LandmarkNormalizer`)
   ↓
Versioned Model Classifier (`models/asl_rf_v001/model.joblib`)
   ↓
Confidence Thresholding (`MODEL_CONFIDENCE_THRESHOLD = 0.75`)
   ↓
Structured `PredictionResult` Object
```

---

## 3. Modular Subsystems
- **Assessment Engine**: Evaluates `hand_shape_accuracy`, `position_accuracy`, `motion_accuracy` (static proxy), `timing_score`, `stability_score`.
- **Centralized Performance Model**: Weighted scoring ($0.40 \cdot \text{Gesture} + 0.25 \cdot \text{Assessment} + 0.15 \cdot \text{Lesson} + 0.10 \cdot \text{Consistency} + 0.10 \cdot \text{Improvement}$).
- **Feedback Engine**: Modular landmark geometry rules evaluating thumb placement, finger extension, wrist position, scale, and stability.
- **Learner State Machine**: 5-state transition engine (`Not Attempted` $\rightarrow$ `Learning` $\rightarrow$ `Improving` $\rightarrow$ `Mastered` $\rightarrow$ `Needs Revision`).
