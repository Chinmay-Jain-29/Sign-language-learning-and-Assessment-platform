# API Reference Manual (`docs/api.md`)

All REST endpoints are versioned under `/api/v1/` and follow a unified JSON envelope standard.

---

## 1. Response Standards

### Success Envelope
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {},
  "error": null,
  "meta": {}
}
```

### Error Envelope
```json
{
  "success": false,
  "message": "Human readable error message",
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "details": {}
  },
  "meta": {}
}
```

---

## 2. Core Endpoint Summary

| Module | Method & Path | Authorization Role | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST /api/v1/auth/register` | Public | Register new user account |
| **Auth** | `POST /api/v1/auth/login` | Public | Authenticate user & issue OAuth2 tokens |
| **Auth** | `POST /api/v1/auth/refresh` | Public | Refresh expired access token |
| **Auth** | `POST /api/v1/auth/logout` | Authenticated | Revoke refresh token |
| **Users** | `GET /api/v1/users/me` | Authenticated | Fetch current user profile |
| **Lessons** | `GET /api/v1/lessons` | Authenticated | List all ASL sign lessons (A-Z) |
| **Lessons** | `POST /api/v1/lessons` | Instructor / Admin | Create new sign lesson |
| **Practice** | `POST /api/v1/practice/sessions/start` | Learner | Start new practice session |
| **Practice** | `POST /api/v1/practice/attempt` | Learner | Submit webcam landmark attempt |
| **Recognition** | `POST /api/v1/recognition/predict` | Authenticated | Perform AI image prediction |
| **Analytics** | `GET /api/v1/analytics/dashboard` | Learner | Fetch learner dashboard payload |
| **Reports** | `GET /api/v1/reports/performance/pdf` | Authenticated | Download PDF performance report |
| **Reports** | `GET /api/v1/reports/performance/excel` | Authenticated | Download Excel data report |
| **Certification**| `POST /api/v1/certification/submit` | Learner | Submit certification exam score |
| **Notifications**| `GET /api/v1/notifications` | Authenticated | Fetch user notification list |
| **Health** | `GET /api/v1/health` | Public | Service health check |
