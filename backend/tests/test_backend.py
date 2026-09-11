import sys
import os
import unittest

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

class BackendIntegrationTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)

    def test_login_learner(self):
        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "Learner")

    def test_practice_attempt_ai_inference(self):
        # Login as learner
        login_res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Start session
        start_res = self.client.post("/api/v1/practice/sessions/start", json=["A", "B"], headers=headers)
        session_id = start_res.json()["session_id"]

        # Generate 21 sample landmark coordinates for Sign 'A'
        landmarks = [{"x": 0.0, "y": 0.0, "z": 0.0}] + [{"x": 0.05 * i, "y": -0.1 * i, "z": 0.01} for i in range(1, 21)]
        
        payload = {
            "expected_sign": "A",
            "landmarks": landmarks
        }
        
        res = self.client.post(f"/api/v1/practice/attempt?session_id={session_id}", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        assessment = data["assessment"]
        self.assertEqual(assessment["expected_sign"], "A")
        self.assertIn("confidence", assessment)
        self.assertIn("is_correct", assessment)

    def test_learner_dashboard_analytics(self):
        login_res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/analytics/learner", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("profile", data)
        self.assertIn("recommended_sign", data)
        self.assertIn("mastery_list", data)

if __name__ == "__main__":
    unittest.main()
