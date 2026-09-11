import sys
import os
import unittest
import numpy as np

# Ensure both backend and project root directories are in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.ai.pipeline import ai_pipeline, PredictionResult
try:
    from app.ai.preprocessing.normalize_landmarks import LandmarkNormalizer
except ImportError:
    from preprocessing.normalize_landmarks import LandmarkNormalizer

class TestMLPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = ai_pipeline
        self.normalizer = LandmarkNormalizer()

    def test_01_input_validation_missing_frame(self):
        res = self.pipeline.predict(None)
        self.assertEqual(res.status, "invalid_input")
        self.assertFalse(res.landmarks_valid)

    def test_02_input_validation_low_resolution(self):
        dummy_small = np.zeros((32, 32, 3), dtype=np.uint8)
        res = self.pipeline.predict(dummy_small)
        self.assertEqual(res.status, "invalid_input")
        self.assertFalse(res.landmarks_valid)

    def test_03_no_hand_detected_handling(self):
        blank_frame = np.zeros((240, 240, 3), dtype=np.uint8)
        res = self.pipeline.predict(blank_frame)
        self.assertEqual(res.status, "invalid_input")
        self.assertIn("No hand detected", res.reason)

    def test_04_landmark_normalization_wrist_origin(self):
        mock_raw = np.random.rand(63).astype(np.float32)
        norm_63 = self.normalizer.normalize(mock_raw)
        self.assertEqual(len(norm_63), 63)
        self.assertAlmostEqual(norm_63[0], 0.0, places=5)
        self.assertAlmostEqual(norm_63[1], 0.0, places=5)
        self.assertAlmostEqual(norm_63[2], 0.0, places=5)

    def test_05_model_version_loading(self):
        self.assertIsNotNone(self.pipeline.model_version)
        self.assertEqual(self.pipeline.model_version, "asl_rf_v001")

if __name__ == "__main__":
    unittest.main()
