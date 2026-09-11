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

class TestDashboardDataIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = TestingSessionLocal()

        cls.new_user_email = "new_clean_learner@test.com"
        cls.active_user_email = "active_real_learner@test.com"
        cls.pwd = "password123"

        # 1. Seed New User (Zero practice history)
        cls.new_user = User(
            email=cls.new_user_email,
            full_name="New Clean Learner",
            hashed_password=get_password_hash(cls.pwd),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.new_user)
        cls.db.commit()
        cls.db.refresh(cls.new_user)
        p = LearnerProfile(user_id=cls.new_user.id, preferred_language="English")
        cls.db.add(p)
        cls.db.commit()

        # 2. Seed Active User (With real practice sessions and attempts)
        cls.active_user = User(
            email=cls.active_user_email,
            full_name="Active Real Learner",
            hashed_password=get_password_hash(cls.pwd),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.active_user)
        cls.db.commit()
        cls.db.refresh(cls.active_user)
        
        p_active = LearnerProfile(
            user_id=cls.active_user.id,
            overall_performance_score=100.0,
            practice_streak_days=1,
            total_practice_time_mins=25,
            preferred_language="English"
        )
        cls.db.add(p_active)
        cls.db.commit()

        # Add real session
        s1 = PracticeSession(
            learner_id=cls.active_user.id,
            selected_signs=["A"],
            total_attempts=5,
            correct_count=5,
            incorrect_count=0,
            average_accuracy=100.0,
            start_time=datetime.utcnow()
        )
        cls.db.add(s1)
        cls.db.commit()
        cls.db.refresh(s1)

        # Add 5 real attempts for letter 'A'
        for _ in range(5):
            a = AssessmentAttempt(
                learner_id=cls.active_user.id,
                session_id=s1.id,
                expected_sign="A",
                predicted_sign="A",
                confidence=0.95,
                gesture_accuracy=100.0,
                hand_shape_accuracy=100.0,
                position_accuracy=100.0,
                motion_accuracy=100.0,
                is_correct=True,
                timestamp=datetime.utcnow()
            )
            cls.db.add(a)

        # Add alphabet state for 'A'
        st = LearnerAlphabetState(
            learner_id=cls.active_user.id,
            sign_character="A",
            current_state=StateEnum.MASTERED,
            total_attempts=5,
            successful_attempts=5,
            average_accuracy=100.0,
            average_confidence=95.0,
            mastery_percentage=100.0,
            last_updated=datetime.utcnow()
        )
        cls.db.add(st)
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

    def test_01_new_user_returns_strictly_zero_or_null_metrics(self):
        """New user with no practice records returns 0/null and empty lists."""
        token = self._get_token(self.new_user_email)
        res = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Profile context
        self.assertEqual(data["user"]["full_name"], "New Clean Learner")
        self.assertEqual(data["user"]["email"], self.new_user_email)

        # Mathematical performance aggregates
        perf = data["performance"]
        self.assertEqual(perf["total_attempts"], 0)
        self.assertEqual(perf["total_sessions"], 0)
        self.assertIsNone(perf["overall_score"])
        self.assertIsNone(perf["overall_accuracy"])
        self.assertIsNone(perf["current_session_accuracy"])
        self.assertIsNone(perf["average_confidence"])
        self.assertEqual(perf["practice_streak_days"], 0)
        self.assertEqual(perf["total_practice_time_mins"], 0)

        # Lists must be empty (no fake items)
        self.assertEqual(data["strongest_signs"], [])
        self.assertEqual(data["weakest_signs"], [])
        self.assertEqual(data["signs_needing_revision"], [])
        self.assertEqual(data["session_trend"], [])
        self.assertEqual(data["mastery_list"], [])
        self.assertEqual(data["recent_attempts"], [])
        self.assertFalse(data["has_data"])

    def test_02_active_user_returns_verified_real_database_metrics(self):
        """Active user returns calculated values matching their database records."""
        token = self._get_token(self.active_user_email)
        res = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Profile
        self.assertEqual(data["user"]["full_name"], "Active Real Learner")
        self.assertEqual(data["user"]["email"], self.active_user_email)

        # Real performance metrics
        perf = data["performance"]
        self.assertEqual(perf["total_attempts"], 5)
        self.assertEqual(perf["total_sessions"], 1)
        self.assertEqual(perf["overall_accuracy"], 100.0)
        self.assertEqual(perf["current_session_accuracy"], 100.0)
        self.assertEqual(perf["practice_streak_days"], 1)

        # Mastered signs contains 'A'
        self.assertIn("A", data["strongest_signs"])
        self.assertTrue(len(data["session_trend"]) >= 1)
        self.assertTrue(len(data["recent_attempts"]) >= 1)
        self.assertEqual(data["recent_attempts"][0]["expected_sign"], "A")
        self.assertEqual(data["recent_attempts"][0]["predicted_sign"], "A")
        self.assertEqual(data["recent_attempts"][0]["confidence"], 95.0)
        self.assertEqual(data["recent_attempts"][0]["overall_accuracy"], 100.0)
        self.assertTrue(data["has_data"])

    def test_03_user_isolation_no_data_leakage(self):
        """User A records are completely invisible to User B."""
        token_a = self._get_token(self.active_user_email)
        token_b = self._get_token(self.new_user_email)

        res_a = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token_a}"})
        res_b = self.client.get("/api/v1/analytics/learner", headers={"Authorization": f"Bearer {token_b}"})

        data_a = res_a.json()
        data_b = res_b.json()

        # User A has 1 attempt, User B has 0
        self.assertEqual(data_a["performance"]["total_attempts"], 5)
        self.assertEqual(data_b["performance"]["total_attempts"], 0)
        self.assertEqual(len(data_b["session_trend"]), 0)
        self.assertEqual(len(data_a["recent_attempts"]), 5)
        self.assertEqual(len(data_b["recent_attempts"]), 0)

if __name__ == "__main__":
    unittest.main()
