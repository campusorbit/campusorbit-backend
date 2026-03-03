import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_service import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_reset_token,
    generate_verification_token,
    get_current_user,
    hash_password,
    security,
    send_email,
    store_reset_token,
    store_verification_token,
    verify_password,
    verify_reset_token,
    verify_verification_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    token_data = {"sub": user.id, "email": user.email, "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "avatar": user.avatar
        },
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Validate role
    try:
        user_role = UserRole(request.role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role: {request.role}")

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        name=request.name,
        hashed_password=hash_password(request.password),
        role=user_role,
        department=request.department,
        phone=request.phone,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Generate verification token
    verification_token = generate_verification_token()
    await store_verification_token(user.id, verification_token)

    # Send verification email
    verification_link = f"http://localhost:3001/verify-email?token={verification_token}"
    await send_email(
        user.email,
        "Verify your CampusOrbit account",
        f"""
        <html>
            <body>
                <h2>Welcome to CampusOrbit, {user.name}!</h2>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create this account, please ignore this email.</p>
            </body>
        </html>
        """
    )

    return user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    token_data = {"sub": user.id, "email": user.email, "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "avatar": user.avatar
        },
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout and blacklist the current token."""
    token = credentials.credentials
    # Blacklist token for remaining lifetime (max 30 minutes for access token)
    await blacklist_token(token, ttl=1800)
    return MessageResponse(message="Successfully logged out")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request password reset email."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if not user:
        return MessageResponse(message="If the email exists, a password reset link has been sent")

    # Generate reset token
    reset_token = generate_reset_token()
    await store_reset_token(user.email, reset_token)

    # Send reset email
    reset_link = f"http://localhost:3001/reset-password?token={reset_token}"
    await send_email(
        user.email,
        "Reset your CampusOrbit password",
        f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hi {user.name},</p>
                <p>We received a request to reset your password. Click the link below to set a new password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """
    )

    return MessageResponse(message="If the email exists, a password reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using token from email."""
    email = await verify_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update password
    user.hashed_password = hash_password(request.new_password)
    await db.flush()

    return MessageResponse(message="Password reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change password for authenticated user."""
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    if request.current_password == request.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    # Update password
    current_user.hashed_password = hash_password(request.new_password)
    await db.flush()

    return MessageResponse(message="Password changed successfully")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(request: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    """Verify email address using token."""
    user_id = await verify_verification_token(request.token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Mark user as verified (you might want to add an email_verified field to User model)
    # For now, we'll just ensure they're active
    user.is_active = True
    await db.flush()

    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(current_user: User = Depends(get_current_user)):
    """Resend email verification link."""
    # Generate new verification token
    verification_token = generate_verification_token()
    await store_verification_token(current_user.id, verification_token)

    # Send verification email
    verification_link = f"http://localhost:3001/verify-email?token={verification_token}"
    await send_email(
        current_user.email,
        "Verify your CampusOrbit account",
        f"""
        <html>
            <body>
                <h2>Email Verification</h2>
                <p>Hi {current_user.name},</p>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
            </body>
        </html>
        """
    )

    return MessageResponse(message="Verification email sent")
