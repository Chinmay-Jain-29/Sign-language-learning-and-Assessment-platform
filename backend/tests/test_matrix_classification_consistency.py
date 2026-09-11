import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.main import app
from app.models.domain import User, RoleEnum, LearnerProfile, PracticeSession, AssessmentAttempt, LearnerAlphabetState, StateEnum
from app.core.security import get_password_hash
from app.services.practice_analytics_service import ALL_SIGNS

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

class TestMatrixClassificationConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = TestingSessionLocal()
        cls.pwd = "password123"

        cls.user_a_email = "matrix_user_a@aslsensei.com"
        cls.user_b_email = "matrix_user_b@aslsensei.com"

        # User A
        cls.user_a = User(
            email=cls.user_a_email,
            full_name="Matrix Learner A",
            hashed_password=get_password_hash(cls.pwd),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.user_a)
        cls.db.commit()
        cls.db.refresh(cls.user_a)
        cls.db.add(LearnerProfile(user_id=cls.user_a.id))
        cls.db.commit()

        # User B
        cls.user_b = User(
            email=cls.user_b_email,
            full_name="Matrix Learner B",
            hashed_password=get_password_hash(cls.pwd),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.user_b)
        cls.db.commit()
        cls.db.refresh(cls.user_b)
        cls.db.add(LearnerProfile(user_id=cls.user_b.id))
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

    def test_01_sign_d_mastery_consistency(self):
        token = self._get_token(self.user_a_email)
        headers = {"Authorization": f"Bearer {token}"}

        # 10 attempts for D
        for _ in range(10):
            res = self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "D",
                "predicted_sign": "D",
                "confidence": 0.91,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Correct D"
            }, headers=headers)
            self.assertEqual(res.status_code, 200)

        # Query analytics endpoint
        analytics_res = self.client.get("/api/v1/analytics/learner", headers=headers)
        self.assertEqual(analytics_res.status_code, 200)
        data = analytics_res.json()

        # Check sign classification list
        sign_class_map = {s["sign"]: s for s in data["sign_classification"]}

        # Verify D in Sign Classification
        self.assertEqual(sign_class_map["D"]["category"], "Mastered")
        self.assertEqual(sign_class_map["D"]["accuracy"], 100.0)
        self.assertEqual(sign_class_map["D"]["average_confidence"], 91.0)
        self.assertEqual(sign_class_map["D"]["total_attempts"], 10)

        # Verify strongest_signs list
        self.assertIn("D", data["strongest_signs"])

    def test_02_negative_test_sign_e_not_mastered(self):
        token = self._get_token(self.user_a_email)
        headers = {"Authorization": f"Bearer {token}"}

        # 10 attempts for E (4 correct, 6 wrong)
        for i in range(10):
            is_corr = i < 4
            self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "E",
                "predicted_sign": "E" if is_corr else "F",
                "confidence": 0.90,
                "is_correct": is_corr,
                "gesture_accuracy": 100.0 if is_corr else 0.0,
                "feedback": "Feedback for E"
            }, headers=headers)

        data = self.client.get("/api/v1/analytics/learner", headers=headers).json()
        sign_class_map = {s["sign"]: s for s in data["sign_classification"]}

        self.assertNotEqual(sign_class_map["E"]["category"], "Mastered")
        self.assertNotIn("E", data["strongest_signs"])

    def test_03_multi_sign_classification_matrix_agreement(self):
        token = self._get_token(self.user_a_email)
        headers = {"Authorization": f"Bearer {token}"}

        # 5 attempts for A
        for _ in range(5):
            self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "A",
                "predicted_sign": "A",
                "confidence": 0.90,
                "is_correct": True,
                "gesture_accuracy": 100.0,
                "feedback": "Correct A"
            }, headers=headers)

        # 1 attempt for B
        self.client.post("/api/v1/practice/attempt", json={
            "expected_sign": "B",
            "predicted_sign": "B",
            "confidence": 0.90,
            "is_correct": True,
            "gesture_accuracy": 100.0,
            "feedback": "Correct B"
        }, headers=headers)

        # 4 attempts for C (1 correct, 3 wrong)
        for i in range(4):
            is_corr = i == 0
            self.client.post("/api/v1/practice/attempt", json={
                "expected_sign": "C",
                "predicted_sign": "C" if is_corr else "D",
                "confidence": 0.85,
                "is_correct": is_corr,
                "gesture_accuracy": 100.0 if is_corr else 0.0,
                "feedback": "Feedback C"
            }, headers=headers)

        data = self.client.get("/api/v1/analytics/learner", headers=headers).json()
        sign_class_map = {s["sign"]: s for s in data["sign_classification"]}

        self.assertEqual(sign_class_map["A"]["category"], "Mastered")
        self.assertIn("A", data["strongest_signs"])
        self.assertIn("D", data["strongest_signs"])
        self.assertNotIn("B", data["strongest_signs"])
        self.assertNotIn("C", data["strongest_signs"])

    def test_04_user_isolation(self):
        token_a = self._get_token(self.user_a_email)
        token_b = self._get_token(self.user_b_email)

        data_a = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token_a}"}).json()
        data_b = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token_b}"}).json()

        map_a = {s["sign"]: s for s in data_a["sign_classification"]}
        map_b = {s["sign"]: s for s in data_b["sign_classification"]}

        self.assertEqual(map_a["D"]["category"], "Mastered")
        self.assertEqual(map_b["D"]["category"], "Not Attempted")
        self.assertIn("D", data_a["strongest_signs"])
        self.assertNotIn("D", data_b["strongest_signs"])

    def test_05_all_29_signs_represented(self):
        token = self._get_token(self.user_a_email)
        data = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token}"}).json()

        signs = [s["sign"] for s in data["sign_classification"]]
        self.assertEqual(len(signs), 29)
        self.assertEqual(signs, ALL_SIGNS)

if __name__ == "__main__":
    unittest.main()
