import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import Base, get_db
from app.database.init_db import init_db

class AdaptiveLearningPlatformTestSuite(unittest.TestCase):
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
        db = cls.TestingSessionLocal()
        init_db(db)
        db.close()
        cls.client = TestClient(app)
        
        # Login as Learner
        login_res = cls.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        cls.token = login_res.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=cls.engine)
        app.dependency_overrides.clear()

    def test_adaptive_learning_flow_and_3_sessions(self):
        dummy_landmarks = [{"x": 0.1, "y": 0.2, "z": 0.3} for _ in range(21)]

        # --- SESSION 1: Practice Sign 'A' (Successful Attempt) ---
        with patch("app.services.adaptive_learning_service.evaluate_gesture_attempt") as mock_eval:
            mock_eval.return_value = {
                "expected_sign": "A",
                "predicted_sign": "A",
                "confidence": 95.0,
                "overall_accuracy": 95.0,
                "hand_shape_accuracy": 96.0,
                "position_accuracy": 94.0,
                "motion_accuracy": 95.0
            }

            start_sess1 = self.client.post("/api/v1/practice/sessions/start", json=["A"], headers=self.headers)
            self.assertEqual(start_sess1.status_code, 200)
            sess1_id = start_sess1.json()["session_id"]

            attempt1_res = self.client.post(
                f"/api/v1/practice/attempt?session_id={sess1_id}",
                json={"expected_sign": "A", "landmarks": dummy_landmarks},
                headers=self.headers
            )
            self.assertEqual(attempt1_res.status_code, 200)
            data1 = attempt1_res.json()
            
            # Assert closed-loop payload keys present
            self.assertIn("assessment", data1)
            self.assertIn("feedback", data1)
            self.assertIn("learner_state", data1)
            self.assertIn("recommendation", data1)

            end_sess1 = self.client.post(f"/api/v1/practice/sessions/{sess1_id}/end", headers=self.headers)
            self.assertEqual(end_sess1.json()["status"], "completed")

            rec1_sign = data1["recommendation"]["recommended_sign"]
            rec1_reason = data1["recommendation"]["reason"]
            print(f"\n[Session 1 Complete] Target: A (Correct) | Rec: {rec1_sign} | Reason: {rec1_reason}")

        # --- SESSION 2: Practice Sign 'B' with mistakes ---
        with patch("app.services.adaptive_learning_service.evaluate_gesture_attempt") as mock_eval:
            mock_eval.return_value = {
                "expected_sign": "B",
                "predicted_sign": "X",  # Incorrect gesture
                "confidence": 45.0,
                "overall_accuracy": 35.0,
                "hand_shape_accuracy": 30.0,
                "position_accuracy": 40.0,
                "motion_accuracy": 35.0
            }

            start_sess2 = self.client.post("/api/v1/practice/sessions/start", json=["B"], headers=self.headers)
            sess2_id = start_sess2.json()["session_id"]

            attempt2_res = self.client.post(
                f"/api/v1/practice/attempt?session_id={sess2_id}",
                json={"expected_sign": "B", "landmarks": dummy_landmarks},
                headers=self.headers
            )
            self.assertEqual(attempt2_res.status_code, 200)
            data2 = attempt2_res.json()
            
            end_sess2 = self.client.post(f"/api/v1/practice/sessions/{sess2_id}/end", headers=self.headers)
            self.assertEqual(end_sess2.json()["status"], "completed")

            rec2_sign = data2["recommendation"]["recommended_sign"]
            rec2_reason = data2["recommendation"]["reason"]
            print(f"[Session 2 Complete] Target: B (Mistake) | Rec: {rec2_sign} | Reason: {rec2_reason}")

            # Assert recommendation targeted Sign 'B' due to consecutive incorrect / low mastery!
            self.assertEqual(rec2_sign, "B")
            self.assertIn("consecutive incorrect attempts", rec2_reason)

        # --- SESSION 3: Practice Sign 'B' with High Accuracy to Achieve Mastery ---
        with patch("app.services.adaptive_learning_service.evaluate_gesture_attempt") as mock_eval:
            mock_eval.return_value = {
                "expected_sign": "B",
                "predicted_sign": "B",  # Correct gesture
                "confidence": 98.0,
                "overall_accuracy": 98.0,
                "hand_shape_accuracy": 98.0,
                "position_accuracy": 98.0,
                "motion_accuracy": 98.0
            }

            start_sess3 = self.client.post("/api/v1/practice/sessions/start", json=["B"], headers=self.headers)
            sess3_id = start_sess3.json()["session_id"]

            for i in range(5):
                attempt3_res = self.client.post(
                    f"/api/v1/practice/attempt?session_id={sess3_id}",
                    json={"expected_sign": "B", "landmarks": dummy_landmarks},
                    headers=self.headers
                )
                self.assertEqual(attempt3_res.status_code, 200)

            data3 = attempt3_res.json()
            end_sess3 = self.client.post(f"/api/v1/practice/sessions/{sess3_id}/end", headers=self.headers)
            self.assertEqual(end_sess3.json()["status"], "completed")

            rec3_sign = data3["recommendation"]["recommended_sign"]
            rec3_reason = data3["recommendation"]["reason"]
            print(f"[Session 3 Complete] Target: B (5 Correct Attempts) | Rec: {rec3_sign} | Reason: {rec3_reason}\n")

            # Verify state transition for B reached IMPROVING or MASTERED
            self.assertIn(data3["learner_state"]["current_state"], ["Improving", "Mastered"])

            # Verify recommendations dynamically changed between Session 2 and Session 3!
            self.assertNotEqual(rec2_reason, rec3_reason)

if __name__ == "__main__":
    unittest.main()
