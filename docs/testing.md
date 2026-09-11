# Testing Architecture & Verification Manual (`docs/testing.md`)

## 1. Overview
The platform contains a test suite (`backend/tests/`) covering unit tests, ML pipeline tests, E2E closed-loop integration tests, and performance benchmarks.

---

## 2. Test Suites Overview

### A. Backend Unit Test Suite (`backend/tests/`)
- Tests database models, authentication, JWT tokens, RBAC permissions, practice sessions, assessment calculations, weighted performance model, and feedback rules.
- Command: `python -m unittest discover -s backend/tests -p "test_*.py"`

### B. ML Pipeline Test Suite (`backend/tests/test_ml_pipeline.py`)
- Tests MediaPipe tracking, invalid keypoints, missing hands, wrist scale normalization, versioned model loading, and confidence thresholding.
- Command: `python backend/tests/test_ml_pipeline.py`

### C. End-to-End Closed-Loop Test Suite (`backend/tests/test_e2e_closed_loop.py`)
- Tests the complete 16-step closed-loop workflow: Register -> Login -> Dashboard -> Start Practice -> Recommended Alphabet -> Reference Sign -> Webcam Predict -> Assess -> Feedback -> State Update -> Recommendation Update -> Session Complete -> PDF/Excel Download.
- Command: `python backend/tests/test_e2e_closed_loop.py`

---

## 3. Empirical Test Results

```text
Ran 70 tests in 216.049s
Status: OK (100% Passing)
```
