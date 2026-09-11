import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_db, SessionLocal
from app.models.domain import User, RoleEnum, LearnerProfile
from app.core.security import get_password_hash

class TestAuthModuleFlow(unittest.TestCase):
    """
    Comprehensive Authentication & RBAC Test Suite
    Covers:
    - ID, Password, and Role selection
    - Backend actual role verification vs requested role
    - Escalation prevention
    - Registration validation
    - Duplicate email rejection
    - Missing fields validation
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Seed Test Accounts with known roles
        cls.test_users = [
            ("auth_learner@test.com", "password123", "Auth Learner", RoleEnum.LEARNER),
            ("auth_instructor@test.com", "password123", "Auth Instructor", RoleEnum.INSTRUCTOR),
            ("auth_trainer@test.com", "password123", "Auth Trainer", RoleEnum.ACCESSIBILITY_TRAINER),
            ("auth_admin@test.com", "password123", "Auth Admin", RoleEnum.ADMINISTRATOR),
        ]
        for email, pwd, name, role in cls.test_users:
            existing = cls.db.query(User).filter(User.email == email).first()
            if not existing:
                u = User(
                    email=email,
                    full_name=name,
                    hashed_password=get_password_hash(pwd),
                    role=role
                )
                cls.db.add(u)
                cls.db.commit()
                cls.db.refresh(u)
                profile = LearnerProfile(user_id=u.id, preferred_language="English")
                cls.db.add(profile)
                cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        for email, _, _, _ in cls.test_users:
            u = cls.db.query(User).filter(User.email == email).first()
            if u:
                cls.db.delete(u)
        cls.db.commit()
        cls.db.close()

    def test_01_valid_login_correct_role(self):
        """Test 1: Valid ID + password + correct matching role succeeds."""
        payload = {
            "id": "auth_learner@test.com",
            "password": "password123",
            "role": "Learner"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "Learner")
        self.assertEqual(data["email"], "auth_learner@test.com")

    def test_02_invalid_password_rejected(self):
        """Test 2: Invalid password rejected with 401."""
        payload = {
            "id": "auth_learner@test.com",
            "password": "wrong_password_999",
            "role": "Learner"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid credentials", res.text)

    def test_03_invalid_id_rejected(self):
        """Test 3: Non-existent ID rejected with 401."""
        payload = {
            "id": "non_existent_user_999@test.com",
            "password": "password123",
            "role": "Learner"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid credentials", res.text)

    def test_04_missing_id_validation_error(self):
        """Test 4: Missing ID rejected with validation error."""
        payload = {
            "id": "",
            "password": "password123",
            "role": "Learner"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertIn(res.status_code, [400, 422])
        self.assertIn("Please enter your ID", res.text)

    def test_05_missing_password_validation_error(self):
        """Test 5: Missing password rejected with validation error."""
        payload = {
            "id": "auth_learner@test.com",
            "password": "",
            "role": "Learner"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertIn(res.status_code, [400, 422])
        self.assertIn("Please enter your password", res.text)

    def test_06_correct_credentials_incorrect_selected_role_rejected(self):
        """Test 6: Valid credentials but learner selecting Instructor is rejected."""
        payload = {
            "id": "auth_learner@test.com",
            "password": "password123",
            "role": "Instructor"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertIn("Access denied", res.text)
        self.assertIn("registered as 'Learner'", res.text)

    def test_07_unauthorized_role_escalation_to_admin_rejected(self):
        """Test 7: Learner selecting Administrator role is rejected by backend RBAC."""
        payload = {
            "id": "auth_learner@test.com",
            "password": "password123",
            "role": "Administrator"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertIn("Access denied", res.text)

    def test_08_administrator_login_with_correct_role_succeeds(self):
        """Test 8: Administrator logging in with Administrator role succeeds."""
        payload = {
            "id": "auth_admin@test.com",
            "password": "password123",
            "role": "Administrator"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "Administrator")

    def test_09_valid_registration_creates_account(self):
        """Test 9: Valid registration creates new account."""
        reg_payload = {
            "full_name": "New Test Learner",
            "email": "new_unique_learner_999@test.com",
            "password": "securepassword123",
            "role": "Learner",
            "preferred_language": "English",
            "learning_level": "Beginner"
        }
        res = self.client.post("/api/v1/auth/register", json=reg_payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["message"], "Account created successfully.")

        # Cleanup created user
        u = self.db.query(User).filter(User.email == "new_unique_learner_999@test.com").first()
        if u:
            self.db.delete(u)
            self.db.commit()

    def test_10_duplicate_email_registration_rejected(self):
        """Test 10: Registering with existing email is rejected."""
        reg_payload = {
            "full_name": "Duplicate Learner",
            "email": "auth_learner@test.com",
            "password": "securepassword123",
            "role": "Learner"
        }
        res = self.client.post("/api/v1/auth/register", json=reg_payload)
        self.assertIn(res.status_code, [400, 422])
        self.assertIn("already exists", res.text)

    def test_11_short_password_registration_rejected(self):
        """Test 11: Registering with short password (<6 chars) is rejected."""
        reg_payload = {
            "full_name": "Short Password Learner",
            "email": "short_pwd_learner@test.com",
            "password": "123",
            "role": "Learner"
        }
        res = self.client.post("/api/v1/auth/register", json=reg_payload)
        self.assertIn(res.status_code, [400, 422])
        self.assertIn("at least 6 characters", res.text)

if __name__ == "__main__":
    unittest.main()
