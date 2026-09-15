from typing import List, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from app.models.user import UserModel, UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.database.connection import get_database
from app.database.repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["User Directory & RBAC Management"])


class UserPublicResponse(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: UserRole
    department: str
    designation: Optional[str] = "Personnel"
    email: Optional[str] = None
    phone: Optional[str] = None


@router.get("", response_model=List[UserPublicResponse], summary="List Registered Users for Action Assignment & Directory")
async def list_users(
    current_user: UserModel = Depends(get_current_user),
    db=Depends(get_database)
):
    repo = UserRepository(db)
    all_users = await repo.find_all_users()

    # Apply privacy rules based on role
    is_authorized = current_user.role in [UserRole.SAFETY_OFFICER, UserRole.MANAGER, UserRole.ADMIN]

    res = []
    for u in all_users:
        res.append(UserPublicResponse(
            user_id=u.user_id,
            username=u.username,
            full_name=u.full_name or u.username,
            role=u.role,
            department=u.department,
            designation=u.designation or "Personnel",
            email=u.email if is_authorized else None,
            phone=(u.phone if u.phone else "Not provided") if is_authorized else None
        ))

    return res
