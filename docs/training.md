# Model Training & Benchmark Experiments (`docs/training.md`)

## 1. Overview
Model training scripts are isolated inside `scripts/train_classifiers.py`. Training strictly utilizes normalized landmark feature vectors derived from the 87,000 training images to prevent data leakage.

---

## 2. Training Execution Command
```bash
python scripts/train_classifiers.py --data datasets/train.csv --val datasets/val.csv --out datasets/comparison_report.csv
```

---

## 3. Evaluated Classifiers & Metrics

```json
{
  "RandomForest": {
    "n_estimators": 200,
    "max_depth": 20,
    "val_accuracy": 0.9938,
    "test_accuracy": 0.9936,
    "f1_macro": 0.9912
  },
  "DecisionTree": {
    "max_depth": 15,
    "val_accuracy": 0.9342,
    "test_accuracy": 0.9310,
    "f1_macro": 0.9280
  },
  "SVC": {
    "C": 10.0,
    "kernel": "rbf",
    "val_accuracy": 0.9864,
    "test_accuracy": 0.9851,
    "f1_macro": 0.9820
  },
  "KNN": {
    "n_neighbors": 5,
    "val_accuracy": 0.9780,
    "test_accuracy": 0.9765,
    "f1_macro": 0.9740
  }
}
```

---

## 4. Hyperparameter Grid Search Logs
Hyperparameter study results are serialized in `datasets/rf_hyperparameter_study.json` and packaged inside `models/asl_rf_v001/metadata.json`.
