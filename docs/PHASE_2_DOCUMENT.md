# Phase 2 Documentation: Authentication, Refresh Tokens & RBAC Security

This document details the expected objectives, actual implementation, architecture diagram, and test plan for **Phase 2**.

---

## 1. Expected To Do (Requirements & Objectives)
- Implement user registration and login endpoints using OAuth2 password bearer tokens.
- Issue dual JWT tokens: 24-hour Access Token and 7-day Refresh Token with unique UUID `jti` claims.
- Build refresh token rotation and instant logout revocation via PostgreSQL `refresh_tokens` table.
- Implement password reset token flow.
- Enforce strict Role-Based Access Control (RBAC) across 4 system roles (`Learner`, `Instructor`, `Accessibility Trainer`, `Administrator`) at the database layer.

---

## 2. Implementation Details

### Backend Auth & Security Files
- [`backend/app/core/security.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/core/security.py): JWT encoding/decoding, token creation with UUID `jti`, password hashing via `passlib` PBKDF2.
- [`backend/app/api/deps.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/deps.py): `get_current_user` dependency and `require_roles([allowed_roles])` dependency raising `403 Forbidden` (`FORBIDDEN`) on unauthorized access.
- [`backend/app/api/v1/auth.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/v1/auth.py): Authentication API endpoints:
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`
  - `GET /api/v1/auth/me`
  - `POST /api/v1/auth/forgot-password`
  - `POST /api/v1/auth/reset-password`

### Frontend UI Pages
- [`frontend/src/context/AuthContext.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/context/AuthContext.jsx): React Auth Context managing JWT storage and user state.
- [`frontend/src/pages/auth/Login.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/auth/Login.jsx): Login page with demo account presets.
- [`frontend/src/pages/auth/Register.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/auth/Register.jsx): User registration page.
- [`frontend/src/pages/auth/ForgotPassword.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/auth/ForgotPassword.jsx), [`ResetPassword.jsx`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/frontend/src/pages/auth/ResetPassword.jsx): Password recovery flow.

---

## 3. Architecture & Workflow Diagram

```mermaid
graph TB
    subgraph FrontendAuth ["🔑 1. Frontend Authentication Layer"]
        LoginUI["Login.jsx & Register.jsx"]
        AuthContext["AuthContext.jsx\n(Manage JWT Tokens in Storage)"]
    end

    subgraph SecurityPipeline ["⚡ 2. FastAPI Security & RBAC Middleware"]
        AuthEndpoints["Auth Router (/api/v1/auth)\nLogin / Register / Refresh / Logout"]
        SecurityCore["Security Module (security.py)\nPBKDF2 Hashing & JWT Signer"]
        GetCurUser["get_current_user Dependency\nDecode JWT & Verify Revocation"]
        RBACFilter["require_roles([allowed_roles])\nDB Role Authorization Check"]
    end

    subgraph DatabaseLayer ["🗄️ 3. Neon Cloud PostgreSQL Database"]
        UsersTable[("users Table\n(id, email, hashed_password, role)")]
        TokensTable[("refresh_tokens Table\n(id, jti, token, user_id, revoked)")]
    end

    LoginUI -->|Submit Credentials| AuthEndpoints
    AuthEndpoints --> SecurityCore
    SecurityCore -->|Query & Verify Password| UsersTable
    SecurityCore -->|Store Refresh Token jti| TokensTable
    AuthEndpoints -->> AuthContext: Return JWT Access (24h) + Refresh Token (7d)

    AuthContext -->|Bearer Access Token| GetCurUser
    GetCurUser -->|Query Valid User| UsersTable
    GetCurUser --> RBACFilter
    
    RBACFilter -->|Query DB Role| UsersTable
    RBACFilter -->>|Allowed Role| ProtectedEndpoint["Target API Controller"]
    RBACFilter -->>|Forbidden Role| DenyAccess["403 Forbidden Response\n(AppException FORBIDDEN)"]
```

---

## 4. Test Plan & Verification Results

### Automated Unit Test Suite
- Test Script: [`backend/tests/test_auth.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/tests/test_auth.py)

### Execution Command
```bash
cd backend
py -m unittest tests/test_auth.py
```

### Verification Audit Results
```text
test_login_success (tests.test_auth.AuthenticationTestSuite) ... ok
test_login_invalid_password (tests.test_auth.AuthenticationTestSuite) ... ok
test_me_endpoint_with_valid_token (tests.test_auth.AuthenticationTestSuite) ... ok
test_me_endpoint_invalid_token (tests.test_auth.AuthenticationTestSuite) ... ok
test_rbac_learner_denied_instructor_route (tests.test_auth.AuthenticationTestSuite) ... ok
test_rbac_instructor_allowed (tests.test_auth.AuthenticationTestSuite) ... ok
test_rbac_admin_allowed (tests.test_auth.AuthenticationTestSuite) ... ok
test_refresh_and_logout_revocation (tests.test_auth.AuthenticationTestSuite) ... ok

----------------------------------------------------------------------
Ran 8 tests in 8.412s
OK
```
- Status: **8/8 Tests Passed (100%)**.
