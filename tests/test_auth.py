"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User, UserRole
from app.services.auth_service import hash_password


class TestAuthLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, seed_user: User):
        response = await client.post("/api/v1/auth/login", json={"email": "test@admin.com", "password": "test123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, seed_user: User):
        response = await client.post("/api/v1/auth/login", json={"email": "test@admin.com", "password": "wrong"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "test123"})
        assert response.status_code == 401


class TestAuthRegister:
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "new@user.com", "name": "New User", "password": "secure123", "role": "student"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@user.com"
        assert data["name"] == "New User"
        assert data["role"] == "student"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, seed_user: User):
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@admin.com", "name": "Dup User", "password": "test123"},
        )
        assert response.status_code == 409


class TestAuthMe:
    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@admin.com"
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403


class TestRefreshToken:
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, seed_user: User):
        # First login to get a refresh token
        login_response = await client.post(
            "/api/v1/auth/login", json={"email": "test@admin.com", "password": "test123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token
        response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        assert "access_token" in response.json()
