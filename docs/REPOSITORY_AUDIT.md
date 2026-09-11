# Repository Audit & GitHub Release Preparation Report

**Date**: September 2026  
**Project**: AI-Powered Sign Language Learning & Assessment Platform  
**Target**: Production-grade Open Source GitHub Release

---

## 1. Executive Summary

A full audit of the repository was conducted across **106,100 files** (~6.94 GB total disk footprint).
The primary disk usage consists of raw image datasets (**99,045 files**, ~6.57 GB) and pre-installed frontend dependencies (`node_modules`).

This audit establishes:
1. Complete separation of source code from heavy datasets and compiled model binaries.
2. Exclusion of local secrets, database files, temporary caches, and logs.
3. Establishment of a professional multi-tiered architecture with organized `frontend/`, `backend/`, `ml/`, `datasets/`, `models/`, `scripts/`, `docs/`, `reports/`, and `.github/` directories.

---

## 2. Current Directory Structure Breakdown

```
PROJECT_ROOT/
├── .github/                       # CI/CD Workflows
├── backend/                       # FastAPI application & test suites (220 files, 7.3 MB)
│   ├── app/
│   │   ├── ai/                    # ML integration, MediaPipe, evaluators
│   │   ├── api/                   # REST API routes (v1 endpoints, role-based controllers)
│   │   ├── core/                  # Security, logging, exceptions, config
│   │   ├── database/              # SQLAlchemy session & seed initializers
│   │   ├── models/                # Domain models & SQLite/PostgreSQL schemas
│   │   ├── repositories/          # Data access abstractions
│   │   ├── schemas/               # Pydantic DTOs
│   │   ├── services/              # Business logic & adaptive learning engines
│   │   └── main.py                # FastAPI entry point
│   ├── tests/                     # 33 unit and integration test suites
│   ├── uploads/                   # Uploaded avatars (runtime generated)
│   ├── Dockerfile                 # Backend container definition
│   └── requirements.txt           # Python dependency specifications
├── datasets/                      # Raw datasets & extraction artifacts (99,045 files, 6.57 GB)
│   ├── asl_alphabet/              # 87,028 raw Kaggle ASL images (MUST NOT BE TRACKED)
│   ├── wlasl/                     # 11,987 raw WLASL video/image files (MUST NOT BE TRACKED)
│   ├── sign_mnist/                # Sign MNIST subset
│   ├── *.csv                      # Extracted feature CSVs (train, val, test, landmarks)
│   └── *.json                     # Dataset quality and split JSON reports
├── docs/                          # Architecture & phase specifications (34 files)
├── experiments/                   # Experiment configs and run notes
├── frontend/                      # React + Vite frontend application (6,755 files, 129 MB)
│   ├── src/
│   │   ├── api/                   # Axios API client
│   │   ├── assets/                # Static SVGs, icons, illustrations
│   │   ├── components/            # Reusable UI & practice components
│   │   ├── context/               # Auth & Theme React contexts
│   │   ├── pages/                 # Role-based pages (auth, learner, instructor, trainer, admin)
│   │   ├── routes/                # Router configurations & route guards
│   │   ├── App.jsx                # Main React router shell
│   │   └── main.jsx               # React DOM bootstrap
│   ├── public/                    # Static assets
│   ├── node_modules/              # NPM package dependencies (MUST NOT BE TRACKED)
│   ├── package.json               # Frontend dependencies & scripts
│   ├── vite.config.js             # Vite bundler configuration
│   └── Dockerfile                 # Frontend container definition
├── models/                        # Trained ML models & metadata (9 files, 230 MB)
│   ├── asl_rf_v001/               # Production pipeline export (model.joblib, metadata.json)
│   └── *.joblib                   # DecisionTree, KNN, SVM, RandomForest checkpoints
├── preprocessing/                 # Landmark normalization scripts
├── scripts/                       # Developer utility scripts (audit, explorer, camera test)
├── uploads/                       # Root uploads folder
├── .env.example                   # Environment configuration template
├── docker-compose.yml             # Full-stack container orchestration
├── Dockerfile.backend             # Root alias for backend Dockerfile
├── Dockerfile.frontend            # Root alias for frontend Dockerfile
├── README.md                      # Primary project documentation
├── RUN_GUIDE.md                   # Local execution guide
└── sign_language.db               # Local SQLite database (MUST NOT BE TRACKED)
```

---

## 3. Categorization: Files to Track vs. Exclude

