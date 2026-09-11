# Phase 3 Documentation: Learner Profile, Course & Lesson Content Infrastructure

This document details the expected objectives, actual implementation, architecture diagram, and test plan for **Phase 3**.

---

## 1. Expected To Do (Requirements & Objectives)
- Provide API endpoints for fetching and updating learner profiles (`GET`/`PUT /api/v1/users/profile`).
- Build complete Learning Goals CRUD management (`/api/v1/users/goals`).
- Build structured Course and Lesson hierarchy (`Course` $\rightarrow$ `CourseModules` $\rightarrow$ `Lessons` $\rightarrow$ `Signs`).
- Implement RBAC-enforced lesson content management (`POST`, `PUT`, `DELETE /api/v1/lessons/` restricted to `Instructor` and `Administrator` roles).
- Update frontend Curriculum page with live API fetch, search input filter, detail modal, and direct practice shortcuts.

---

## 2. Implementation Details

### Data Transfer Objects (DTOs)
- [`backend/app/schemas/dto.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/schemas/dto.py): Added `ProfileUpdate`, `ProfileResponse`, `GoalCreate`, `GoalUpdate`, `GoalResponse`, `LessonCreate`, `LessonUpdate`, `LessonResponse`, `CourseResponse`.

### Backend API Routers
- [`backend/app/api/users.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/users.py):
  - `GET /api/v1/users/profile`
  - `PUT /api/v1/users/profile`
  - `GET /api/v1/users/goals`
  - `POST /api/v1/users/goals`
  - `PUT /api/v1/users/goals/{goal_id}`
  - `DELETE /api/v1/users/goals/{goal_id}`
- [`backend/app/api/lessons.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/lessons.py):
  - `GET /api/v1/lessons/courses`
  - `GET /api/v1/lessons/`
  - `GET /api/v1/lessons/{lesson_id}`
  - `POST /api/v1/lessons/` (Requires Instructor / Admin role)
  - `PUT /api/v1/lessons/{lesson_id}` (Requires Instructor / Admin role)
  - `DELETE /api/v1/lessons/{lesson_id}` (Requires Instructor / Admin role)

### Frontend Page
- [`frontend/src/pages/learner/Lessons.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/learner/Lessons.jsx): Live search filter, interactive lesson detail modal, practice shortcut triggers.

---

## 3. Architecture & Workflow Diagram

```mermaid
graph TB
    subgraph FrontendCurriculum ["📚 1. Frontend Curriculum Layer"]
        LessonsPage["Lessons.jsx Page"]
        SearchFilter["Live Search Filter Input"]
        LessonModal["Lesson Details Modal"]
    end

    subgraph APIRouters ["⚡ 2. Content API Controllers"]
        UsersRouter["Users Router (/api/v1/users/)\nProfile & Learning Goals CRUD"]
        LessonsRouter["Lessons Router (/api/v1/lessons/)\nCourse Hierarchy & Lessons CRUD"]
        RBACCheck["require_roles([Instructor, Admin])\nContent Authoring Auth Check"]
    end

    subgraph NeonDB ["🗄️ 3. Neon Cloud PostgreSQL Engine"]
        ProfilesTable[("learner_profiles Table")]
        GoalsTable[("learning_goals Table")]
        CoursesTable[("courses & course_modules Tables")]
        LessonsTable[("lessons & signs Tables")]
    end

    LessonsPage --> SearchFilter
    LessonsPage -->|GET /api/v1/lessons/| LessonsRouter
    LessonsRouter -->|Query Ordered Lessons| LessonsTable
    LessonsTable -->> LessonsPage: Return 26 Alphabet Lessons

    LessonsPage -->|Click Lesson| LessonModal
    LessonModal -->|Trigger Practice| PracticePage["Practice WebApp (/practice)"]

    InstructorClient["Instructor Dashboard"] -->|POST /api/v1/lessons/| RBACCheck
    RBACCheck -->|Authorized| LessonsRouter
    LessonsRouter -->|INSERT INTO lessons| LessonsTable
    
    LearnerClient["Learner Account"] -->|POST /api/v1/lessons/| RBACCheck
    RBACCheck -->> LearnerClient: 403 Forbidden Response
```

---

## 4. Test Plan & Verification Results

### Automated Unit Test Suite
- Test Script: [`backend/tests/test_phase3_content.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/tests/test_phase3_content.py)

### Execution Command
```bash
cd backend
py -m unittest tests/test_phase3_content.py
```

### Verification Audit Results
```text
test_01_profile_retrieval_and_update (tests.test_phase3_content.Phase3ContentInfrastructureTestSuite) ... ok
test_02_learning_goals_crud (tests.test_phase3_content.Phase3ContentInfrastructureTestSuite) ... ok
test_03_courses_and_lessons_retrieval (tests.test_phase3_content.Phase3ContentInfrastructureTestSuite) ... ok
test_04_lesson_crud_authorization (tests.test_phase3_content.Phase3ContentInfrastructureTestSuite) ... ok

----------------------------------------------------------------------
Ran 4 tests in 61.876s
OK
```
- Status: **4/4 Tests Passed (100%)**.
