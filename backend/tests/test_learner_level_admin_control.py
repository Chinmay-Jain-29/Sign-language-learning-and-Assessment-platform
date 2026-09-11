import unittest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import get_db, Base
from app.core.security import get_password_hash, create_access_token
from app.models.domain import (
    User, LearnerProfile, RoleEnum, LearningLevelEnum, 
    AssessmentAttempt, LearningLevelAudit
)

class TestLearnerLevelAdminControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
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

        # Clean tables
        self.db.query(LearningLevelAudit).delete()
        self.db.query(AssessmentAttempt).delete()
        self.db.query(LearnerProfile).delete()
        self.db.query(User).delete()
        self.db.commit()

        # Seed Users:
        # 1. Admin
        self.admin = User(
            id=1,
            email="admin@test.com",
            full_name="Administrator Test",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.ADMINISTRATOR,
            is_active=True
        )
        self.db.add(self.admin)

        # 2. Instructor
        self.instructor = User(
            id=2,
            email="instructor@test.com",
            full_name="Instructor Test",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.INSTRUCTOR,
            is_active=True
        )
        self.db.add(self.instructor)

        # 3. Trainer
        self.trainer = User(
            id=3,
            email="trainer@test.com",
            full_name="Trainer Test",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.ACCESSIBILITY_TRAINER,
            is_active=True
        )
        self.db.add(self.trainer)

        # 4. Learner with established level (Beginner)
        self.learner_established = User(
            id=4,
            email="learner.established@test.com",
            full_name="Established Learner",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.learner_established)
        self.profile_established = LearnerProfile(
            user_id=4,
            learning_level=LearningLevelEnum.BEGINNER,
            preferred_language="English"
        )
        self.db.add(self.profile_established)

        # 5. Learner with unset level (None / Unset)
        self.learner_unset = User(
            id=5,
            email="learner.unset@test.com",
            full_name="Unset Level Learner",
            hashed_password=get_password_hash("pass123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.learner_unset)
        self.profile_unset = LearnerProfile(
            user_id=5,
            learning_level=None,
            preferred_language="English"
        )
        self.db.add(self.profile_unset)

        # Add practice attempts to learner_established
        attempt = AssessmentAttempt(
            learner_id=4,
            expected_sign="A",
            predicted_sign="A",
            confidence=95.0,
            is_correct=True,
            gesture_accuracy=94.0,
            hand_shape_accuracy=93.0,
            position_accuracy=95.0,
            motion_accuracy=94.0,
            timestamp=datetime.utcnow()
        )
        self.db.add(attempt)

        self.db.commit()

        # Generate tokens
        self.admin_token = create_access_token(subject=str(self.admin.id))
        self.instructor_token = create_access_token(subject=str(self.instructor.id))
        self.trainer_token = create_access_token(subject=str(self.trainer.id))
        self.learner_est_token = create_access_token(subject=str(self.learner_established.id))
        self.learner_unset_token = create_access_token(subject=str(self.learner_unset.id))

    def tearDown(self):
        self.db.close()

    def test_01_first_time_learner_can_set_initial_level(self):
        """Learner with unset level can select their initial learning level once."""
        headers = {"Authorization": f"Bearer {self.learner_unset_token}"}
        res = self.client.put(
            "/api/v1/users/profile",
            json={"learning_level": "Intermediate", "bio": "Starting ASL journey"},
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["learning_level"], "Intermediate")
        self.assertEqual(data["bio"], "Starting ASL journey")

        # Verify DB persisted
        prof = self.db.query(LearnerProfile).filter(LearnerProfile.user_id == 5).first()
        self.assertEqual(prof.learning_level, LearningLevelEnum.INTERMEDIATE)

    def test_02_learner_cannot_modify_established_learning_level(self):
        """Learner with established level cannot modify learning_level via profile API (403 Forbidden)."""
        headers = {"Authorization": f"Bearer {self.learner_est_token}"}
        res = self.client.put(
            "/api/v1/users/profile",
            json={"learning_level": "Expert"},
            headers=headers
        )
        self.assertEqual(res.status_code, 403)
        data = res.json()
        err_msg = data.get("message") or data.get("detail") or ""
        self.assertIn("cannot be modified once set", err_msg)

        # DB level remains Beginner
        prof = self.db.query(LearnerProfile).filter(LearnerProfile.user_id == 4).first()
        self.assertEqual(prof.learning_level, LearningLevelEnum.BEGINNER)

    def test_03_learner_can_update_other_profile_fields_without_touching_level(self):
        """Learner can update name, bio, phone while preserving established level."""
        headers = {"Authorization": f"Bearer {self.learner_est_token}"}
        res = self.client.put(
            "/api/v1/users/profile",
            json={"bio": "Updated bio text", "phone": "+1234567890"},
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["bio"], "Updated bio text")
        self.assertEqual(data["learning_level"], "Beginner")

    def test_04_non_admin_cannot_access_admin_level_endpoint(self):
        """Learner, Instructor, and Trainer cannot call admin level change API (403)."""
        for role_name, token in [
            ("Learner", self.learner_est_token),
            ("Instructor", self.instructor_token),
            ("Trainer", self.trainer_token)
        ]:
            headers = {"Authorization": f"Bearer {token}"}
            res = self.client.patch(
                "/api/v1/admin/learners/4/level",
                json={"learning_level": "Expert"},
                headers=headers
            )
            self.assertEqual(res.status_code, 403, f"{role_name} should not be authorized to change level")

    def test_05_admin_can_update_learner_level_upward_and_downward(self):
        """Administrator can update learner level both upward and downward with audit logging."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Upward change: Beginner -> Expert
        res1 = self.client.patch(
            "/api/v1/admin/learners/4/level",
            json={"learning_level": "Expert"},
            headers=headers
        )
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertTrue(data1["success"])
        self.assertEqual(data1["old_level"], "Beginner")
        self.assertEqual(data1["new_level"], "Expert")

        # Downward change: Expert -> Intermediate
        res2 = self.client.patch(
            "/api/v1/admin/learners/4/level",
            json={"learning_level": "Intermediate"},
            headers=headers
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["old_level"], "Expert")
        self.assertEqual(data2["new_level"], "Intermediate")

        # Downward change: Intermediate -> Beginner
        res3 = self.client.patch(
            "/api/v1/admin/learners/4/level",
            json={"learning_level": "Beginner"},
            headers=headers
        )
        self.assertEqual(res3.status_code, 200)
        data3 = res3.json()
        self.assertEqual(data3["old_level"], "Intermediate")
        self.assertEqual(data3["new_level"], "Beginner")

    def test_06_audit_trail_is_accurately_recorded_and_retrievable(self):
        """Every admin level change generates a complete audit trail record."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Make 2 changes
        self.client.patch("/api/v1/admin/learners/4/level", json={"learning_level": "Intermediate"}, headers=headers)
        self.client.patch("/api/v1/admin/learners/4/level", json={"learning_level": "Expert"}, headers=headers)

        # Retrieve level history
        res = self.client.get("/api/v1/admin/learners/4/level-history", headers=headers)
        self.assertEqual(res.status_code, 200)
        history = res.json()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["new_level"], "Expert")
        self.assertEqual(history[0]["old_level"], "Intermediate")
        self.assertEqual(history[0]["admin_name"], "Administrator Test")
        self.assertEqual(history[1]["new_level"], "Intermediate")
        self.assertEqual(history[1]["old_level"], "Beginner")

    def test_07_learner_practice_attempts_preserved_on_level_change(self):
        """Changing a learner's level does not delete or alter historical practice attempts."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.client.patch("/api/v1/admin/learners/4/level", json={"learning_level": "Expert"}, headers=headers)

        # Verify practice attempt exists unchanged
        attempts = self.db.query(AssessmentAttempt).filter(AssessmentAttempt.learner_id == 4).all()
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].expected_sign, "A")
        self.assertEqual(attempts[0].confidence, 95.0)

    def test_08_admin_telemetry_includes_level_and_history(self):
        """Admin user activity telemetry endpoint returns user level and audit history."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.client.patch("/api/v1/admin/learners/4/level", json={"learning_level": "Expert"}, headers=headers)

        res = self.client.get("/api/v1/admin/users/4/activity", headers=headers)
        self.assertEqual(res.status_code, 200)
        telemetry = res.json()
        self.assertEqual(telemetry["type"], "learner")
        self.assertEqual(telemetry["user"]["learning_level"], "Expert")
        self.assertIn("level_history", telemetry)
        self.assertGreaterEqual(len(telemetry["level_history"]), 1)


if __name__ == "__main__":
    unittest.main()
