# Machine Learning Pipeline & Lifecycle Specification (`docs/ml_pipeline.md`)

This document details the complete end-to-end Machine Learning pipeline, dataset exploration, landmark extraction, validation rules, normalization strategy, classifier benchmarks, hyperparameter study, error analysis, benchmarking, model versioning, and real-time inference.

---

## 1. End-to-End ML Pipeline Flowchart

```text
ASL Alphabet Dataset (87,000 images across 29 classes)
   ↓
Dataset Exploration (`scripts/dataset_explorer.py`)
   ↓
MediaPipe Hand Landmark Extractor (`scripts/extract_landmarks.py`)
   ↓
Quality Audit & Quarantining (Invalid count check, NaN check, zero-scale check)
   ↓
Wrist-Centered Max Euclidean Scale Normalization (`preprocessing/normalize_landmarks.py`)
   ↓
Stratified Train/Val/Test Split (70% / 15% / 15%)
   ↓
Classifier Benchmark Comparison (Random Forest, Decision Tree, SVM, KNN)
   ↓
Random Forest Hyperparameter Study (Grid Search tuning `n_estimators`, `max_depth`)
   ↓
Confusion Matrix Error Analysis (Top 5 confused gesture pairs)
   ↓
Real-Time Inference Benchmarking (P50/P95 latency, FPS profiling)
   ↓
Model Selection & Package Versioning (`models/asl_rf_v001/`)
   ↓
Production Real-Time Webcam Pipeline (`backend/app/ai/pipeline.py`)
```

---

## 2. Empirical Datasets & Feature Pipeline Metrics

- **Dataset Source**: `dataset/asl_alphabet/asl_alphabet_train` (Full training set)
- **Scanned Images**: 87,000 images across 29 sign classes ('A'–'Z', 'del', 'nothing', 'space')
- **Extracted Valid Landmark Poses**: 56,929 valid hand poses
- **Feature Vector**: 63 floating-point spatial coordinates ($21 \text{ keypoints} \times 3 \text{ axes } [x, y, z]$)
- **Stratified Dataset Split**:
  - **Train Set**: 39,848 samples (70%)
  - **Validation Set**: 8,538 samples (15%)
  - **Test Set**: 8,543 samples (15%)

---

## 3. Classifier Comparison Benchmark Results

| Algorithm | Validation Accuracy | Test Accuracy | Training Latency | Evaluation Speed | Selected Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Default)** | **99.37%** | **99.35%** | 1.84s | Fast (1.8 ms/frame) | Candidate |
| **Random Forest (Tuned v001)** | **99.38%** | **99.36%** | 3.12s | Fast (1.8 ms/frame) | **SELECTED FOR PRODUCTION** |
| Decision Tree | 93.42% | 93.10% | 0.42s | Ultra Fast (0.2 ms/frame) | Rejected (Lower Accuracy) |
| Support Vector Classifier (SVM) | 98.64% | 98.51% | 14.80s | Medium (4.2 ms/frame) | Backup Candidate |
| K-Nearest Neighbors (KNN) | 97.80% | 97.65% | 0.05s | Slow (12.4 ms/frame) | Rejected (High Inference Latency) |

---

## 4. Random Forest Hyperparameter Study

- **Parameter Grid**:
  - `n_estimators`: `[50, 100, 200]`
  - `max_depth`: `[10, 20, None]`
  - `min_samples_leaf`: `[1, 2, 4]`
- **Optimal Hyperparameters Selected**:
  - `n_estimators`: `200`
  - `max_depth`: `20`
  - `min_samples_leaf`: `1`
  - `min_samples_split`: `2`
- **Validation Accuracy**: **99.38%**
- **Test Accuracy**: **99.36%**

---

## 5. Confusion Matrix & Top 5 Confused Gesture Pairs

1. **`N` vs `M`**: 10 misclassifications (thumb folded under 2 fingers vs 3 fingers)
2. **`M` vs `N`**: 5 misclassifications
3. **`D` vs `O`**: 4 misclassifications (index finger curvature variance)
4. **`R` vs `U`**: 3 misclassifications (crossed vs parallel finger depth jitter)
5. **`V` vs `W`**: 2 misclassifications

---

## 6. Real-Time Inference Benchmarking

- **P50 Latency (Median)**: **31.11 ms**
- **P95 Latency**: **32.11 ms**
- **Throughput (FPS)**: **31.9 FPS**
- **Model Disk Size**: **85.79 MB**
- **RSS Memory Footprint**: **182.0 MB**

---

## 7. Model Packaging & Versioning

- **Version Directory**: `models/asl_rf_v001/`
  - `model.joblib`: Serialized Random Forest binary ($85.79\text{ MB}$)
  - `metadata.json`: Model version, dataset version, algorithm, metrics
  - `preprocessing.json`: Wrist-origin translation + max Euclidean scale specification
  - `labels.json`: 29 sign class label array
