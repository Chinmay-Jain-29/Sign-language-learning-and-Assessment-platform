import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

class BackendTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_root_endpoint(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("AI Sign Language", data["message"])

    def test_02_health_endpoint(self):
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "Healthy")

    def test_03_auth_login(self):
        res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)

    def test_04_ai_practice_attempt(self):
        login_res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        landmarks = [{"x": 0.0, "y": 0.0, "z": 0.0}] + [{"x": 0.05 * i, "y": -0.1 * i, "z": 0.01} for i in range(1, 21)]
        payload = {"expected_sign": "A", "landmarks": landmarks}
        
        res = self.client.post("/api/v1/practice/attempt", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["assessment"]["expected_sign"], "A")

if __name__ == "__main__":
    unittest.main()
