import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from scripts.study_rf_hyperparameters import RFHyperparameterStudier
from app.ai.rf_hyperparameter_service import get_rf_hyperparameter_report, run_rf_hyperparameter_study

class Phase11RFHyperparameterStudyTestSuite(unittest.TestCase):
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
        cls.rep_json = os.path.join(base_dir, "rf_hyperparameter_study.json")

    def test_01_rf_hyperparameter_studier(self):
        # Run a quick 2-config micro study into isolated test report file
        test_rep_json = os.path.join(os.path.dirname(self.rep_json), "test_rf_hyperparameter_study.json")
        studier = RFHyperparameterStudier(
            self.tr_csv, self.va_csv, self.m_dir, test_rep_json, seed=42
        )
        res = studier.run_study(
            n_estimators_grid=[10, 20],
            max_depth_grid=[10],
            min_samples_leaf_grid=[1]
        )

        self.assertIn("experiments", res)
        self.assertIn("best_config", res)
        self.assertIn("best_accuracy", res)
        self.assertIn("selection_rationale", res)
        self.assertGreater(len(res["experiments"]), 0)

        # Verify tuned model joblib artifact exists
        tuned_model_file = os.path.join(self.m_dir, "randomforest_tuned.joblib")
        self.assertTrue(os.path.exists(tuned_model_file))

    def test_02_rf_hyperparameter_service(self):
        rep = get_rf_hyperparameter_report(self.rep_json)
        self.assertIn("best_config", rep)
        self.assertIn("best_accuracy", rep)

    def test_03_rf_hyperparameter_api_authorization(self):
        # GET report by Learner -> 403 Forbidden
        l_res = self.client.get("/api/v1/ai/rf/hyperparameters/report", headers=self.learner_headers)
        self.assertEqual(l_res.status_code, 403)

        # GET report by Instructor -> 200 OK
        i_res = self.client.get("/api/v1/ai/rf/hyperparameters/report", headers=self.inst_headers)
        self.assertEqual(i_res.status_code, 200)
        data = i_res.json()
        self.assertIn("best_config", data)

        # POST study by Learner -> 403 Forbidden
        l_study = self.client.post("/api/v1/ai/rf/hyperparameters/study", headers=self.learner_headers)
        self.assertEqual(l_study.status_code, 403)

        # POST study by Instructor -> 200 OK
        i_study = self.client.post("/api/v1/ai/rf/hyperparameters/study", headers=self.inst_headers)
        self.assertEqual(i_study.status_code, 200)

if __name__ == "__main__":
    unittest.main()
