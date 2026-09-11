# Phase 5 Documentation: Isolated MediaPipe Hand Tracking Module

This document details the expected objectives, actual implementation, architecture diagram, and test plan for **Phase 5**.

---

## 1. Expected To Do (Requirements & Objectives)
- Build an isolated, decoupled, high-performance hand tracking detector class `HandTracker` wrapping Google MediaPipe Hands (`mediapipe.solutions.hands`).
- Extract 21 3D hand keypoints ($[x, y, z]$ coordinates) per detected hand.
- Calculate pixel bounding boxes (`xmin`, `ymin`, `width`, `height`), detection confidence scores, and handedness classification (`Right`/`Left`).
- Provide visual landmark and skeleton annotation helper (`draw_landmarks`).
- Expose a backend API endpoint (`POST /api/v1/ai/detect-landmarks`) accepting uploaded image frames and returning structured 21 3D landmark objects.

---

## 2. Implementation Details

### Hand Tracking Module Files (`backend/app/ai/hand_tracking/`)
- [`backend/app/ai/hand_tracking/schemas.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/ai/hand_tracking/schemas.py): Pydantic data schemas:
  - `LandmarkPoint` ($x, y, z$ coordinates)
  - `BoundingBox` ($xmin, ymin, width, height$)
  - `HandDetectionResult` (`handedness`, `score`, `landmarks`, `bbox`)
- [`backend/app/ai/hand_tracking/hand_tracker.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/ai/hand_tracking/hand_tracker.py): `HandTracker` class:
  - `detect(image_np) -> List[HandDetectionResult]`
  - `draw_landmarks(image_np, detections) -> np.ndarray`

### Backend API Endpoint
- [`backend/app/api/v1/ai.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/v1/ai.py):
  - `POST /api/v1/ai/detect-landmarks`: Accepts uploaded image files (PNG/JPG), decodes array via OpenCV, runs `HandTracker`, and returns extracted 21 3D landmark arrays.

---

## 3. Architecture & Workflow Diagram

```mermaid
graph TB
    subgraph ClientInput ["📹 1. Client Video Frame / Image Upload"]
        ImageUpload["Uploaded Image File / Base64 Frame"]
        OpenCVDecoder["OpenCV cv2.imdecode\n(Convert Bytes to BGR Array)"]
    end

    subgraph HandTrackerEngine ["⚡ 2. MediaPipe Hand Tracking Engine (HandTracker)"]
        ColorConversion["Color Space Converter\n(BGR to RGB Format)"]
        MediaPipeHands["Google MediaPipe Hands Model\n(static_image_mode=True, max_num_hands=2)"]
        KeypointExtractor["21 3D Landmark Extractor\n(x, y, z Relative Coordinates)"]
        BoundingBoxCalc["Bounding Box Calculator\n(xmin, ymin, width, height)"]
    end

    subgraph SchemaConverter ["📋 3. Schema Formatting & Annotation"]
        HandnessClassifier["Handedness Classifier\n(Right / Left Hand + Score)"]
        VisualAnnotator["draw_landmarks Utility\n(Draw Skeleton & Joints on Frame)"]
        PydanticResult["HandDetectionResult Object"]
    end

    subgraph APIOutput ["🌐 4. Endpoint Response"]
        LandmarkEndpoint["POST /api/v1/ai/detect-landmarks"]
        JSONPayload["JSON Landmark Array Payload\n[{handedness: 'Right', score: 0.98, landmarks: [...]}]"]
    end

    ImageUpload --> OpenCVDecoder
    OpenCVDecoder --> ColorConversion
    ColorConversion --> MediaPipeHands
    MediaPipeHands --> KeypointExtractor
    KeypointExtractor --> BoundingBoxCalc
    
    BoundingBoxCalc --> HandnessClassifier
    HandnessClassifier --> PydanticResult
    PydanticResult --> VisualAnnotator
    PydanticResult --> LandmarkEndpoint
    LandmarkEndpoint --> JSONPayload
```

---

## 4. Test Plan & Verification Results

### Automated Unit Test Suite
- Test Script: [`backend/tests/test_phase5_hand_tracking.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/tests/test_phase5_hand_tracking.py)

### Execution Command
```bash
cd backend
py -m unittest tests/test_phase5_hand_tracking.py
```

### Verification Audit Results
```text
test_01_hand_tracker_initialization (tests.test_phase5_hand_tracking.Phase5HandTrackingTestSuite) ... ok
test_02_detect_empty_image (tests.test_phase5_hand_tracking.Phase5HandTrackingTestSuite) ... ok
test_03_detect_landmarks_synthetic_or_sample (tests.test_phase5_hand_tracking.Phase5HandTrackingTestSuite) ... ok
test_04_landmark_drawing_utility (tests.test_phase5_hand_tracking.Phase5HandTrackingTestSuite) ... ok
test_05_detect_landmarks_api_endpoint (tests.test_phase5_hand_tracking.Phase5HandTrackingTestSuite) ... ok

----------------------------------------------------------------------
Ran 5 tests in 12.758s
OK
```
- Status: **5/5 Tests Passed (100%)**.
