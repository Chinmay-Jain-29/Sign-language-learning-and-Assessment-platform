# Phase 7 Documentation: Invalid Sample Handling & Dataset Quality Reporting

This document details the expected objectives, actual implementation, architecture diagram, and test plan for **Phase 7**.

---

## 1. Expected To Do (Requirements & Objectives)
- Build an automated Dataset Quality Reporter utility (`scripts/dataset_quality_reporter.py`) to audit landmark CSV datasets (`landmarks.csv`).
- Detect invalid samples:
  - Missing keypoints or `NaN`/`Infinity` float values.
  - Out-of-bounds coordinates ($x < -0.15$ or $x > 1.15$, $y < -0.15$ or $y > 1.15$).
  - Degenerate point collapse (all 21 hand keypoints collapsed into identical points).
- Separate valid rows into clean dataset (`landmarks_clean.csv`) and log quarantined samples into invalid dataset (`landmarks_invalid.csv`).
- Output structured dataset quality report (`dataset_quality_report.json`) calculating quality score percentages and failure breakdown reasons.
- Expose a backend service layer (`backend/app/ai/dataset_quality_service.py`) and API endpoint (`GET /api/v1/ai/dataset/quality-report`) with RBAC role protection.

---

## 2. Implementation Details

### Quality Audit Script Created (`scripts/`)
- [`scripts/dataset_quality_reporter.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/scripts/dataset_quality_reporter.py): `DatasetQualityReporter` class executing row validation, coordinate bounds checking, point collapse detection, clean CSV generation, and quarantine logging.

### Service Layer & API Endpoint
- [`backend/app/ai/dataset_quality_service.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/ai/dataset_quality_service.py): Service wrapper `audit_dataset_quality` executing dataset quality filtering programmatically.
- [`backend/app/api/v1/ai.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/v1/ai.py): Added `GET /api/v1/ai/dataset/quality-report` (Restricted to Instructor, Admin, and Trainer roles via `require_roles`).

---

## 3. Architecture & Workflow Diagram

```mermaid
graph TB
    subgraph RawLandmarkDataset ["📄 1. Extracted Landmark Input"]
        RawCSV[("datasets/landmarks.csv\n(65-Column Raw Keypoint Dataset)")]
    end

    subgraph QualityAuditEngine ["⚡ 2. Dataset Quality Audit & Validation Engine"]
        RowValidator["DatasetQualityReporter (dataset_quality_reporter.py)"]
        NaNFilter["NaN / Inf Value Filter"]
        BoundsFilter["Coordinate Bounds Filter\n(x, y in [-0.15, 1.15])"]
        CollapseFilter["Degenerate Point Collapse Detector"]
    end

    subgraph QuarantinedDatasets ["🗄️ 3. Processed Datasets & Quarantine"]
        CleanCSV[("datasets/landmarks_clean.csv\n(Verified 100% Valid Samples)")]
        InvalidCSV[("datasets/landmarks_invalid.csv\n(Quarantined Samples + Failure Reasons)")]
    end

    subgraph ServiceAPILayer ["⚙️ 4. Backend Service & API Controller"]
        QualityService["Dataset Quality Service (dataset_quality_service.py)"]
        QualityEndpoint["GET /api/v1/ai/dataset/quality-report"]
        RBACAuth["require_roles([Instructor, Admin, Trainer])"]
        QualityJSON[("datasets/dataset_quality_report.json\n(Quality Score % & Failure Breakdown)")]
    end

    RawCSV --> RowValidator
    RowValidator --> NaNFilter & BoundsFilter & CollapseFilter

    NaNFilter & BoundsFilter & CollapseFilter -->|Pass Verification| CleanCSV
    NaNFilter & BoundsFilter & CollapseFilter -->|Fail Validation| InvalidCSV

    RowValidator -->|Generate JSON Metrics| QualityJSON
    QualityJSON --> QualityService
    
    QualityEndpoint --> RBACAuth
    RBACAuth -->|Authorized Request| QualityService
    QualityService -->> QualityEndpoint: Return Quality Report Payload
```

---

## 4. Test Plan & Verification Results

### Automated Unit Test Suite
- Test Script: [`backend/tests/test_phase7_quality_report.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/tests/test_phase7_quality_report.py)

### Execution Command
```bash
cd backend
py -m unittest tests/test_phase7_quality_report.py
```

### Verification Audit Results
```text
test_01_dataset_quality_reporter_validation (tests.test_phase7_quality_report.Phase7DatasetQualityReportTestSuite) ... ok
test_02_quality_service (tests.test_phase7_quality_report.Phase7DatasetQualityReportTestSuite) ... ok
test_03_quality_report_api_authorization (tests.test_phase7_quality_report.Phase7DatasetQualityReportTestSuite) ... ok

----------------------------------------------------------------------
Ran 3 tests in 13.231s
OK
```
- Status: **3/3 Tests Passed (100%)**.
