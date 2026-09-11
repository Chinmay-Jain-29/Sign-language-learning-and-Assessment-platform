# Changelog

All notable changes to the **AI-Powered Sign Language Learning & Assessment Platform** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-09-11

### Initial GitHub Production Release

### Added
- **Authentication & RBAC**:
  - Secure JWT authentication with Access & Refresh token rotation and logout revocation.
  - Role-Based Access Control supporting 4 dedicated roles: `Learner`, `Instructor`, `Accessibility Trainer`, `Administrator`.
  - User profile management with customizable role fields, avatar photo uploads (JPEG, PNG, WebP with 5MB validation), and profile deletion.
- **Learner Level & Practice Modes**:
  - Controlled one-time learning level setup for learners (`Beginner`, `Intermediate`, `Expert`).
  - Immutable level protection preventing learner modification once set.
  - Administrator override endpoints with persistent audit history (`LearningLevelAudit`).
  - Tiered practice mode unlock rules (`Beginner` static letters, `Intermediate` timed challenges, `Expert` word sequences).
  - Achievement badge modal with direct single-click alphabet practice routing.
- **Machine Learning & Computer Vision**:
  - Real-time hand tracking pipeline powered by MediaPipe Hands extracting 21 3D spatial landmarks.
  - Scale and translation-invariant normalization algorithm zero-centering wrist coordinate and scaling by maximum bounding dimension.
  - Multi-classifier training suite (Random Forest, SVM, KNN, Decision Tree) with hyperparameter grid search and confusion matrix analysis.
  - Production Random Forest ensemble checkpoint (`models/asl_rf_v001/`) achieving 99.2% validation accuracy with sub-2ms inference latency.
  - 15-state real-time camera feedback engine detecting lighting, distance, occlusion, and hand stability.
- **Adaptive Learning & Mastery**:
  - State machine tracking sign progression across 5 states: `Not Attempted`, `Learning`, `Improving`, `Mastered`, `Needs Revision`.
  - Closed-loop recommendation engine identifying struggling signs and confusion pairs.
  - Timed skill assessment system with automatic competency certificates.
- **Monitoring & Reporting**:
  - Role-based real-time dashboard analytics with progress visualizers.
  - Private instructor and administrator instruction broadcast system with in-app notification dispatch.
  - Automated PDF and Excel performance report generator.
- **DevOps & Architecture**:
  - Multi-stage container definitions (`Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`).
  - GitHub Actions CI workflow for multi-version Python backend tests and Vite frontend build.
  - In-memory SQLite testing isolation across 33 test suites.
