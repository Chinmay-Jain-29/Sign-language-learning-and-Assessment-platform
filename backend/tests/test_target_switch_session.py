import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from app.api.recognition import (
    predict_landmarks_endpoint,
    reset_stabilizer_endpoint,
    PredictLandmarksRequest,
    ResetStabilizerRequest,
    LandmarkPointItem
)
from app.models.domain import User, RoleEnum
from app.ai.canonical_landmarks import get_canonical_landmarks_for_sign

class TestTargetSwitchingWithoutRefresh(unittest.TestCase):
    """
    Automated Tests for Continuous Target Switching within the SAME Session
    without requiring page refresh, server restart, or model reload.
    """

    def setUp(self):
        self.mock_user = User(id=1, email="learner@test.com", full_name="Learner One", role=RoleEnum.LEARNER)

    def test_continuous_target_sequence_a_b_c_d(self):
        """
        Simulates:
        1. Select Target A -> Perform A -> CORRECT
        2. Select Target B -> Perform B -> CORRECT
        3. Select Target C -> Perform C -> CORRECT
        4. Select Target D -> Perform D -> CORRECT
        All within the same continuous session.
        """
        sequence = ["A", "B", "C", "D", "E", "F"]
        for target in sequence:
            # 1. Target change triggers stabilizer reset
            reset_res = reset_stabilizer_endpoint(ResetStabilizerRequest(target_sign=target), self.mock_user)
            self.assertTrue(reset_res["success"])

            # 2. Perform gesture matching target
            raw_lms = get_canonical_landmarks_for_sign(target)
            lm_items = [LandmarkPointItem(x=p["x"], y=p["y"], z=p["z"]) for p in raw_lms]
            req = PredictLandmarksRequest(landmarks=lm_items, target_sign=target)

            res = predict_landmarks_endpoint(req, self.mock_user)
            self.assertEqual(res.target_sign, target)
            self.assertEqual(res.predicted_sign, target)
            self.assertTrue(res.correct)
            self.assertEqual(res.status, "CORRECT")
            self.assertEqual(res.message, f"Correct! You performed sign {target}.")

    def test_target_switch_with_mismatch_recovery(self):
        """
        Simulates:
        1. Target A -> Perform A -> CORRECT
        2. Switch Target B -> User still shows A gesture -> INCORRECT
        3. User corrects gesture to B -> CORRECT
        4. Switch Target C -> User performs C -> CORRECT
        """
        # Step 1: Target A, Perform A
        reset_stabilizer_endpoint(ResetStabilizerRequest(target_sign="A"), self.mock_user)
        lms_a = [LandmarkPointItem(**p) for p in get_canonical_landmarks_for_sign("A")]
        res1 = predict_landmarks_endpoint(PredictLandmarksRequest(landmarks=lms_a, target_sign="A"), self.mock_user)
        self.assertTrue(res1.correct)
        self.assertEqual(res1.status, "CORRECT")

        # Step 2: Switch to Target B, user still performs gesture A
        reset_stabilizer_endpoint(ResetStabilizerRequest(target_sign="B"), self.mock_user)
        res2 = predict_landmarks_endpoint(PredictLandmarksRequest(landmarks=lms_a, target_sign="B"), self.mock_user)
        self.assertFalse(res2.correct)
        self.assertEqual(res2.status, "INCORRECT")
        self.assertEqual(res2.predicted_sign, "A")
        self.assertEqual(res2.message, "Detected sign A. Please perform sign B.")

        # Step 3: User corrects posture to gesture B
        lms_b = [LandmarkPointItem(**p) for p in get_canonical_landmarks_for_sign("B")]
        res3 = predict_landmarks_endpoint(PredictLandmarksRequest(landmarks=lms_b, target_sign="B"), self.mock_user)
        self.assertTrue(res3.correct)
        self.assertEqual(res3.status, "CORRECT")
        self.assertEqual(res3.predicted_sign, "B")

        # Step 4: Switch Target C, perform C
        reset_stabilizer_endpoint(ResetStabilizerRequest(target_sign="C"), self.mock_user)
        lms_c = [LandmarkPointItem(**p) for p in get_canonical_landmarks_for_sign("C")]
        res4 = predict_landmarks_endpoint(PredictLandmarksRequest(landmarks=lms_c, target_sign="C"), self.mock_user)
        self.assertTrue(res4.correct)
        self.assertEqual(res4.status, "CORRECT")

    def test_arbitrary_random_target_hops(self):
        """Tests arbitrary out-of-order target switches (e.g. Z -> M -> A -> Y -> K)"""
        hops = ["Z", "M", "A", "Y", "K"]
        for target in hops:
            reset_stabilizer_endpoint(ResetStabilizerRequest(target_sign=target), self.mock_user)
            lms = [LandmarkPointItem(**p) for p in get_canonical_landmarks_for_sign(target)]
            res = predict_landmarks_endpoint(PredictLandmarksRequest(landmarks=lms, target_sign=target), self.mock_user)
            self.assertEqual(res.target_sign, target)
            self.assertEqual(res.predicted_sign, target)
            self.assertTrue(res.correct)

if __name__ == "__main__":
    unittest.main()
