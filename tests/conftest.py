"""Shared test fixtures and configuration."""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import fakeredis.aioredis

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.services.auth_service import create_access_token, hash_password

# Use SQLite for testing (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


# Create fake Redis instance for testing
fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)


# Patch get_redis_client to return fake Redis
@pytest.fixture(autouse=True)
def mock_redis():
    """Automatically mock Redis for all tests."""
    with patch('app.services.auth_service.get_redis_client', return_value=fake_redis):
        yield fake_redis


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Clear fake Redis
    await fake_redis.flushall()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Alias for client fixture."""
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_user(db_session: AsyncSession) -> User:
    """Create a test admin user."""
    user = User(
        id="test-admin",
        email="test@admin.com",
        name="Test Admin",
        hashed_password=hash_password("test123"),
        role=UserRole.admin,
        department="Test",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(seed_user: User) -> dict[str, str]:
    """Return auth headers with a valid JWT."""
    token = create_access_token({"sub": seed_user.id, "email": seed_user.email, "role": seed_user.role.value})
    return {"Authorization": f"Bearer {token}"}
