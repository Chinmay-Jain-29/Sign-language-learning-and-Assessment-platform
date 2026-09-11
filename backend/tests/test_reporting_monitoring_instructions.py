import unittest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.main import app
from app.models.domain import (
    User, RoleEnum, LearnerProfile, LearningLevelEnum,
    AssessmentAttempt, PracticeSession, InstructorInstruction, Notification, LearningGoal
)
from app.core.security import get_password_hash, create_access_token

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

class TestReportingMonitoringInstructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

        # Seed Learner A
        learner_a = User(
            id=101,
            email="learner_a@example.com",
            full_name="Learner Alice",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(learner_a)

        prof_a = LearnerProfile(
            id=101,
            user_id=101,
            learning_level=LearningLevelEnum.BEGINNER,
            overall_performance_score=90.0,
            practice_streak_days=5
        )
        self.db.add(prof_a)

        goal_a = LearningGoal(
            profile_id=101,
            goal_description="Master ASL Alphabet by next month",
            is_completed=False
        )
        self.db.add(goal_a)

        # Seed Learner B
        learner_b = User(
            id=102,
            email="learner_b@example.com",
            full_name="Learner Bob",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(learner_b)

        prof_b = LearnerProfile(
            id=102,
            user_id=102,
            learning_level=LearningLevelEnum.INTERMEDIATE,
            overall_performance_score=40.0,
            practice_streak_days=1
        )
        self.db.add(prof_b)

        # Seed Instructor A
        instructor = User(
            id=201,
            email="instructor_jane@example.com",
            full_name="Prof. Jane",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.INSTRUCTOR,
            is_active=True
        )
        self.db.add(instructor)

        # Seed Instructor B (Other Instructor)
        instructor_b = User(
            id=202,
            email="instructor_bob@example.com",
            full_name="Prof. Bob",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.INSTRUCTOR,
            is_active=True
        )
        self.db.add(instructor_b)

        # Seed Trainer
        trainer = User(
            id=301,
            email="trainer_sam@example.com",
            full_name="Trainer Sam",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.ACCESSIBILITY_TRAINER,
            is_active=True
        )
        self.db.add(trainer)

        # Seed Administrator
        admin = User(
            id=401,
            email="admin_chief@example.com",
            full_name="Chief Admin",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.ADMINISTRATOR,
            is_active=True
        )
        self.db.add(admin)

        # Seed 6 attempts for Learner A on sign 'A' (all correct, high confidence -> Mastered)
        sess_a = PracticeSession(id=1, learner_id=101, selected_signs=["A"])
        self.db.add(sess_a)

        for i in range(6):
            self.db.add(AssessmentAttempt(
                learner_id=101,
                session_id=1,
                expected_sign="A",
                predicted_sign="A",
                is_correct=True,
                confidence=0.92,
                gesture_accuracy=95.0,
                hand_shape_accuracy=94.0,
                motion_accuracy=96.0,
                position_accuracy=95.0,
                timestamp=datetime.utcnow()
            ))

        # Seed 2 attempts for Learner B on sign 'Z' (incorrect)
        sess_b = PracticeSession(id=2, learner_id=102, selected_signs=["Z"])
        self.db.add(sess_b)

        for i in range(2):
            self.db.add(AssessmentAttempt(
                learner_id=102,
                session_id=2,
                expected_sign="Z",
                predicted_sign="A",
                is_correct=False,
                confidence=0.45,
                gesture_accuracy=30.0,
                hand_shape_accuracy=30.0,
                motion_accuracy=30.0,
                position_accuracy=30.0,
                timestamp=datetime.utcnow()
            ))

        self.db.commit()
        self.client = TestClient(app)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    def get_auth_header(self, user_id: int, role: str = None):
        token = create_access_token(subject=str(user_id))
        return {"Authorization": f"Bearer {token}"}

    # TEST 1 — Learner PDF
    def test_01_learner_pdf_download_success(self):
        headers = self.get_auth_header(101, "Learner")
        res = self.client.get("/api/v1/reports/me/pdf", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/pdf", res.headers.get("content-type", ""))
        self.assertGreater(len(res.content), 1000)

    # TEST 2 — Learner Report Privacy (Learner A cannot access Learner B's report)
    def test_02_learner_report_privacy_protection(self):
        headers_a = self.get_auth_header(101, "Learner")
        res = self.client.get("/api/v1/reports/learners/102/pdf", headers=headers_a)
        self.assertEqual(res.status_code, 403)

    # TEST 3 — Instructor Learner Count matches database
    def test_03_instructor_learner_count(self):
        headers = self.get_auth_header(201, "Instructor")
        res = self.client.get("/api/v1/analytics/instructor", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_students"], 2)

    # TEST 4 — Instructor Learner List
    def test_04_instructor_learners_list(self):
        headers = self.get_auth_header(201, "Instructor")
        res = self.client.get("/api/v1/analytics/instructor/learners", headers=headers)
        self.assertEqual(res.status_code, 200)
        learners = res.json()
        self.assertEqual(len(learners), 2)
        emails = [l["email"] for l in learners]
        self.assertIn("learner_a@example.com", emails)
        self.assertIn("learner_b@example.com", emails)

    # TEST 5 — Instructor Tracks Learner A
    def test_05_instructor_track_learner_a(self):
        headers = self.get_auth_header(201, "Instructor")
        res = self.client.get("/api/v1/analytics/learners/101", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user"]["full_name"], "Learner Alice")
        self.assertEqual(data["performance"]["total_attempts"], 6)
        self.assertEqual(data["performance"]["overall_accuracy"], 100.0)
        sign_a = next((item for item in data["sign_classification"] if item["sign"] == "A"), None)
        self.assertIsNotNone(sign_a)
        self.assertEqual(sign_a["category"], "Mastered")

    # TEST 6 — Non-Instructor / Unauthorized Learner Access to Tracking
    def test_06_unauthorized_learner_cannot_track(self):
        headers = self.get_auth_header(101, "Learner")
        res = self.client.get("/api/v1/analytics/learners/102", headers=headers)
        self.assertEqual(res.status_code, 403)

    # TEST 7 — Strict 4-Way Private Instruction Isolation
    def test_07_private_instruction_isolation(self):
        headers_inst_a = self.get_auth_header(201, "Instructor")
        send_res = self.client.post(
            "/api/v1/instructions",
            headers=headers_inst_a,
            json={"learner_id": 101, "message": "Practice sign D for 15 minutes."}
        )
        self.assertEqual(send_res.status_code, 201)
        inst_id = send_res.json()["id"]

        # 1. Target Learner A logs in -> CAN see instruction
        headers_a = self.get_auth_header(101, "Learner")
        res_a = self.client.get("/api/v1/instructions/me", headers=headers_a)
        self.assertEqual(res_a.status_code, 200)
        msgs_a = [i["message"] for i in res_a.json()]
        self.assertIn("Practice sign D for 15 minutes.", msgs_a)

        # 2. Different Learner B logs in -> CANNOT see instruction
        headers_b = self.get_auth_header(102, "Learner")
        res_b = self.client.get("/api/v1/instructions/me", headers=headers_b)
        self.assertEqual(res_b.status_code, 200)
        msgs_b = [i["message"] for i in res_b.json()]
        self.assertNotIn("Practice sign D for 15 minutes.", msgs_b)

        # 3. Other Instructor (Instructor B) logs in -> CANNOT see instruction (returns empty list)
        headers_inst_b = self.get_auth_header(202, "Instructor")
        res_inst_b = self.client.get("/api/v1/instructions/me", headers=headers_inst_b)
        self.assertEqual(res_inst_b.status_code, 200)
        self.assertEqual(res_inst_b.json(), [])

        # 4. Admin logs in -> CANNOT see instruction (returns empty list)
        headers_admin = self.get_auth_header(401, "Administrator")
        res_admin = self.client.get("/api/v1/instructions/me", headers=headers_admin)
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.json(), [])

    # TEST 7b — Read Status Privacy and Non-Owner Alteration Protection
    def test_07b_read_status_security_and_non_owner_rejection(self):
        headers_inst = self.get_auth_header(201, "Instructor")
        send_res = self.client.post(
            "/api/v1/instructions",
            headers=headers_inst,
            json={"learner_id": 101, "message": "Security verification instruction"}
        )
        inst_id = send_res.json()["id"]

        headers_a = self.get_auth_header(101, "Learner")
        headers_b = self.get_auth_header(102, "Learner")
        headers_admin = self.get_auth_header(401, "Administrator")

        # Admin attempts to alter/mark read -> 403 Forbidden
        admin_patch = self.client.patch(f"/api/v1/instructions/{inst_id}/read", headers=headers_admin)
        self.assertEqual(admin_patch.status_code, 403)

        # Learner B attempts to alter Learner A's instruction -> 404 Not Found
        b_patch = self.client.patch(f"/api/v1/instructions/{inst_id}/read", headers=headers_b)
        self.assertEqual(b_patch.status_code, 404)

        # Authorized Learner A marks as read -> 200 OK
        a_patch = self.client.patch(f"/api/v1/instructions/{inst_id}/read", headers=headers_a)
        self.assertEqual(a_patch.status_code, 200)
        self.assertTrue(a_patch.json()["is_read"])

    # TEST 8 — Notification Unread & Read State Transitions
    def test_08_notification_read_state_transition(self):
        headers_inst = self.get_auth_header(201, "Instructor")
        send_res = self.client.post(
            "/api/v1/instructions",
            headers=headers_inst,
            json={"learner_id": 101, "message": "Read state test instruction"}
        )
        inst_id = send_res.json()["id"]

        headers_a = self.get_auth_header(101, "Learner")
        res_before = self.client.get("/api/v1/instructions/me", headers=headers_a)
        inst_obj = next(i for i in res_before.json() if i["id"] == inst_id)
        self.assertFalse(inst_obj["is_read"])

        # Mark as read
        read_res = self.client.patch(f"/api/v1/instructions/{inst_id}/read", headers=headers_a)
        self.assertEqual(read_res.status_code, 200)
        self.assertTrue(read_res.json()["is_read"])

        res_after = self.client.get("/api/v1/instructions/me", headers=headers_a)
        inst_obj_after = next(i for i in res_after.json() if i["id"] == inst_id)
        self.assertTrue(inst_obj_after["is_read"])

    # TEST 9 — Admin Role Counts
    def test_09_admin_role_counts(self):
        headers_admin = self.get_auth_header(401, "Administrator")
        res = self.client.get("/api/v1/admin/counts", headers=headers_admin)
        self.assertEqual(res.status_code, 200)
        counts = res.json()
        self.assertEqual(counts["learner_count"], 2)
        self.assertEqual(counts["trainer_count"], 1)
        self.assertEqual(counts["instructor_count"], 2)

    # TEST 10 — Admin Filtered Lists
    def test_10_admin_filtered_lists(self):
        headers_admin = self.get_auth_header(401, "Administrator")
        
        # Filter Learners
        res_learners = self.client.get("/api/v1/admin/users-by-role?role=Learner", headers=headers_admin)
        self.assertEqual(res_learners.status_code, 200)
        self.assertEqual(len(res_learners.json()), 2)
        for u in res_learners.json():
            self.assertEqual(u["role"], "Learner")

        # Filter Trainers
        res_trainers = self.client.get("/api/v1/admin/users-by-role?role=Accessibility%20Trainer", headers=headers_admin)
        self.assertEqual(res_trainers.status_code, 200)
        self.assertEqual(len(res_trainers.json()), 1)
        self.assertEqual(res_trainers.json()[0]["role"], "Accessibility Trainer")

        # Filter Instructors
        res_instructors = self.client.get("/api/v1/admin/users-by-role?role=Instructor", headers=headers_admin)
        self.assertEqual(res_instructors.status_code, 200)
        self.assertEqual(len(res_instructors.json()), 2)
        for u in res_instructors.json():
            self.assertEqual(u["role"], "Instructor")

    # TEST 11 — Admin User Activity Tracking & Zero Message Leakage
    def test_11_admin_user_activity_tracking(self):
        headers_admin = self.get_auth_header(401, "Administrator")
        # Learner activity
        res_learner = self.client.get("/api/v1/admin/users/101/activity", headers=headers_admin)
        self.assertEqual(res_learner.status_code, 200)
        data_l = res_learner.json()
        self.assertEqual(data_l["type"], "learner")
        self.assertEqual(data_l["user"]["full_name"], "Learner Alice")
        self.assertEqual(data_l["analytics"]["performance"]["total_attempts"], 6)

        # Instructor activity returns telemetry only, NO private message text
        res_inst = self.client.get("/api/v1/admin/users/201/activity", headers=headers_admin)
        self.assertEqual(res_inst.status_code, 200)
        data_i = res_inst.json()
        self.assertEqual(data_i["type"], "instructor")
        self.assertIn("total_instructions_issued", data_i)
        self.assertNotIn("recent_instructions", data_i)

    # TEST 12 — Cross-User Data Isolation
    def test_12_cross_user_data_isolation(self):
        headers_a = self.get_auth_header(101, "Learner")
        res_a = self.client.get("/api/v1/analytics/dashboard", headers=headers_a)
        data_a = res_a.json()
        self.assertEqual(data_a["performance"]["total_attempts"], 6)
        self.assertEqual(data_a["performance"]["overall_accuracy"], 100.0)

        headers_b = self.get_auth_header(102, "Learner")
        res_b = self.client.get("/api/v1/analytics/dashboard", headers=headers_b)
        data_b = res_b.json()
        self.assertEqual(data_b["performance"]["total_attempts"], 2)
        self.assertEqual(data_b["performance"]["overall_accuracy"], 0.0)

    # TEST 13 — No Fake Data / All calculated from DB
    def test_13_no_fake_data_accuracy(self):
        headers_a = self.get_auth_header(101, "Learner")
        res_a = self.client.get("/api/v1/analytics/dashboard", headers=headers_a)
        data_a = res_a.json()
        self.assertEqual(data_a["performance"]["overall_accuracy"], 100.0)
        self.assertEqual(data_a["performance"]["average_confidence"], 92.0)

    # TEST 14 — Analytics Consistency Across Dashboard, Instructor Tracking, Admin Tracking, and PDF
    def test_14_analytics_consistency_across_surfaces(self):
        # 1. Learner A's Dashboard
        headers_a = self.get_auth_header(101, "Learner")
        dash = self.client.get("/api/v1/analytics/dashboard", headers=headers_a).json()

        # 2. Instructor Tracking of Learner A
        headers_inst = self.get_auth_header(201, "Instructor")
        inst_track = self.client.get("/api/v1/analytics/learners/101", headers=headers_inst).json()

        # 3. Admin Tracking of Learner A
        headers_admin = self.get_auth_header(401, "Administrator")
        admin_track = self.client.get("/api/v1/admin/users/101/activity", headers=headers_admin).json()

        # Verify identical values
        self.assertEqual(dash["performance"]["overall_accuracy"], inst_track["performance"]["overall_accuracy"])
        self.assertEqual(dash["performance"]["overall_accuracy"], admin_track["analytics"]["performance"]["overall_accuracy"])

        self.assertEqual(dash["performance"]["total_attempts"], inst_track["performance"]["total_attempts"])
        self.assertEqual(dash["performance"]["total_attempts"], admin_track["analytics"]["performance"]["total_attempts"])

        self.assertEqual(dash["performance"]["average_confidence"], inst_track["performance"]["average_confidence"])
        self.assertEqual(dash["performance"]["average_confidence"], admin_track["analytics"]["performance"]["average_confidence"])

        # 4. PDF generation succeeds for all three authorized actors
        self.assertEqual(self.client.get("/api/v1/reports/me/pdf", headers=headers_a).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/reports/learners/101/pdf", headers=headers_inst).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/reports/learners/101/pdf", headers=headers_admin).status_code, 200)

if __name__ == "__main__":
    unittest.main()
