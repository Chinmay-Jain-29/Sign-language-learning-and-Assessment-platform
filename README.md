# AI-Powered Sign Language Learning & Assessment Platform

[![CI Pipeline](https://github.com/asl-platform/asl-learning-assessment/actions/workflows/ci.yml/badge.svg)](https://github.com/asl-platform/asl-learning-assessment/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18.x-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-00C853.svg)](https://mediapipe.dev/)

An enterprise-grade EdTech & Accessibility platform providing real-time AI gesture recognition, live webcam hand tracking, closed-loop adaptive practice, role-based dashboards, alphabet mastery tracking, and administrative governance for American Sign Language (ASL).

---

## 📑 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Directory Structure](#project-directory-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running Locally](#running-locally)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Deployment](#deployment)
- [Security & Secrets](#security--secrets)
- [License](#license)

---

## Overview

The platform bridges accessibility gaps by offering real-time AI computer vision feedback to sign language learners. It features interactive alphabet practice (A–Z), assessment simulations, real-time geometry analysis, adaptive curriculum recommendations, and 4 dedicated role-based portals (**Learner**, **Instructor**, **Accessibility Trainer**, and **Administrator**).

---

## Key Features

- **AI Real-Time Gesture Recognition**: 21-landmark 3D hand tracking with sub-25ms inference latency.
- **Interactive Practice Modes**: Beginner (Static Gestures), Intermediate (Timed Gestures), and Expert (Dynamic Sequences).
- **One-Time Learner Level Selection with Admin Governance**: Learners choose their initial proficiency (`Beginner`, `Intermediate`, `Expert`); subsequent adjustments are controlled by administrators with full audit logging.
- **Achievement & Alphabet Practice Navigation**: Direct alphabet practice jumps from achievement badges.
- **Granular Visual Feedback**: 15 distinct camera states handling low lighting, multiple hands, occlusions, and stability.
- **Adaptive Learning Engine**: Tracks sign mastery (`Not Attempted` $\rightarrow$ `Learning` $\rightarrow$ `Improving` $\rightarrow$ `Mastered`) and recommends targeted revision.
- **Role-Based Portals**:
  - **Learner Portal**: Interactive practice, assessment tests, progress analytics, achievements, and personal profile.
  - **Instructor Portal**: Curriculum oversight, learner progress monitoring, and classroom instruction broadcasts.
  - **Accessibility Trainer Portal**: Specialized feedback, trainer instructions, and learner session tracking.
  - **Administrator Portal**: System user governance, learner level control, audit logs, and performance reports.
- **PDF & Export Analytics**: Downloadable performance summaries and progress certificates.

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│              React 18 + Vite Frontend SPA               │
│          (Learner, Instructor, Trainer, Admin)          │
└────────────────────────────┬────────────────────────────┘
                             │ REST API / WebSocket
                             ▼
┌─────────────────────────────────────────────────────────┐
│               FastAPI Application Layer                 │
│         (/api/v1/ auth, users, practice, admin)         │
└──────────────┬───────────────────────────┬──────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────────┐ ┌────────────────────────┐
│      SQLAlchemy ORM DB       │ │   AI / ML Subsystem    │
│   (PostgreSQL / SQLite)      │ │ (MediaPipe + Scikit)   │
└──────────────────────────────┘ └────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, TailwindCSS, Lucide Icons, Axios | Responsive Single Page Application |
| **Backend** | Python 3.9+, FastAPI, Pydantic v2, Uvicorn | High-throughput REST API & Business Logic |
| **Database** | SQLAlchemy 2.0, PostgreSQL (Production) / SQLite (Dev) | Relational persistence & audit logs |
| **Computer Vision** | MediaPipe Hands, OpenCV | 21 3D hand landmark extraction & normalization |
| **Machine Learning** | scikit-learn, joblib, NumPy | Tuned Random Forest / SVM multi-class classifiers |
| **DevOps** | Docker, Docker Compose, GitHub Actions | Multi-stage containerization & automated CI |

---

## Project Directory Structure

```
PROJECT_ROOT/
├── frontend/               # React 18 frontend client
├── backend/                # FastAPI backend service
├── ml/                     # ML pipelines, training, & experiments
├── datasets/               # Dataset documentation & keeper guides
├── models/                 # Model checkpoints registry & metadata
├── scripts/                # Developer & ML CLI utilities
├── docs/                   # Technical architecture & phase documentation
├── reports/                # Performance benchmarks & evaluation reports
├── tests/                  # Test suite overview & instructions
├── docker/                 # Container Dockerfiles & deployment guides
├── .github/                # GitHub Actions CI workflows
├── .env.example            # Environment configuration template
├── .gitignore              # Git ignore rules
├── .gitattributes          # Line ending normalization
├── docker-compose.yml      # Local container orchestration
├── LICENSE                 # MIT License
├── README.md               # Primary project documentation
└── CHANGELOG.md            # Release history
```

---

## Prerequisites

- **Python**: `3.9` or higher
- **Node.js**: `18.x` or `20.x` (with `npm`)
- **Webcam**: Standard USB or integrated camera for real-time sign detection
- **Docker & Docker Compose** *(Optional, for containerized run)*

---

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/asl-platform/asl-learning-assessment.git
cd asl-learning-assessment
```

### 2. Configure Environment Variables
```bash
# Copy template configuration
cp .env.example .env
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## Running Locally

### Option A: Local Development Server

**Terminal 1 — Backend API**:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*API Documentation available at: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)*

**Terminal 2 — Frontend Client**:
```bash
cd frontend
npm run dev
```
*Frontend Application available at: [http://localhost:5173](http://localhost:5173)*

---

### Option B: Docker Compose

```bash
docker-compose up --build -d
```
- Frontend: `http://localhost/`
- Backend Health: `http://localhost:8000/api/v1/health`

---

## Default Test Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| **Learner** | `learner@example.com` | `password123` |
| **Administrator** | `admin@example.com` | `password123` |
| **Instructor** | `instructor@example.com` | `password123` |
| **Accessibility Trainer** | `trainer@example.com` | `password123` |

---

## Machine Learning Pipeline

1. **Landmark Extraction**: Detects 21 3D hand landmarks via MediaPipe Hands.
2. **Geometric Normalization**: Centers the wrist coordinate at $(0, 0, 0)$ and scales by maximum bounding dimension for distance/position invariance.
3. **Classifier Prediction**: Fast inference using trained Random Forest ensemble ($63$ input features $\rightarrow$ $29$ class probabilities).

To retrain the model locally:
```bash
python scripts/train_classifiers.py --train datasets/train.csv --val datasets/val.csv --output-dir models/
```
*See [`ml/README.md`](ml/README.md) for detailed ML documentation.*

---

## Testing & Quality Assurance

### Run Backend Tests (33 Test Suites):
```bash
cd backend
python -m unittest discover -s tests -p "test_*.py"
```

### Run Frontend Production Build:
```bash
cd frontend
npm run build
```

---

## Security & Secrets

- **Zero Secret Policy**: Do not commit `.env` files or API secrets.
- **Database Safety**: Production database credentials must be injected via environment variables.
- **Isolation**: Test suites run on in-memory SQLite instances to guarantee zero side-effects.

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
