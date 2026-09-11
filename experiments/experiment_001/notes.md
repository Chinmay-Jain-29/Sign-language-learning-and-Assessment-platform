# Experiment 001 — Tuned Random Forest Baseline Notes

## Experiment Overview
- **Objective**: Evaluate Random Forest classifier baseline with hyperparameter tuning (`n_estimators=200`, `max_depth=20`, `min_samples_leaf=1`) on 63 normalized 3D hand keypoints.
- **Dataset**: `datasets/asl_alphabet/asl_alphabet_train/asl_alphabet_train` (87,000 images, 56,929 valid 21-landmark poses).
- **Splits**: 70% Train (39,848), 15% Validation (8,538), 15% Test (8,543).

## Key Results
- **Validation Accuracy**: **99.38%**
- **Test Accuracy**: **99.36%**
- **Macro F1 Score**: **0.9912**
- **Inference P50 Latency**: **31.11 ms** (31.9 FPS real-time webcam throughput).

## Reproducibility Requirements
- Set `random_state=42` across dataset split and model initialization.
- Apply `LandmarkNormalizer` (wrist translation + max Euclidean distance scaling).
