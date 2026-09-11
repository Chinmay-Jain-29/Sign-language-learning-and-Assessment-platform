import sys
import os
import unittest
import numpy as np
import cv2
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.ai.hand_tracking.hand_tracker import HandTracker
from app.ai.hand_tracking.schemas import HandDetectionResult, LandmarkPoint

class Phase5HandTrackingTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.tracker = HandTracker(static_image_mode=True, max_num_hands=2)

        # Login as Learner
        login_res = cls.client.post(
            "/api/v1/auth/login",
            data={"username": "learner@example.com", "password": "password123"}
        )
        cls.token = login_res.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_01_hand_tracker_initialization(self):
        self.assertIsNotNone(self.tracker.hands)

    def test_02_detect_empty_image(self):
        blank_img = np.zeros((100, 100, 3), dtype=np.uint8)
        detections = self.tracker.detect(blank_img)
        self.assertIsInstance(detections, list)
        self.assertEqual(len(detections), 0)

    def test_03_detect_landmarks_synthetic_or_sample(self):
        # Create a synthetic test image with dimensions
        test_img = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.circle(test_img, (150, 150), 50, (255, 255, 255), -1)
        
        detections = self.tracker.detect(test_img)
        self.assertIsInstance(detections, list)

    def test_04_landmark_drawing_utility(self):
        sample_img = np.zeros((200, 200, 3), dtype=np.uint8)
        annotated = self.tracker.draw_landmarks(sample_img, [])
        self.assertEqual(annotated.shape, sample_img.shape)

    def test_05_detect_landmarks_api_endpoint(self):
        # Create dummy image bytes
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, img_encoded = cv2.imencode('.png', dummy_img)
        img_bytes = img_encoded.tobytes()

        files = {"file": ("test_hand.png", BytesIO(img_bytes), "image/png")}
        response = self.client.post("/api/v1/ai/detect-landmarks", files=files, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

if __name__ == "__main__":
    unittest.main()
