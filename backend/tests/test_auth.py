import sys
import os
import unittest
from datetime import timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.database.session import SessionLocal, engine
from app.database.init_db import init_db

class AuthenticationAndAuthorizationTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        init_db(db)
        db.close()
        cls.client = TestClient(app)

    def test_01_valid_login(self):
        res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data["role"], "Learner")

    def test_02_invalid_password(self):
        res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "wrong_password"}
        )
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertFalse(data["success"])

    def test_03_missing_token(self):
        res = self.client.get("/api/v1/auth/me")
        self.assertEqual(res.status_code, 401)

    def test_04_expired_token(self):
        expired_token = create_access_token(subject=1, expires_delta=timedelta(hours=-1))
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        res = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertFalse(data["success"])

    def test_05_learner_accessing_admin_route_forbidden(self):
        login_res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/admin/users", headers=headers)
        self.assertEqual(res.status_code, 403)
        data = res.json()
        self.assertFalse(data["success"])

    def test_06_instructor_accessing_admin_route_forbidden(self):
        login_res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "instructor@example.com", "password": "password123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/admin/users", headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_07_administrator_access_admin_route_allowed(self):
        login_res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "admin@example.com", "password": "password123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/admin/users", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_08_refresh_token_and_logout(self):
        login_res = self.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        ref_token = login_res.json()["refresh_token"]

        ref_res = self.client.post("/api/v1/auth/refresh", json={"refresh_token": ref_token})
        self.assertEqual(ref_res.status_code, 200)
        self.assertIn("access_token", ref_res.json()["data"])

        acc_token = ref_res.json()["data"]["access_token"]
        logout_res = self.client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": ref_token},
            headers={"Authorization": f"Bearer {acc_token}"}
        )
        self.assertEqual(logout_res.status_code, 200)

        fail_res = self.client.post("/api/v1/auth/refresh", json={"refresh_token": ref_token})
        self.assertEqual(fail_res.status_code, 401)

if __name__ == "__main__":
    unittest.main()
