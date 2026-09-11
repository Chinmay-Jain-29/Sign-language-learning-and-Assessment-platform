import unittest
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import Base, get_db
from app.models.domain import (
    User, LearnerProfile, RoleEnum, AssessmentAttempt,
    AchievementDefinition, AchievementUnlock
)
from app.core.security import get_password_hash, create_access_token
from app.database.init_db import init_db

class TestAchievementSystem(unittest.TestCase):
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

    def setUp(self):
        self.db = self.TestingSessionLocal()
        # Seed definitions
        init_db(self.db)
        self.db.query(AchievementUnlock).delete()
        self.db.query(AssessmentAttempt).delete()
        self.db.query(LearnerProfile).delete()
        self.db.query(User).delete()
        self.db.commit()

        # Learner 1
        self.learner1 = User(
            id=101,
            email="learner1@example.com",
            full_name="Learner One",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.learner1)
        self.db.commit()

        self.profile1 = LearnerProfile(user_id=101)
        self.db.add(self.profile1)

        # Learner 2
        self.learner2 = User(
            id=102,
            email="learner2@example.com",
            full_name="Learner Two",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.learner2)
        self.db.commit()

        self.profile2 = LearnerProfile(user_id=102)
        self.db.add(self.profile2)
        self.db.commit()

        self.token_l1 = create_access_token(subject=str(self.learner1.id))
        self.token_l2 = create_access_token(subject=str(self.learner2.id))

    def tearDown(self):
        self.db.close()

    def _add_mastered_attempts(self, user_id: int, sign: str):
        """Helper to create 5 high-accuracy attempts satisfying canonical mastery rule (>=5 attempts, >=85% acc, >=85% conf)."""
        for _ in range(5):
            attempt = AssessmentAttempt(
                learner_id=user_id,
                expected_sign=sign,
                predicted_sign=sign,
                confidence=0.95,
                gesture_accuracy=95.0,
                hand_shape_accuracy=95.0,
                motion_accuracy=95.0,
                position_accuracy=95.0,
                is_correct=True,
                timestamp=datetime.utcnow()
            )
            self.db.add(attempt)
        self.db.commit()

    def test_01_new_learner_zero_unlocked(self):
        """TEST 1: New learner with no practice history has 26 achievements, 0 unlocked, 26 locked."""
        headers = {"Authorization": f"Bearer {self.token_l1}"}
        res = self.client.get("/api/v1/achievements", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 26)
        self.assertEqual(data["unlocked_count"], 0)
        self.assertEqual(data["locked_count"], 26)
        self.assertEqual(data["mastered_signs_count"], 0)
        self.assertEqual(data["completion_percentage"], 0.0)
        self.assertEqual(len(data["achievements"]), 26)
        for ach in data["achievements"]:
            self.assertFalse(ach["is_unlocked"])
            self.assertIsNone(ach["unlocked_at"])

    def test_02_mastered_sign_a_unlocks_achievement(self):
        """TEST 2: Sign A satisfies canonical mastery -> A achievement is unlocked."""
        self._add_mastered_attempts(user_id=101, sign="A")
        headers = {"Authorization": f"Bearer {self.token_l1}"}
        res = self.client.get("/api/v1/achievements", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["unlocked_count"], 1)
        self.assertEqual(data["locked_count"], 25)
        self.assertEqual(data["mastered_signs_count"], 1)

        ach_a = next(a for a in data["achievements"] if a["sign"] == "A")
        self.assertTrue(ach_a["is_unlocked"])
        self.assertEqual(ach_a["current_category"], "Mastered")
        self.assertIsNotNone(ach_a["unlocked_at"])

    def test_03_non_mastered_sign_b_remains_locked(self):
        """TEST 3: Sign B with only 1 attempt (not mastered) remains locked."""
        attempt = AssessmentAttempt(
            learner_id=101,
            expected_sign="B",
            predicted_sign="B",
            confidence=0.9,
            gesture_accuracy=90.0,
            hand_shape_accuracy=90.0,
            motion_accuracy=90.0,
            position_accuracy=90.0,
            is_correct=True,
            timestamp=datetime.utcnow()
        )
        self.db.add(attempt)
        self.db.commit()

        headers = {"Authorization": f"Bearer {self.token_l1}"}
        res = self.client.get("/api/v1/achievements", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        ach_b = next(a for a in data["achievements"] if a["sign"] == "B")
        self.assertFalse(ach_b["is_unlocked"])
        self.assertNotEqual(ach_b["current_category"], "Mastered")

    def test_04_multiple_mastered_signs(self):
        """TEST 4: Multiple signs mastered (A, D, I) -> exactly A, D, I unlocked."""
        for s in ["A", "D", "I"]:
            self._add_mastered_attempts(user_id=101, sign=s)

        headers = {"Authorization": f"Bearer {self.token_l1}"}
        res = self.client.get("/api/v1/achievements", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["unlocked_count"], 3)
        self.assertEqual(data["locked_count"], 23)
        self.assertEqual(data["mastered_signs_count"], 3)

        unlocked_signs = {a["sign"] for a in data["achievements"] if a["is_unlocked"]}
        self.assertEqual(unlocked_signs, {"A", "D", "I"})

    def test_05_no_duplicate_unlock_records(self):
        """TEST 5: Repeatedly practicing mastered A does not create duplicate unlock rows."""
        self._add_mastered_attempts(user_id=101, sign="A")
        headers = {"Authorization": f"Bearer {self.token_l1}"}
        
        # Call achievements twice
        self.client.get("/api/v1/achievements", headers=headers)
        self.client.get("/api/v1/achievements", headers=headers)

        # Record another attempt via practice API
        self.client.post(
            "/api/v1/practice/attempt",
            json={"expected_sign": "A", "predicted_sign": "A", "confidence": 0.98, "accuracy": 98.0},
            headers=headers
        )

        unlock_count = self.db.query(AchievementUnlock).filter(
            AchievementUnlock.user_id == 101,
            AchievementUnlock.sign == "A"
        ).count()
        self.assertEqual(unlock_count, 1)

    def test_06_user_isolation(self):
        """TEST 6: Learner 1 has A unlocked; Learner 2 has A locked. Learner 2 cannot see Learner 1's achievement."""
        self._add_mastered_attempts(user_id=101, sign="A")

        headers_l1 = {"Authorization": f"Bearer {self.token_l1}"}
        headers_l2 = {"Authorization": f"Bearer {self.token_l2}"}

        res_l1 = self.client.get("/api/v1/achievements", headers=headers_l1).json()
        res_l2 = self.client.get("/api/v1/achievements", headers=headers_l2).json()

        self.assertEqual(res_l1["unlocked_count"], 1)
        self.assertEqual(res_l2["unlocked_count"], 0)

        ach_a_l1 = next(a for a in res_l1["achievements"] if a["sign"] == "A")
        ach_a_l2 = next(a for a in res_l2["achievements"] if a["sign"] == "A")

        self.assertTrue(ach_a_l1["is_unlocked"])
        self.assertFalse(ach_a_l2["is_unlocked"])

    def test_07_mastery_regression_maintains_unlocked_status(self):
        """TEST 7: Sign A is mastered & unlocked. Later performance drops to Needs Revision. Achievement remains unlocked."""
        # 1. Master sign A
        self._add_mastered_attempts(user_id=101, sign="A")
        headers = {"Authorization": f"Bearer {self.token_l1}"}
        self.client.get("/api/v1/achievements", headers=headers)

        # 2. Add 10 failed attempts to drag accuracy down to < 50%
        for _ in range(10):
            attempt = AssessmentAttempt(
                learner_id=101,
                expected_sign="A",
                predicted_sign="B",
                confidence=0.2,
                gesture_accuracy=20.0,
                hand_shape_accuracy=20.0,
                motion_accuracy=20.0,
                position_accuracy=20.0,
                is_correct=False,
                timestamp=datetime.utcnow()
            )
            self.db.add(attempt)
        self.db.commit()

        # 3. Verify canonical mastery is now 'Needs Revision'
        res_analytics = self.client.get("/api/v1/analytics/learner", headers=headers).json()
        stat_a = next(s for s in res_analytics["sign_classification"] if s["sign"] == "A")
        self.assertEqual(stat_a["category"], "Needs Revision")

        # 4. Verify achievement remains UNLOCKED in achievement history
        res_ach = self.client.get("/api/v1/achievements", headers=headers).json()
        ach_a = next(a for a in res_ach["achievements"] if a["sign"] == "A")
        self.assertTrue(ach_a["is_unlocked"])
        self.assertEqual(ach_a["current_category"], "Needs Revision")
        self.assertEqual(res_ach["unlocked_count"], 1)

    def test_08_completion_percentage_calculation(self):
        """TEST 8: If 13 achievements unlocked, completion is exactly 50.0%."""
        half_signs = [chr(i) for i in range(ord('A'), ord('A') + 13)]
        for s in half_signs:
            self._add_mastered_attempts(user_id=101, sign=s)

        headers = {"Authorization": f"Bearer {self.token_l1}"}
        res = self.client.get("/api/v1/achievements", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["unlocked_count"], 13)
        self.assertEqual(data["completion_percentage"], 50.0)

    def test_09_canonical_consistency(self):
        """TEST 9: Sign classification == Mastery Matrix == Achievement state."""
        self._add_mastered_attempts(user_id=101, sign="Z")
        headers = {"Authorization": f"Bearer {self.token_l1}"}

        res_analytics = self.client.get("/api/v1/analytics/learner", headers=headers).json()
        stat_z = next(s for s in res_analytics["sign_classification"] if s["sign"] == "Z")
        self.assertEqual(stat_z["category"], "Mastered")

        res_ach = self.client.get("/api/v1/achievements", headers=headers).json()
        ach_z = next(a for a in res_ach["achievements"] if a["sign"] == "Z")
        self.assertTrue(ach_z["is_unlocked"])
        self.assertEqual(ach_z["current_category"], "Mastered")

    def test_10_security_unauthenticated_rejected(self):
        """TEST 10: Unauthorized request rejected with 401."""
        res = self.client.get("/api/v1/achievements")
        self.assertEqual(res.status_code, 401)

if __name__ == "__main__":
    unittest.main()
