import unittest
import os
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.models.domain import User, LearnerProfile, RoleEnum, LearningLevelEnum, AssessmentAttempt
from app.core.security import get_password_hash, create_access_token
from app.main import app

class TestPracticeModesNavigation(unittest.TestCase):
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
        # Clean users and learner profiles
        self.db.query(AssessmentAttempt).delete()
        self.db.query(LearnerProfile).delete()
        self.db.query(User).delete()
        self.db.commit()

        # Seed 3 Learners with different levels
        # 1. Beginner Learner
        self.user_beginner = User(
            id=101,
            email="beginner@test.com",
            full_name="Beginner Learner",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.user_beginner)
        self.db.flush()
        self.profile_beginner = LearnerProfile(
            user_id=101,
            learning_level=LearningLevelEnum.BEGINNER
        )
        self.db.add(self.profile_beginner)

        # 2. Intermediate Learner
        self.user_intermediate = User(
            id=102,
            email="intermediate@test.com",
            full_name="Intermediate Learner",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.user_intermediate)
        self.db.flush()
        self.profile_intermediate = LearnerProfile(
            user_id=102,
            learning_level=LearningLevelEnum.INTERMEDIATE
        )
        self.db.add(self.profile_intermediate)

        # 3. Advanced Learner
        self.user_advanced = User(
            id=103,
            email="advanced@test.com",
            full_name="Advanced Learner",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.user_advanced)
        self.db.flush()
        self.profile_advanced = LearnerProfile(
            user_id=103,
            learning_level=LearningLevelEnum.EXPERT
        )
        self.db.add(self.profile_advanced)

        self.db.commit()

        self.token_beginner = create_access_token(subject=str(self.user_beginner.id))
        self.token_intermediate = create_access_token(subject=str(self.user_intermediate.id))
        self.token_advanced = create_access_token(subject=str(self.user_advanced.id))

    def tearDown(self):
        self.db.close()

    def test_01_beginner_profile_returns_beginner_level(self):
        """Beginner learner profile returns learning_level == 'Beginner'."""
        res = self.client.get(
            "/api/v1/users/profile",
            headers={"Authorization": f"Bearer {self.token_beginner}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["learning_level"], "Beginner")
        self.assertEqual(data["role"], "Learner")

    def test_02_intermediate_profile_returns_intermediate_level(self):
        """Intermediate learner profile returns learning_level == 'Intermediate'."""
        res = self.client.get(
            "/api/v1/users/profile",
            headers={"Authorization": f"Bearer {self.token_intermediate}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["learning_level"], "Intermediate")

    def test_03_advanced_profile_returns_advanced_level(self):
        """Expert learner profile returns learning_level == 'Expert'."""
        res = self.client.get(
            "/api/v1/users/profile",
            headers={"Authorization": f"Bearer {self.token_advanced}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["learning_level"], "Expert")

    def test_04_admin_level_progression_updates_in_real_time(self):
        """Admin updating learner profile from Beginner to Intermediate updates learning_level immediately."""
        # Seed an admin
        admin_user = User(
            id=999,
            email="admin_nav@test.com",
            full_name="Nav Admin",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.ADMINISTRATOR,
            is_active=True
        )
        self.db.add(admin_user)
        self.db.commit()
        admin_token = create_access_token(subject=str(admin_user.id))

        # Admin updates level to Intermediate
        update_res = self.client.patch(
            "/api/v1/admin/learners/101/level",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"learning_level": "Intermediate"}
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["new_level"], "Intermediate")

        # Refetch learner profile
        get_res = self.client.get(
            "/api/v1/users/profile",
            headers={"Authorization": f"Bearer {self.token_beginner}"}
        )
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["learning_level"], "Intermediate")

    def test_05_learner_cannot_modify_own_level(self):
        """Learner attempting to self-modify established learning level is rejected with 403."""
        update_res = self.client.put(
            "/api/v1/users/profile",
            headers={"Authorization": f"Bearer {self.token_beginner}"},
            json={"learning_level": "Expert"}
        )
        self.assertEqual(update_res.status_code, 403)

    def test_06_practice_attempt_persistence_unaffected(self):
        """Existing practice attempt persistence works identically for beginner mode."""
        res = self.client.post(
            "/api/v1/practice/attempt",
            headers={"Authorization": f"Bearer {self.token_beginner}"},
            json={
                "expected_sign": "A",
                "predicted_sign": "A",
                "confidence": 0.92,
                "accuracy": 92.0,
                "gesture_accuracy": 92.0,
                "hand_shape_accuracy": 92.0,
                "motion_accuracy": 92.0,
                "position_accuracy": 92.0,
                "is_correct": True
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["expected_sign"], "A")
        self.assertEqual(data["is_correct"], True)

if __name__ == "__main__":
    unittest.main()
