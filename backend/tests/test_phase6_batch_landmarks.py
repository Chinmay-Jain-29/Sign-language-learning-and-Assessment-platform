import sys
import os
import unittest
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from scripts.extract_landmarks import BatchLandmarkExtractor
from app.ai.landmark_extraction_service import run_landmark_extraction

class Phase6BatchLandmarkExtractorTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        # Login as Instructor
        inst_login = cls.client.post(
            "/api/v1/auth/login",
            data={"username": "instructor@example.com", "password": "password123"}
        )
        cls.inst_token = inst_login.json()["access_token"]
        cls.inst_headers = {"Authorization": f"Bearer {cls.inst_token}"}

        # Login as Learner
        learner_login = cls.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        cls.learner_token = learner_login.json()["access_token"]
        cls.learner_headers = {"Authorization": f"Bearer {cls.learner_token}"}

    def test_01_batch_landmark_extractor_class(self):
        datasets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets"))
        test_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "test_landmarks.csv"))

        extractor = BatchLandmarkExtractor(datasets_dir, test_csv)
        res = extractor.extract_landmarks_batch(max_samples_per_class=2)

        self.assertIn("total_images_scanned", res)
        self.assertIn("successful_extractions", res)
        self.assertIn("duration_seconds", res)

        if os.path.exists(test_csv):
            with open(test_csv, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                self.assertEqual(header[0], "label")
                self.assertEqual(header[-1], "sample_path")
                self.assertEqual(len(header), 65)  # label + 63 coords + sample_path
            os.remove(test_csv)

    def test_02_landmark_extraction_service(self):
        temp_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "temp_test_landmarks_service.csv"))
        stats = run_landmark_extraction(output_csv=temp_csv, max_samples_per_class=1)
        self.assertIn("successful_extractions", stats)
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

    def test_03_extract_landmarks_api_authorization(self):
        # Learner -> 403 Forbidden
        learner_res = self.client.post("/api/v1/ai/extract-landmarks", headers=self.learner_headers)
        self.assertEqual(learner_res.status_code, 403)

        # Instructor -> 200 OK
        temp_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "temp_test_landmarks_api.csv"))
        stats = run_landmark_extraction(output_csv=temp_csv, max_samples_per_class=1)
        self.assertIn("successful_extractions", stats)
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

if __name__ == "__main__":
    unittest.main()
