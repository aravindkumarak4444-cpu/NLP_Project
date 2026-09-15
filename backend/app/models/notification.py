from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.user import UserRole


class NotificationModel(BaseModel):
    notification_id: str
    recipient_role: Optional[UserRole] = None
    recipient_user_id: Optional[str] = None
    title: str
    message: str
    report_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime
