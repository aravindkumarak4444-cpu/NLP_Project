import logging
from typing import Optional, List, Tuple
from fastapi import status
from app.database.repositories.report_repository import ReportRepository
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportStatusUpdate,
    ReportResponse,
    ReportListResponse,
    ActionItemCreate,
    ActionItemUpdate
)
from app.models.report import (
    ReportModel,
    ReportStatus,
    SIFRiskLevel,
    ReportType,
    ActionItemModel,
    ActionStatus
)
from app.models.user import UserModel
from app.utils.ids import generate_report_id, generate_action_id
from app.utils.timestamps import utc_now
from app.middleware.error_handler import APIException

logger = logging.getLogger("sif_backend")


class ReportService:
    # Allowed lifecycle status transitions
    ALLOWED_TRANSITIONS = {
        ReportStatus.SUBMITTED: [ReportStatus.AI_ANALYZED, ReportStatus.CLOSED],
        ReportStatus.AI_ANALYZED: [ReportStatus.REVIEW_REQUIRED, ReportStatus.ACTION_ASSIGNED, ReportStatus.RESOLVED, ReportStatus.CLOSED],
        ReportStatus.REVIEW_REQUIRED: [ReportStatus.ACTION_ASSIGNED, ReportStatus.RESOLVED, ReportStatus.CLOSED],
        ReportStatus.ACTION_ASSIGNED: [ReportStatus.IN_PROGRESS, ReportStatus.RESOLVED, ReportStatus.CLOSED],
        ReportStatus.IN_PROGRESS: [ReportStatus.RESOLVED],
        ReportStatus.RESOLVED: [ReportStatus.VERIFIED, ReportStatus.IN_PROGRESS],
        ReportStatus.VERIFIED: [ReportStatus.CLOSED],
        ReportStatus.CLOSED: []
    }

    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    async def create_report(self, report_in: ReportCreate, user: UserModel) -> ReportResponse:
        report_id = generate_report_id(prefix="NM" if report_in.report_type == ReportType.NEAR_MISS else "REP")
        now = utc_now()

        model = ReportModel(
            report_id=report_id,
            report_type=report_in.report_type,
            description=report_in.description,
            location=report_in.location,
            department=report_in.department,
            submitted_by=user.email,
            created_at=now,
            updated_at=now,
            status=ReportStatus.SUBMITTED
        )

        saved = await self.report_repo.create_report(model)
        logger.info(f"Created safety report: {saved.report_id} by {user.email}")
        return ReportResponse(**saved.model_dump())

    async def get_report_by_id(self, report_id: str) -> ReportResponse:
        report = await self.report_repo.find_by_id(report_id)
        if not report:
            raise APIException(
                code="REPORT_NOT_FOUND",
                message=f"Safety report with ID '{report_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return ReportResponse(**report.model_dump())

    async def update_report(self, report_id: str, update_in: ReportUpdate, user: UserModel) -> ReportResponse:
        existing = await self.report_repo.find_by_id(report_id)
        if not existing:
            raise APIException(
                code="REPORT_NOT_FOUND",
                message=f"Safety report with ID '{report_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        update_data = {k: v for k, v in update_in.model_dump(exclude_unset=True).items() if v is not None}
        if not update_data:
            return ReportResponse(**existing.model_dump())

        update_data["updated_at"] = utc_now()
        updated = await self.report_repo.update_report(report_id, update_data)
        return ReportResponse(**updated.model_dump())

    async def update_report_status(self, report_id: str, status_in: ReportStatusUpdate, user: UserModel) -> ReportResponse:
        existing = await self.report_repo.find_by_id(report_id)
        if not existing:
            raise APIException(
                code="REPORT_NOT_FOUND",
                message=f"Safety report with ID '{report_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        current_status = existing.status
        new_status = status_in.status

        if current_status == new_status:
            return ReportResponse(**existing.model_dump())

        allowed = self.ALLOWED_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise APIException(
                code="INVALID_STATUS_TRANSITION",
                message=f"Cannot transition report status from '{current_status.value}' to '{new_status.value}'. Allowed next statuses: {[s.value for s in allowed]}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        update_data = {
            "status": new_status,
            "updated_at": utc_now()
        }
        updated = await self.report_repo.update_report(report_id, update_data)
        logger.info(f"Report '{report_id}' status updated to '{new_status.value}' by {user.email}")
        return ReportResponse(**updated.model_dump())

    async def add_action_item(self, report_id: str, action_in: ActionItemCreate, user: UserModel) -> ReportResponse:
        existing = await self.report_repo.find_by_id(report_id)
        if not existing:
            raise APIException(
                code="REPORT_NOT_FOUND",
                message=f"Safety report with ID '{report_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        now = utc_now()
        new_action = ActionItemModel(
            action_id=generate_action_id(),
            description=action_in.description,
            assigned_to=action_in.assigned_to,
            status=ActionStatus.PENDING,
            due_date=action_in.due_date,
            created_at=now
        )

        actions = existing.actions or []
        actions.append(new_action)

        new_status = existing.status
        if existing.status in [ReportStatus.SUBMITTED, ReportStatus.AI_ANALYZED, ReportStatus.REVIEW_REQUIRED]:
            new_status = ReportStatus.ACTION_ASSIGNED

        update_data = {
            "actions": [a.model_dump() for a in actions],
            "status": new_status,
            "updated_at": now
        }

        updated = await self.report_repo.update_report(report_id, update_data)
        return ReportResponse(**updated.model_dump())

    async def list_reports(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[ReportStatus] = None,
        report_type: Optional[ReportType] = None,
        risk_level: Optional[SIFRiskLevel] = None,
        sif_precursor: Optional[bool] = None,
        department: Optional[str] = None,
        location: Optional[str] = None,
        search: Optional[str] = None
    ) -> ReportListResponse:
        page = max(1, page)
        limit = max(1, min(100, limit))

        items, total = await self.report_repo.list_reports(
            page=page,
            limit=limit,
            status=status,
            report_type=report_type,
            risk_level=risk_level,
            sif_precursor=sif_precursor,
            department=department,
            location=location,
            search=search
        )

        total_pages = (total + limit - 1) // limit if total > 0 else 0

        responses = [ReportResponse(**m.model_dump()) for m in items]
        return ReportListResponse(
            items=responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def delete_report(self, report_id: str, user: UserModel) -> bool:
        existing = await self.report_repo.find_by_id(report_id)
        if not existing:
            raise APIException(
                code="REPORT_NOT_FOUND",
                message=f"Safety report with ID '{report_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        success = await self.report_repo.delete_report(report_id)
        logger.info(f"Deleted report '{report_id}' by {user.email}")
        return success
