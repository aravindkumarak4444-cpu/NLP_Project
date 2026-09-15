from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    WORKER = "WORKER"
    SAFETY_OFFICER = "SAFETY_OFFICER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class UserModel(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.WORKER
    department: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
