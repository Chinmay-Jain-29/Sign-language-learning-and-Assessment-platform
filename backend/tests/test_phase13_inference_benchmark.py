import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from scripts.benchmark_inference import AIInferenceBenchmarker
from app.ai.benchmark_service import get_benchmark_report, run_inference_benchmark

class Phase13InferenceBenchmarkTestSuite(unittest.TestCase):
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

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets"))
        cls.test_csv = os.path.join(base_dir, "test.csv")
        cls.model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "randomforest_tuned.joblib"))
        if not os.path.exists(cls.model_path):
            cls.model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "randomforest_model.joblib"))
        cls.rep_json = os.path.join(base_dir, "benchmark_report.json")

    def test_01_benchmark_script(self):
        test_rep_json = os.path.join(os.path.dirname(self.rep_json), "test_benchmark_report.json")
        benchmarker = AIInferenceBenchmarker(self.test_csv, self.model_path, test_rep_json, iterations=20)
        res = benchmarker.run_benchmark()

        self.assertIn("single_sample_latency", res)
        self.assertIn("p50_ms", res["single_sample_latency"])
        self.assertIn("p95_ms", res["single_sample_latency"])
        self.assertIn("fps_throughput", res)
        self.assertGreater(res["fps_throughput"], 1.0)

    def test_02_benchmark_service(self):
        rep = get_benchmark_report(self.rep_json)
        self.assertIn("single_sample_latency", rep)
        self.assertIn("model_size_mb", rep)

    def test_03_benchmark_api_authorization(self):
        # GET report by Learner -> 403 Forbidden
        l_res = self.client.get("/api/v1/ai/benchmark/report", headers=self.learner_headers)
        self.assertEqual(l_res.status_code, 403)

        # GET report by Instructor -> 200 OK
        i_res = self.client.get("/api/v1/ai/benchmark/report", headers=self.inst_headers)
        self.assertEqual(i_res.status_code, 200)
        data = i_res.json()
        self.assertIn("single_sample_latency", data)

        # POST run by Learner -> 403 Forbidden
        l_run = self.client.post("/api/v1/ai/benchmark/run", headers=self.learner_headers)
        self.assertEqual(l_run.status_code, 403)

        # POST run by Instructor -> 200 OK
        i_run = self.client.post("/api/v1/ai/benchmark/run", headers=self.inst_headers)
        self.assertEqual(i_run.status_code, 200)

if __name__ == "__main__":
    unittest.main()
