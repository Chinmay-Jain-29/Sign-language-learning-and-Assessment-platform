from typing import Generator, List, Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import decode_token
from app.core.exceptions import AuthException, ForbiddenException
from app.database.session import get_db
from app.models.domain import User, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        if user_id_str is None or token_type != "access":
            raise AuthException(message="Invalid token payload", details={"code": "INVALID_TOKEN"})
        user_id = int(user_id_str)
    except jwt.ExpiredSignatureError:
        raise AuthException(message="Token has expired", details={"code": "EXPIRED_TOKEN"})
    except Exception as e:
        raise AuthException(message="Could not validate credentials", details={"code": "INVALID_TOKEN"})

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise AuthException(message="User account is inactive or not found", details={"code": "INACTIVE_USER"})
    
    return user

def get_optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        if user_id_str is None or token_type != "access":
            return None
        user_id = int(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()
        return user if user and user.is_active else None
    except Exception:
        return None

def require_roles(allowed_roles: List[RoleEnum]):
    def role_checker(current_user: User = Depends(get_current_user)):
        # Strictly verify database role entity
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                message=f"Role '{current_user.role.value}' is not authorized to access this resource.",
                details={"required_roles": [r.value for r in allowed_roles], "user_role": current_user.role.value}
            )
        return current_user
    return role_checker
