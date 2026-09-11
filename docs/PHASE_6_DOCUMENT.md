# Phase 6 Documentation: Batch Landmark Extraction Pipeline

This document details the expected objectives, actual implementation, architecture diagram, and test plan for **Phase 6**.

---

## 1. Expected To Do (Requirements & Objectives)
- Build a Batch Landmark Extraction Pipeline (`scripts/extract_landmarks.py`) to process sign images across dataset folders.
- Use `HandTracker` to detect 21 3D hand landmarks ($[x, y, z]$ coordinates = 63 numerical features) per sign image.
- Format extracted keypoints into a standardized CSV file (`datasets/landmarks.csv`):
  `label, x0, y0, z0, x1, y1, z1, ..., x20, y20, z20, sample_path`
- Track performance metrics: Total images scanned, successful extractions, failed/no-hand detections, extraction duration (seconds), and throughput (FPS).
- Expose a backend service layer (`backend/app/ai/landmark_extraction_service.py`) and API endpoint (`POST /api/v1/ai/extract-landmarks`) restricted to Instructors and Admins.

---

## 2. Implementation Details

### Extraction Script Created (`scripts/`)
- [`scripts/extract_landmarks.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/scripts/extract_landmarks.py): `BatchLandmarkExtractor` class reading sign folders (A-Z), calling MediaPipe `HandTracker`, and writing 65-column rows into `landmarks.csv`.

### Service Layer & API Endpoint
- [`backend/app/ai/landmark_extraction_service.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/ai/landmark_extraction_service.py): Service wrapper `run_landmark_extraction` executing batch processing programmatically.
- [`backend/app/api/v1/ai.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/v1/ai.py): Added `POST /api/v1/ai/extract-landmarks` (Restricted to Instructor and Admin roles via `require_roles`).

---

## 3. Architecture & Workflow Diagram

```mermaid
graph TB
    subgraph DatasetInput ["📁 1. Dataset Directory & Image Folders"]
        SignFolders["ASL Alphabet Directories\n(datasets/asl_alphabet_train/A..Z)"]
        ImageFiles["Raw Sign Images (.jpg, .png)"]
    end

    subgraph BatchExtractionPipeline ["⚡ 2. Batch Landmark Extraction Pipeline (extract_landmarks.py)"]
        OpenCVReader["OpenCV Image Loader"]
        HandTrackerModule["MediaPipe HandTracker\n(Phase 5 Module)"]
        LandmarkExtractor["21 3D Keypoint Extractor\n(63 Coordinates: x0..z20)"]
        RowFormatter["CSV Row Formatter\n[label, x0..z20, sample_path]"]
    end

    subgraph BackendAPIService ["⚙️ 3. Backend AI Service & API Controller"]
        ExtractionService["Landmark Extraction Service\n(landmark_extraction_service.py)"]
        ExtractEndpoint["POST /api/v1/ai/extract-landmarks"]
        RBACAuth["require_roles([Instructor, Admin])"]
    end

    subgraph OutputDataset ["📄 4. Generated Dataset & Extraction Stats"]
        LandmarksCSV[("datasets/landmarks.csv\n(65 Columns Structured Dataset)")]
        ExtractionStats["JSON Performance Report\n(Total Scanned, Success Count, FPS)"]
    end

    SignFolders --> ImageFiles
    ImageFiles --> OpenCVReader
    OpenCVReader --> HandTrackerModule
    HandTrackerModule --> LandmarkExtractor
    LandmarkExtractor --> RowFormatter
    RowFormatter --> LandmarksCSV

    ExtractEndpoint --> RBACAuth
    RBACAuth -->|Authorized Request| ExtractionService
    ExtractionService --> BatchExtractionPipeline
    BatchExtractionPipeline --> ExtractionStats
    ExtractionStats -->> ExtractEndpoint
```

---

## 4. Test Plan & Verification Results

### Automated Unit Test Suite
- Test Script: [`backend/tests/test_phase6_batch_landmarks.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/tests/test_phase6_batch_landmarks.py)

### Execution Command
```bash
cd backend
py -m unittest tests/test_phase6_batch_landmarks.py
```

### Verification Audit Results
```text
test_01_batch_landmark_extractor_class (tests.test_phase6_batch_landmarks.Phase6BatchLandmarkExtractorTestSuite) ... ok
test_02_landmark_extraction_service (tests.test_phase6_batch_landmarks.Phase6BatchLandmarkExtractorTestSuite) ... ok
test_03_extract_landmarks_api_authorization (tests.test_phase6_batch_landmarks.Phase6BatchLandmarkExtractorTestSuite) ... ok

----------------------------------------------------------------------
Ran 3 tests in 15.392s
OK
```
- Status: **3/3 Tests Passed (100%)**.
