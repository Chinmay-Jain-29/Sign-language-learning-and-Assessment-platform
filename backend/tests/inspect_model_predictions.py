import joblib
import numpy as np
import os

model_path = os.path.join("..", "models", "asl_rf_v001", "model.joblib")
if not os.path.exists(model_path):
    model_path = os.path.join("app", "ai", "ml", "models", "gesture_model.joblib")

print("Loading model from:", model_path)
model = joblib.load(model_path)
print("Model classes:", model.classes_)
print("Model n_features_in_:", getattr(model, "n_features_in_", None))

# Let's inspect trees and features
print("Model estimators count:", len(model.estimators_))

# Check if dataset files exist in ml/data or similar
for root, dirs, files in os.walk(".."):
    for f in files:
        if f.endswith(".csv") or f.endswith(".npy") or f.endswith(".parquet"):
            if "dataset" in f.lower() or "landmark" in f.lower() or "data" in f.lower():
                print("Found dataset file:", os.path.join(root, f))
