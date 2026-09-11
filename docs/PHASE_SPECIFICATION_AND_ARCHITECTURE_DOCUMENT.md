# Sign Language Learning and Assessment Platform
## Master Phase Specification & Architecture Document

This document provides a comprehensive, phase-by-phase technical breakdown for the **AI Sign Language Learning and Assessment Platform**. For each completed phase, this document details:

1. **Expected Requirements**: Goals, functionality, and constraints.
2. **Implemented Specifications & Code Structure**: Exact files, API endpoints, database entities, and UI components.
3. **Testing Plan & Automated Verification**: Test scripts, verification commands, and pass/fail audit results.
4. **Architecture & Flow of Plan**: Mermaid sequence and data flow diagrams.

---

## 🏛️ Overall System Architecture Topology

```mermaid
graph TD
    Client["React + Vite Frontend (Port 5173)\nTailwindCSS + Custom Glassmorphism UI"]
    API["FastAPI Backend Server (Port 8000)\nREST API /api/v1/"]
    DB[("Neon Cloud PostgreSQL\n(23 Entities)")]
    AI["AI/ML Pipeline & Adaptive Engine\n(MediaPipe + Random Forest Classifier)"]

    Client -->|JWT HTTP Requests| API
    API -->|SQLAlchemy ORM| DB
    API -->|Landmarks & Practice Data| AI
    AI -->|Real-time Feedback & Recommendation| API
```

---

## 📄 Phase 0: Repository Audit & Specification Documentation

### 1. Expected Requirements
- Perform a complete codebase audit.
- Map existing legacy files against the 36 Master Development Phases.
- Produce authoritative documentation detailing current state, progress tracking, and implementation plans.

### 2. Implemented Specifications & Code Structure
- Created [`docs/CURRENT_STATE.md`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/docs/CURRENT_STATE.md): Comprehensive inventory of legacy frontend and backend files.
- Created [`docs/PROJECT_STATUS.md`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/docs/PROJECT_STATUS.md): Master specification roadmap tracking all 36 phases.
- Created [`docs/IMPLEMENTATION_PLAN.md`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/docs/IMPLEMENTATION_PLAN.md): Technical plan for execution.

### 3. Testing Plan & Automated Verification
- Manual verification of file structure and repository integrity.
- Status: **100% COMPLETED**

### 4. Architecture & Flow of Plan

```mermaid
flowchart LR
    A[Legacy Codebase Audit] --> B[Generate CURRENT_STATE.md]
    B --> C[Establish 36-Phase PROJECT_STATUS.md]
    C --> D[Create IMPLEMENTATION_PLAN.md Strategy]
```

---

## 🏗️ Foundation Phase: Clean Architecture & Cloud Database

### 1. Expected Requirements
- Establish clean multi-layer backend architecture (API Controllers $\rightarrow$ Services $\rightarrow$ Data Repositories $\rightarrow$ Domain Models).
- Build 23 normalized database entities with SQLAlchemy ORM.
- Support seamless connection to server-based **Cloud PostgreSQL** (Neon Cloud DB).
- Enforce standardized API envelope format `{ success, message, data, error, meta }`.
- Provide health endpoint (`GET /api/v1/health`) and dockerization.

### 2. Implemented Specifications & Code Structure
- **Backend Configuration**: [`backend/.env`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/.env) configured with database connection URI template: `DATABASE_URL="postgresql://username:password@hostname:5432/dbname?sslmode=require"` (or SQLite fallback `sqlite:///./sign_language.db`)
- **Database Session & Base**: [`backend/app/database/session.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/database/session.py)
- **Domain Models**: 23 entities in [`backend/app/models/domain.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/models/domain.py) (`User`, `Role`, `UserRole`, `LearnerProfile`, `LearningGoal`, `Course`, `CourseModule`, `Lesson`, `Sign`, `LessonSign`, `LearnerAlphabetState`, `AssessmentAttempt`, `PracticeSession`, `Recommendation`, `RefreshToken`, `PasswordResetToken`, etc.)
- **Error Handling**: Custom `AppException` handler in [`backend/app/core/exceptions.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/core/exceptions.py)
- **Health Endpoint**: [`backend/app/api/v1/health.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/v1/health.py)

### 3. Testing Plan & Automated Verification
- **Automated Test**: `http://127.0.0.1:8000/api/v1/health`
- **Result**: `{"success": true, "data": {"status": "Healthy", "database": "Healthy", "ai_model_loaded": true}}`
- Status: **100% COMPLETED**

### 4. Architecture & Flow of Plan

