from typing import List
from fastapi import APIRouter, Depends
from app.models.audit import AuditLogModel
from app.models.user import UserModel, UserRole
from app.auth.dependencies import require_roles
from app.database.connection import get_database
from app.database.repositories.audit_repository import AuditRepository

router = APIRouter(prefix="/audit-logs", tags=["Audit Logging"])


@router.get("", response_model=List[AuditLogModel], summary="List Audit Logs")
async def get_audit_logs(
    current_user: UserModel = Depends(require_roles([UserRole.MANAGER, UserRole.ADMIN, UserRole.SAFETY_OFFICER])),
    db=Depends(get_database)
):
    repo = AuditRepository(db)
    return await repo.list_logs(limit=100)
