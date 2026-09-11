import io
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import Base, get_db
from app.models.domain import User, LearnerProfile, RoleEnum, LearningLevelEnum
from app.core.security import get_password_hash, create_access_token

class TestRoleBasedProfileAndPhoto(unittest.TestCase):
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
        cls.client = TestClient(app)

    def setUp(self):
        self.db = self.TestingSessionLocal()
        self.db.query(LearnerProfile).delete()
        self.db.query(User).delete()
        self.db.commit()

        # Create Learner
        self.learner = User(
            id=10,
            email="learner_test@example.com",
            full_name="Alex Learner",
            first_name="Alex",
            last_name="Learner",
            phone="+1-555-0101",
            bio="Learning ASL every day!",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.LEARNER,
            is_active=True
        )
        self.db.add(self.learner)
        self.db.commit()

        self.learner_profile = LearnerProfile(
            user_id=10,
            learning_level=LearningLevelEnum.BEGINNER,
            preferred_language="English"
        )
        self.db.add(self.learner_profile)
        self.db.commit()

        # Create Instructor
        self.instructor = User(
            id=20,
            email="instructor_test@example.com",
            full_name="Prof. Sarah Jenkins",
            first_name="Sarah",
            last_name="Jenkins",
            title="Senior ASL Professor",
            department="Deaf Studies & Linguistics",
            specialization="Tactile ASL & Morphology",
            qualification="Ph.D. in Linguistics",
            experience_years=12,
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.INSTRUCTOR,
            is_active=True
        )
        self.db.add(self.instructor)

        # Create Trainer
        self.trainer = User(
            id=30,
            email="trainer_test@example.com",
            full_name="Marcus Trainer",
            first_name="Marcus",
            last_name="Trainer",
            title="Lead Accessibility Coach",
            specialization="Workplace ADA Compliance",
            qualification="Certified Accessibility Specialist",
            experience_years=7,
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.ACCESSIBILITY_TRAINER,
            is_active=True
        )
        self.db.add(self.trainer)

        # Create Administrator
        self.admin = User(
            id=40,
            email="admin_test@example.com",
            full_name="Elena Admin",
            first_name="Elena",
            last_name="Admin",
            department="Operations & IT Infrastructure",
            designation="Platform Administrator",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.ADMINISTRATOR,
            is_active=True
        )
        self.db.add(self.admin)
        self.db.commit()

        self.token_learner = create_access_token(subject=str(self.learner.id))
        self.token_instructor = create_access_token(subject=str(self.instructor.id))
        self.token_trainer = create_access_token(subject=str(self.trainer.id))
        self.token_admin = create_access_token(subject=str(self.admin.id))

    def tearDown(self):
        self.db.close()

    def test_01_learner_profile_retrieval(self):
        """TEST 1: Authenticated Learner retrieves own profile."""
        headers = {"Authorization": f"Bearer {self.token_learner}"}
        res = self.client.get("/api/v1/users/profile", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["email"], "learner_test@example.com")
        self.assertEqual(data["role"], "Learner")
        self.assertEqual(data["learning_level"], "Beginner")
        self.assertEqual(data["first_name"], "Alex")
        self.assertIn("completeness_percentage", data)

    def test_02_learner_profile_update(self):
        """TEST 2: Learner updates own profile."""
        headers = {"Authorization": f"Bearer {self.token_learner}"}
        payload = {
            "first_name": "Alexander",
            "last_name": "Learner-Smith",
            "bio": "Advanced Sign Language Aspirant",
            "phone": "+1-555-9999",
            "preferred_language": "Spanish",
            "learning_level": "Beginner"
        }
        res = self.client.put("/api/v1/users/profile", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["first_name"], "Alexander")
        self.assertEqual(data["last_name"], "Learner-Smith")
        self.assertEqual(data["full_name"], "Alexander Learner-Smith")
        self.assertEqual(data["bio"], "Advanced Sign Language Aspirant")
        self.assertEqual(data["preferred_language"], "Spanish")
        self.assertEqual(data["learning_level"], "Beginner")

        # Verify changing established level is rejected with 403
        bad_res = self.client.put(
            "/api/v1/users/profile",
            json={"learning_level": "Expert"},
            headers=headers
        )
        self.assertEqual(bad_res.status_code, 403)

    def test_03_instructor_profile_retrieval_and_update(self):
        """TEST 3: Instructor retrieves and updates own profile."""
        headers = {"Authorization": f"Bearer {self.token_instructor}"}
        res = self.client.get("/api/v1/users/profile", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "Instructor")
        self.assertEqual(data["department"], "Deaf Studies & Linguistics")
        self.assertEqual(data["experience_years"], 12)

        # Update instructor fields
        payload = {
            "title": "Principal ASL Researcher & Professor",
            "department": "Faculty of Cognitive Linguistics",
            "experience_years": 14
        }
        res_update = self.client.put("/api/v1/users/profile", json=payload, headers=headers)
        self.assertEqual(res_update.status_code, 200)
        updated = res_update.json()
        self.assertEqual(updated["title"], "Principal ASL Researcher & Professor")
        self.assertEqual(updated["department"], "Faculty of Cognitive Linguistics")
        self.assertEqual(updated["experience_years"], 14)

    def test_04_trainer_profile_retrieval_and_update(self):
        """TEST 4: Trainer retrieves and updates own profile."""
        headers = {"Authorization": f"Bearer {self.token_trainer}"}
        res = self.client.get("/api/v1/users/profile", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "Accessibility Trainer")
        self.assertEqual(data["specialization"], "Workplace ADA Compliance")

        # Update trainer fields
        payload = {
            "specialization": "Universal Design & Inclusive Workplace Training",
            "experience_years": 8
        }
        res_update = self.client.put("/api/v1/users/profile", json=payload, headers=headers)
        self.assertEqual(res_update.status_code, 200)
        updated = res_update.json()
        self.assertEqual(updated["specialization"], "Universal Design & Inclusive Workplace Training")
        self.assertEqual(updated["experience_years"], 8)

    def test_05_admin_profile_retrieval_and_update(self):
        """TEST 5: Admin retrieves and updates own profile."""
        headers = {"Authorization": f"Bearer {self.token_admin}"}
        res = self.client.get("/api/v1/users/profile", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "Administrator")
        self.assertEqual(data["designation"], "Platform Administrator")

        # Update admin fields
        payload = {
            "designation": "Chief System Architect & Administrator",
            "department": "Platform Security & Infrastructure"
        }
        res_update = self.client.put("/api/v1/users/profile", json=payload, headers=headers)
        self.assertEqual(res_update.status_code, 200)
        updated = res_update.json()
        self.assertEqual(updated["designation"], "Chief System Architect & Administrator")
        self.assertEqual(updated["department"], "Platform Security & Infrastructure")

    def test_06_profile_photo_upload_valid_formats(self):
        """TEST 6: Valid profile photo upload (PNG, JPG, WebP)."""
        headers = {"Authorization": f"Bearer {self.token_learner}"}

        # 1. PNG image (starts with \x89PNG\r\n\x1a\n)
        png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4'
        file_obj = io.BytesIO(png_bytes)
        res = self.client.post(
            "/api/v1/users/profile/photo",
            headers=headers,
            files={"file": ("avatar.png", file_obj, "image/png")}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("profile_photo_url", data)
        self.assertTrue(data["profile_photo_url"].startswith("/uploads/avatars/"))

        # Verify persisted on profile GET
        res_prof = self.client.get("/api/v1/users/profile", headers=headers)
        self.assertEqual(res_prof.json()["profile_photo_url"], data["profile_photo_url"])

    def test_07_invalid_photo_format_rejected(self):
        """TEST 7: Upload unsupported file format (e.g. text/exe)."""
        headers = {"Authorization": f"Bearer {self.token_learner}"}
        fake_file = io.BytesIO(b'<!DOCTYPE html><html><body>malicious payload</body></html>')
        res = self.client.post(
            "/api/v1/users/profile/photo",
            headers=headers,
            files={"file": ("evil.html", fake_file, "text/html")}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unsupported image format", res.text)

    def test_08_oversized_photo_rejected(self):
        """TEST 8: Oversized photo rejected (>5MB)."""
        headers = {"Authorization": f"Bearer {self.token_learner}"}
        oversized = io.BytesIO(b'\xff\xd8\xff' + b'0' * (6 * 1024 * 1024))
        res = self.client.post(
            "/api/v1/users/profile/photo",
            headers=headers,
            files={"file": ("huge.jpg", oversized, "image/jpeg")}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("exceeds maximum allowed limit", res.text)

    def test_09_photo_deletion(self):
        """TEST 9: User deletes own profile photo."""
        headers = {"Authorization": f"Bearer {self.token_learner}"}
        
        # First upload
        png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4'
        self.client.post(
            "/api/v1/users/profile/photo",
            headers=headers,
            files={"file": ("avatar.png", io.BytesIO(png_bytes), "image/png")}
        )

        # Delete photo
        res_del = self.client.delete("/api/v1/users/profile/photo", headers=headers)
        self.assertEqual(res_del.status_code, 200)
        self.assertIsNone(res_del.json()["profile_photo_url"])

        # Check profile GET
        res_prof = self.client.get("/api/v1/users/profile", headers=headers)
        self.assertIsNone(res_prof.json()["profile_photo_url"])

    def test_10_role_protection_prevent_self_promotion(self):
        """TEST 10: Learner attempts to modify role to Administrator -> rejected/ignored."""
        headers = {"Authorization": f"Bearer {self.token_learner}"}
        res = self.client.put(
            "/api/v1/users/profile",
            json={"role": "Administrator", "is_active": False, "id": 9999},
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "Learner")
        self.assertEqual(data["id"], 10)
        self.assertTrue(data["is_active"])

    def test_11_sensitive_secrets_never_returned(self):
        """TEST 11: Profile API must NEVER return password, hashed_password, or tokens."""
        headers = {"Authorization": f"Bearer {self.token_learner}"}
        res = self.client.get("/api/v1/users/profile", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertNotIn("password", data)
        self.assertNotIn("hashed_password", data)
        self.assertNotIn("password_hash", data)
        self.assertNotIn("token", data)
        self.assertNotIn("access_token", data)

    def test_12_cross_user_photo_isolation(self):
        """TEST 12: Ownership enforcement: photo operations only affect authenticated token subject."""
        headers_learner = {"Authorization": f"Bearer {self.token_learner}"}
        headers_instructor = {"Authorization": f"Bearer {self.token_instructor}"}

        # Learner uploads photo
        png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4'
        res_l = self.client.post(
            "/api/v1/users/profile/photo",
            headers=headers_learner,
            files={"file": ("learner.png", io.BytesIO(png_bytes), "image/png")}
        )
        self.assertEqual(res_l.status_code, 200)
        learner_photo = res_l.json()["profile_photo_url"]

        # Instructor deletes photo -> only deletes instructor's (which is null)
        res_inst_del = self.client.delete("/api/v1/users/profile/photo", headers=headers_instructor)
        self.assertEqual(res_inst_del.status_code, 200)

        # Verify Learner photo is still intact
        res_l_check = self.client.get("/api/v1/users/profile", headers=headers_learner)
        self.assertEqual(res_l_check.json()["profile_photo_url"], learner_photo)

if __name__ == "__main__":
    unittest.main()
