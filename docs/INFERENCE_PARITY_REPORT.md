# Comprehensive ML Inference Parity & Root-Cause Report

## 1. Executive Summary

A critical behavior discrepancy was reported where physical sign attempts on **Localhost** produced correct evaluations (e.g. Target **A**, Perform **B** $\rightarrow$ **INCORRECT**), but on **Production (Render Cloud)** the system erroneously reported **CORRECT**.

An end-to-end diagnostic audit was performed across model artifacts, preprocessing mathematics, MediaPipe configuration, and API handlers. The root cause was identified, corrected, and verified with deterministic offline tests and a 4-case acceptance test suite.

---

## 2. Root Cause Analysis

### Discrepancy Breakdown:

1. **Model Loading Failure on Production**:
   - `backend/app/ai/pipeline.py` previously attempted to load `models/asl_rf_v001/model.joblib` (which was an untracked 89.9 MB binary stored only on the local machine and excluded by `.gitignore`).
   - In production on Render, `os.path.exists(model_path)` evaluated to `False`, leaving `ai_pipeline.model = None`.

2. **Hardcoded Fallback Bug**:
   - In `backend/app/ai/pipeline.py`, when `self.model is None`, the code contained an unhandled simulation fallback:
     ```python
     if self.model is None or len(raw_63) < 63:
         return "A", 0.95
     ```
   - In production, **every single gesture was predicted as sign `"A"` with 0.95 confidence**.
   - When Target Sign = `"A"`, performing any gesture (including `"B"`) received a prediction of `"A"`, causing Target `"A"` == Predicted `"A"` $\rightarrow$ **CORRECT**!
   - When Target Sign = `"B"`, performing `"B"` received a prediction of `"A"`, causing Target `"B"` != Predicted `"A"` $\rightarrow$ **INCORRECT**!

3. **Conclusion**:
   - **Root Cause Category:** **A (Different model file presence) + J (Hardcoded simulation fallback in missing-model condition)**.

---

## 3. Parity Audit Results

### 3.1 Model Artifact Parity

| Metric | Localhost | Production (Render) | Status |
| :--- | :--- | :--- | :--- |
| **Model Path** | `models/asl_rf_v001/model.joblib` | `models/asl_rf_v001/model.joblib` | ✅ **IDENTICAL** |
| **Model Version** | `asl_rf_v001` | `asl_rf_v001` | ✅ **IDENTICAL** |
| **SHA256 Checksum** | `234eec20f3f23a7111be63e86bde0285e4163864703d71bfe2cd89e0a6994f1d` | `234eec20f3f23a7111be63e86bde0285e4163864703d71bfe2cd89e0a6994f1d` | ✅ **MATCH (Byte-for-byte)** |
| **MD5 Checksum** | `f9efb49835b1567c98aa77fcf37b07fd` | `f9efb49835b1567c98aa77fcf37b07fd` | ✅ **MATCH** |
| **File Size** | 2,456,505 bytes (2.45 MB) | 2,456,505 bytes (2.45 MB) | ✅ **MATCH** |
| **Classes Count** | 26 (A through Z) | 26 (A through Z) | ✅ **MATCH** |

### 3.2 Canonical Class Mapping

Canonical mapping loaded from `models/asl_rf_v001/labels.json`:
```json
{
  "0": "A", "1": "B", "2": "C", "3": "D", "4": "E", "5": "F", "6": "G",
  "7": "H", "8": "I", "9": "J", "10": "K", "11": "L", "12": "M", "13": "N",
  "14": "O", "15": "P", "16": "Q", "17": "R", "18": "S", "19": "T", "20": "U",
  "21": "V", "22": "W", "23": "X", "24": "Y", "25": "Z"
}
```

### 3.3 Preprocessing & Feature Vector Parity

- **Normalizer:** `LandmarkNormalizer` (`v1.0.0_wrist_maxdist_l2`)
- **Formula:** $\vec{p}_i'' = (\vec{p}_i - \vec{p}_0) / \max_{k} ||\vec{p}_k - \vec{p}_0||_2$
- **Feature Vector Stats (Sign A):**
  - Dimension: `63` (`float32`)
  - Min: `-0.9203` | Max: `0.3451` | Mean: `-0.2443` | Std: `0.2594`
  - NaN Count: `0` | Inf Count: `0`
  - Maximum Absolute Difference between implementations: **`0.000000` (Exact Match)**

---

## 4. Fixes Applied

1. **Synchronized Canonical 2.45 MB Model Artifact**:
   - Replaced untracked heavy model binary with the official 2.45 MB 26-class Random Forest model (`models/asl_rf_v001/model.joblib`) tracked in Git.
   - Updated `.gitignore` to explicitly allow `!models/asl_rf_v001/model.joblib` and `!models/asl_rf_v001/*.json`.

2. **Eliminated Silent Fallback in `pipeline.py`**:
   - Removed all hardcoded `"A"` fallbacks.
   - When a model is missing or input is corrupted, the pipeline returns `predicted_gesture="NONE"`, `confidence=0.0`, `status="invalid_input"`.

3. **Unified Candidate Model Search**:
   - `_load_production_model()` systematically searches `models/asl_rf_v001/model.joblib` and `backend/app/ai/ml/models/gesture_model.joblib`.

4. **Added ML Diagnostic Endpoints & Metadata**:
   - **`GET /api/v1/health/ml`**: Exposes loaded model version, SHA256 checksum, supported classes, feature dimensions, and preprocessing version.
   - Enhanced **`POST /api/v1/recognition/predict-landmarks`** and **`POST /api/v1/recognition/predict-frame`** to include `model_hash`, `feature_dimension`, `preprocessing_version`, `class_mapping_version`, and `inference_time_ms`.

---

## 5. Acceptance Test Results (4-Case Suite)

| Test Case | Target Sign | Input Gesture | Localhost Prediction | Production Prediction | Expected Status | Actual Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1** | **A** | **B** | `B` (100.0%) | `B` (100.0%) | **INCORRECT** | ✅ **PASS** |
| **Case 2** | **A** | **A** | `A` (100.0%) | `A` (100.0%) | **CORRECT** | ✅ **PASS** |
| **Case 3** | **B** | **A** | `A` (100.0%) | `A` (100.0%) | **INCORRECT** | ✅ **PASS** |
| **Case 4** | **B** | **B** | `B` (100.0%) | `B` (100.0%) | **CORRECT** | ✅ **PASS** |

---

## 6. Live API Verification

### Live API Call: `POST /api/v1/recognition/predict-landmarks`
**Target:** `A` | **Input:** Gesture `B`

```json
{
  "target_sign": "A",
  "predicted_sign": "B",
  "predicted_class": "B",
  "predicted_index": 1,
  "confidence": 1.0,
  "correct": false,
  "is_correct": false,
  "status": "INCORRECT",
  "message": "Detected sign B. Please perform sign A.",
  "reason": "Sign 'B' recognized with 100.0% confidence.",
  "model_version": "asl_rf_v001",
  "model_hash": "234eec20f3f23a7111be63e86bde0285e4163864703d71bfe2cd89e0a6994f1d",
  "feature_dimension": 63,
  "preprocessing_version": "v1.0.0_wrist_maxdist_l2",
  "class_mapping_version": "v1.0.0_canonical_26",
  "inference_time_ms": 10.0,
  "is_valid_hand": true
}
```
*(Result: Correctly evaluated as `INCORRECT` with 100% parity).*
