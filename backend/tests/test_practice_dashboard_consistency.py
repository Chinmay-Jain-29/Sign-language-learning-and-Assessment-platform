import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.main import app
from app.models.domain import User, RoleEnum, LearnerProfile, PracticeSession, AssessmentAttempt, LearnerAlphabetState
from app.core.security import get_password_hash

# Test in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

class TestPracticeDashboardConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = TestingSessionLocal()

        cls.user_email = "practice_consistency_learner@test.com"
        cls.pwd = "password123"

        # Seed new user
        cls.user = User(
            email=cls.user_email,
            full_name="Consistency Tester",
            hashed_password=get_password_hash(cls.pwd),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.user)
        cls.db.commit()
        cls.db.refresh(cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()

    def _get_token(self):
        res = self.client.post("/api/v1/auth/login", json={
            "id": self.user_email,
            "password": self.pwd,
            "role": "Learner"
        })
        return res.json()["access_token"]

    def test_01_practice_attempt_saved_identically_to_db_and_dashboard(self):
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Start a practice session
        start_res = self.client.post("/api/v1/practice/sessions/start", json=["A", "B", "C"], headers=headers)
        self.assertEqual(start_res.status_code, 200)
        session_id = start_res.json()["session_id"]

        # 2. Record Attempt 1: Target A, Detected A, Confidence 92% (0.92)
        att1_res = self.client.post(
            f"/api/v1/practice/attempt?session_id={session_id}",
            json={
                "expected_sign": "A",
                "predicted_sign": "A",
                "confidence": 0.92,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Correct! You performed sign A."
            },
            headers=headers
        )
        self.assertEqual(att1_res.status_code, 200)
        att1_data = att1_res.json()
        self.assertEqual(att1_data["expected_sign"], "A")
        self.assertEqual(att1_data["predicted_sign"], "A")
        self.assertEqual(att1_data["confidence"], 0.92)
        self.assertTrue(att1_data["is_correct"])

        # 3. Record Attempt 2: Target B, Detected A (Incorrect), Confidence 88% (0.88)
        att2_res = self.client.post(
            f"/api/v1/practice/attempt?session_id={session_id}",
            json={
                "expected_sign": "B",
                "predicted_sign": "A",
                "confidence": 0.88,
                "is_correct": False,
                "gesture_accuracy": 0.0,
                "feedback": "Detected sign A. Please perform sign B."
            },
            headers=headers
        )
        self.assertEqual(att2_res.status_code, 200)

        # 4. Record Attempt 3: Target C, Detected C, Confidence 90% (0.90)
        att3_res = self.client.post(
            f"/api/v1/practice/attempt?session_id={session_id}",
            json={
                "expected_sign": "C",
                "predicted_sign": "C",
                "confidence": 0.90,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Correct! You performed sign C."
            },
            headers=headers
        )
        self.assertEqual(att3_res.status_code, 200)

        # 5. Query Dashboard Summary API
        dash_res = self.client.get("/api/v1/analytics/learner", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.json()

        # Check Aggregates
        perf = dash_data["performance"]
        self.assertEqual(perf["total_attempts"], 3)
        self.assertEqual(perf["overall_score"], 66.7) # 2/3 * 100
        self.assertEqual(perf["overall_accuracy"], 66.7)
        self.assertEqual(perf["average_confidence"], 90.0) # (92 + 88 + 90) / 3 = 90.0
        self.assertEqual(perf["current_session_accuracy"], 66.7)

        # Check Recent Attempt History (Newest first)
        recent = dash_data["recent_attempts"]
        self.assertEqual(len(recent), 3)

        # Item 1: Attempt 3 (C -> C -> 90%)
        self.assertEqual(recent[0]["expected_sign"], "C")
        self.assertEqual(recent[0]["predicted_sign"], "C")
        self.assertEqual(recent[0]["confidence"], 90.0)
        self.assertTrue(recent[0]["is_correct"])
        self.assertEqual(recent[0]["overall_accuracy"], 100.0)
        self.assertIn("Correct! You performed sign C.", recent[0]["feedback"])

        # Item 2: Attempt 2 (B -> A -> 88%)
        self.assertEqual(recent[1]["expected_sign"], "B")
        self.assertEqual(recent[1]["predicted_sign"], "A")
        self.assertEqual(recent[1]["confidence"], 88.0)
        self.assertFalse(recent[1]["is_correct"])
        self.assertEqual(recent[1]["overall_accuracy"], 0.0)
        self.assertIn("Detected sign A", recent[1]["feedback"])

        # Item 3: Attempt 1 (A -> A -> 92%)
        self.assertEqual(recent[2]["expected_sign"], "A")
        self.assertEqual(recent[2]["predicted_sign"], "A")
        self.assertEqual(recent[2]["confidence"], 92.0)
        self.assertTrue(recent[2]["is_correct"])
        self.assertEqual(recent[2]["overall_accuracy"], 100.0)
        self.assertIn("Correct! You performed sign A.", recent[2]["feedback"])

    def test_02_session_isolation_and_multi_session_accuracy(self):
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Start Session 2
        start2_res = self.client.post("/api/v1/practice/sessions/start", json=["D", "E"], headers=headers)
        self.assertEqual(start2_res.status_code, 200)
        session2_id = start2_res.json()["session_id"]

        # Record single 100% attempt in Session 2
        att_res = self.client.post(
            f"/api/v1/practice/attempt?session_id={session2_id}",
            json={
                "expected_sign": "D",
                "predicted_sign": "D",
                "confidence": 0.96,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Correct! You performed sign D."
            },
            headers=headers
        )
        self.assertEqual(att_res.status_code, 200)

        # Check Dashboard
        dash_res = self.client.get("/api/v1/analytics/learner", headers=headers)
        dash_data = dash_res.json()

        perf = dash_data["performance"]
        self.assertEqual(perf["total_sessions"], 2)
        # Latest session (Session 2) accuracy is 100.0%
        self.assertEqual(perf["current_session_accuracy"], 100.0)
        # Overall accuracy across all 4 attempts (3 correct out of 4) = 75.0%
        self.assertEqual(perf["overall_accuracy"], 75.0)

if __name__ == "__main__":
    unittest.main()