### Files That MUST Be Tracked (Source Code & Core Config)
- **Frontend Source**: `frontend/src/**/*`, `frontend/public/**/*`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.js`, `frontend/Dockerfile`
- **Backend Source**: `backend/app/**/*`, `backend/tests/**/*`, `backend/requirements.txt`, `backend/Dockerfile`
- **ML Tooling**: `ml/**/*`, training pipelines, inference evaluators
- **Documentation**: `docs/**/*`, `README.md`, `CHANGELOG.md`, `LICENSE`
- **CI/CD & DevOps**: `.github/workflows/ci.yml`, `docker-compose.yml`, `.env.example`, `.gitignore`, `.gitattributes`
- **Directory Keepers**: `datasets/README.md`, `datasets/.gitkeep`, `models/README.md`, `models/.gitkeep`, `reports/README.md`

### Files That MUST NOT Be Tracked (Ignored / Excluded)
1. **Raw Heavy Datasets**:
   - `datasets/asl_alphabet/**` (87,000+ files, ~5GB)
   - `datasets/wlasl/**` (11,000+ files, ~1.5GB)
   - `datasets/*.csv` (30MB+ raw landmark CSV extractions)
2. **Heavy Model Binaries**:
   - `models/*.joblib` (85MB+ raw training artifacts; re-creatable via `ml/training/train_classifiers.py`)
   - Note: Active lightweight runtime model (`backend/app/ai/ml/models/gesture_model.joblib`, 2.3MB) or downloadable releases.
3. **Environment Secrets & Local DBs**:
   - `.env`, `.env.local`, `backend/.env`
   - `sign_language.db`, `*.sqlite`, `*.db`
   - `uploads/avatars/*` (runtime user uploads)
4. **Build & Dependency Outputs**:
   - `frontend/node_modules/`, `frontend/dist/`, `frontend/build/`
   - `**/__pycache__/`, `**/*.pyc`, `.pytest_cache/`, `.mypy_cache/`
5. **OS & IDE Caches**:
   - `.DS_Store`, `Thumbs.db`, `.vscode/`, `.idea/`, `*.log`

---

## 4. Secrets & Credentials Audit

| Target Area | Finding | Status / Remediation |
| :--- | :--- | :--- |
| **`backend/.env`** | Local development secret file present | Added to `.gitignore`; clean `.env.example` created. |
| **`docs/FOUNDATION_PHASE_DOCUMENT.md`** | Mentioned legacy connection URI string | Redacted to standard environment template format `postgresql://USER:PASSWORD@HOST:PORT/DB`. |
| **`docs/PHASE_SPECIFICATION_AND_ARCHITECTURE_DOCUMENT.md`** | Sample connection URI in architectural doc | Redacted to template placeholder format. |
| **`backend/app/core/config.py`** | Default development `SECRET_KEY` string | Safe development fallback configured; documented requirement to set `SECRET_KEY` in production `.env`. |
| **Hardcoded API Keys** | None found (0 external private keys or cloud secrets in repository) | ✅ Clean |

---

## 5. Recommended Final Structure

```
PROJECT_ROOT/
├── frontend/                      # React 18 + Vite + TailwindCSS SPA
├── backend/                       # FastAPI + SQLAlchemy + MediaPipe
├── ml/                            # Machine Learning Engineering Framework
│   ├── preprocessing/             # Landmark extraction and normalization
│   ├── training/                  # Classifier training & hyperparameter tuning
│   ├── evaluation/                # Benchmark inference & error analysis
│   ├── inference/                 # Real-time gesture prediction engine
│   ├── experiments/               # Experiment configurations & logs
│   └── README.md                  # Complete ML architecture & guide
├── datasets/                      # Dataset ingestion directory (README + .gitkeep)
├── models/                        # Trained weights storage (README + .gitkeep)
├── scripts/                       # Operational & developer utilities
├── docs/                          # Full technical architecture & guides
├── reports/                       # Training, benchmarking, and quality reports
├── tests/                         # Root test overview & documentation
├── docker/                        # Container configuration & entrypoints
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated backend test & frontend build CI
├── .env.example                   # Root environment template
├── .gitignore                     # Comprehensive ignore rules
├── .gitattributes                 # Cross-platform line ending normalization
├── docker-compose.yml             # Orchestration for local development
├── LICENSE                        # Open Source License (MIT)
├── README.md                      # Production README & quick start
└── CHANGELOG.md                   # Release history & feature log
```