```mermaid
sequenceDiagram
    participant Client
    participant Router as FastAPI Router (/api/v1)
    participant Middleware as Error Handler
    participant DB as Neon Cloud PostgreSQL

    Client->>Router: GET /api/v1/health
    Router->>DB: SELECT 1 (Ping Check)
    DB-->>Router: Connection OK
    Router-->>Middleware: Format Standard Envelope
    Middleware-->>Client: { success: true, data: { status: "Healthy" } }
```

---

## 🎨 Phase 1: UI/UX Design System & Accessible Component Library

### 1. Expected Requirements
- Create custom WCAG 2.1 AA design tokens in CSS.
- Implement glassmorphic dark theme styling with responsive layouts and focus rings.
- Build reusable UI component library without generic browser styles.
- Create an interactive UI Showcase page at `/design-system`.

### 2. Implemented Specifications & Code Structure
- **Global CSS & Tokens**: [`frontend/src/index.css`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/index.css) (CSS variables, `.glass-panel`, `.glass-card`, `*:focus-visible` focus rings).
- **Reusable Component Library**:
  - [`Button.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/Button.jsx) (primary, secondary, danger, outline, ghost)
  - [`Input.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/Input.jsx) (icon support, validation states, accessibility attributes)
  - [`Card.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/Card.jsx) (glassmorphism hover states)
  - [`Badge.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/Badge.jsx) (success, warning, error, info)
  - [`ProgressBar.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/ProgressBar.jsx) (animated fill, ARIA attributes)
  - [`Modal.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/Modal.jsx) (dialog overlay, keyboard escape handler)
  - [`Toast.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/Toast.jsx) (ToastProvider, toast queue)
  - [`Table.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/Table.jsx) (sortable, paginated headers)
  - [`Skeleton.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/Skeleton.jsx), [`EmptyState.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/EmptyState.jsx), [`ErrorMessage.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/components/common/ErrorMessage.jsx)
- **Showcase Page**: [`frontend/src/pages/DesignSystemShowcase.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/DesignSystemShowcase.jsx) at `/design-system`.

### 3. Testing Plan & Automated Verification
- Production build command: `npm run build`
- Result: **Successfully built in 3.52s with 0 errors**.
- Interactive page verified via browser automated snapshots.
- Status: **100% COMPLETED**

### 4. Architecture & Flow of Plan

```mermaid
graph LR
    Tokens[Design Tokens & CSS Variables] --> BaseComponents[Base Components: Button, Input, Badge]
    BaseComponents --> LayoutComponents[Layout Components: Card, Modal, Table]
    LayoutComponents --> FeedbackComponents[Feedback: Toast, Skeleton, EmptyState]
    FeedbackComponents --> ShowcasePage[Showcase Page /design-system]
```

---

## 🔐 Phase 2: Authentication, Refresh Tokens & RBAC Security

### 1. Expected Requirements
- Implement secure OAuth2 password bearer flow with JWT dual tokens (24-hour Access Token + 7-day Refresh Token).
- Enforce unique UUID `jti` claims on refresh tokens to prevent duplicate token reuse.
- Implement token revocation table (`refresh_tokens`) for instant logout invalidation.
- Build password reset flow with token expiration.
- Enforce Role-Based Access Control (RBAC) across 4 roles (`Learner`, `Instructor`, `Accessibility Trainer`, `Administrator`) at the database level.

### 2. Implemented Specifications & Code Structure
- **Security Core**: [`backend/app/core/security.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/core/security.py) (`create_access_token`, `create_refresh_token`, `verify_password`, `get_password_hash`).
- **Dependencies**: [`backend/app/api/deps.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/deps.py) (`get_current_user`, `require_roles([allowed_roles])`).
- **Auth Endpoints**: [`backend/app/api/v1/auth.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/v1/auth.py) (`/register`, `/login`, `/refresh`, `/logout`, `/me`, `/forgot-password`, `/reset-password`).
- **Frontend Pages**: [`frontend/src/pages/auth/Login.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/auth/Login.jsx), [`Register.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/auth/Register.jsx), [`ForgotPassword.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/auth/ForgotPassword.jsx), [`ResetPassword.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/auth/ResetPassword.jsx).

### 3. Testing Plan & Automated Verification
- **Test Suite**: [`backend/tests/test_auth.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/tests/test_auth.py)
- **Tests Executed**:
  1. `test_login_success`: ✅ PASSED
  2. `test_login_invalid_password`: ✅ PASSED
  3. `test_me_endpoint_with_valid_token`: ✅ PASSED
  4. `test_me_endpoint_invalid_token`: ✅ PASSED
  5. `test_rbac_learner_denied_instructor_route`: ✅ PASSED (403 Forbidden)
  6. `test_rbac_instructor_allowed`: ✅ PASSED
  7. `test_rbac_admin_allowed`: ✅ PASSED
  8. `test_refresh_and_logout_revocation`: ✅ PASSED
