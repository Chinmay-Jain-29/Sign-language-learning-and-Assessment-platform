# Master Dataset Documentation (`docs/DATASET_DOCUMENTATION.md`)

This document serves as the authoritative specification for all datasets integrated across the ASL Sign Language Learning and Assessment Platform.

---

## 1. Dataset Overview & Intended Task Breakdown

| Dataset Name | Primary Purpose | Gesture Type | Samples Count | Format | Primary Intended Task |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ASL Alphabet Dataset** | Static Alphabet Gesture Recognition | 29 Classes ('A'–'Z', 'DEL', 'NOTHING', 'SPACE') | 87,000 Images (3,000 / class) | $200 \times 200$ RGB JPEG | Static ASL Alphabet Landmark Feature Extraction & Classifier Training |
| **Sign Language MNIST** | Grayscale Landmark Benchmark | 24 Classes ('A'–'Z', excluding 'J' and 'Z') | 34,627 Grayscale Images | $28 \times 28$ Grayscale Pixel Values | Lightweight Edge Model Pre-training & Benchmark Validation |
| **WLASL (Word-Level ASL)** | Dynamic Word-Level Sign Recognition | 2,000 Word Classes | 21,083 Video Clips | H.264 MP4 Videos ($30$ FPS) | Dynamic Word-Level Gesture Recognition & Temporal Sequence Tracking |
| **RWTH-PHOENIX-Weather 2014** | Continuous Sign Language Translation | Sentence-Level Sequences | 8,257 Annotated Video Sequences | Frame Sequences + Gloss Annotations | Continuous Sign Language Sentence Translation & Sequence Research |

---

## 2. Detailed Dataset Specifications

### A. ASL Alphabet Dataset (Primary Training Set)
- **Directory Path**: `datasets/asl_alphabet/asl_alphabet_train/asl_alphabet_train`
- **Class Taxonomy**: 29 Classes:
  - Letters `A` through `Z` (26 classes)
  - `del` (Delete gesture)
  - `nothing` (No hand in frame)
  - `space` (Spacebar gesture)
- **Total Images**: 87,000 ($3,000$ images per class)
- **Resolution**: $200 \times 200$ pixels (RGB)
- **Directory Structure**:
  ```text
  datasets/asl_alphabet/asl_alphabet_train/asl_alphabet_train/
  ├── A/ (3000 JPGs)
  ├── B/ (3000 JPGs)
  ├── ...
  ├── Z/ (3000 JPGs)
  ├── del/ (3000 JPGs)
  ├── nothing/ (3000 JPGs)
  └── space/ (3000 JPGs)
  ```
- **Extracted Feature Representation**: 65-column tabular landmark CSV (`datasets/landmarks.csv` / `landmarks_normalized.csv`) containing label, 63 spatial coordinates ($x_0, y_0, z_0 \dots x_{20}, y_{20}, z_{20}$), and sample filepath.

---

### B. Sign Language MNIST Dataset
- **Directory Path**: `datasets/sign_mnist/`
- **Class Taxonomy**: 24 Classes (A–I, K–Y; excluding motion letters `J` and `Z`)
- **Total Samples**: 34,627 images (27,455 training, 7,172 testing)
- **Resolution**: $28 \times 28$ single-channel grayscale pixels
- **Data Format**: CSV files (`sign_mnist_train.csv`, `sign_mnist_test.csv`) with 785 columns (label + 784 pixel values).
- **Intended Task**: Rapid offline feature extraction verification and lightweight model benchmarking.

---

### C. WLASL (Word-Level American Sign Language)
- **Directory Path**: `datasets/wlasl/`
- **Class Taxonomy**: 2,000 common ASL words (e.g. "hello", "thank you", "book", "computer")
- **Total Samples**: 21,083 video clips
- **Format**: MP4 videos with JSON annotations (`WLASL_v0.3.json`) containing bounding boxes, start/end frames, and signer IDs.
- **Intended Task**: Future dynamic word-level sequence recognition using MediaPipe Pose + Hand temporal buffers.

---

### D. RWTH-PHOENIX-Weather 2014
- **Directory Path**: `datasets/phoenix_weather/`
- **Class Taxonomy**: Sentence-level continuous sign language glosses (German Sign Language DGS)
- **Total Sequences**: 8,257 annotated video clips (7,096 train, 519 dev, 642 test)
- **Format**: Full-frame video sequences ($210 \times 260$ @ 25 FPS) paired with ELAN transcriptions.
- **Intended Task**: Advanced sign language translation research and continuous sentence segmentation.

---

## 3. Strict Rules & Data Integrity

1. **No Blind Combination**: Datasets are kept strictly segregated by task type. Static alphabet classifiers operate solely on 63-coordinate normalized hand landmarks derived from ASL Alphabet and Sign MNIST benchmarks.
2. **Train / Validation / Test Partitioning**: The 56,929 extracted valid ASL Alphabet landmarks are split 70% Train (39,848), 15% Validation (8,538), and 15% Test (8,543) using stratified split (`scripts/split_dataset.py`).
