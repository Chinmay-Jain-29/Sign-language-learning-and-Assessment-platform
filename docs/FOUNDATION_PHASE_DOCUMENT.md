# Foundation Phase Documentation: Clean Architecture & Cloud Database Setup

This document details the expected objectives, actual implementation, architecture diagram, and test plan for the **Foundation Phase**.

---

## 1. Expected To Do (Requirements & Objectives)
- Establish a clean, multi-layered FastAPI backend architecture.
- Design 23 normalized database entities covering users, roles, profiles, courses, lessons, states, assessments, and tokens.
- Connect seamlessly to **Neon Cloud PostgreSQL** database.
- Standardize all API responses with envelope `{ success, message, data, error, meta }`.
- Build a health check endpoint (`GET /api/v1/health`) and dockerization setup.

---

## 2. Implementation Details

### Database & Environment Setup
- Configured [`backend/.env`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/.env) with PostgreSQL connection string template:
  `DATABASE_URL="postgresql://username:password@hostname:5432/dbname?sslmode=require"` (or local SQLite fallback `sqlite:///./sign_language.db`)
- Initialized database schema script in [`backend/app/database/init_db.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/database/init_db.py).

### Core Backend Files Created
- [`backend/app/database/session.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/database/session.py): SQLAlchemy SessionLocal generator.
- [`backend/app/models/domain.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/models/domain.py): 23 Domain Entities (`User`, `Role`, `UserRole`, `LearnerProfile`, `LearningGoal`, `Course`, `CourseModule`, `Lesson`, `Sign`, `LessonSign`, `LearnerAlphabetState`, `AssessmentAttempt`, `PracticeSession`, `Recommendation`, `RefreshToken`, `PasswordResetToken`, etc.).
- [`backend/app/core/exceptions.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/core/exceptions.py): Centralized `AppException` handler formatting standardized envelopes.
- [`backend/app/api/v1/health.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/v1/health.py): Health check API endpoint.
- [`Dockerfile`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/Dockerfile), [`docker-compose.yml`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/docker-compose.yml): Containerization setup.

---

## 3. Architecture & Workflow Diagram

```mermaid
graph TB
    subgraph ClientLayer ["💻 1. Presentation Layer"]
        WebClient["React + Vite Client\n(Port 5173)"]
    end

    subgraph APIGateway ["⚡ 2. FastAPI Gateway & Middleware (/api/v1)"]
        CorsMiddleware["CORS Middleware"]
        Router["ApiV1 Router Router"]
        HealthEndpoint["/health Endpoint Handler"]
        ErrorHandler["AppException Central Handler\nFormat Response Envelope"]
    end

    subgraph DataLayer ["🗄️ 3. Database Service Layer"]
        SessionManager["SQLAlchemy SessionLocal"]
        ORMModels["23 Domain Entities\n(User, Role, Course, Lesson, Attempt...)"]
    end

    subgraph CloudStorage ["☁️ 4. Cloud Database Engine"]
        NeonDB[("Neon Cloud PostgreSQL\n(Port 5432 SSL Pooler)")]
    end

    WebClient -->|HTTP GET /api/v1/health| CorsMiddleware
    CorsMiddleware --> Router
    Router --> HealthEndpoint
    HealthEndpoint -->|Verify Connection| SessionManager
    SessionManager --> ORMModels
    ORMModels -->|SSL Connection| NeonDB
    NeonDB -->> SessionManager: Connection Status OK
    SessionManager -->> HealthEndpoint: Database Healthy
    HealthEndpoint --> ErrorHandler
    ErrorHandler -->> WebClient: Envelope: { success: true, data: { status: "Healthy" } }
```

---

## 4. Test Plan & Verification Results

### Test Strategy
- Issue HTTP request to `/api/v1/health`.
- Verify database connection status and standardized JSON envelope format.

### Execution Command
```bash
curl http://127.0.0.1:8000/api/v1/health
```

### Verification Result
```json
{
  "success": true,
  "message": "System health check successful",
  "data": {
    "status": "Healthy",
    "service": "Sign Language Learning and Assessment",
    "version": "1.0.0",
    "environment": "development",
    "database": "Healthy",
    "ai_model_loaded": true
  },
  "error": null,
  "meta": {}
}
```
- Status: **100% Passed**.
