import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.main import app
from app.models.domain import User, AssessmentAttempt, PracticeSession, RoleEnum, LearnerAlphabetState
from app.core.security import get_password_hash

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

class TestSignIMasteryMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = TestingSessionLocal()

        cls.user_i_email = "test_sign_i_mastery@aslsensei.com"
        cls.user_d_email = "test_sign_d_mastery@aslsensei.com"
        cls.user_b_email = "test_sign_isolated@aslsensei.com"
        cls.password = "password123"

        # Create user for Sign I test
        cls.user_i = User(
            email=cls.user_i_email,
            hashed_password=get_password_hash(cls.password),
            full_name="Sign I Master Learner",
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.user_i)
        cls.db.commit()
        cls.db.refresh(cls.user_i)

        # Create user for Sign D & Multi-sign test
        cls.user_d = User(
            email=cls.user_d_email,
            hashed_password=get_password_hash(cls.password),
            full_name="Sign D Multi Master Learner",
            role=RoleEnum.LEARNER,
            is_active=True
        )
        cls.db.add(cls.user_d)
        cls.db.commit()
        cls.db.refresh(cls.user_d)

        # Create session for User I
        cls.session_i = PracticeSession(
            learner_id=cls.user_i.id,
            selected_signs=["I"],
            total_attempts=7,
            correct_count=7,
            incorrect_count=0,
            average_accuracy=100.0,
            average_confidence=90.5,
            status="completed"
        )
        cls.db.add(cls.session_i)
        cls.db.commit()
        cls.db.refresh(cls.session_i)

        # Create 7 attempts matching real scenario:
        # Expected: I, Predicted: I, Conf: 90.5%, Acc: 100%, Correct: True
        for i in range(7):
            att = AssessmentAttempt(
                session_id=cls.session_i.id,
                learner_id=cls.user_i.id,
                expected_sign="I",
                predicted_sign="I",
                is_correct=True,
                confidence=0.905,
                gesture_accuracy=100.0,
                hand_shape_accuracy=100.0,
                motion_accuracy=100.0,
                position_accuracy=100.0,
                timing_score=100.0,
                stability_score=100.0,
                timestamp=datetime(2026, 8, 22, 10, i, 0)
            )
            cls.db.add(att)

        cls.db.commit()

        # Login User I
        login_res_i = cls.client.post(
            "/api/v1/auth/login",
            data={"username": cls.user_i_email, "password": cls.password}
        )
        cls.token_i = login_res_i.json()["access_token"]
        cls.headers_i = {"Authorization": f"Bearer {cls.token_i}"}

        # Login User D
        login_res_d = cls.client.post(
            "/api/v1/auth/login",
            data={"username": cls.user_d_email, "password": cls.password}
        )
        cls.token_d = login_res_d.json()["access_token"]
        cls.headers_d = {"Authorization": f"Bearer {cls.token_d}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()

    def test_01_sign_i_mastered_in_both_classification_and_matrix(self):
        """Verify Sign I (7 attempts, 100% acc, 90.5% conf) is strictly Mastered in both APIs."""
        res = self.client.get("/api/v1/analytics/dashboard", headers=self.headers_i)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # 1. Check in sign_classification
        sign_classifications = data.get("sign_classification", [])
        sign_i_classification = next((s for s in sign_classifications if s["sign"] == "I"), None)
        self.assertIsNotNone(sign_i_classification, "Sign I missing from sign_classification")

        self.assertEqual(sign_i_classification["total_attempts"], 7)
        self.assertEqual(sign_i_classification["correct_attempts"], 7)
        self.assertEqual(sign_i_classification["accuracy"], 100.0)
        self.assertEqual(sign_i_classification["average_confidence"], 90.5)
        self.assertEqual(sign_i_classification["category"], "Mastered", "Sign I in sign_classification must be Mastered")

        # 2. Check in strongest_signs (must contain I)
        strongest = data.get("strongest_signs", [])
        self.assertIn("I", strongest, "Sign I must be in strongest_signs (Mastered signs list)")

        # 3. Check in alphabet_mastery_matrix dictionary representation
        matrix = data.get("alphabet_mastery_matrix", {})
        sign_i_matrix = matrix.get("I")
        self.assertIsNotNone(sign_i_matrix, "Sign I missing from alphabet_mastery_matrix")
        self.assertEqual(sign_i_matrix["status"], "Mastered", "Sign I status in matrix must be Mastered")
        self.assertEqual(sign_i_matrix["color"], "green", "Sign I color in matrix must be green")

    def test_02_insufficient_attempts_not_mastered(self):
        """Sign with 3 attempts, 100% accuracy, 90.5% confidence is Learning (attempts < 5)."""
        session_d = PracticeSession(
            learner_id=self.user_d.id,
            selected_signs=["D"],
            total_attempts=3,
            correct_count=3,
            incorrect_count=0,
            average_accuracy=100.0,
            average_confidence=90.5,
            status="completed"
        )
        self.db.add(session_d)
        self.db.commit()

        for i in range(3):
            self.db.add(AssessmentAttempt(
                session_id=session_d.id,
                learner_id=self.user_d.id,
                expected_sign="D",
                predicted_sign="D",
                is_correct=True,
                confidence=0.905,
                gesture_accuracy=100.0,
                hand_shape_accuracy=100.0,
                motion_accuracy=100.0,
                position_accuracy=100.0,
                timestamp=datetime.utcnow()
            ))
        self.db.commit()

        res = self.client.get("/api/v1/analytics/dashboard", headers=self.headers_d)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        sign_d_classification = next((s for s in data.get("sign_classification", []) if s["sign"] == "D"), None)
        self.assertIsNotNone(sign_d_classification)
        self.assertEqual(sign_d_classification["category"], "Practicing")
        self.assertNotIn("D", data.get("strongest_signs", []))
        self.assertEqual(data.get("alphabet_mastery_matrix", {}).get("D", {}).get("status"), "Practicing")
        self.assertEqual(data.get("alphabet_mastery_matrix", {}).get("D", {}).get("color"), "blue")

    def test_03_low_accuracy_not_mastered(self):
        """Sign with 5 attempts, 60% accuracy, 90.5% confidence is NOT Mastered."""
        session_e = PracticeSession(
            learner_id=self.user_d.id,
            selected_signs=["E"],
            total_attempts=5,
            correct_count=3,
            incorrect_count=2,
            average_accuracy=60.0,
            average_confidence=90.5,
            status="completed"
        )
        self.db.add(session_e)
        self.db.commit()

        for i in range(5):
            is_corr = (i < 3)
            self.db.add(AssessmentAttempt(
                session_id=session_e.id,
                learner_id=self.user_d.id,
                expected_sign="E",
                predicted_sign="E" if is_corr else "F",
                is_correct=is_corr,
                confidence=0.905,
                gesture_accuracy=100.0 if is_corr else 0.0,
                hand_shape_accuracy=100.0 if is_corr else 0.0,
                motion_accuracy=100.0,
                position_accuracy=100.0,
                timestamp=datetime.utcnow()
            ))
        self.db.commit()

        res = self.client.get("/api/v1/analytics/dashboard", headers=self.headers_d)
        data = res.json()

        sign_e_classification = next((s for s in data.get("sign_classification", []) if s["sign"] == "E"), None)
        self.assertIsNotNone(sign_e_classification)
        self.assertEqual(sign_e_classification["category"], "Practicing")
        self.assertNotIn("E", data.get("strongest_signs", []))
        self.assertEqual(data.get("alphabet_mastery_matrix", {}).get("E", {}).get("status"), "Practicing")
        self.assertEqual(data.get("alphabet_mastery_matrix", {}).get("E", {}).get("color"), "blue")

    def test_04_low_confidence_not_mastered(self):
        """Sign with 10 attempts, 100% accuracy, but 70% confidence is NOT Mastered."""
        session_f = PracticeSession(
            learner_id=self.user_d.id,
            selected_signs=["F"],
            total_attempts=10,
            correct_count=10,
            incorrect_count=0,
            average_accuracy=100.0,
            average_confidence=70.0,
            status="completed"
        )
        self.db.add(session_f)
        self.db.commit()

        for i in range(10):
            self.db.add(AssessmentAttempt(
                session_id=session_f.id,
                learner_id=self.user_d.id,
                expected_sign="F",
                predicted_sign="F",
                is_correct=True,
                confidence=0.70,
                gesture_accuracy=100.0,
                hand_shape_accuracy=100.0,
                motion_accuracy=100.0,
                position_accuracy=100.0,
                timestamp=datetime.utcnow()
            ))
        self.db.commit()

        res = self.client.get("/api/v1/analytics/dashboard", headers=self.headers_d)
        data = res.json()

        sign_f_classification = next((s for s in data.get("sign_classification", []) if s["sign"] == "F"), None)
        self.assertIsNotNone(sign_f_classification)
        self.assertEqual(sign_f_classification["category"], "Practicing")
        self.assertNotIn("F", data.get("strongest_signs", []))
        self.assertEqual(data.get("alphabet_mastery_matrix", {}).get("F", {}).get("status"), "Practicing")
        self.assertEqual(data.get("alphabet_mastery_matrix", {}).get("F", {}).get("color"), "blue")

    def test_05_multi_sign_mastery_persistence_and_matrix(self):
        """Test multiple signs (I, D Mastered, K Practicing, J Learning) persist accurately."""
        # Add 5 correct attempts for D with 90% confidence -> D is Mastered
        session_d_mastered = PracticeSession(
            learner_id=self.user_d.id,
            selected_signs=["D"],
            total_attempts=2,
            correct_count=2,
            incorrect_count=0,
            average_accuracy=100.0,
            average_confidence=90.0,
            status="completed"
        )
        self.db.add(session_d_mastered)
        self.db.commit()

        for i in range(2):
            self.db.add(AssessmentAttempt(
                session_id=session_d_mastered.id,
                learner_id=self.user_d.id,
                expected_sign="D",
                predicted_sign="D",
                is_correct=True,
                confidence=0.90,
                gesture_accuracy=100.0,
                hand_shape_accuracy=100.0,
                motion_accuracy=100.0,
                position_accuracy=100.0,
                timestamp=datetime.utcnow()
            ))
        self.db.commit()

        res = self.client.get("/api/v1/analytics/dashboard", headers=self.headers_d)
        data = res.json()

        sign_d_classification = next((s for s in data.get("sign_classification", []) if s["sign"] == "D"), None)
        self.assertIsNotNone(sign_d_classification)
        self.assertEqual(sign_d_classification["total_attempts"], 5)
        self.assertEqual(sign_d_classification["accuracy"], 100.0)
        self.assertEqual(sign_d_classification["category"], "Mastered")
        self.assertIn("D", data.get("strongest_signs", []))
        self.assertEqual(data.get("alphabet_mastery_matrix", {}).get("D", {}).get("status"), "Mastered")
        self.assertEqual(data.get("alphabet_mastery_matrix", {}).get("D", {}).get("color"), "green")

if __name__ == "__main__":
    unittest.main()
