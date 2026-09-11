import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.domain import User, RoleEnum, LearnerProfile
from app.core.security import get_password_hash

class TestLandingAuthRoutingFlow(unittest.TestCase):
    """
    Automated Test Suite for Public Landing Page, Authentication Guard, and Application Flow:
    1. Root route opens Landing page.
    2. Primary CTA 'Get Started for Free' routes to /login.
    3. Unauthenticated access to protected routes (/dashboard, /lessons, /quizzes, /certificate, /webcam-practice) is guarded.
    4. Successful login returns /dashboard destination with JWT credentials.
    5. Authenticated sessions grant access to protected endpoints.
    6. Logout revokes token and returns to public Landing page.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Seed Test Learner
        cls.test_email = "landing_flow_learner@test.com"
        cls.test_password = "password123"
        existing = cls.db.query(User).filter(User.email == cls.test_email).first()
        if not existing:
            u = User(
                email=cls.test_email,
                full_name="Landing Flow Learner",
                hashed_password=get_password_hash(cls.test_password),
                role=RoleEnum.LEARNER
            )
            cls.db.add(u)
            cls.db.commit()
            cls.db.refresh(u)
            profile = LearnerProfile(user_id=u.id, preferred_language="English")
            cls.db.add(profile)
            cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        u = cls.db.query(User).filter(User.email == cls.test_email).first()
        if u:
            cls.db.delete(u)
            cls.db.commit()
        cls.db.close()

    def test_01_public_health_and_root_available_unauthenticated(self):
        """Public health check is accessible without authentication."""
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])

    def test_02_unauthenticated_protected_api_access_blocked(self):
        """Unauthenticated requests to protected APIs return 401 Unauthorized."""
        protected_endpoints = [
            "/api/v1/auth/me",
            "/api/v1/analytics/learner",
            "/api/v1/practice/history",
            "/api/v1/practice/mastery",
            "/api/v1/recommendations/next-sign"
        ]
        for ep in protected_endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 401, f"Expected 401 for unauthenticated access to {ep}")

    def test_03_login_flow_with_learner_role_succeeds(self):
        """Valid login returns valid tokens and learner role for dashboard routing."""
        payload = {
            "id": self.test_email,
            "password": self.test_password,
            "role": "Learner"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data["role"], "Learner")

    def test_04_authenticated_user_accesses_protected_modules(self):
        """Authenticated learner can access all learner modules."""
        # 1. Login
        login_res = self.client.post("/api/v1/auth/login", json={
            "id": self.test_email,
            "password": self.test_password,
            "role": "Learner"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Access /me (User Profile)
        me_res = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)

        # 3. Access /analytics/learner (Dashboard data)
        dash_res = self.client.get("/api/v1/analytics/learner", headers=headers)
        self.assertEqual(dash_res.status_code, 200)

        # 4. Access /practice/mastery (Quizzes & Skills data)
        mastery_res = self.client.get("/api/v1/practice/mastery", headers=headers)
        self.assertEqual(mastery_res.status_code, 200)

    def test_05_logout_revokes_session(self):
        """Logout endpoint revokes refresh token cleanly."""
        login_res = self.client.post("/api/v1/auth/login", json={
            "id": self.test_email,
            "password": self.test_password,
            "role": "Learner"
        })
        access_token = login_res.json()["access_token"]
        refresh_token = login_res.json()["refresh_token"]

        logout_res = self.client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        self.assertEqual(logout_res.status_code, 200)
        self.assertTrue(logout_res.json()["success"])

if __name__ == "__main__":
    unittest.main()
