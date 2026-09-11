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
from app.models.domain import User, RoleEnum, LearnerProfile, PracticeSession, AssessmentAttempt, LearnerAlphabetState, StateEnum
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

class TestMasteryAndSessionTrendAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = TestingSessionLocal()
        cls.pwd = "password123"

        cls.user_email = "mastery_tester@example.com"
        cls.user2_email = "isolation_tester@example.com"

        # Primary test user
        cls.user = User(
            email=cls.user_email,
            full_name="Mastery Tester",
            hashed_password=get_password_hash(cls.pwd),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.user)
        cls.db.commit()
        cls.db.refresh(cls.user)

        p = LearnerProfile(user_id=cls.user.id)
        cls.db.add(p)
        cls.db.commit()

        # Isolation test user
        cls.user2 = User(
            email=cls.user2_email,
            full_name="Isolation Tester",
            hashed_password=get_password_hash(cls.pwd),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.user2)
        cls.db.commit()
        cls.db.refresh(cls.user2)

        p2 = LearnerProfile(user_id=cls.user2.id)
        cls.db.add(p2)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()

    def _get_token(self, email):
        res = self.client.post("/api/v1/auth/login", json={
            "id": email,
            "password": self.pwd,
            "role": "Learner"
        })
        return res.json()["access_token"]

    def test_01_sign_mastery_rules_comprehensive(self):
        token = self._get_token(self.user_email)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Sign A: 5 consecutive correct with 92% confidence
        for _ in range(5):
            res = self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "A",
                "predicted_sign": "A",
                "confidence": 0.92,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Correct! You performed sign A."
            }, headers=headers)
            self.assertEqual(res.status_code, 200)

        # 2. Sign B: 5 attempts (3 correct, 2 incorrect, 90% confidence)
        for i in range(5):
            is_corr = i < 3
            pred = "B" if is_corr else "C"
            self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "B",
                "predicted_sign": pred,
                "confidence": 0.90,
                "is_correct": is_corr,
                "gesture_accuracy": 100.0 if is_corr else 0.0,
                "feedback": "Feedback for B"
            }, headers=headers)

        # 3. Sign C: 3 attempts (3 correct, 92% confidence) - insufficient attempts
        for _ in range(3):
            self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "C",
                "predicted_sign": "C",
                "confidence": 0.92,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Correct C"
            }, headers=headers)

        # 4. Sign D: 10 attempts (10 correct, 70% confidence) - low confidence
        for _ in range(10):
            self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "D",
                "predicted_sign": "D",
                "confidence": 0.70,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Correct D"
            }, headers=headers)

        # 5. Sign E: 10 attempts (4 correct, 6 incorrect, 95% confidence) - low accuracy
        for i in range(10):
            is_corr = i < 4
            pred = "E" if is_corr else "F"
            self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "E",
                "predicted_sign": pred,
                "confidence": 0.95,
                "is_correct": is_corr,
                "gesture_accuracy": 100.0 if is_corr else 0.0,
                "feedback": "Feedback for E"
            }, headers=headers)

        # Now query dashboard analytics
        dash_res = self.client.get("/api/v1/analytics/learner", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        data = dash_res.json()

        sign_class = {s["sign"]: s for s in data["sign_classification"]}

        # Check Sign A -> MASTERED
        self.assertEqual(sign_class["A"]["category"], "Mastered")
        self.assertEqual(sign_class["A"]["total_attempts"], 5)
        self.assertEqual(sign_class["A"]["correct_attempts"], 5)
        self.assertEqual(sign_class["A"]["accuracy"], 100.0)
        self.assertGreaterEqual(sign_class["A"]["average_confidence"], 85.0)
        self.assertIn("A", data["strongest_signs"])

        # Check Sign B -> PRACTICING (Not Mastered because accuracy = 60.0% < 85%)
        self.assertEqual(sign_class["B"]["category"], "Practicing")
        self.assertEqual(sign_class["B"]["total_attempts"], 5)
        self.assertEqual(sign_class["B"]["correct_attempts"], 3)
        self.assertEqual(sign_class["B"]["accuracy"], 60.0)

        # Check Sign C -> PRACTICING (Not Mastered because total_attempts = 3 < 5)
        self.assertEqual(sign_class["C"]["category"], "Practicing")
        self.assertEqual(sign_class["C"]["total_attempts"], 3)
        self.assertEqual(sign_class["C"]["accuracy"], 100.0)

        # Check Sign D -> PRACTICING (Not Mastered because avg_conf = 70.0% < 85%)
        self.assertEqual(sign_class["D"]["category"], "Practicing")
        self.assertEqual(sign_class["D"]["total_attempts"], 10)
        self.assertEqual(sign_class["D"]["accuracy"], 100.0)
        self.assertEqual(sign_class["D"]["average_confidence"], 70.0)

        # Check Sign E -> LEARNING / NEEDS REVISION (Not Mastered because accuracy = 40.0% < 50%)
        self.assertIn(sign_class["E"]["category"], ["Learning", "Needs Revision"])
        self.assertEqual(sign_class["E"]["total_attempts"], 10)
        self.assertEqual(sign_class["E"]["accuracy"], 40.0)

    def test_02_session_performance_trend_chronological(self):
        token = self._get_token(self.user2_email)
        headers = {"Authorization": f"Bearer {token}"}

        # Session 1: 60%
        s1_res = self.client.post("/api/v1/practice/sessions/start", json=["A"], headers=headers)
        s1_id = s1_res.json()["session_id"]
        for i in range(5):
            is_corr = i < 3
            self.client.post(f"/api/v1/practice/attempt?session_id={s1_id}", json={
                "expected_sign": "A",
                "predicted_sign": "A" if is_corr else "B",
                "confidence": 0.88,
                "is_correct": is_corr,
                "gesture_accuracy": 100.0 if is_corr else 0.0,
                "feedback": "Feedback"
            }, headers=headers)

        # Session 2: 80%
        s2_res = self.client.post("/api/v1/practice/sessions/start", json=["B"], headers=headers)
        s2_id = s2_res.json()["session_id"]
        for i in range(5):
            is_corr = i < 4
            self.client.post(f"/api/v1/practice/attempt?session_id={s2_id}", json={
                "expected_sign": "B",
                "predicted_sign": "B" if is_corr else "C",
                "confidence": 0.90,
                "is_correct": is_corr,
                "gesture_accuracy": 100.0 if is_corr else 0.0,
                "feedback": "Feedback"
            }, headers=headers)

        # Session 3: 100%
        s3_res = self.client.post("/api/v1/practice/sessions/start", json=["C"], headers=headers)
        s3_id = s3_res.json()["session_id"]
        for _ in range(5):
            self.client.post(f"/api/v1/practice/attempt?session_id={s3_id}", json={
                "expected_sign": "C",
                "predicted_sign": "C",
                "confidence": 0.94,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Feedback"
            }, headers=headers)

        # Query dashboard for User 2
        res = self.client.get("/api/v1/analytics/learner", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        trend = data["session_trend"]
        self.assertEqual(len(trend), 3)

        self.assertEqual(trend[0]["session_number"], 1)
        self.assertEqual(trend[0]["accuracy"], 60.0)
        self.assertEqual(trend[0]["score"], 60.0)

        self.assertEqual(trend[1]["session_number"], 2)
        self.assertEqual(trend[1]["accuracy"], 80.0)
        self.assertEqual(trend[1]["score"], 80.0)

        self.assertEqual(trend[2]["session_number"], 3)
        self.assertEqual(trend[2]["accuracy"], 100.0)
        self.assertEqual(trend[2]["score"], 100.0)

    def test_03_user_isolation(self):
        token1 = self._get_token(self.user_email)
        token2 = self._get_token(self.user2_email)

        data1 = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token1}"}).json()
        data2 = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token2}"}).json()

        # User 1 has sign A Mastered
        user1_a = next(s for s in data1["sign_classification"] if s["sign"] == "A")
        self.assertEqual(user1_a["category"], "Mastered")

        # User 2 practiced A only in session 1 (5 attempts, 3 correct = 60%) -> Practicing
        user2_a = next(s for s in data2["sign_classification"] if s["sign"] == "A")
        self.assertEqual(user2_a["category"], "Practicing")

if __name__ == "__main__":
    unittest.main()
