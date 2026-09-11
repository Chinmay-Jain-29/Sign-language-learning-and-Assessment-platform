import sys
import os
import unittest
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from scripts.split_dataset import StratifiedDatasetSplitter
from app.ai.dataset_split_service import run_dataset_split

class Phase9DatasetSplitTestSuite(unittest.TestCase):
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

        # Setup temporary dataset for testing
        cls.temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "temp_split_test"))
        os.makedirs(cls.temp_dir, exist_ok=True)
        cls.in_csv = os.path.join(cls.temp_dir, "test_normalized.csv")
        cls.tr_csv = os.path.join(cls.temp_dir, "train.csv")
        cls.va_csv = os.path.join(cls.temp_dir, "val.csv")
        cls.te_csv = os.path.join(cls.temp_dir, "test.csv")
        cls.rep_json = os.path.join(cls.temp_dir, "split_report.json")

        header = ["label"] + [f"x{i}" for i in range(21)] + [f"y{i}" for i in range(21)] + [f"z{i}" for i in range(21)] + ["sample_path"]

        with open(cls.in_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            # Create 100 samples for Class A and 100 for Class B
            for i in range(100):
                row_a = ["A"] + [str(round(0.01 * (i % 10), 3))] * 63 + [f"a_{i}.jpg"]
                row_b = ["B"] + [str(round(0.02 * (i % 10), 3))] * 63 + [f"b_{i}.jpg"]
                writer.writerow(row_a)
                writer.writerow(row_b)

    @classmethod
    def tearDownClass(cls):
        for p in [cls.in_csv, cls.tr_csv, cls.va_csv, cls.te_csv, cls.rep_json]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def test_01_stratified_splitter(self):
        splitter = StratifiedDatasetSplitter(
            self.in_csv, self.tr_csv, self.va_csv, self.te_csv, self.rep_json,
            train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42
        )
        res = splitter.process_and_split()

        self.assertEqual(res["total_samples"], 200)
        self.assertEqual(res["train_count"], 140)
        self.assertEqual(res["val_count"], 30)
        self.assertEqual(res["test_count"], 30)
        self.assertEqual(res["train_ratio_achieved"], 70.0)

        # Check Class A and B distribution in split
        self.assertEqual(res["class_distribution"]["A"]["train"], 70)
        self.assertEqual(res["class_distribution"]["A"]["val"], 15)
        self.assertEqual(res["class_distribution"]["A"]["test"], 15)

    def test_02_split_service(self):
        res = run_dataset_split(self.in_csv, self.tr_csv, self.va_csv, self.te_csv, self.rep_json)
        self.assertIn("train_count", res)

    def test_03_split_api_authorization(self):
        # Learner -> 403 Forbidden
        learner_res = self.client.post("/api/v1/ai/dataset/split", headers=self.learner_headers)
        self.assertEqual(learner_res.status_code, 403)

        # Instructor -> 200 OK
        inst_res = self.client.post("/api/v1/ai/dataset/split", headers=self.inst_headers)
        self.assertEqual(inst_res.status_code, 200)
        data = inst_res.json()
        self.assertIn("train_count", data)

if __name__ == "__main__":
    unittest.main()
