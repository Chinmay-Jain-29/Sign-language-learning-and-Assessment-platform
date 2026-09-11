# Final Project Repository Structure

This document records the complete, organized repository structure of the **AI-Powered Sign Language Learning & Assessment Platform** prepared for GitHub release.

---

```text
PROJECT_ROOT/
├── .github/
│   └── workflows/
│       └── ci.yml                             # Automated multi-job CI workflow (Backend tests + Frontend build)
│
├── backend/
│   ├── app/
│   │   ├── ai/                                # AI Subsystems & MediaPipe Hand Tracking
│   │   │   ├── assessment/                    # Multi-dimensional gesture evaluator & scoring config
│   │   │   ├── feedback/                      # Modular landmark geometry rules & feedback engine
│   │   │   ├── gesture_recognition/           # Real-time gesture classifier wrapper
│   │   │   ├── hand_tracking/                 # MediaPipe 21 3D landmark detector & schemas
│   │   │   ├── ml/                            # Machine learning models & training modules
│   │   │   │   └── models/
│   │   │   │       └── gesture_model.joblib   # Production lightweight gesture model (2.34 MB)
│   │   │   ├── preprocessing/                 # Wrist translation & scale normalization
│   │   │   ├── temporal/                      # Landmark temporal stabilizer & sliding buffer
│   │   │   ├── benchmark_service.py           # Inference latency benchmarking
│   │   │   ├── classifier_service.py          # Classifier comparison service
│   │   │   ├── error_analysis_service.py      # Error analysis & confusion matrix service
│   │   │   ├── landmark_extraction_service.py # Batch landmark extraction service
│   │   │   ├── pipeline.py                    # Production end-to-end AI Pipeline
│   │   │   └── rf_hyperparameter_service.py   # Random Forest hyperparameter study service
│   │   │
│   │   ├── api/                               # REST API Routes & Controllers
│   │   │   ├── v1/                            # Version 1 route namespace
│   │   │   │   ├── auth.py                    # Authentication & token endpoints
│   │   │   │   ├── ai.py                      # AI inspection & benchmark endpoints
│   │   │   │   └── health.py                  # Service health check
│   │   │   ├── achievements.py                # Achievement definitions & direct practice routes
│   │   │   ├── admin.py                       # Administrator governance & level management
│   │   │   ├── analytics.py                   # Role-based dashboard analytics
│   │   │   ├── assessment.py                  # Assessment attempt evaluators & scoring
│   │   │   ├── certification.py               # Skill certificates generator
│   │   │   ├── instructions.py                # Instructor & admin private instructions
│   │   │   ├── lessons.py                     # Curriculum & alphabet lessons
│   │   │   ├── notifications.py               # User notifications & alerts
│   │   │   ├── practice.py                    # Real-time practice session controllers
│   │   │   ├── recommendations.py             # Adaptive practice recommendations
│   │   │   ├── reports.py                     # PDF & Excel report exports
│   │   │   └── users.py                       # User profiles & photo upload
│   │   │
│   │   ├── core/                              # Core Configuration, Security & Utilities
│   │   │   ├── config.py                      # Pydantic BaseSettings environment config
│   │   │   ├── exceptions.py                  # Centralized AppException handlers
│   │   │   ├── logging.py                     # Standardized application logger
│   │   │   ├── response.py                    # Standard response envelopes
│   │   │   └── security.py                    # Bcrypt hashing & JWT token handling
│   │   │
│   │   ├── database/                          # Database Connections & Initializers
│   │   │   ├── init_db.py                     # Schema initialization & role/user seeder
│   │   │   └── session.py                     # SQLAlchemy engine & SessionLocal generator
│   │   │
│   │   ├── models/                            # Domain Entities & Database Schemas
│   │   │   └── domain.py                      # 24 normalized SQLAlchemy ORM models
│   │   │
│   │   ├── repositories/                      # Data Access Layer Abstractions
│   │   │   ├── user_repository.py             # User & profile repository
│   │   │   └── lesson_repository.py           # Lesson & sign repository
│   │   │
│   │   ├── schemas/                           # Pydantic Request & Response DTOs
│   │   │   └── dto.py                         # Request/Response validation schemas
│   │   │
│   │   ├── services/                          # Business Logic & Adaptive Engines
│   │   │   ├── adaptive_learning_service.py   # Closed-loop adaptive learning
│   │   │   ├── learner_state_service.py       # Mastery state transitions
│   │   │   ├── notification_service.py        # Real-time notification dispatcher
│   │   │   └── recommendation_service.py      # Recommendation generation
│   │   │
│   │   └── main.py                            # FastAPI application entrypoint & static mount
│   │
│   ├── tests/                                 # 33 Backend Unit, Integration & API Test Suites
│   ├── uploads/avatars/                       # User profile avatars storage (.gitkeep)
│   ├── .env.example                           # Backend environment template
│   ├── Dockerfile                             # Backend container definition
│   └── requirements.txt                       # Python dependencies
│
├── frontend/
│   ├── public/                                # Static web assets & icons
│   ├── src/
│   │   ├── api/                               # Axios HTTP client configuration
│   │   ├── assets/                            # SVG icons, logos, and UI graphics
│   │   ├── components/                        # Reusable React components
│   │   │   ├── common/                        # Buttons, inputs, badges, cards, modals, error boundaries
│   │   │   ├── feedback/                      # Camera visual states & feedback overlays
│   │   │   ├── layout/                        # Navigation bars, headers, footers, sidebars
│   │   │   └── practice/                      # Practice canvas, target display, level guards
│   │   ├── context/                           # AuthContext & ThemeContext providers
│   │   ├── pages/                             # 44 Role-Based Application Pages
│   │   │   ├── auth/                          # Login, Register, Forgot Password
│   │   │   ├── learner/                       # Dashboard, Practice, Modes, Assessments, Profile
│   │   │   ├── instructor/                    # Instructor Dashboard, Classroom, Instructions
│   │   │   ├── trainer/                       # Accessibility Trainer Portal & Feedback
│   │   │   └── admin/                         # User management, Level control modal, Analytics
│   │   ├── routes/                            # Route definitions & Role-Based Route Guards
│   │   ├── App.jsx                            # React Router tree & error boundary wrapper
│   │   ├── index.css                          # Tailwind CSS styling & design system tokens
│   │   └── main.jsx                           # React DOM root mounting
│   ├── .env.example                           # Frontend environment template
│   ├── Dockerfile                             # Frontend Nginx container definition
│   ├── package.json                           # NPM dependencies & scripts
│   ├── package-lock.json                      # Deterministic package lockfile
│   └── vite.config.js                         # Vite bundler configuration
│
├── ml/
│   ├── preprocessing/                         # Landmark extraction & scale normalization
│   ├── training/                              # Classifier training & hyperparameter search
│   ├── evaluation/                            # Inference benchmark & error analysis
│   ├── inference/                             # Camera test & prediction scripts
│   ├── experiments/                           # Experiment run configs & logs
│   └── README.md                              # Complete ML Framework guide
│
├── datasets/
│   ├── asl_alphabet/                          # ASL Alphabet dataset placeholder (.gitkeep)
│   ├── sign_mnist/                            # Sign MNIST dataset placeholder (.gitkeep)
│   ├── wlasl/                                 # WLASL video corpus placeholder (.gitkeep)
│   ├── rwth_phoenix/                          # RWTH Phoenix corpus placeholder (.gitkeep)
│   ├── features/                              # Extracted features placeholder (.gitkeep)
│   ├── README.md                              # Dataset acquisition & extraction guide
│   └── .gitkeep                               # Directory keeper
│
├── models/
│   ├── asl_rf_v001/                           # Model package metadata & labels (.gitkeep)
│   ├── README.md                              # Trained model registry & export guide
│   └── .gitkeep                               # Directory keeper
│
├── scripts/                                   # Operational & Developer CLI Utilities
│   ├── benchmark_inference.py                 # Latency & throughput benchmarking
│   ├── camera_test.py                         # Live webcam validation & FPS counter
│   ├── dataset_audit_pipeline.py              # End-to-end dataset audit & extraction
│   ├── dataset_explorer.py                    # Dataset class balance & sample inspector
│   ├── dataset_quality_reporter.py            # Preprocessing quality validation
│   ├── error_analysis.py                      # Confusion matrix & per-class error analysis
│   ├── extract_landmarks.py                   # MediaPipe batch landmark extractor
│   ├── image_loader.py                        # Dataset image batch loader
│   ├── normalize_dataset.py                   # Coordinate translation/scale normalizer
│   ├── split_dataset.py                       # Stratified train/val/test dataset splitter
│   ├── study_rf_hyperparameters.py            # Random Forest grid search optimizer
│   └── train_classifiers.py                   # Multi-model classifier trainer
│
├── docs/                                      # Complete Technical Documentation
│   ├── README.md                              # Documentation table of contents
│   ├── architecture.md                        # Multi-tier system architecture
│   ├── api.md                                 # REST API specification
│   ├── database.md                            # Database schema & entity models
│   ├── ml_pipeline.md                         # End-to-end machine learning pipeline
│   ├── deployment.md                          # Deployment & Docker containerization
│   ├── testing.md                             # Test suite architecture & instructions
│   ├── uiux.md                                # Accessibility & UI/UX design system
│   ├── REPOSITORY_AUDIT.md                    # Pre-release repository audit report
│   ├── PROJECT_STATUS.md                      # Feature status & project roadmap
│   └── FINAL_PROJECT_STRUCTURE.md             # This document
│
├── reports/                                   # Performance & Evaluation Reports
│   ├── benchmark_report.json                  # P50/P90/P99 latency benchmarks
│   ├── classifier_experiments_report.json     # Multi-classifier accuracy comparison
│   ├── dataset_audit.json                     # Dataset statistics & class distribution
│   ├── dataset_quality_report.json            # Missing keypoint & occlusion checks
│   ├── error_analysis_report.json             # Confusion matrix & false-positive analysis
│   ├── rf_hyperparameter_study.json           # Grid search parameter evaluation
│   └── README.md                              # Summary of benchmark results
│
├── tests/
│   ├── README.md                              # Test overview & execution manual
│   └── .gitkeep                               # Directory keeper
│
├── docker/
│   ├── Dockerfile.backend                     # Backend container definition
│   ├── Dockerfile.frontend                    # Frontend container definition
│   └── README.md                              # Docker instructions
│
├── uploads/avatars/                           # Root avatar uploads directory (.gitkeep)
│
├── .env.example                               # Global environment configuration template
├── .gitattributes                             # Cross-platform line ending normalization (LF)
├── .gitignore                                 # Comprehensive Git ignore rules
├── docker-compose.yml                         # Full-stack Docker Compose orchestration
├── Dockerfile.backend                         # Root alias for backend Dockerfile
├── Dockerfile.frontend                        # Root alias for frontend Dockerfile
├── LICENSE                                    # Open source MIT License
├── README.md                                  # Production project README
├── RUN_GUIDE.md                               # Local development & quickstart guide
└── CHANGELOG.md                               # Version 1.0.0 release notes
```
