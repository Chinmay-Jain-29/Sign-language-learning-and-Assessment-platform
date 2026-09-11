import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from scripts.train_classifiers import ClassifierExperimentRunner
from app.ai.classifier_service import get_classifier_report, run_classifier_experiments

class Phase10ClassifierExperimentsTestSuite(unittest.TestCase):
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
        cls.tr_csv = os.path.join(base_dir, "train.csv")
        cls.va_csv = os.path.join(base_dir, "val.csv")
        cls.m_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
        cls.rep_json = os.path.join(base_dir, "classifier_experiments_report.json")

    def test_01_classifier_experiment_runner(self):
        runner = ClassifierExperimentRunner(
            self.tr_csv, self.va_csv, self.m_dir, self.rep_json, seed=42
        )
        res = runner.run_experiments()

        self.assertIn("classifiers", res)
        self.assertIn("RandomForest", res["classifiers"])
        self.assertIn("DecisionTree", res["classifiers"])
        self.assertIn("SVM", res["classifiers"])
        self.assertIn("KNN", res["classifiers"])

        # Check that RandomForest accuracy is high (> 85%)
        rf_acc = res["classifiers"]["RandomForest"]["accuracy"]
        self.assertGreater(rf_acc, 0.85)

        # Check joblib model files creation
        rf_model_file = os.path.join(self.m_dir, "randomforest_model.joblib")
        self.assertTrue(os.path.exists(rf_model_file))

    def test_02_classifier_service(self):
        rep = get_classifier_report(self.rep_json)
        self.assertIn("best_model", rep)

    def test_03_classifier_api_authorization(self):
        # GET report by Learner -> 403 Forbidden
        l_res = self.client.get("/api/v1/ai/classifiers/report", headers=self.learner_headers)
        self.assertEqual(l_res.status_code, 403)

        # GET report by Instructor -> 200 OK
        i_res = self.client.get("/api/v1/ai/classifiers/report", headers=self.inst_headers)
        self.assertEqual(i_res.status_code, 200)
        data = i_res.json()
        self.assertIn("best_model", data)

        # POST train by Learner -> 403 Forbidden
        l_train = self.client.post("/api/v1/ai/classifiers/train", headers=self.learner_headers)
        self.assertEqual(l_train.status_code, 403)

        # POST train by Instructor -> 200 OK
        i_train = self.client.post("/api/v1/ai/classifiers/train", headers=self.inst_headers)
        self.assertEqual(i_train.status_code, 200)

if __name__ == "__main__":
    unittest.main()
