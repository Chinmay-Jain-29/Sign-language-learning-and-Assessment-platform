# Troubleshooting & Diagnostic Guide (`docs/troubleshooting.md`)

## 1. Common Operational Issues & Solutions

### A. Camera Access Failure or Blank Video Screen
- **Symptom**: Webcam indicator displays *Camera permission denied* or *Camera unavailable*.
- **Diagnostic Step**: Check browser HTTPS context or localhost settings. Webcams require secure origin (`https://` or `http://localhost`).
- **Resolution**: Grant browser webcam permission in site settings. Ensure no other application (e.g. Zoom, Teams) is locking the webcam hardware device.

### B. Database Connection Timeout
- **Symptom**: `AppException: Database Error` or connection timeout during startup.
- **Diagnostic Step**: Inspect `DATABASE_URL` in `.env`.
- **Resolution**: Neon Cloud PostgreSQL requires `sslmode=require` appended to the database URL string. Verify network connectivity to Neon Cloud hosts.

### C. MediaPipe Model Initialization Warning
- **Symptom**: `INFO: Created TensorFlow Lite XNNPACK delegate for CPU`.
- **Diagnostic Step**: Standard MediaPipe CPU delegate output notice.
- **Resolution**: Normal operational log output. No action needed.

### D. CORS Pre-Flight Option Rejection
- **Symptom**: Browser console error `CORS policy: No 'Access-Control-Allow-Origin' header is present`.
- **Diagnostic Step**: Inspect `CORS_ORIGINS` setting in `backend/app/core/config.py`.
- **Resolution**: Add client origin URL (e.g. `http://localhost:5173`) to `CORS_ORIGINS` array.
