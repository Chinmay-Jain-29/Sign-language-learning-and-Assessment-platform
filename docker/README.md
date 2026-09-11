# Docker Deployment & Containerization

This directory contains containerization definitions and deployment configurations for the **AI-Powered Sign Language Learning & Assessment Platform**.

---

## 1. Container Images

- **Backend (`Dockerfile.backend`)**: Python 3.9-slim container equipped with OpenCV/MediaPipe system libraries, FastAPI server, and scikit-learn runtime dependencies.
- **Frontend (`Dockerfile.frontend`)**: Multi-stage build (Node.js 20 builder $\rightarrow$ Nginx Alpine production server).

---

## 2. Running via Docker Compose

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Build and launch all services (Postgres, FastAPI Backend, React Frontend)
docker-compose up --build -d

# 3. View service logs
docker-compose logs -f backend

# 4. Stop all services
docker-compose down
```

---

## 3. Service Endpoints

| Container | Host Port | Internal Port | URL |
| :--- | :---: | :---: | :--- |
| **Frontend** | `80` | `80` | `http://localhost/` |
| **Backend** | `8000` | `8000` | `http://localhost:8000/api/v1/health` |
| **PostgreSQL** | `5432` | `5432` | `localhost:5432` |
