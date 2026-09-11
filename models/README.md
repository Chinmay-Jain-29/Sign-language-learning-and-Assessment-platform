# Trained Models Directory Guide

This directory houses trained sign language recognition models, serialization artifacts, and versioned configuration metadata.

---

## 1. Model Registry & Checkpoints

| Model ID / Checkpoint | Algorithm | Input Shape | Accuracy (Val) | Inference Latency | Size |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`gesture_model.joblib`** (Active) | Random Forest (`n_estimators=100`, `max_depth=20`) | `(63,)` float32 | **99.2%** | ~1.8 ms | 2.34 MB |
| **`asl_rf_v001/`** | Versioned Pipeline (Metadata + Preprocessing + Model) | `(63,)` float32 | **99.2%** | ~1.8 ms | 85.79 MB (Full) |
| **`svm_model.joblib`** | Support Vector Classifier (RBF, $C=10.0$) | `(63,)` float32 | **98.7%** | ~2.5 ms | 5.38 MB |
| **`knn_model.joblib`** | K-Nearest Neighbors ($k=5$) | `(63,)` float32 | **97.4%** | ~4.1 ms | 9.88 MB |
| **`decisiontree_model.joblib`** | Decision Tree Classifier (`max_depth=15`) | `(63,)` float32 | **94.8%** | ~0.4 ms | 0.31 MB |

---

## 2. Model Structure: `asl_rf_v001` Package

The versioned deployment bundle consists of:
```
models/asl_rf_v001/
├── metadata.json           # Model training timestamp, metrics, and hyperparameter logs
├── preprocessing.json      # Coordinate normalization and bounding box scaling schema
├── labels.json             # Ordered alphabet class labels ['A', 'B', ..., 'Z', 'SPACE', 'DELETE']
└── model.joblib            # Serialized scikit-learn ensemble weights
```

---

## 3. How to Retrain & Export Models

All models in this directory can be deterministically reproduced from normalized landmark features using:

```bash
# Train all 4 model architectures (Random Forest, SVM, KNN, Decision Tree)
python scripts/train_classifiers.py \
  --train datasets/train.csv \
  --val datasets/val.csv \
  --output-dir models/

# Perform Random Forest hyperparameter grid search
python scripts/study_rf_hyperparameters.py \
  --train datasets/train.csv \
  --val datasets/val.csv
```

---

## 4. Production Deployment

The FastAPI backend server automatically loads the active production model from:
- Path specified by `MODEL_PATH` in `.env` (default: `backend/app/ai/ml/models/gesture_model.joblib`).
- When the backend starts up, `AIPipeline` verifies the model signature and warms up inference on dummy landmarks.
