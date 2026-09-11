import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from scripts.dataset_explorer import DatasetExplorer
from scripts.image_loader import ASLImageLoader
from scripts.camera_test import CameraVerifier

class Phase4DatasetExplorerTestSuite(unittest.TestCase):
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

    def test_01_dataset_explorer_scan(self):
        datasets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets"))
        explorer = DatasetExplorer(datasets_dir)
        report = explorer.scan_dataset()
        
        self.assertIn("base_directory", report)
        self.assertIn("total_classes", report)
        self.assertIn("total_images", report)
        self.assertIn("class_distribution", report)

    def test_02_image_loader_utility(self):
        loader = ASLImageLoader(target_size=(64, 64), normalize=True)
        self.assertEqual(loader.target_size, (64, 64))
        self.assertTrue(loader.normalize)

    def test_03_camera_verifier_utility(self):
        verifier = CameraVerifier(camera_index=0)
        status = verifier.verify_camera()
        self.assertIn("is_available", status)
        self.assertIn("fps_estimate", status)

    def test_04_dataset_summary_api_authorization(self):
        # Learner -> 403 Forbidden
        learner_res = self.client.get("/api/v1/ai/dataset/summary", headers=self.learner_headers)
        self.assertEqual(learner_res.status_code, 403)

        # Instructor -> 200 OK
        inst_res = self.client.get("/api/v1/ai/dataset/summary", headers=self.inst_headers)
        self.assertEqual(inst_res.status_code, 200)
        data = inst_res.json()
        self.assertIn("total_classes", data)

if __name__ == "__main__":
    unittest.main()