- **Result**: **8/8 Tests Passed (100%)**.

### 4. Architecture & Flow of Plan

```mermaid
sequenceDiagram
    participant User
    participant Client as React AuthContext
    participant AuthAPI as /api/v1/auth
    participant Security as Security & RBAC Dep
    participant DB as Neon PostgreSQL

    User->>Client: Enter Email & Password
    Client->>AuthAPI: POST /login
    AuthAPI->>DB: Query User & Verify PBKDF2 Password
    AuthAPI->>AuthAPI: Generate Access Token + Refresh Token (UUID jti)
    AuthAPI->>DB: Store RefreshToken
    AuthAPI-->>Client: Return Tokens + User Payload
    Client->>AuthAPI: GET /protected-route (Bearer Access Token)
    AuthAPI->>Security: require_roles([Instructor, Admin])
    Security->>DB: Query User DB Role
    alt Authorized
        Security-->>AuthAPI: Allow Access
        AuthAPI-->>Client: 200 OK Response Data
    else Unauthorized
        Security-->>Client: 403 Forbidden (AppException)
    end
```

---

## 📚 Phase 3: Learner Profile, Course & Lesson Content Infrastructure

### 1. Expected Requirements
- Learner profile retrieval & updating (`GET`/`PUT /api/v1/users/profile`).
- Complete Learning Goals CRUD management (`GET`, `POST`, `PUT`, `DELETE /api/v1/users/goals`).
- Structured Course Hierarchy (`Course` $\rightarrow$ `CourseModules` $\rightarrow$ `Lessons` $\rightarrow$ `Signs`).
- Lesson CRUD endpoints with RBAC authorization (`POST`, `PUT`, `DELETE /api/v1/lessons/` restricted to `Instructor` and `Administrator`).
- Interactive frontend curriculum view with live search filtering and detail modal.

### 2. Implemented Specifications & Code Structure
- **DTO Schemas**: [`backend/app/schemas/dto.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/schemas/dto.py) (`ProfileUpdate`, `ProfileResponse`, `GoalCreate`, `GoalUpdate`, `GoalResponse`, `LessonCreate`, `LessonUpdate`, `LessonResponse`, `CourseResponse`).
- **Profile Router**: [`backend/app/api/users.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/users.py)
- **Lessons Router**: [`backend/app/api/lessons.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/lessons.py)
- **Frontend View**: [`frontend/src/pages/learner/Lessons.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/learner/Lessons.jsx)

