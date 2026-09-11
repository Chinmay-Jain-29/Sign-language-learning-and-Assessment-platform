# Deployment & Containerization Guide (`docs/deployment.md`)

## 1. Overview
The platform supports containerized deployment using Docker and Docker Compose, orchestrating PostgreSQL, Python FastAPI backend, and Nginx React frontend.

---

## 2. Docker Service Architecture

```text
               Client Web Browser (Port 80)
                           ↓
              Frontend Container (`Dockerfile.frontend`)
                     React 18 + Nginx
                           ↓
              Backend Container (`Dockerfile.backend`)
                    Python 3.9 + FastAPI
                           ↓
            PostgreSQL Database Container (Port 5432)
```

---

## 3. Deployment Commands

### Production Docker Compose Deployment
```bash
docker-compose up --build -d
```

### Checking Running Services
```bash
docker-compose ps
```

### Viewing Container Logs
```bash
docker-compose logs -f backend
```

---

## 4. Environment Variables Checklist (`.env`)
- `DATABASE_URL`: Connection string to PostgreSQL database.
- `JWT_SECRET`: Secret key for JWT token signing.
- `MODEL_PATH`: Path to production model binary (`models/asl_rf_v001/model.joblib`).
- `CONFIDENCE_THRESHOLD`: Confidence threshold (`0.75`).
- `CORS_ORIGINS`: Allowed CORS origins.
