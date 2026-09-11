import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.models.domain import User, LearnerProfile, RoleEnum, LearningLevelEnum, AssessmentAttempt, AchievementUnlock, AchievementDefinition
from app.database.init_db import init_db
from app.core.security import get_password_hash, create_access_token
from app.main import app

class TestAchievementDirectPracticeNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=cls.engine)
        app.dependency_overrides.clear()

    def setUp(self):
        self.db = self.TestingSessionLocal()
        init_db(self.db)
        self.db.query(AchievementUnlock).delete()
        self.db.query(AssessmentAttempt).delete()
        self.db.query(LearnerProfile).delete()
        self.db.query(User).delete()
        self.db.commit()

        # Create authenticated learner
        self.learner = User(
            id=101,
            email="learner_nav@example.com",
            full_name="Navigation Tester",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.learner)
        self.db.commit()

        self.profile = LearnerProfile(
            user_id=101,
            learning_level=LearningLevelEnum.BEGINNER
        )
        self.db.add(self.profile)
        self.db.commit()

        self.token = create_access_token(subject=str(self.learner.id))

    def tearDown(self):
        self.db.close()

    def test_01_achievement_endpoint_returns_all_26_classes(self):
        """Achievements endpoint returns all 26 alphabet classes (A to Z) with canonical metadata."""
        res = self.client.get(
            "/api/v1/achievements",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 26)
        signs = [a["sign"] for a in data["achievements"]]
        expected_signs = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        self.assertEqual(signs, expected_signs)

    def test_02_individual_sign_achievement_lookup(self):
        """Direct achievement lookup for individual signs (A, D, I, Z) returns complete details."""
        for test_sign in ["A", "D", "I", "Z"]:
            res = self.client.get(
                f"/api/v1/achievements/{test_sign}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.assertEqual(res.status_code, 200)
            item = res.json()
            self.assertEqual(item["sign"], test_sign)
            self.assertEqual(item["title"], f"Master of {test_sign}")
            self.assertIn("is_unlocked", item)
            self.assertIn("accuracy", item)
            self.assertIn("total_attempts", item)

    def test_03_practice_attempt_with_preselected_target(self):
        """Practice attempt recorded with target sign from achievement navigation persists cleanly."""
        for sign in ["A", "D", "I", "Z"]:
            res = self.client.post(
                "/api/v1/practice/attempt",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "expected_sign": sign,
                    "predicted_sign": sign,
                    "confidence": 0.94,
                    "accuracy": 94.0,
                    "gesture_accuracy": 94.0,
                    "hand_shape_accuracy": 94.0,
                    "motion_accuracy": 94.0,
                    "position_accuracy": 94.0,
                    "is_correct": True
                }
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["expected_sign"], sign)
            self.assertEqual(data["is_correct"], True)

    def test_04_target_switching_during_session(self):
        """Learner can start at sign 'I' from Achievement and switch to 'B' cleanly."""
        # Step 1: Attempt sign 'I'
        res1 = self.client.post(
            "/api/v1/practice/attempt",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "expected_sign": "I",
                "predicted_sign": "I",
                "confidence": 0.95,
                "accuracy": 95.0,
                "gesture_accuracy": 95.0,
                "hand_shape_accuracy": 95.0,
                "motion_accuracy": 95.0,
                "position_accuracy": 95.0,
                "is_correct": True
            }
        )
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["expected_sign"], "I")

        # Step 2: Switch target to 'B'
        res2 = self.client.post(
            "/api/v1/practice/attempt",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "expected_sign": "B",
                "predicted_sign": "B",
                "confidence": 0.90,
                "accuracy": 90.0,
                "gesture_accuracy": 90.0,
                "hand_shape_accuracy": 90.0,
                "motion_accuracy": 90.0,
                "position_accuracy": 90.0,
                "is_correct": True
            }
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["expected_sign"], "B")

    def test_05_unauthenticated_request_rejected(self):
        """Unauthenticated request to achievement or practice endpoint is rejected with 401."""
        res = self.client.get("/api/v1/achievements")
        self.assertEqual(res.status_code, 401)

if __name__ == "__main__":
    unittest.main()
