import hashlib
import shutil
import json
import os

src_model = os.path.join("..", "models", "randomforest_model.joblib")
dest_canonical = os.path.join("..", "models", "asl_rf_v001", "model.joblib")
dest_backend = os.path.join("app", "ai", "ml", "models", "gesture_model.joblib")

# Compute SHA256 of the 99.37% accuracy model
with open(src_model, "rb") as f:
    sha256_hash = hashlib.sha256(f.read()).hexdigest()

print(f"Random Forest (99.37% Acc) SHA256: {sha256_hash}")

# Copy to destination locations
shutil.copy2(src_model, dest_canonical)
shutil.copy2(src_model, dest_backend)
print("Copied to canonical model locations successfully.")

# Update metadata.json
meta_path = os.path.join("..", "models", "asl_rf_v001", "metadata.json")
metadata = {
    "model_name": "asl_rf_v001",
    "model_type": "RandomForestClassifier",
    "architecture": "RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)",
    "version": "v1.0.0",
    "sha256": sha256_hash,
    "feature_dimension": 63,
    "landmark_count": 21,
    "classes_count": 26,
    "classes": [chr(ord('A') + i) for i in range(26)],
    "accuracy": 0.9937,
    "macro_f1": 0.9913,
    "weighted_f1": 0.9937,
    "training_samples": 39848,
    "validation_samples": 8538,
    "preprocessing": "wrist_origin_euclidean_max_normalized",
    "inference_framework": "scikit-learn",
    "model_size_bytes": os.path.getsize(src_model)
}

with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print("Updated metadata.json successfully:")
print(json.dumps(metadata, indent=2))
