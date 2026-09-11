import sys
import os
import unittest
import uuid

# Ensure workspace backend directory is at front of sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

class TestE2EClosedLoopWorkflow(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.email = f"e2e_user_{uuid.uuid4().hex[:6]}@example.com"
        self.password = "TestPassword123!"
        self.full_name = "E2E Integration Learner"

    def test_e2e_16_step_closed_loop_workflow(self):
        # 1. Register User
        reg_resp = self.client.post("/api/v1/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": self.full_name,
            "role": "Learner"
        })
        self.assertEqual(reg_resp.status_code, 201)

        # 2. Login User & Obtain Token
        login_resp = self.client.post("/api/v1/auth/login", data={
            "username": self.email,
            "password": self.password
        })
        self.assertEqual(login_resp.status_code, 200)
        res_json = login_resp.json()
        token = res_json.get("access_token") or res_json.get("data", {}).get("access_token")
        self.assertIsNotNone(token)
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Load Learner Dashboard Initial State
        dash_resp = self.client.get("/api/v1/analytics/dashboard", headers=headers)
        self.assertEqual(dash_resp.status_code, 200)

        # 4. Start Practice Session
        sess_start_resp = self.client.post("/api/v1/practice/sessions/start", json=["A", "B", "C"], headers=headers)
        self.assertEqual(sess_start_resp.status_code, 200)
        session_id = sess_start_resp.json()["session_id"]

        # 5. Fetch Recommended Sign
        rec_resp = self.client.get("/api/v1/recommendations", headers=headers)
        self.assertEqual(rec_resp.status_code, 200)
        rec_data = rec_resp.json()
        target_sign = rec_data[0]["recommended_sign"] if isinstance(rec_data, list) else rec_data.get("recommended_sign", "A")

        # 6. Fetch Reference Sign Details
        target_lesson_id = rec_data.get("target_lesson_id", 1)
        lesson_resp = self.client.get(f"/api/v1/lessons/{target_lesson_id}", headers=headers)
        self.assertEqual(lesson_resp.status_code, 200)

        # 7. Submit Webcam Landmark Practice Attempt
        mock_landmarks = [{"x": 0.5, "y": 0.5, "z": 0.0} for _ in range(21)]
        attempt_resp = self.client.post(
            f"/api/v1/practice/attempt?session_id={session_id}",
            json={
                "expected_sign": target_sign,
                "landmarks": mock_landmarks
            },
            headers=headers
        )
        self.assertEqual(attempt_resp.status_code, 200)
        att_data = attempt_resp.json()

        # 8. Verify Assessment Metrics
        self.assertIn("assessment", att_data)
        has_acc = ("accuracy" in att_data["assessment"] or "overall_accuracy" in att_data["assessment"])
        self.assertTrue(has_acc)

        # 9. Verify Feedback Generation
        self.assertIn("feedback", att_data)
        self.assertIn("text", att_data["feedback"])

        # 10. Verify Learner State Machine Update
        self.assertIn("learner_state", att_data)
        self.assertIsNotNone(att_data["learner_state"]["current_state"])

        # 11. Verify Updated Recommendation Generation
        self.assertIn("recommendation", att_data)

        # 12. Complete Practice Session
        sess_end_resp = self.client.post(f"/api/v1/practice/sessions/{session_id}/end", headers=headers)
        self.assertEqual(sess_end_resp.status_code, 200)

        # 13. Verify Progress Analytics Updated
        prog_resp = self.client.get("/api/v1/analytics/progress", headers=headers)
        self.assertEqual(prog_resp.status_code, 200)

        # 14. Verify Refreshed Dashboard Metrics
        dash_updated = self.client.get("/api/v1/analytics/dashboard", headers=headers)
        self.assertEqual(dash_updated.status_code, 200)

        # 15. Verify PDF Report Download
        pdf_resp = self.client.get("/api/v1/reports/performance/pdf", headers=headers)
        self.assertEqual(pdf_resp.status_code, 200)

        # 16. Verify Excel Report Download
        excel_resp = self.client.get("/api/v1/reports/performance/excel", headers=headers)
        self.assertEqual(excel_resp.status_code, 200)

if __name__ == "__main__":
    unittest.main()
