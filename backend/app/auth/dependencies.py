from typing import List, Callable, Optional
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import decode_access_token
from app.database.connection import get_database
from app.database.repositories.user_repository import UserRepository
from app.models.user import UserModel, UserRole
from app.middleware.error_handler import APIException

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserModel:
    """Dependency that extracts JWT from Auth header and validates current user."""
    if not credentials or not credentials.credentials:
        raise APIException(
            code="UNAUTHORIZED",
            message="Invalid or expired authentication token.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    token = credentials.credentials
    token_data = decode_access_token(token)

    if not token_data or not token_data.user_id:
        raise APIException(
            code="UNAUTHORIZED",
            message="Invalid or expired authentication token.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    db = get_database()
    repo = UserRepository(db)
    user = await repo.find_by_id(token_data.user_id)
    if not user:
        user = await repo.find_by_email(token_data.user_id)

    if not user:
        raise APIException(
            code="USER_NOT_FOUND",
            message="User associated with token no longer exists.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        raise APIException(
            code="USER_INACTIVE",
            message="User account is deactivated.",
            status_code=status.HTTP_403_FORBIDDEN
        )

    return user


def require_roles(allowed_roles: List[UserRole]) -> Callable:
    """Dependency factory enforcing Role-Based Access Control (RBAC)."""
    async def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role not in allowed_roles:
            raise APIException(
                code="FORBIDDEN_ROLE",
                message=f"Operation not permitted. Required role: {[r.value for r in allowed_roles]}",
                status_code=status.HTTP_403_FORBIDDEN
            )
        return current_user

    return role_checker
