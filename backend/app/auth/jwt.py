from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from app.config import settings
from app.schemas.auth import TokenData
from app.models.user import UserRole


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Encodes JWT access token with user claims and expiration time."""
    to_encode = data.copy()
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])

    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decodes and validates JWT token."""
    if not token or not isinstance(token, str):
        return None

    cleaned_token = token.strip()
    if (cleaned_token.startswith('"') and cleaned_token.endswith('"')) or (cleaned_token.startswith("'") and cleaned_token.endswith("'")):
        cleaned_token = cleaned_token[1:-1].strip()

    while cleaned_token.lower().startswith("bearer "):
        cleaned_token = cleaned_token[7:].strip()

    try:
        payload = jwt.decode(
            cleaned_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            leeway=60
        )
        raw_sub = payload.get("sub")
        if raw_sub is None:
            raw_sub = payload.get("user_id") or payload.get("id") or payload.get("email")

        user_id: Optional[str] = str(raw_sub) if raw_sub is not None else None
        role_str: Optional[str] = payload.get("role")

        if user_id is None or role_str is None:
            return None

        return TokenData(user_id=user_id, role=UserRole(role_str))
    except (jwt.PyJWTError, ValueError, KeyError, AttributeError):
        return None
