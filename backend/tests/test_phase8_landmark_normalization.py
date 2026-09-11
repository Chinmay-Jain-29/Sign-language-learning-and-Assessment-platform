import sys
import os
import unittest
import numpy as np
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.ai.preprocessing.normalize_landmarks import LandmarkNormalizer
from app.ai.hand_tracking.schemas import LandmarkPoint
from scripts.normalize_dataset import DatasetNormalizer

class Phase8LandmarkNormalizationTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        # Login as Learner
        login_res = cls.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        cls.token = login_res.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

        # Create 21 distinct synthetic 3D points
        cls.raw_points = [LandmarkPoint(x=float(i * 0.05), y=float(i * 0.04), z=float(i * 0.01)) for i in range(21)]

    def test_01_translation_invariance(self):
        # Create translated points (+10.0 on X, Y, Z)
        translated_points = [
            LandmarkPoint(x=p.x + 10.0, y=p.y + 10.0, z=p.z + 10.0) for p in self.raw_points
        ]

        norm_original = LandmarkNormalizer.normalize_points(self.raw_points)
        norm_translated = LandmarkNormalizer.normalize_points(translated_points)

        # Wrist (point 0) must be (0, 0, 0) for both
        self.assertAlmostEqual(norm_original[0].x, 0.0, places=5)
        self.assertAlmostEqual(norm_original[0].y, 0.0, places=5)
        self.assertAlmostEqual(norm_translated[0].x, 0.0, places=5)
        self.assertAlmostEqual(norm_translated[0].y, 0.0, places=5)

        # Normalized X, Y, Z coordinates must match between original and translated
        for i in range(21):
            self.assertAlmostEqual(norm_original[i].x, norm_translated[i].x, places=5)
            self.assertAlmostEqual(norm_original[i].y, norm_translated[i].y, places=5)
            self.assertAlmostEqual(norm_original[i].z, norm_translated[i].z, places=5)

    def test_02_scale_invariance(self):
        # Create scaled points (scaled by 3.5x)
        scaled_points = [
            LandmarkPoint(x=p.x * 3.5, y=p.y * 3.5, z=p.z * 3.5) for p in self.raw_points
        ]

        norm_original = LandmarkNormalizer.normalize_points(self.raw_points)
        norm_scaled = LandmarkNormalizer.normalize_points(scaled_points)

        for i in range(21):
            self.assertAlmostEqual(norm_original[i].x, norm_scaled[i].x, places=5)
            self.assertAlmostEqual(norm_original[i].y, norm_scaled[i].y, places=5)
            self.assertAlmostEqual(norm_original[i].z, norm_scaled[i].z, places=5)

    def test_03_array_normalization(self):
        flat_coords = np.array([float(i * 0.02) for i in range(63)], dtype=np.float32)
        norm_flat = LandmarkNormalizer.normalize_array(flat_coords)

        self.assertEqual(norm_flat.shape, (63,))
        self.assertAlmostEqual(norm_flat[0], 0.0, places=5)
        self.assertAlmostEqual(norm_flat[1], 0.0, places=5)
        self.assertAlmostEqual(norm_flat[2], 0.0, places=5)

    def test_04_normalize_landmarks_api_endpoint(self):
        payload = {"landmarks": [{"x": p.x, "y": p.y, "z": p.z} for p in self.raw_points]}
        response = self.client.post("/api/v1/ai/normalize-landmarks", json=payload, headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 21)
        self.assertEqual(data[0]["x"], 0.0)
        self.assertEqual(data[0]["y"], 0.0)
        self.assertEqual(data[0]["z"], 0.0)

if __name__ == "__main__":
    unittest.main()
