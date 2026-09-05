from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.WORKER
    department: str = Field(..., min_length=2, max_length=100)


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    department: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
