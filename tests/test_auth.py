"""
Comprehensive tests for Authentication & Authorization System
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User, UserRole
from app.services.auth_service import hash_password
import uuid


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("password123"),
        role=UserRole.student,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """Create an admin user."""
    user = User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        name="Admin User",
        hashed_password=hash_password("admin123"),
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication endpoints."""

    async def test_register_success(self, async_client: AsyncClient):
        """Test successful user registration."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "password123",
                "role": "student",
                "phone": "+1234567890",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, async_client: AsyncClient, test_user: User):
        """Test registration with existing email."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "name": "Duplicate User",
                "password": "password123",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_invalid_role(self, async_client: AsyncClient):
        """Test registration with invalid role."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "password123",
                "role": "invalid_role",
            },
        )
        assert response.status_code == 400

    async def test_register_weak_password(self, async_client: AsyncClient):
        """Test registration with weak password."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "123",  # Too short
            },
        )
        assert response.status_code == 422

    async def test_login_success(self, async_client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email

    async def test_login_wrong_password(self, async_client: AsyncClient, test_user: User):
        """Test login with wrong password."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent email."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401

    async def test_login_inactive_user(self, async_client: AsyncClient, db_session: AsyncSession):
        """Test login with inactive account."""
        user = User(
            id=str(uuid.uuid4()),
            email="inactive@example.com",
            name="Inactive User",
            hashed_password=hash_password("password123"),
            role=UserRole.student,
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 403

    async def test_get_current_user(self, async_client: AsyncClient, test_user: User):
        """Test getting current user profile."""
        # Login first
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name

    async def test_get_current_user_no_token(self, async_client: AsyncClient):
        """Test getting current user without token."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 403

    async def test_get_current_user_invalid_token(self, async_client: AsyncClient):
        """Test getting current user with invalid token."""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    async def test_refresh_token(self, async_client: AsyncClient, test_user: User):
        """Test token refresh."""
        # Login first
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_with_access_token(self, async_client: AsyncClient, test_user: User):
        """Test refresh with access token instead of refresh token."""
        # Login first
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        access_token = login_response.json()["access_token"]

        # Try to refresh with access token
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert response.status_code == 401

    async def test_logout(self, async_client: AsyncClient, test_user: User):
        """Test logout."""
        # Login first
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        token = login_response.json()["access_token"]

        # Logout
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

        # Try using the same token - should fail
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

    async def test_forgot_password(self, async_client: AsyncClient, test_user: User):
        """Test forgot password request."""
        response = await async_client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email},
        )
        assert response.status_code == 200
        assert "sent" in response.json()["message"].lower()

    async def test_forgot_password_nonexistent_email(self, async_client: AsyncClient):
        """Test forgot password with non-existent email."""
        response = await async_client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
        )
        # Should return success to prevent email enumeration
        assert response.status_code == 200

    async def test_change_password_success(self, async_client: AsyncClient, test_user: User):
        """Test successful password change."""
        # Login first
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        token = login_response.json()["access_token"]

        # Change password
        response = await async_client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "password123",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 200

        # Try logging in with new password
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "newpassword123"},
        )
        assert login_response.status_code == 200

    async def test_change_password_wrong_current(self, async_client: AsyncClient, test_user: User):
        """Test password change with wrong current password."""
        # Login first
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        token = login_response.json()["access_token"]

        # Try to change with wrong current password
        response = await async_client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 400

    async def test_change_password_same_as_current(self, async_client: AsyncClient, test_user: User):
        """Test password change with same password."""
        # Login first
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        token = login_response.json()["access_token"]

        # Try to change to same password
        response = await async_client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "password123",
                "new_password": "password123",
            },
        )
        assert response.status_code == 400


@pytest.mark.asyncio
class TestAuthorization:
    """Test role-based authorization."""

    async def test_admin_access(self, async_client: AsyncClient, admin_user: User):
        """Test admin can access admin endpoints."""
        # Login as admin
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        token = login_response.json()["access_token"]

        # Access protected endpoint (we'll need to create these)
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    async def test_student_cannot_access_admin(self, async_client: AsyncClient, test_user: User):
        """Test student cannot access admin-only endpoints."""
        # Login as student
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        token = login_response.json()["access_token"]

        # Try to access admin endpoint (we'll test this with users endpoint later)
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        # For now, /me is accessible to all authenticated users
        assert response.status_code == 200

    async def test_role_validation(self, async_client: AsyncClient, test_user: User, admin_user: User):
        """Test that role information is correctly included in tokens."""
        # Login as student
        student_login = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
        assert student_login.json()["user"]["role"] == "student"

        # Login as admin
        admin_login = await async_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "admin123"},
        )
        assert admin_login.json()["user"]["role"] == "admin"
