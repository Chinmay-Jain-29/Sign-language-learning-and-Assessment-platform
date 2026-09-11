# Future Dynamic Sign Language Architecture (`docs/DYNAMIC_SIGN_ARCHITECTURE.md`)

This architectural document defines the component responsibilities, input specifications, output schemas, and data flow pipeline for extending the static ASL alphabet classifier into continuous word and sentence-level dynamic sign language recognition.

---

## 1. End-to-End Pipeline Overview

```text
Webcam Stream
   ↓
Frame Capture & Rate Limiting
   ↓
MediaPipe Holistic Tracking (Hands + Pose + Face)
   ↓
Landmark Coordinate Extractor
   ↓
Sliding Temporal Buffer (20–30 frames × 63 features)
   ↓
Dynamic Sequence Builder
   ↓
Sequence Classifier (Bi-LSTM / GRU / Spatial-Temporal Transformer)
   ↓
Gesture / Word Prediction
   ↓
Language Model Sentence Formation
```

---

## 2. Component Specifications

### 1. Frame Capture & Processing Frequency Regulator
- **Responsibility**: Captures raw webcam frames at 30 FPS and regulates processing frequency so heavy neural models are not evaluated unnecessarily on identical frames.
- **Input**: OpenCV / HTML5 Video Stream (`640x480x3` BGR/RGB).
- **Output**: Downsampled normalized frame tensor (`224x224x3`).

### 2. MediaPipe Landmark Extractor
- **Responsibility**: Detects hand keypoints (21 points $\times 3 = 63$), pose keypoints (33 points $\times 3 = 99$), and facial contours.
- **Input**: Normalized frame tensor (`224x224x3`).
- **Output**: Raw spatial coordinate tuple $(x_0, y_0, z_0 \dots x_{20}, y_{20}, z_{20})$.

### 3. Landmark Normalization & Validation
- **Responsibility**: Applies wrist-centered translation and max Euclidean scale normalization to maintain translation/scale invariance.
- **Input**: 63 raw spatial floats.
- **Output**: 63 normalized spatial floats.

### 4. Sliding Temporal Buffer (`LandmarkTemporalBuffer`)
- **Responsibility**: Maintains a rolling FIFO queue of the latest $T$ frames (e.g. $T = 20$ to $30$).
- **Input**: 63 normalized spatial floats per frame.
- **Output**: Tensor of shape $(T, 63)$ representing temporal motion trajectory.

### 5. Dynamic Sequence Builder
- **Responsibility**: Detects motion start/stop boundaries (wrist velocity exceeding threshold $\Delta v > v_{\text{threshold}}$) to segment continuous stream into discrete sign gesture sequences.
- **Input**: Tensor of shape $(T, 63)$.
- **Output**: Segmented sequence tensor $(B, T, 63)$.

### 6. Dynamic Sequence Classifier (Bi-LSTM / GRU / Transformer)
- **Responsibility**: Evaluates temporal sequence tensor $(B, T, 63)$ and predicts word gloss probability distribution.
- **Input**: Segmented sequence tensor $(B, T, 63)$.
- **Output**: Gloss probability distribution vector $P(\text{word}_i \mid \text{sequence})$.

### 7. Language Model & Sentence Formation Engine
- **Responsibility**: Converts continuous sequence of predicted sign glosses (e.g., `["ME", "WANT", "LEARN", "SIGN"]`) into grammatically fluent natural language sentences (*"I want to learn sign language."*).
- **Input**: Sequence of predicted gloss tokens.
- **Output**: Natural language sentence string + confidence score.
