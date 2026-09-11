# Test Suites & Quality Assurance

This directory outlines the comprehensive test suites, automated verification workflows, and test execution procedures for the **AI-Powered Sign Language Learning & Assessment Platform**.

---

## 1. Test Architecture

```
PROJECT_ROOT/
├── backend/tests/          # 33 Backend Unit, Integration & API Test Suites
│   ├── test_auth.py
│   ├── test_auth_module_flow.py
│   ├── test_learner_level_admin_control.py
│   ├── test_practice_modes_navigation.py
│   ├── test_achievement_direct_practice_navigation.py
│   ├── test_role_based_profile_and_photo.py
│   ├── test_reporting_monitoring_instructions.py
│   ├── test_dashboard_data_integrity.py
│   ├── test_ml_pipeline.py
│   └── ...
└── frontend/               # Frontend component verification & TypeScript/Vite bundle checks
```

---

## 2. Running Backend Tests

Backend tests utilize Python's standard `unittest` framework with in-memory SQLite isolation to ensure zero side-effects on development or production databases.

### Run All Backend Tests:
```bash
# Execute from backend directory
cd backend
python -m unittest discover -s tests

# Or execute from project root
python -m unittest discover -s backend/tests
```

### Run Specific Test Suites:
```bash
# Learner Level Administrative Control (8 tests)
python -m unittest backend/tests/test_learner_level_admin_control.py

# Achievement Direct Practice Navigation (6 tests)
python -m unittest backend/tests/test_achievement_direct_practice_navigation.py

# Role-based Profiles & Photo Upload (12 tests)
python -m unittest backend/tests/test_role_based_profile_and_photo.py

# Reporting & Private Instructor Monitoring (14 tests)
python -m unittest backend/tests/test_reporting_monitoring_instructions.py
```

---

## 3. Running Frontend Checks & Production Build

```bash
# Change to frontend directory
cd frontend

# Run production bundle build check
npm run build
```

---

## 4. Test Fixtures & Database Isolation

- All backend tests run against an isolated in-memory SQLite engine (`sqlite:///:memory:`) using `StaticPool`.
- No mock credentials or test users are seeded into external production databases.
- Test suites teardown all session dependencies cleanly upon completion.
