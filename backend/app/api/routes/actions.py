from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from app.models.report import ActionItemModel, ActionStatus, ReportStatus
from app.models.user import UserModel, UserRole
from app.models.audit import AuditLogModel
from app.models.notification import NotificationModel
from app.auth.dependencies import get_current_user, require_roles
from app.database.connection import get_database
from app.database.repositories.report_repository import ReportRepository
from app.database.repositories.audit_repository import AuditRepository
from app.database.repositories.notification_repository import NotificationRepository
from app.utils.timestamps import utc_now
from app.middleware.error_handler import APIException

router = APIRouter(prefix="/actions", tags=["Corrective Actions Workflow"])


class ActionStatusUpdateRequest(BaseModel):
    status: ActionStatus


class AssignedActionResponse(BaseModel):
    action_id: str
    report_id: str
    description: str
    assigned_to: Optional[str] = None
    status: ActionStatus
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    report_description: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None


@router.get("/my", response_model=List[AssignedActionResponse], summary="Get Corrective Actions Assigned to Current User")
async def get_my_actions(
    current_user: UserModel = Depends(get_current_user),
    db=Depends(get_database)
):
    repo = ReportRepository(db)
    all_reports = await repo.get_all_reports_for_analytics()

    user_identifiers = {
        current_user.user_id.lower(),
        current_user.username.lower(),
        current_user.email.lower(),
        (current_user.full_name or "").lower()
    }

    my_actions = []
    for r in all_reports:
        for a in (r.actions or []):
            if a.assigned_to:
                assign_lower = a.assigned_to.lower()
                if any(ui and (ui in assign_lower or assign_lower in ui) for ui in user_identifiers):
                    my_actions.append(AssignedActionResponse(
                    action_id=a.action_id,
                    report_id=r.report_id,
                    description=a.description,
                    assigned_to=a.assigned_to,
                    status=a.status,
                    due_date=a.due_date,
                    completed_at=a.completed_at,
                    created_at=a.created_at,
                    report_description=r.description,
                    location=r.location,
                    department=r.department
                ))

    return my_actions


@router.patch("/{report_id}/{action_id}", response_model=AssignedActionResponse, summary="Update Action Item Status (Responsible Person / Officer)")
async def update_action_status(
    report_id: str,
    action_id: str,
    req: ActionStatusUpdateRequest,
    current_user: UserModel = Depends(get_current_user),
    db=Depends(get_database)
):
    report_repo = ReportRepository(db)
    audit_repo = AuditRepository(db)
    notif_repo = NotificationRepository(db)

    report = await report_repo.find_by_id(report_id)
    if not report:
        raise APIException(
            code="REPORT_NOT_FOUND",
            message=f"Safety report with ID '{report_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    actions = report.actions or []
    target_action = None
    now = utc_now()

    for a in actions:
        if a.action_id == action_id:
            target_action = a
            a.status = req.status
            if req.status == ActionStatus.COMPLETED and not a.completed_at:
                a.completed_at = now
            break

    if not target_action:
        raise APIException(
            code="ACTION_NOT_FOUND",
            message=f"Action item '{action_id}' not found in report '{report_id}'.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # If all actions are completed, update report status to RESOLVED
    all_completed = all(a.status == ActionStatus.COMPLETED for a in actions)
    new_status = report.status
    if all_completed and report.status in [ReportStatus.ACTION_ASSIGNED, ReportStatus.IN_PROGRESS]:
        new_status = ReportStatus.RESOLVED

    update_dict = {
        "actions": [a.model_dump() for a in actions],
        "status": new_status,
        "updated_at": now
    }
    await report_repo.update_report(report_id, update_dict)

    # Audit Logging & Notification
    await audit_repo.log_event(AuditLogModel(
        log_id=f"AUD-{int(now.timestamp())}",
        event="ACTION_STATUS_UPDATED",
        user_id=current_user.user_id,
        user_name=current_user.full_name or current_user.username,
        user_role=current_user.role,
        report_id=report.report_id,
        details={"action_id": action_id, "new_status": req.status.value},
        timestamp=now
    ))

    if req.status == ActionStatus.COMPLETED:
        await notif_repo.create_notification(NotificationModel(
            notification_id=f"NOTIF-{int(now.timestamp())}",
            recipient_role=UserRole.SAFETY_OFFICER,
            title="Corrective Action Completed",
            message=f"Action '{target_action.description}' for report {report_id} was completed by {current_user.full_name or current_user.username}.",
            report_id=report_id,
            created_at=now
        ))

    return AssignedActionResponse(
        action_id=target_action.action_id,
        report_id=report.report_id,
        description=target_action.description,
        assigned_to=target_action.assigned_to,
        status=target_action.status,
        due_date=target_action.due_date,
        completed_at=target_action.completed_at,
        created_at=target_action.created_at,
        report_description=report.description,
        location=report.location,
        department=report.department
    )