### 3. Testing Plan & Automated Verification
- **Test Suite**: [`backend/tests/test_phase3_content.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/tests/test_phase3_content.py)
- **Tests Executed**:
  1. `test_01_profile_retrieval_and_update`: ✅ PASSED
  2. `test_02_learning_goals_crud`: ✅ PASSED (Create, list, update to completed, delete)
  3. `test_03_courses_and_lessons_retrieval`: ✅ PASSED (Course hierarchy & lessons list)
  4. `test_04_lesson_crud_authorization`: ✅ PASSED (Learner 403 Forbidden, Instructor CRUD success)
- **Result**: **4/4 Tests Passed (100%)**.

### 4. Architecture & Flow of Plan

```mermaid
sequenceDiagram
    participant Learner
    participant Instructor
    participant LessonsAPI as /api/v1/lessons
    participant DB as Neon Cloud PostgreSQL

    Learner->>LessonsAPI: GET /lessons/ (List Lessons)
    LessonsAPI->>DB: SELECT * FROM lessons ORDER BY order_index
    DB-->>LessonsAPI: Lessons List
    LessonsAPI-->>Learner: 200 OK

    Learner->>LessonsAPI: POST /lessons/ (Create Lesson)
    LessonsAPI->>LessonsAPI: require_roles([Instructor, Admin])
    LessonsAPI-->>Learner: 403 Forbidden (Role 'Learner' unauthorized)

    Instructor->>LessonsAPI: POST /lessons/ (Create Lesson)
    LessonsAPI->>DB: INSERT INTO lessons ...
    DB-->>LessonsAPI: Lesson Created (ID 26)
    LessonsAPI-->>Instructor: 201 Created Response
```

---

## 🧠 Intelligent Platform & Adaptive Learning Engine Core

### 1. Expected Requirements
- Closed-Loop Assessment Workflow:
  $$\text{Assessment} \rightarrow \text{Analytics} \rightarrow \text{Learner Profile} \rightarrow \text{Learner State} \rightarrow \text{Feedback} \rightarrow \text{Recommendation} \rightarrow \text{Dashboard}$$
- Data-driven 5-State Machine (`Not Attempted`, `Learning`, `Improving`, `Mastered`, `Needs Revision`).
- Persistent state transition logging in `learner_state_history` table.
- Adaptive Recommendation Engine providing explicit data-driven reasons based on consecutive mistakes, accuracy percentages, and unattempted signs.
- Complete execution without page refreshes.

### 2. Implemented Specifications & Code Structure
- **State Machine Evaluator**: [`backend/app/services/learner_state_service.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING AND ASSESSNMENT/backend/app/services/learner_state_service.py)
- **Recommendation Engine**: [`backend/app/services/recommendation_service.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING AND ASSESSNMENT/backend/app/services/recommendation_service.py)
- **Adaptive Pipeline**: [`backend/app/services/adaptive_learning_service.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING AND ASSESSNMENT/backend/app/services/adaptive_learning_service.py)
- **Assessment Router**: [`backend/app/api/assessment.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING AND ASSESSNMENT/backend/app/api/assessment.py)

### 3. Testing Plan & Automated Verification
- **Test Suite**: [`backend/tests/test_adaptive_learning.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING AND ASSESSNMENT/backend/tests/test_adaptive_learning.py)
- **3-Session Simulation Test**:
  - *Session 1*: Poor accuracy on sign 'D' $\rightarrow$ State transitions to `LEARNING` $\rightarrow$ Recommendation generated: *"Focus on sign 'D' - repeated low accuracy"*.
  - *Session 2*: 3 consecutive mistakes on 'D' $\rightarrow$ State transitions to `NEEDS_REVISION` $\rightarrow$ Priority recommendation generated: *"High mistake count on 'D'"*.
  - *Session 3*: High score (95%) $\rightarrow$ State transitions to `MASTERED` $\rightarrow$ Recommendation shifts to unattempted sign 'E'.
- **Result**: **100% Passed**.

### 4. Architecture & Flow of Plan

```mermaid
flowchart TD
    A[Webcam Assessment Attempt] -->|POST /api/v1/assessment/submit| B[Assessment Pipeline]
    B --> C[Compute Gesture, Hand Shape, Motion Metrics]
    C --> D[Log AssessmentAttempt in DB]
    D --> E[Evaluate State Machine Transitions]
    E -->|State Shift| F[Log LearnerStateHistory]
    E --> G[Update LearnerProfile Performance & Streak]
    G --> H[Run Adaptive Recommendation Engine]
    H -->|Generate Reasoned Priority Actions| I[Store Recommendations in DB]
    I --> J[Return Unified Payload to Dashboard]
```

---

## 🗺️ Roadmap & Architecture Specifications for Phases 4–35

| Phase Block | Target Scope | Architecture & Testing Plan |
| :--- | :--- | :--- |
| **Phases 4–9** | Dataset Explorer, MediaPipe Hand Tracking, Landmark Extraction & Normalization | `scripts/dataset_explorer.py`, landmark extraction into CSV, min-max landmark normalization, stratified train/val/test splits. |
| **Phases 10–14** | Classifier Experiments, RF Hyperparameter Study, Error Analysis & Inference Benchmarking | Train Random Forest vs SVM vs Decision Tree, generate `error_analysis.md`, evaluate latency (<50ms target) in `benchmark_report.md`. |
| **Phases 15–18** | 15 Webcam States UI, Temporal Buffers, Practice Sessions & Anatomical Feedback Engine | WebSockets / MediaPipe Web SDK, n-frame temporal buffer, joint alignment anatomical feedback engine (`backend/app/ai/feedback/`). |
| **Phases 23–26** | Complete 44 Frontend Sub-Pages across Learner, Instructor, Trainer & Admin Dashboards | Role-scoped routing, real-time metrics widgets, user management tables, curriculum authoring tools. |
| **Phases 27–35** | PDF/Excel Exports, Certification Module, CI/CD Pipeline, Production Deployment | ReportLab PDF generator, OpenPyXL exporter, GitHub Actions workflow, Docker production build & AWS/Azure deployment manifests. |

---

### 📌 Document Maintenance Notice
*This document is automatically updated upon the completion and verification of each implementation phase.*
