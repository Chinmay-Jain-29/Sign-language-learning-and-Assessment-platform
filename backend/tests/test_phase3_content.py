import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.database.init_db import init_db

class Phase3ContentInfrastructureTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        init_db(db)
        db.close()
        cls.client = TestClient(app)

        # Login as Learner
        login_learner = cls.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        cls.learner_token = login_learner.json()["access_token"]
        cls.learner_headers = {"Authorization": f"Bearer {cls.learner_token}"}

        # Login as Instructor
        login_inst = cls.client.post(
            "/api/v1/auth/login",
            data={"username": "instructor@example.com", "password": "password123"}
        )
        cls.inst_token = login_inst.json()["access_token"]
        cls.inst_headers = {"Authorization": f"Bearer {cls.inst_token}"}

    def test_01_profile_retrieval_and_update(self):
        # GET Profile
        res = self.client.get("/api/v1/users/profile", headers=self.learner_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("preferred_language", data)

        # PUT Update Profile
        update_res = self.client.put(
            "/api/v1/users/profile",
            json={"learning_level": "Intermediate", "preferred_language": "Spanish"},
            headers=self.learner_headers
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["learning_level"], "Intermediate")
        self.assertEqual(update_res.json()["preferred_language"], "Spanish")

    def test_02_learning_goals_crud(self):
        # 1. Create Goal
        create_res = self.client.post(
            "/api/v1/users/goals",
            json={"goal_description": "Master ASL letters A through G this week"},
            headers=self.learner_headers
        )
        self.assertEqual(create_res.status_code, 201)
        goal_id = create_res.json()["id"]
        self.assertFalse(create_res.json()["is_completed"])

        # 2. List Goals
        list_res = self.client.get("/api/v1/users/goals", headers=self.learner_headers)
        self.assertEqual(list_res.status_code, 200)
        self.assertTrue(len(list_res.json()) > 0)

        # 3. Update Goal (Mark as completed)
        update_res = self.client.put(
            f"/api/v1/users/goals/{goal_id}",
            json={"is_completed": True},
            headers=self.learner_headers
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertTrue(update_res.json()["is_completed"])

        # 4. Delete Goal
        del_res = self.client.delete(f"/api/v1/users/goals/{goal_id}", headers=self.learner_headers)
        self.assertEqual(del_res.status_code, 204)

    def test_03_courses_and_lessons_retrieval(self):
        # Courses retrieval
        c_res = self.client.get("/api/v1/lessons/courses", headers=self.learner_headers)
        self.assertEqual(c_res.status_code, 200)
        self.assertTrue(len(c_res.json()) > 0)

        # Lessons retrieval
        l_res = self.client.get("/api/v1/lessons/", headers=self.learner_headers)
        self.assertEqual(l_res.status_code, 200)
        self.assertTrue(len(l_res.json()) > 0)

    def test_04_lesson_crud_authorization(self):
        # Learner attempting to create lesson -> 403 Forbidden
        learner_create = self.client.post(
            "/api/v1/lessons/",
            json={"title": "Unauthorized Lesson", "sign_character": "Z", "description": "Test"},
            headers=self.learner_headers
        )
        self.assertEqual(learner_create.status_code, 403)

        # Instructor creating lesson -> 201 Created
        inst_create = self.client.post(
            "/api/v1/lessons/",
            json={
                "title": "Sign 'Z' Advanced Lesson",
                "sign_character": "Z",
                "description": "Trace Z shape in the air with index finger",
                "tips": "Index finger extended, draw Z pattern",
                "order_index": 26
            },
            headers=self.inst_headers
        )
        self.assertEqual(inst_create.status_code, 201)
        created_id = inst_create.json()["id"]

        # Instructor updating lesson -> 200 OK
        inst_update = self.client.put(
            f"/api/v1/lessons/{created_id}",
            json={"title": "Sign 'Z' Updated Lesson"},
            headers=self.inst_headers
        )
        self.assertEqual(inst_update.status_code, 200)
        self.assertEqual(inst_update.json()["title"], "Sign 'Z' Updated Lesson")

        # Instructor deleting lesson -> 204 No Content
        inst_del = self.client.delete(f"/api/v1/lessons/{created_id}", headers=self.inst_headers)
        self.assertEqual(inst_del.status_code, 204)

if __name__ == "__main__":
    unittest.main()
