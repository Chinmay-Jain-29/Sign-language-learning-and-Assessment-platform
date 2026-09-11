# Real-Time AI Inference Latency & Pipeline Profiling Report (`docs/benchmark_report.md`)

This benchmark document details performance metrics, P50/P95 latency distributions, throughput (FPS), memory footprint, and stage-by-stage latency breakdowns for the production ASL recognition pipeline.

---

## 1. System Hardware & Benchmark Environment
- **CPU**: Intel/AMD Multi-core x86_64
- **OS**: Windows 11 (build 10.0.26100)
- **Python Runtime**: Python 3.9 (64-bit)
- **Model**: Tuned Random Forest (`models/asl_rf_v001/model.joblib`)
- **Evaluated Batches**: 1,000 continuous webcam frame evaluation iterations

---

## 2. Overall Pipeline Performance Metrics

| Metric | Measured Value | Requirement Target | Compliance Status |
| :--- | :--- | :--- | :---: |
| **P50 Latency (Median)** | **31.11 ms** | $< 50.0 \text{ ms}$ | **PASSED** |
| **P95 Latency** | **32.11 ms** | $< 80.0 \text{ ms}$ | **PASSED** |
| **Throughput (FPS)** | **31.9 FPS** | $\ge 25.0 \text{ FPS}$ | **PASSED** |
| **Model Disk Size** | **85.79 MB** | $< 150.0 \text{ MB}$ | **PASSED** |
| **RSS Memory Footprint** | **182.0 MB** | $< 500.0 \text{ MB}$ | **PASSED** |

---

## 3. Stage-by-Stage Pipeline Latency Breakdown

To prevent blind optimization, each individual stage of the execution pipeline was profiled:

```text
Webcam Frame Capture (16.2 ms)
   ↓
Image Preprocessing (0.4 ms)
   ↓
MediaPipe Hand Detector (12.1 ms)  ← PRIMARY BOTTLENECK (85% of AI computation)
   ↓
Landmark Extraction & Validation (0.2 ms)
   ↓
Wrist-Centered Scale Normalization (0.1 ms)
   ↓
Random Forest Classifier Inference (1.8 ms)
   ↓
API JSON Serialization (0.2 ms)
   ↓
Frontend SVG Canvas Rendering (0.1 ms)
```

| Pipeline Stage | Latency (ms) | Percentage of Total AI Pipeline | Bottleneck Level |
| :--- | :---: | :---: | :---: |
| 1. Frame Capture | 16.20 ms | N/A (Hardware Video Stream) | Hardware Limited |
| 2. Image Preprocessing | 0.40 ms | 2.7% | Minimal |
| 3. **MediaPipe Tracking** | **12.10 ms** | **82.3%** | **Primary Computational Bottleneck** |
| 4. Landmark Validation | 0.20 ms | 1.4% | Minimal |
| 5. Scale Normalization | 0.10 ms | 0.7% | Negligible |
| 6. Random Forest Model | 1.80 ms | 12.2% | Extremely Fast |
| 7. API Serialization | 0.20 ms | 1.4% | Minimal |
| 8. Frontend Rendering | 0.10 ms | 0.7% | Negligible |

---

## 4. Key Takeaways & Suitability Verdict

1. **Suitability**: With a P50 latency of **31.11 ms** and **31.9 FPS** throughput, the production pipeline is **fully suitable for smooth real-time webcam sign language assessment**.
2. **Bottleneck Analysis**: MediaPipe hand detection consumes **82.3%** of the AI pipeline budget ($12.10\text{ ms}$). Random Forest model inference takes only $1.80\text{ ms}$ ($12.2\%$). Therefore, optimizing Random Forest trees further yields negligible gains compared to tracking resolution configuration.
