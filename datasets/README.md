# Datasets Documentation & Setup Guide

> [!IMPORTANT]
> **Zero Dataset Policy for GitHub**:  
> The raw datasets (totaling ~6.5 GB across ~99,000 files) and extracted coordinate CSVs are **intentionally NOT included in this GitHub repository**.  
> This repository provides the complete open-source codebase, preprocessing pipelines, model architectures, and setup instructions to acquire, verify, and preprocess datasets locally.

---

## 1. Required Datasets

| Dataset | Modality | Primary Use Case | Recommended Source | Expected Location |
| :--- | :--- | :--- | :--- | :--- |
| **ASL Alphabet** | 87,000 RGB Images (29 classes) | Static Alphabet Gesture Recognition | [Kaggle ASL Alphabet](https://www.kaggle.com/datasets/grassknoted/asl-alphabet) | `datasets/asl_alphabet/` |
| **Sign Language MNIST** | $28 \times 28$ Grayscale CSVs | Baseline Benchmark & Pixel Modeling | [Kaggle Sign MNIST](https://www.kaggle.com/datasets/datamunge/sign-language-mnist) | `datasets/sign_mnist/` |
| **WLASL** | 2,000 Video Classes | Word-Level Sign Vocabulary | [WLASL Dataset (GitHub)](https://github.com/dxli94/WLASL) | `datasets/wlasl/` |
| **RWTH-PHOENIX** | Continuous Video Sequences | Continuous Sentence Translation | [RWTH-PHOENIX-Weather](https://www-i6.informatik.rwth-aachen.de/~koller/RWTH-PHOENIX/) | `datasets/rwth_phoenix/` |

---

## 2. Expected Directory Structure

When placed locally on your machine, organize the folders as follows:

```text
datasets/
├── README.md                      # This setup guide (tracked in Git)
├── .gitkeep                       # Placeholder (tracked in Git)
│
├── asl_alphabet/                  # (Local only — ignored in Git)
│   ├── .gitkeep
│   ├── A/                         # Images: A1.jpg, A2.jpg, ...
│   ├── B/                         # Images: B1.jpg, B2.jpg, ...
│   └── ... (Classes A-Z, del, nothing, space)
│
├── sign_mnist/                    # (Local only — ignored in Git)
│   ├── .gitkeep
│   ├── sign_mnist_train.csv
│   └── sign_mnist_test.csv
│
├── wlasl/                         # (Local only — ignored in Git)
│   ├── .gitkeep
│   ├── WLASL_v0.3.json
│   └── videos/                    # Video clips (*.mp4)
│
├── rwth_phoenix/                  # (Local only — ignored in Git)
│   └── .gitkeep
│
└── features/                      # (Local only — ignored in Git)
    └── .gitkeep
```

---

## 3. Dataset Verification & Quality Audit

After downloading and extracting your local dataset, verify data integrity, file counts, and image validity using the provided CLI tools:

```bash
# 1. Explore dataset directory structure and class balance
python scripts/dataset_explorer.py --dataset-dir datasets/asl_alphabet

# 2. Run automated dataset quality validation & occlusion checks
python scripts/dataset_quality_reporter.py --dataset-dir datasets/asl_alphabet

# 3. Run full audit pipeline
python scripts/dataset_audit_pipeline.py --dataset-dir datasets/asl_alphabet
```

---

## 4. Preprocessing & Feature Extraction Workflow

The raw image files must be converted into normalized 63-dimensional coordinate feature vectors ($21 \times 3\text{D keypoints}$) for training:

```bash
# Step 1: Batch extract 21 3D landmarks via MediaPipe Hands
python scripts/extract_landmarks.py \
  --input-dir datasets/asl_alphabet \
  --output datasets/landmarks.csv

# Step 2: Apply wrist translation zero-centering and bounding-box scale normalization
python scripts/normalize_dataset.py \
  --input datasets/landmarks.csv \
  --output datasets/landmarks_normalized.csv

# Step 3: Generate stratified Train (70%), Validation (15%), and Test (15%) splits
python scripts/split_dataset.py \
  --input datasets/landmarks_normalized.csv \
  --train-ratio 0.70 \
  --val-ratio 0.15 \
  --test-ratio 0.15
```

The resulting `datasets/train.csv`, `datasets/val.csv`, and `datasets/test.csv` will be generated locally on your machine, ready for model training via `scripts/train_classifiers.py`.
