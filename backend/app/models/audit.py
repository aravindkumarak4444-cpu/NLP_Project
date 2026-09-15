from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.user import UserRole


class AuditLogModel(BaseModel):
    log_id: str
    event: str
    user_id: str
    user_name: str
    user_role: UserRole
    report_id: Optional[str] = None
    details: Dict[str, Any] = {}
    timestamp: datetime
