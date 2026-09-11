import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from app.api.recognition import (
    compute_generic_assessment,
    predict_landmarks_endpoint,
    PredictLandmarksRequest,
    LandmarkPointItem
)
from app.models.domain import User, RoleEnum
from app.ai.canonical_landmarks import get_canonical_landmarks_for_sign

class TestGenericClassAssessment(unittest.TestCase):
    """
    Automated Parameterized Tests covering ALL 26 ASL classes (A through Z).
    Verifies that comparison logic is 100% generic, class-agnostic, and
    operates dynamically without any hardcoded class branches.
    """

    def setUp(self):
        self.mock_user = User(id=1, email="learner@test.com", full_name="Learner One", role=RoleEnum.LEARNER)
        self.alphabet = [chr(65 + i) for i in range(26)]

    def test_all_26_classes_self_match_correct(self):
        """For every class X in A-Z: target X + prediction X -> CORRECT"""
        for char in self.alphabet:
            assessment = compute_generic_assessment(
                target_sign=char,
                predicted_class=char,
                confidence=0.95,
                min_confidence=0.70
            )
            self.assertTrue(assessment["correct"], f"Failed self-match for class '{char}'")
            self.assertEqual(assessment["status"], "CORRECT")
            self.assertEqual(
                assessment["message"],
                f"Correct. The model detected {char}, which matches the expected {char} sign.",
                f"Incorrect success message for class '{char}'"
            )

    def test_all_26_classes_cyclic_mismatch_incorrect(self):
        """For every class X in A-Z: target X + prediction (X+1) -> INCORRECT"""
        for i, target_char in enumerate(self.alphabet):
            pred_char = self.alphabet[(i + 1) % 26] # e.g. A vs B, B vs C, ..., Z vs A
            assessment = compute_generic_assessment(
                target_sign=target_char,
                predicted_class=pred_char,
                confidence=0.94,
                min_confidence=0.70
            )
            self.assertFalse(assessment["correct"], f"Failed mismatch detection for target '{target_char}' vs pred '{pred_char}'")
            self.assertEqual(assessment["status"], "INCORRECT")
            self.assertEqual(
                assessment["message"],
                f"Incorrect. The model detected {pred_char}, while the expected sign was {target_char}. Please adjust your hand position and try the {target_char} sign again."
            )

    def test_cross_class_mismatches(self):
        """Test specific cross-class pairs (A vs B, B vs A, C vs D, D vs C, M vs N, Y vs Z)"""
        test_pairs = [
            ("A", "B"),
            ("B", "A"),
            ("C", "D"),
            ("D", "C"),
            ("M", "N"),
            ("N", "M"),
            ("Y", "Z"),
            ("Z", "A"),
            ("K", "V"),
            ("U", "V")
        ]
        for target, pred in test_pairs:
            assessment = compute_generic_assessment(
                target_sign=target,
                predicted_class=pred,
                confidence=0.92,
                min_confidence=0.70
            )
            self.assertFalse(assessment["correct"])
            self.assertEqual(assessment["status"], "INCORRECT")
            self.assertEqual(
                assessment["message"],
                f"Incorrect. The model detected {pred}, while the expected sign was {target}. Please adjust your hand position and try the {target} sign again."
            )

    def test_low_confidence_uncertainty_all_classes(self):
        """When confidence < 0.70, system must return UNCERTAIN regardless of matching letter"""
        for char in ["A", "B", "C", "M", "Z"]:
            assessment = compute_generic_assessment(
                target_sign=char,
                predicted_class=char,
                confidence=0.45, # below 0.70 threshold
                min_confidence=0.70
            )
            self.assertFalse(assessment["correct"])
            self.assertEqual(assessment["status"], "UNCERTAIN")
            self.assertEqual(
                assessment["message"],
                f"Unable to confidently identify the performed sign. The model currently detects {char} with 45% confidence. Please position your hand clearly and try again."
            )

    def test_case_insensitivity_and_whitespace_normalization(self):
        """Ensures comparison handles lowercase, mixed case, and whitespace transparently"""
        assessment = compute_generic_assessment(
            target_sign="  b  ",
            predicted_class="b",
            confidence=0.95
        )
        self.assertTrue(assessment["correct"])
        self.assertEqual(assessment["status"], "CORRECT")
        self.assertEqual(assessment["message"], "Correct. The model detected B, which matches the expected B sign.")

    def test_real_model_inference_endpoint_all_26_classes(self):
        """
        Feeds real 63-element canonical spatial feature vectors for all 26 classes
        through the FastAPI endpoint and verifies prediction match.
        """
        for char in self.alphabet:
            raw_lms = get_canonical_landmarks_for_sign(char)
            lm_items = [LandmarkPointItem(x=p["x"], y=p["y"], z=p["z"]) for p in raw_lms]
            
            # 1. Matching target
            req_match = PredictLandmarksRequest(landmarks=lm_items, target_sign=char)
            res_match = predict_landmarks_endpoint(req_match, self.mock_user)
            self.assertEqual(res_match.predicted_sign, char)
            self.assertTrue(res_match.correct)
            self.assertEqual(res_match.status, "CORRECT")

            # 2. Mismatched target (target = next letter)
            mismatch_target = self.alphabet[(ord(char) - 65 + 1) % 26]
            req_mismatch = PredictLandmarksRequest(landmarks=lm_items, target_sign=mismatch_target)
            res_mismatch = predict_landmarks_endpoint(req_mismatch, self.mock_user)
            self.assertEqual(res_mismatch.predicted_sign, char)
            self.assertFalse(res_mismatch.correct)
            self.assertEqual(res_mismatch.status, "INCORRECT")
            self.assertEqual(
                res_mismatch.message,
                f"Incorrect. The model detected {char}, while the expected sign was {mismatch_target}. Please adjust your hand position and try the {mismatch_target} sign again."
            )

if __name__ == "__main__":
    unittest.main()
