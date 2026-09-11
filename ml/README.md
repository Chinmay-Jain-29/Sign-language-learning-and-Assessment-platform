# Machine Learning Framework & Pipeline

This directory contains the machine learning pipelines, preprocessing modules, training scripts, evaluation benchmarks, and experiment configs for the **AI-Powered Sign Language Learning & Assessment Platform**.

---

## 1. Directory Structure

```
ml/
├── preprocessing/          # MediaPipe hand landmark extraction & normalization
│   ├── extract_landmarks.py
│   └── normalize_landmarks.py
├── training/               # Multi-model training pipelines (Random Forest, SVM, KNN, Decision Tree)
│   ├── train_classifiers.py
│   └── study_rf_hyperparameters.py
├── evaluation/             # Benchmarking, error analysis, and confusion matrices
│   ├── benchmark_inference.py
│   └── error_analysis.py
├── inference/              # Real-time inference engine and camera verification
│   └── camera_test.py
├── experiments/            # Hyperparameter configs, tracking logs, and ablation notes
│   └── experiment_001/
│       ├── experiment_config.json
│       ├── results.json
│       └── notes.md
└── README.md               # Pipeline documentation
```

---

## 2. Pipeline Overview

```
Raw Hand Images / Video
         │
         ▼
[ MediaPipe Hands (21 3D Landmarks) ]
         │
         ▼
[ Translation & Scale Invariant Normalization ]
         │
         ▼
[ 63-Dimensional Feature Vector ]
         │
         ▼
[ Tuned Multi-Class Classifier (Random Forest / SVM) ]
         │
         ▼
[ Real-Time Prediction & Confidence Scoring ]
```

---

## 3. Feature Extraction & Normalization

1. **21 Landmark Coordinates**: Each detected hand generates 21 3D landmarks $(x_i, y_i, z_i)$.
2. **Wrist Translation Centering**: The wrist (Landmark 0) is translated to origin $(0, 0, 0)$:
   $$x'_i = x_i - x_0, \quad y'_i = y_i - y_0, \quad z'_i = z_i - z_0$$
3. **Bounding Box Scale Invariance**: Features are scaled by the maximum bounding dimension $d_{\max}$:
   $$x''_i = \frac{x'_i}{d_{\max}}, \quad y''_i = \frac{y'_i}{d_{\max}}, \quad z''_i = \frac{z'_i}{d_{\max}}$$
4. **Flattened Feature Representation**: Produces a robust 63-dimensional numerical vector independent of distance and camera position.

---

## 4. Models & Algorithms

| Model | Implementation | Strengths | Target Latency |
| :--- | :--- | :--- | :--- |
| **Random Forest (Primary)** | `scikit-learn` Ensemble (100 estimators, max_depth=20) | High non-linear accuracy (99.2%), robust to outliers | ~1.8 ms / frame |
| **Support Vector Machine (SVM)** | RBF Kernel ($C=10.0, \gamma=0.01$) | Excellent margin separation, memory-efficient | ~2.5 ms / frame |
| **K-Nearest Neighbors (KNN)** | $k=5$, Euclidean Distance | Instant baseline, non-parametric | ~4.1 ms / frame |
| **Decision Tree** | CART algorithm (max_depth=15) | Ultra-low latency, highly interpretable | ~0.4 ms / frame |

---

## 5. How to Train & Evaluate

### Step 1: Extract Landmarks
```bash
python scripts/extract_landmarks.py --input-dir datasets/asl_alphabet --output datasets/landmarks.csv
```

### Step 2: Normalize Landmarks
```bash
python scripts/normalize_dataset.py --input datasets/landmarks.csv --output datasets/landmarks_normalized.csv
```

### Step 3: Split Dataset (Train / Val / Test)
```bash
python scripts/split_dataset.py --input datasets/landmarks_normalized.csv --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15
```

### Step 4: Train Classifiers & Run Hyperparameter Grid Search
```bash
python scripts/train_classifiers.py --train datasets/train.csv --val datasets/val.csv --output-dir models/
python scripts/study_rf_hyperparameters.py --train datasets/train.csv --val datasets/val.csv
```

### Step 5: Benchmark & Error Analysis
```bash
python scripts/benchmark_inference.py --model models/randomforest_tuned.joblib --iterations 1000
python scripts/error_analysis.py --model models/randomforest_tuned.joblib --test datasets/test.csv
```
