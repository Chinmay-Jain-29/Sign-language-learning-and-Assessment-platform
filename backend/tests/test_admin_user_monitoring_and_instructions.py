import unittest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import get_db, Base
from app.models.domain import (
    User, RoleEnum, LearnerProfile, PracticeSession,
    AssessmentAttempt, Notification, InstructorInstruction
)
from app.core.security import create_access_token

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestAdminUserMonitoringAndInstructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

        def override_get_db():
            try:
                yield self.db
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

        # Seed test users
        # 1. Admin A (id=1)
        self.admin = User(
            id=1, email="admin@test.com", full_name="Admin Chief",
            hashed_password="fakehash", role=RoleEnum.ADMINISTRATOR, is_active=True
        )
        # 2. Instructor A (id=10)
        self.instructor_a = User(
            id=10, email="inst_a@test.com", full_name="Instructor Alice",
            hashed_password="fakehash", role=RoleEnum.INSTRUCTOR, is_active=True
        )
        # 3. Instructor B (id=11)
        self.instructor_b = User(
            id=11, email="inst_b@test.com", full_name="Instructor Bob",
            hashed_password="fakehash", role=RoleEnum.INSTRUCTOR, is_active=True
        )
        # 4. Trainer A (id=20)
        self.trainer_a = User(
            id=20, email="trainer_a@test.com", full_name="Trainer Tom",
            hashed_password="fakehash", role=RoleEnum.ACCESSIBILITY_TRAINER, is_active=True
        )
        # 5. Learner A (id=30)
        self.learner_a = User(
            id=30, email="learner_a@test.com", full_name="Learner Amy",
            hashed_password="fakehash", role=RoleEnum.LEARNER, is_active=True
        )
        # 6. Learner B (id=31)
        self.learner_b = User(
            id=31, email="learner_b@test.com", full_name="Learner Ben",
            hashed_password="fakehash", role=RoleEnum.LEARNER, is_active=True
        )

        self.db.add_all([
            self.admin, self.instructor_a, self.instructor_b,
            self.trainer_a, self.learner_a, self.learner_b
        ])
        self.db.commit()

        # Learner Profiles
        prof_a = LearnerProfile(user_id=30, learning_level="Beginner", preferred_language="English")
        prof_b = LearnerProfile(user_id=31, learning_level="Intermediate", preferred_language="English")
        self.db.add_all([prof_a, prof_b])
        self.db.commit()

        # Practice Session & Attempts for Learner A
        sess_a = PracticeSession(
            learner_id=30, selected_signs=["A", "B"], total_attempts=2, correct_count=2,
            incorrect_count=0, average_accuracy=94.0, average_confidence=0.94, status="completed"
        )
        self.db.add(sess_a)
        self.db.commit()

        att1 = AssessmentAttempt(
            session_id=sess_a.id, learner_id=30, expected_sign="A", predicted_sign="A",
            is_correct=True, confidence=0.96, gesture_accuracy=96.0, hand_shape_accuracy=96.0,
            motion_accuracy=96.0, position_accuracy=96.0, timestamp=datetime.utcnow()
        )
        att2 = AssessmentAttempt(
            session_id=sess_a.id, learner_id=30, expected_sign="B", predicted_sign="B",
            is_correct=True, confidence=0.92, gesture_accuracy=92.0, hand_shape_accuracy=92.0,
            motion_accuracy=92.0, position_accuracy=92.0, timestamp=datetime.utcnow()
        )
        self.db.add_all([att1, att2])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        app.dependency_overrides.clear()

    def get_auth_header(self, user_id: int, role: str = None):
        token = create_access_token(subject=str(user_id))
        return {"Authorization": f"Bearer {token}"}

    # TEST 1, 2, 3 — Role Counts
    def test_01_admin_role_counts(self):
        headers = self.get_auth_header(1, "Administrator")
        res = self.client.get("/api/v1/admin/counts", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["learner_count"], 2)
        self.assertEqual(data["trainer_count"], 1)
        self.assertEqual(data["instructor_count"], 2)
        self.assertEqual(data["total_users"], 5)

    # TEST 4 — View Learners returns only Learner role
    def test_04_view_learners_role_isolation(self):
        headers = self.get_auth_header(1, "Administrator")
        res = self.client.get("/api/v1/admin/users-by-role?role=Learner", headers=headers)
        self.assertEqual(res.status_code, 200)
        learners = res.json()
        self.assertEqual(len(learners), 2)
        for l in learners:
            self.assertEqual(l["role"], "Learner")
            self.assertIn(l["id"], [30, 31])

    # TEST 5 — View Trainers returns only Trainer role
    def test_05_view_trainers_role_isolation(self):
        headers = self.get_auth_header(1, "Administrator")
        res = self.client.get("/api/v1/admin/users-by-role?role=Accessibility%20Trainer", headers=headers)
        self.assertEqual(res.status_code, 200)
        trainers = res.json()
        self.assertEqual(len(trainers), 1)
        self.assertEqual(trainers[0]["role"], "Accessibility Trainer")
        self.assertEqual(trainers[0]["id"], 20)

    # TEST 6 — View Instructors returns only Instructor role
    def test_06_view_instructors_role_isolation(self):
        headers = self.get_auth_header(1, "Administrator")
        res = self.client.get("/api/v1/admin/users-by-role?role=Instructor", headers=headers)
        self.assertEqual(res.status_code, 200)
        instructors = res.json()
        self.assertEqual(len(instructors), 2)
        for i in instructors:
            self.assertEqual(i["role"], "Instructor")
            self.assertIn(i["id"], [10, 11])

    # TEST 7 — Track Learner A returns only Learner A data
    def test_07_track_learner_data_integrity(self):
        headers = self.get_auth_header(1, "Administrator")
        res = self.client.get("/api/v1/admin/users/30/activity", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["type"], "learner")
        self.assertEqual(data["user"]["id"], 30)
        self.assertEqual(data["user"]["full_name"], "Learner Amy")
        self.assertEqual(data["analytics"]["performance"]["total_attempts"], 2)
        self.assertEqual(data["analytics"]["performance"]["overall_accuracy"], 100.0)

    # TEST 8 — Track Instructor A returns only Instructor A data
    def test_08_track_instructor_data_integrity(self):
        headers = self.get_auth_header(1, "Administrator")
        res = self.client.get("/api/v1/admin/users/10/activity", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["type"], "instructor")
        self.assertEqual(data["user"]["id"], 10)
        self.assertEqual(data["user"]["full_name"], "Instructor Alice")
        self.assertEqual(data["total_instructions_issued"], 0)

    # TEST 9 — Track Trainer A returns only Trainer A data
    def test_09_track_trainer_data_integrity(self):
        headers = self.get_auth_header(1, "Administrator")
        res = self.client.get("/api/v1/admin/users/20/activity", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["type"], "trainer")
        self.assertEqual(data["user"]["id"], 20)
        self.assertEqual(data["user"]["full_name"], "Trainer Tom")

    # TEST 10 — Authorization Protection: Non-admin cannot access admin endpoints
    def test_10_non_admin_forbidden(self):
        # Learner
        headers_l = self.get_auth_header(30, "Learner")
        res_l = self.client.get("/api/v1/admin/counts", headers=headers_l)
        self.assertEqual(res_l.status_code, 403)

        # Instructor
        headers_i = self.get_auth_header(10, "Instructor")
        res_i = self.client.get("/api/v1/admin/users/30/activity", headers=headers_i)
        self.assertEqual(res_i.status_code, 403)

        # Trainer
        headers_t = self.get_auth_header(20, "Accessibility Trainer")
        res_t = self.client.post("/api/v1/admin/instructions", headers=headers_t, json={"recipient_id": 10, "message": "hello"})
        self.assertEqual(res_t.status_code, 403)

    # TEST 11 — MANDATORY PRIVATE ADMIN INSTRUCTION TEST
    # Admin sends: recipient = Instructor A, message: "Please review your assigned learners."
    # Instructor A: PASS — sees message
    # Instructor B: PASS — does NOT see message
    # Trainer A: PASS — does NOT see message
    # Learner A: PASS — does NOT see message
    def test_11_mandatory_private_admin_instruction_isolation(self):
        headers_admin = self.get_auth_header(1, "Administrator")
        directive_msg = "Please review your assigned learners."

        # Admin sends directive to Instructor A (id=10)
        send_res = self.client.post(
            "/api/v1/admin/instructions",
            headers=headers_admin,
            json={"recipient_id": 10, "message": directive_msg}
        )
        self.assertEqual(send_res.status_code, 201)
        self.assertTrue(send_res.json()["success"])

        # 1. Instructor A logs in -> CAN SEE
        headers_inst_a = self.get_auth_header(10, "Instructor")
        res_a = self.client.get("/api/v1/notifications/", headers=headers_inst_a)
        self.assertEqual(res_a.status_code, 200)
        msgs_a = [n["message"] for n in res_a.json()]
        self.assertIn(directive_msg, msgs_a)

        # 2. Instructor B logs in -> CANNOT SEE
        headers_inst_b = self.get_auth_header(11, "Instructor")
        res_b = self.client.get("/api/v1/notifications/", headers=headers_inst_b)
        self.assertEqual(res_b.status_code, 200)
        msgs_b = [n["message"] for n in res_b.json()]
        self.assertNotIn(directive_msg, msgs_b)

        # 3. Trainer A logs in -> CANNOT SEE
        headers_trainer = self.get_auth_header(20, "Accessibility Trainer")
        res_t = self.client.get("/api/v1/notifications/", headers=headers_trainer)
        self.assertEqual(res_t.status_code, 200)
        msgs_t = [n["message"] for n in res_t.json()]
        self.assertNotIn(directive_msg, msgs_t)

        # 4. Learner A logs in -> CANNOT SEE
        headers_learner = self.get_auth_header(30, "Learner")
        res_l = self.client.get("/api/v1/notifications/", headers=headers_learner)
        self.assertEqual(res_l.status_code, 200)
        msgs_l = [n["message"] for n in res_l.json()]
        self.assertNotIn(directive_msg, msgs_l)

    # TEST 12 — Cross-User Instruction Isolation
    def test_12_cross_user_admin_instruction_isolation(self):
        headers_admin = self.get_auth_header(1, "Administrator")

        # Admin -> Instructor A
        self.client.post(
            "/api/v1/admin/instructions",
            headers=headers_admin,
            json={"recipient_id": 10, "message": "Directive exclusively for Instructor A."}
        )

        # Admin -> Instructor B
        self.client.post(
            "/api/v1/admin/instructions",
            headers=headers_admin,
            json={"recipient_id": 11, "message": "Directive exclusively for Instructor B."}
        )

        # Instructor A verifies
        headers_a = self.get_auth_header(10, "Instructor")
        res_a = self.client.get("/api/v1/notifications/", headers=headers_a)
        msgs_a = [n["message"] for n in res_a.json()]
        self.assertIn("Directive exclusively for Instructor A.", msgs_a)
        self.assertNotIn("Directive exclusively for Instructor B.", msgs_a)

        # Instructor B verifies
        headers_b = self.get_auth_header(11, "Instructor")
        res_b = self.client.get("/api/v1/notifications/", headers=headers_b)
        msgs_b = [n["message"] for n in res_b.json()]
        self.assertIn("Directive exclusively for Instructor B.", msgs_b)
        self.assertNotIn("Directive exclusively for Instructor A.", msgs_b)

    # TEST 13 — Read status transition persists per user
    def test_13_notification_read_status_per_user(self):
        headers_admin = self.get_auth_header(1, "Administrator")
        send_res = self.client.post(
            "/api/v1/admin/instructions",
            headers=headers_admin,
            json={"recipient_id": 20, "message": "Directive for Trainer Tom"}
        )
        self.assertEqual(send_res.status_code, 201)

        headers_trainer = self.get_auth_header(20, "Accessibility Trainer")
        res_before = self.client.get("/api/v1/notifications/", headers=headers_trainer)
        notif_item = next(n for n in res_before.json() if n["message"] == "Directive for Trainer Tom")
        self.assertFalse(notif_item["is_read"])

        # Mark read
        read_res = self.client.patch(f"/api/v1/notifications/{notif_item['id']}/read", headers=headers_trainer)
        self.assertEqual(read_res.status_code, 200)
        self.assertTrue(read_res.json()["is_read"])

        res_after = self.client.get("/api/v1/notifications/", headers=headers_trainer)
        notif_item_after = next(n for n in res_after.json() if n["id"] == notif_item["id"])
        self.assertTrue(notif_item_after["is_read"])

if __name__ == "__main__":
    unittest.main()
