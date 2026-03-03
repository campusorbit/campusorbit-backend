from datetime import datetime, timedelta, timezone
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
import app.redis as redis_module

security = HTTPBearer()


def get_redis_client():
    """Get Redis client - allows for easy mocking in tests."""
    return redis_module.redis_client


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from e


def generate_reset_token() -> str:
    """Generate a secure random token for password reset."""
    return secrets.token_urlsafe(32)


def generate_verification_token() -> str:
    """Generate a secure random token for email verification."""
    return secrets.token_urlsafe(32)


async def store_reset_token(email: str, token: str, ttl: int = 3600) -> None:
    """Store password reset token in Redis with 1-hour expiry."""
    key = f"reset_token:{token}"
    redis_client = get_redis_client()
    await redis_client.set(key, email, ex=ttl)


async def verify_reset_token(token: str) -> str | None:
    """Verify and retrieve email from reset token."""
    key = f"reset_token:{token}"
    redis_client = get_redis_client()
    email = await redis_client.get(key)
    if email:
        await redis_client.delete(key)  # One-time use
    return email


async def store_verification_token(user_id: str, token: str, ttl: int = 86400) -> None:
    """Store email verification token in Redis with 24-hour expiry."""
    key = f"verify_token:{token}"
    redis_client = get_redis_client()
    await redis_client.set(key, user_id, ex=ttl)


async def verify_verification_token(token: str) -> str | None:
    """Verify and retrieve user_id from verification token."""
    key = f"verify_token:{token}"
    redis_client = get_redis_client()
    user_id = await redis_client.get(key)
    if user_id:
        await redis_client.delete(key)  # One-time use
    return user_id


async def blacklist_token(token: str, ttl: int = 3600) -> None:
    """Add token to blacklist (for logout)."""
    key = f"blacklist:{token}"
    redis_client = get_redis_client()
    await redis_client.set(key, "1", ex=ttl)


async def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    key = f"blacklist:{token}"
    redis_client = get_redis_client()
    return await redis_client.exists(key) > 0


async def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email via SMTP."""
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        print(f"[EMAIL STUB] To: {to_email}, Subject: {subject}")
        print(f"[EMAIL BODY] {body}")
        return True  # Stub mode
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency: extracts and validates JWT, returns the current User."""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if await is_token_blacklisted(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    
    payload = decode_token(token)
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    
    return user


def require_roles(*roles: str):
    """Dependency factory: restricts access to specific roles."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return role_checker
