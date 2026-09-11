# 🚀 Complete Step-by-Step Guide: Running the AI Sign Language Platform

This master guide provides exact, copy-pasteable instructions for setting up, running, testing, and interacting with the entire AI Sign Language Learning & Assessment platform.

---

## 📑 Table of Contents
1. [System Prerequisites](#1-system-prerequisites)
2. [Project Architecture Overview](#2-project-architecture-overview)
3. [Quick Start: Option A (Local Setup - Recommended)](#3-quick-start-option-a-local-setup---recommended)
   - [Step 1: Terminal 1 - Start the Backend FastAPI Server](#step-1-terminal-1---start-the-backend-fastapi-server)
   - [Step 2: Terminal 2 - Start the Frontend React Client](#step-2-terminal-2---start-the-frontend-react-client)
4. [Quick Start: Option B (Docker Microservices Stack)](#4-quick-start-option-b-docker-microservices-stack)
5. [How to Use the Real-Time Practice System](#5-how-to-use-the-real-time-practice-system)
6. [Running the Automated Test Suites](#6-running-the-automated-test-suites)
7. [Environment Variables Reference (`.env`)](#7-environment-variables-reference-env)
8. [Troubleshooting & FAQ](#8-troubleshooting--faq)

---

## 1. System Prerequisites

Before running the application, ensure the following dependencies are installed on your machine:

| Tool | Minimum Version | Check Command | Installation Link |
| :--- | :---: | :---: | :--- |
| **Python** | 3.9+ | `python --version` or `py --version` | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 18+ (includes npm) | `node --version` and `npm --version` | [nodejs.org](https://nodejs.org/) |
| **Git** | 2.0+ | `git --version` | [git-scm.com](https://git-scm.com/) |
| **Webcam** | USB / Integrated | — | Camera permissions enabled in browser |

---

## 2. Project Architecture Overview

```text
SIGN LANGUAGE LEARNING AND ASSESSNMENT/
├── backend/                   # FastAPI Backend (REST API, Clean Architecture)
│   ├── app/
│   │   ├── ai/                # MediaPipe Hand Tracking, Preprocessing, Evaluator
│   │   ├── api/               # API Endpoints (/api/v1/)
│   │   ├── models/            # SQLAlchemy Database Domain Entities
│   │   └── main.py            # Uvicorn Application Entrypoint
│   └── requirements.txt       # Python Dependencies
├── frontend/                  # React 19 + Vite Frontend SPA (Tailwind CSS)
│   ├── src/
│   │   ├── pages/             # 44 Application Pages across 4 Role Portals
│   │   │   └── learner/Practice.jsx  # Real-Time Live Webcam Gesture Engine
│   │   └── App.jsx            # Router and Role-Based Route Guards
│   └── package.json           # Frontend Dependencies
├── models/
│   └── asl_rf_v001/           # Trained Production Random Forest Classifier (99.38% Acc)
├── datasets/                  # ASL Canonical Landmarks & Split Datasets
├── docker-compose.yml         # Container Orchestration
└── RUN_GUIDE.md               # This Step-by-Step Guide
```

---

## 3. Quick Start: Option A (Local Setup - Recommended)

Open **2 separate terminal windows** (Terminal 1 for Backend, Terminal 2 for Frontend).

---

### Step 1: Terminal 1 - Start the Backend FastAPI Server

1. Open your terminal (PowerShell, Command Prompt, or Bash) and navigate to the project directory:
   ```bash
   cd "d:/SIGN LANGUAGE LEARNING AND ASSESSNMENT"
   ```

2. *(Optional but Recommended)* Create and activate a Python Virtual Environment:
   ```powershell
   # Windows PowerShell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   ```bash
   # macOS / Linux / Git Bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install all backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Navigate into the `backend` directory:
   ```bash
   cd backend
   ```

5. Launch the FastAPI server with Uvicorn:
   ```bash
   py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

   **Expected Output in Terminal 1**:
   ```text
   INFO:     Started server process [PID]
   2026-08-21 18:40:00 - asl_platform - INFO - FastAPI application started cleanly!
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   ```

---

### Step 2: Terminal 2 - Start the Frontend React Client

1. Open a **second terminal window** and navigate to the `frontend` directory:
   ```bash
   cd "d:/SIGN LANGUAGE LEARNING AND ASSESSNMENT/frontend"
   ```

2. Install frontend dependencies (if not already done):
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

   **Expected Output in Terminal 2**:
   ```text
     VITE v8.2.1  ready in 420 ms

     ➜  Local:   http://localhost:5173/
     ➜  Network: use --host to expose
   ```

4. Open your browser and go to: **[http://localhost:5173/](http://localhost:5173/)**

---

## 4. Quick Start: Option B (Docker Microservices Stack)

If you have Docker Desktop installed, launch both services with a single command:

```bash
cd "d:/SIGN LANGUAGE LEARNING AND ASSESSNMENT"
docker-compose up --build -d
```

### Useful Docker Commands:
- View live backend logs: `docker-compose logs -f backend`
- Stop the containers: `docker-compose down`

---

## 5. How to Use the Real-Time Practice System

### Real-Time Workflow Walkthrough:

```text
[Step 1] Select Target Sign ('A' through 'Z')
   ↓
[Step 2] Click "Start Camera" (Grants Webcam Permission)
   ↓
[Step 3] Show your hand to the camera
   ↓
[Step 4] MediaPipe extracts 21 3D spatial coordinates in real time
   ↓
[Step 5] Trained ML Model (asl_rf_v001) automatically predicts the gesture
   ↓
[Step 6] Comparison:
   - Target Matches Predicted  ==>  ✅ CORRECT GESTURE (Green badge)
   - Target Mismatches Predicted ==>  ❌ INCORRECT (Red badge)
   - Unclear Hand Posture (<70%) ==>  ⚠️ UNCERTAIN (Amber badge)
   ↓
[Step 7] Switch Target Sign anytime without page refresh!
```

### Key Practice Page Features:
1. **Target Sign Only**: You only select what letter the system expects. There is **no manual "Performed Gesture" selector**; the AI model classifies your hand posture in real time.
2. **Instant Dynamic Target Switching**: Click any letter button (`[A]` through `[Z]`) while the camera is streaming. The UI immediately clears previous prediction state, flushes the temporal consensus buffer on the server, and starts evaluating the new target letter without requiring page refresh or restarting the camera.
3. **Cumulative Attempt Tracking**: Click **Record Attempt** to persist the verified attempt in the PostgreSQL database and update your alphabet skill mastery score.

---

## 6. Running the Automated Test Suites

Verify all layers of the platform with the automated test commands below:

### 1. Full Backend & ML Pipeline Unit Tests (70 Tests)
```bash
cd "d:/SIGN LANGUAGE LEARNING AND ASSESSNMENT"
py -m unittest discover -s backend/tests -p "test_*.py"
```

### 2. Parameterized 26-Class Assessment Tests (A–Z Validation)
```bash
py -m unittest backend/tests/test_generic_class_assessment.py
```

### 3. Continuous Target Switching Tests (Without Refresh)
```bash
py -m unittest backend/tests/test_target_switch_session.py
```

### 4. End-to-End Closed-Loop Test
```bash
py backend/tests/test_e2e_closed_loop.py
```

### 5. Frontend Production Bundle Build
```bash
cd "d:/SIGN LANGUAGE LEARNING AND ASSESSNMENT/frontend"
npm run build
```

---

## 7. Environment Variables Reference (`.env`)

The system works out-of-the-box with default configurations. To customize database credentials or JWT keys, configure a `.env` file in the project root:

```ini
# Application Configuration
ENVIRONMENT=development
PROJECT_NAME="AI Sign Language Platform"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# Database Connection (Neon Cloud PostgreSQL by default)
DATABASE_URL="postgresql://neondb_owner:npg_pDzLKR65Jowm@ep-billowing-flower-axjeigc3-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

# JWT Security
JWT_SECRET="production-secret-key-change-in-prod-2026"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Machine Learning & AI Settings
MODEL_VERSION="asl_rf_v001"
CONFIDENCE_THRESHOLD=0.70
AI_MODE="production"

# CORS Allowed Origins
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

---

## 8. Troubleshooting & FAQ

### Q1: Port 8000 or Port 5173 is already in use (`[Errno 10048]`).
**Fix:** Another process is holding the port. Find and terminate it, or run on an alternate port:
```powershell
# Windows PowerShell - Find process on port 8000
netstat -ano | findstr :8000
# Kill process by PID
taskkill /PID <PID_NUMBER> /F
```

### Q2: "Camera access denied or unavailable" in the Practice page.
**Fix:** 
1. Check browser address bar for the camera permission icon.
2. Ensure permissions are set to **"Allow"**.
3. Ensure no other application (Zoom, Teams, Skype) is exclusively locking the webcam hardware.

### Q3: Model reports "UNCERTAIN".
**Fix:** The model enforces a confidence threshold of **70%**. Position your hand centrally in the camera frame with good lighting and hold the gesture steady for 1–2 seconds.

---

## 🌐 Quick Access URL Summary

| Portal | URL | Description |
| :--- | :--- | :--- |
| **Interactive Web App** | **[http://localhost:5173/](http://localhost:5173/)** | Learner, Instructor & Admin Portals |
| **Live Interactive Practice** | **[http://localhost:5173/practice](http://localhost:5173/practice)** | Real-Time Webcam ASL Recognition |
| **Backend REST API** | **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** | Health & System Info |
| **OpenAPI / Swagger Docs** | **[http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)** | Interactive REST API Documentation |
