import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token
)
from app.core.exceptions import AuthException, ValidationException, NotFoundException
from app.core.response import success_response
from app.models.domain import User, LearnerProfile, RoleEnum, LearningLevelEnum, RefreshToken, PasswordResetToken
from app.schemas.dto import (
    UserRegister, Token, UserResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    if not user_in.full_name or not user_in.full_name.strip():
        raise ValidationException(message="Please enter your full name.")
    if not user_in.email or not str(user_in.email).strip():
        raise ValidationException(message="Please enter your email / ID.")
    if not user_in.password or len(user_in.password) < 6:
        raise ValidationException(message="Password must be at least 6 characters.")

    existing = db.query(User).filter(User.email.ilike(str(user_in.email).strip())).first()
    if existing:
        raise ValidationException(message="A user with this email/ID already exists.")
    
    # Public registration defaults to Learner
    user_role = user_in.role or RoleEnum.LEARNER

    user = User(
        email=str(user_in.email).strip().lower(),
        full_name=user_in.full_name.strip(),
        hashed_password=get_password_hash(user_in.password),
        role=user_role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    profile = LearnerProfile(
        user_id=user.id,
        learning_level=user_in.learning_level or LearningLevelEnum.BEGINNER,
        preferred_language=user_in.preferred_language or "English"
    )
    db.add(profile)
    db.commit()
    
    user_data = UserResponse.model_validate(user).model_dump()
    return success_response(data=user_data, message="Account created successfully.", status_code=201)

@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    content_type = request.headers.get("content-type", "")
    req_id = None
    password = None
    req_role = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            req_id = body.get("id") or body.get("email") or body.get("username")
            password = body.get("password")
            req_role = body.get("role")
        except Exception:
            raise ValidationException(message="Invalid JSON request body.")
    else:
        form = await request.form()
        req_id = form.get("username") or form.get("id") or form.get("email")
        password = form.get("password")
        req_role = form.get("role")

    if not req_id or not str(req_id).strip():
        raise ValidationException(message="Please enter your ID.", details={"field": "id"})
    if not password:
        raise ValidationException(message="Please enter your password.", details={"field": "password"})

    # Look up user by email or numeric ID
    req_id_str = str(req_id).strip()
    user = None
    if req_id_str.isdigit():
        user = db.query(User).filter(User.id == int(req_id_str)).first()
    if not user:
        user = db.query(User).filter(User.email.ilike(req_id_str)).first()

    if not user or not verify_password(password, user.hashed_password):
        raise AuthException(message="Invalid credentials.", details={"code": "INVALID_CREDENTIALS"})

    if not user.is_active:
        raise AuthException(message="User account is deactivated.", details={"code": "INACTIVE_USER"})

    # Validate Requested Role against Actual User Role (RBAC Authorization)
    if req_role and str(req_role).strip():
        req_role_str = str(req_role).strip().lower()
        actual_role_str = user.role.value.lower()
        if req_role_str != actual_role_str:
            raise AuthException(
                message=f"Access denied. Your account is registered as '{user.role.value}', not '{req_role}'.",
                details={"code": "INVALID_ROLE", "actual_role": user.role.value, "requested_role": req_role}
            )

    access_token = create_access_token(subject=user.id)
    refresh_token_str = create_refresh_token(subject=user.id)
    
    # Store Refresh Token in DB
    ref_obj = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(ref_obj)
    db.commit()

    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value
    }
    return token_data

@router.post("/refresh")
def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    ref_obj = db.query(RefreshToken).filter(
        RefreshToken.token == body.refresh_token,
        RefreshToken.revoked == False
    ).first()
    
    if not ref_obj or ref_obj.expires_at < datetime.utcnow():
        raise AuthException(message="Refresh token is expired or revoked.", details={"code": "INVALID_REFRESH_TOKEN"})
        
    user = db.query(User).filter(User.id == ref_obj.user_id).first()
    if not user or not user.is_active:
        raise AuthException(message="User not found or inactive.")
        
    new_access_token = create_access_token(subject=user.id)
    return success_response(
        data={"access_token": new_access_token, "token_type": "bearer"},
        message="Token refreshed successfully"
    )

@router.post("/logout")
def logout(body: RefreshTokenRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ref_obj = db.query(RefreshToken).filter(RefreshToken.token == body.refresh_token).first()
    if ref_obj:
        ref_obj.revoked = True
        db.commit()
    return success_response(message="User logged out successfully")

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    user_data = UserResponse.model_validate(current_user).model_dump()
    return success_response(data=user_data, message="Current user profile retrieved")

@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        # Do not reveal email existence for security
        return success_response(message="If the email exists, a password reset token has been generated.")
        
    reset_str = uuid.uuid4().hex
    reset_obj = PasswordResetToken(
        token=reset_str,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(reset_obj)
    db.commit()
    
    return success_response(
        data={"reset_token": reset_str},
        message="Password reset token generated successfully"
    )

@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_obj = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == body.reset_token,
        PasswordResetToken.used == False
    ).first()
    
    if not reset_obj or reset_obj.expires_at < datetime.utcnow():
        raise ValidationException(message="Invalid or expired reset token.")
        
    user = db.query(User).filter(User.id == reset_obj.user_id).first()
    if not user:
        raise NotFoundException(message="User not found.")
        
    user.hashed_password = get_password_hash(body.new_password)
    reset_obj.used = True
    db.commit()
    
    return success_response(message="Password reset successfully. You may now log in with your new password.")
