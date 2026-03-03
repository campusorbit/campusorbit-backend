"""
Comprehensive tests for Student Information System (Feature #2)
"""
import uuid
from datetime import date, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.student_profile import StudentProfile
from app.models.class_model import Class
from app.services.auth_service import hash_password


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """Create an admin user for testing."""
    user = User(
        id=str(uuid.uuid4()),
        email="admin@test.com",
        name="Admin User",
        hashed_password=hash_password("admin123"),
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def teacher_user(db_session: AsyncSession):
    """Create a teacher user for testing."""
    user = User(
        id=str(uuid.uuid4()),
        email="teacher@test.com",
        name="Teacher User",
        hashed_password=hash_password("teacher123"),
        role=UserRole.teacher,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_class(db_session: AsyncSession, teacher_user: User):
    """Create a test class."""
    class_obj = Class(
        id=str(uuid.uuid4()),
        name="Class 10A",
        grade_level=10,
        section="A",
        academic_year="2025-2026",
        capacity=40,
        class_teacher_id=teacher_user.id,
        is_active=True,
    )
    db_session.add(class_obj)
    await db_session.commit()
    await db_session.refresh(class_obj)
    return class_obj


@pytest.fixture
async def test_student_with_profile(db_session: AsyncSession, test_class: Class):
    """Create a student with profile."""
    student = User(
        id=str(uuid.uuid4()),
        email="student@test.com",
        name="Test Student",
        hashed_password=hash_password("student123"),
        role=UserRole.student,
        roll_no="2025001",
        phone="+1234567890",
        parent_name="Parent Name",
        parent_phone="+0987654321",
        is_active=True,
    )
    db_session.add(student)
    await db_session.flush()
    
    profile = StudentProfile(
        id=str(uuid.uuid4()),
        student_id=student.id,
        admission_number="ADM2025001",
        admission_date=date(2025, 1, 15),
        batch_year=2025,
        class_id=test_class.id,
        section="A",
        guardian_name="Guardian Name",
        guardian_phone="+0987654321",
        blood_group="O+",
        city="Mumbai",
        state="Maharashtra",
        country="India",
    )
    db_session.add(profile)
    
    await db_session.commit()
    await db_session.refresh(student)
    await db_session.refresh(profile)
    return student


@pytest.mark.asyncio
class TestClassManagement:
    """Test class/section management endpoints."""

    async def test_create_class(self, async_client: AsyncClient, admin_user: User, teacher_user: User):
        """Test creating a new class."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Create class
        response = await async_client.post(
            "/api/v1/students/classes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Class 9B",
                "grade_level": 9,
                "section": "B",
                "academic_year": "2025-2026",
                "capacity": 35,
                "class_teacher_id": teacher_user.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Class 9B"
        assert data["grade_level"] == 9
        assert data["section"] == "B"
        assert data["is_active"] is True

    async def test_create_class_invalid_teacher(self, async_client: AsyncClient, admin_user: User):
        """Test creating class with invalid teacher ID."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Create class with invalid teacher
        response = await async_client.post(
            "/api/v1/students/classes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Class 9B",
                "grade_level": 9,
                "section": "B",
                "academic_year": "2025-2026",
                "class_teacher_id": "invalid-id",
            },
        )
        assert response.status_code == 404

    async def test_list_classes(self, async_client: AsyncClient, admin_user: User, test_class: Class):
        """Test listing classes."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # List classes
        response = await async_client.get(
            "/api/v1/students/classes",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_class(self, async_client: AsyncClient, admin_user: User, test_class: Class):
        """Test getting class details."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Get class
        response = await async_client.get(
            f"/api/v1/students/classes/{test_class.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_class.id
        assert data["name"] == test_class.name

    async def test_update_class(self, async_client: AsyncClient, admin_user: User, test_class: Class):
        """Test updating class."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Update class
        response = await async_client.put(
            f"/api/v1/students/classes/{test_class.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"capacity": 50},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] == 50

    async def test_delete_class(self, async_client: AsyncClient, admin_user: User, test_class: Class):
        """Test soft deleting a class."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Delete class
        response = await async_client.delete(
            f"/api/v1/students/classes/{test_class.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204


@pytest.mark.asyncio
class TestStudentManagement:
    """Test student CRUD operations."""

    async def test_create_student(self, async_client: AsyncClient, admin_user: User, test_class: Class):
        """Test creating a new student."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Create student
        response = await async_client.post(
            "/api/v1/students/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "newstudent@test.com",
                "name": "New Student",
                "password": "password123",
                "phone": "+1234567890",
                "roll_no": "2025002",
                "admission_number": "ADM2025002",
                "admission_date": "2025-01-20",
                "batch_year": 2025,
                "class_id": test_class.id,
                "section": "A",
                "guardian_name": "Guardian Name",
                "guardian_phone": "+0987654321",
                "blood_group": "A+",
                "city": "Delhi",
                "state": "Delhi",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newstudent@test.com"
        assert data["name"] == "New Student"
        assert data["profile"] is not None
        assert data["profile"]["admission_number"] == "ADM2025002"

    async def test_create_student_duplicate_email(self, async_client: AsyncClient, admin_user: User, test_student_with_profile: User):
        """Test creating student with duplicate email."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Try to create student with duplicate email
        response = await async_client.post(
            "/api/v1/students/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": test_student_with_profile.email,
                "name": "Duplicate Student",
                "password": "password123",
                "admission_number": "ADM2025999",
                "admission_date": "2025-01-20",
                "batch_year": 2025,
                "guardian_name": "Guardian Name",
                "guardian_phone": "+0987654321",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    async def test_create_student_duplicate_admission_number(self, async_client: AsyncClient, admin_user: User, test_student_with_profile: User, db_session: AsyncSession):
        """Test creating student with duplicate admission number."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Get the existing student's admission number
        from sqlalchemy import select
        result = await db_session.execute(
            select(StudentProfile).where(StudentProfile.student_id == test_student_with_profile.id)
        )
        profile = result.scalar_one()
        
        # Try to create student with duplicate admission number
        response = await async_client.post(
            "/api/v1/students/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "anotherstudent@test.com",
                "name": "Another Student",
                "password": "password123",
                "admission_number": profile.admission_number,
                "admission_date": "2025-01-20",
                "batch_year": 2025,
                "guardian_name": "Guardian Name",
                "guardian_phone": "+0987654321",
            },
        )
        assert response.status_code == 409
        assert "admission number" in response.json()["detail"].lower()

    async def test_list_students(self, async_client: AsyncClient, teacher_user: User, test_student_with_profile: User):
        """Test listing students."""
        # Login as teacher
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_user.email, "password": "teacher123"},
        )
        token = login_response.json()["access_token"]
        
        # List students
        response = await async_client.get(
            "/api/v1/students/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["students"]) >= 1

    async def test_list_students_with_filters(self, async_client: AsyncClient, teacher_user: User, test_student_with_profile: User, test_class: Class):
        """Test listing students with filters."""
        # Login as teacher
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_user.email, "password": "teacher123"},
        )
        token = login_response.json()["access_token"]
        
        # List students with class filter
        response = await async_client.get(
            f"/api/v1/students/?class_id={test_class.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    async def test_get_student(self, async_client: AsyncClient, teacher_user: User, test_student_with_profile: User):
        """Test getting student details."""
        # Login as teacher
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_user.email, "password": "teacher123"},
        )
        token = login_response.json()["access_token"]
        
        # Get student
        response = await async_client.get(
            f"/api/v1/students/{test_student_with_profile.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_student_with_profile.id
        assert data["email"] == test_student_with_profile.email
        assert data["profile"] is not None

    async def test_get_student_self_access(self, async_client: AsyncClient, test_student_with_profile: User):
        """Test student can access their own details."""
        # Login as student
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_student_with_profile.email, "password": "student123"},
        )
        token = login_response.json()["access_token"]
        
        # Get own details
        response = await async_client.get(
            f"/api/v1/students/{test_student_with_profile.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    async def test_get_student_forbidden(self, async_client: AsyncClient, test_student_with_profile: User, db_session: AsyncSession):
        """Test student cannot access other student's details."""
        # Create another student
        another_student = User(
            id=str(uuid.uuid4()),
            email="anotherstudent@test.com",
            name="Another Student",
            hashed_password=hash_password("student123"),
            role=UserRole.student,
            is_active=True,
        )
        db_session.add(another_student)
        await db_session.commit()
        
        # Login as first student
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_student_with_profile.email, "password": "student123"},
        )
        token = login_response.json()["access_token"]
        
        # Try to access another student's details
        response = await async_client.get(
            f"/api/v1/students/{another_student.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_update_student(self, async_client: AsyncClient, admin_user: User, test_student_with_profile: User):
        """Test updating student basic information."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Update student
        response = await async_client.put(
            f"/api/v1/students/{test_student_with_profile.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+9999999999"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+9999999999"

    async def test_delete_student(self, async_client: AsyncClient, admin_user: User, test_student_with_profile: User):
        """Test soft deleting a student."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Delete student
        response = await async_client.delete(
            f"/api/v1/students/{test_student_with_profile.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204


@pytest.mark.asyncio
class TestStudentProfile:
    """Test student profile operations."""

    async def test_get_student_profile(self, async_client: AsyncClient, teacher_user: User, test_student_with_profile: User):
        """Test getting student profile."""
        # Login as teacher
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_user.email, "password": "teacher123"},
        )
        token = login_response.json()["access_token"]
        
        # Get profile
        response = await async_client.get(
            f"/api/v1/students/{test_student_with_profile.id}/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == test_student_with_profile.id
        assert data["admission_number"] == "ADM2025001"

    async def test_update_student_profile(self, async_client: AsyncClient, admin_user: User, test_student_with_profile: User):
        """Test updating student profile."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]
        
        # Update profile
        response = await async_client.put(
            f"/api/v1/students/{test_student_with_profile.id}/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "bio": "Updated bio for testing",
                "medical_conditions": "None",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Updated bio for testing"
        assert data["medical_conditions"] == "None"


@pytest.mark.asyncio
class TestStudentSummaries:
    """Test student summary endpoints."""

    async def test_get_attendance_summary(self, async_client: AsyncClient, test_student_with_profile: User):
        """Test getting attendance summary."""
        # Login as student
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_student_with_profile.email, "password": "student123"},
        )
        token = login_response.json()["access_token"]
        
        # Get attendance summary
        response = await async_client.get(
            f"/api/v1/students/{test_student_with_profile.id}/attendance-summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_days" in data
        assert "present_days" in data
        assert "attendance_percentage" in data

    async def test_get_fee_history(self, async_client: AsyncClient, test_student_with_profile: User):
        """Test getting fee history."""
        # Login as student
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_student_with_profile.email, "password": "student123"},
        )
        token = login_response.json()["access_token"]
        
        # Get fee history
        response = await async_client.get(
            f"/api/v1/students/{test_student_with_profile.id}/fee-history",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_documents(self, async_client: AsyncClient, test_student_with_profile: User):
        """Test getting student documents."""
        # Login as student
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_student_with_profile.email, "password": "student123"},
        )
        token = login_response.json()["access_token"]
        
        # Get documents
        response = await async_client.get(
            f"/api/v1/students/{test_student_with_profile.id}/documents",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
class TestAuthorization:
    """Test authorization rules for student endpoints."""

    async def test_teacher_can_list_students(self, async_client: AsyncClient, teacher_user: User):
        """Test that teachers can list students."""
        # Login as teacher
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_user.email, "password": "teacher123"},
        )
        token = login_response.json()["access_token"]
        
        # List students
        response = await async_client.get(
            "/api/v1/students/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    async def test_student_cannot_create_student(self, async_client: AsyncClient, test_student_with_profile: User):
        """Test that students cannot create other students."""
        # Login as student
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_student_with_profile.email, "password": "student123"},
        )
        token = login_response.json()["access_token"]
        
        # Try to create student
        response = await async_client.post(
            "/api/v1/students/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "newstudent@test.com",
                "name": "New Student",
                "password": "password123",
                "admission_number": "ADM2025999",
                "admission_date": "2025-01-20",
                "batch_year": 2025,
                "guardian_name": "Guardian",
                "guardian_phone": "+1234567890",
            },
        )
        assert response.status_code == 403

    async def test_teacher_cannot_delete_student(self, async_client: AsyncClient, teacher_user: User, test_student_with_profile: User):
        """Test that teachers cannot delete students."""
        # Login as teacher
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_user.email, "password": "teacher123"},
        )
        token = login_response.json()["access_token"]
        
        # Try to delete student
        response = await async_client.delete(
            f"/api/v1/students/{test_student_with_profile.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
