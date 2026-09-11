# Real-Time Inference & Latency Optimization (`docs/inference.md`)

## 1. Production Inference Interface
Real-time prediction is encapsulated within `AIPipeline.predict(image_np) -> PredictionResult` in `backend/app/ai/pipeline.py`.

```python
result = ai_pipeline.predict(camera_frame_bgr)
print(result.predicted_gesture) # e.g. 'A'
print(result.confidence)        # e.g. 0.95
print(result.status)            # 'valid', 'uncertain', 'invalid_input'
```

---

## 2. Real-Time Pipeline Stages
1. **Camera Stream Input**: Raw BGR video frame from webcam ($640 \times 480 \text{ resolution}$).
2. **Frame Validation**: Checks non-null image buffer, $64 \times 64$ minimum resolution, valid color channels.
3. **MediaPipe Hand Tracking**: Detects hand boundaries and extracts 21 3D spatial keypoints ($12.10\text{ ms}$).
4. **Scale Normalization**: Translates origin to wrist (keypoint 0) and scales by max Euclidean distance ($0.10\text{ ms}$).
5. **Model Inference**: Random Forest evaluation ($1.80\text{ ms}$).
6. **Confidence Thresholding**: Evaluates probability against `MODEL_CONFIDENCE_THRESHOLD = 0.75`.
7. **Temporal Stabilizer**: Requires $N=3$ consecutive matching predictions before confirming a stable gesture.

---

## 3. Measured Latency Breakdown

- **MediaPipe Hand Tracking**: $12.10\text{ ms}$ (82.3% of AI latency)
- **Random Forest Inference**: $1.80\text{ ms}$ (12.2% of AI latency)
- **Scale Normalization**: $0.10\text{ ms}$
- **Total Pipeline Latency**: **31.11 ms P50 (31.9 FPS)**
