import sys
import os
import unittest
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from scripts.dataset_quality_reporter import DatasetQualityReporter
from app.ai.dataset_quality_service import audit_dataset_quality

class Phase7DatasetQualityReportTestSuite(unittest.TestCase):
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

        # Create temporary dummy CSV with valid and invalid rows
        cls.temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "temp_test"))
        os.makedirs(cls.temp_dir, exist_ok=True)
        cls.in_csv = os.path.join(cls.temp_dir, "test_landmarks.csv")
        cls.clean_csv = os.path.join(cls.temp_dir, "test_landmarks_clean.csv")
        cls.inv_csv = os.path.join(cls.temp_dir, "test_landmarks_invalid.csv")
        cls.rep_json = os.path.join(cls.temp_dir, "test_quality_report.json")

        header = ["label"]
        for i in range(21):
            header.extend([f"x{i}", f"y{i}", f"z{i}"])
        header.append("sample_path")

        # Distinct non-collapsed normalized coordinates for valid hand sample
        valid_coords = [str(round(0.1 + (i % 21) * 0.03, 4)) for i in range(63)]
        invalid_coords = ["999.0"] * 63  # Out of bounds

        with open(cls.in_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(["A"] + valid_coords + ["sample_a.jpg"])
            writer.writerow(["B"] + invalid_coords + ["sample_b.jpg"])

    @classmethod
    def tearDownClass(cls):
        # Cleanup temp test files
        for p in [cls.in_csv, cls.clean_csv, cls.inv_csv, cls.rep_json]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def test_01_dataset_quality_reporter_validation(self):
        reporter = DatasetQualityReporter(self.in_csv, self.clean_csv, self.inv_csv, self.rep_json)
        report = reporter.process_and_generate_report()

        self.assertEqual(report["total_samples"], 2)
        self.assertEqual(report["valid_samples"], 1)
        self.assertEqual(report["invalid_samples"], 1)
        self.assertEqual(report["quality_score_percentage"], 50.0)

    def test_02_quality_service(self):
        res = audit_dataset_quality(self.in_csv, self.clean_csv, self.inv_csv, self.rep_json)
        self.assertIn("quality_score_percentage", res)

    def test_03_quality_report_api_authorization(self):
        # Learner -> 403 Forbidden
        learner_res = self.client.get("/api/v1/ai/dataset/quality-report", headers=self.learner_headers)
        self.assertEqual(learner_res.status_code, 403)

        # Instructor -> 200 OK
        inst_res = self.client.get("/api/v1/ai/dataset/quality-report", headers=self.inst_headers)
        self.assertEqual(inst_res.status_code, 200)
        data = inst_res.json()
        self.assertIn("quality_score_percentage", data)

if __name__ == "__main__":
    unittest.main()
