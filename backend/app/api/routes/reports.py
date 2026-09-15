from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportStatusUpdate,
    ReportResponse,
    ReportListResponse,
    ActionItemCreate
)
from app.models.report import ReportStatus, ReportType, SIFRiskLevel
from app.models.user import UserModel, UserRole
from app.services.report_service import ReportService
from app.database.connection import get_database
from app.database.repositories.report_repository import ReportRepository
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/reports", tags=["Safety Reports"])


def get_report_service(db=Depends(get_database)) -> ReportService:
    repo = ReportRepository(db)
    return ReportService(repo)


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED, summary="Submit Safety Report")
async def create_report(
    report_in: ReportCreate,
    current_user: UserModel = Depends(get_current_user),
    service: ReportService = Depends(get_report_service)
):
    return await service.create_report(report_in, current_user)


@router.get("/my", response_model=ReportListResponse, summary="Get Reports Submitted by Current Worker")
async def list_my_reports(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserModel = Depends(get_current_user),
    service: ReportService = Depends(get_report_service)
):
    return await service.list_reports(
        page=page,
        limit=limit,
        submitted_by=current_user.email
    )


@router.get("", response_model=ReportListResponse, summary="List & Filter Safety Reports")
async def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ReportStatus] = Query(None, description="Filter by report status"),
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    risk_level: Optional[SIFRiskLevel] = Query(None, description="Filter by SIF risk level"),
    sif_precursor: Optional[bool] = Query(None, description="Filter by SIF precursor flag"),
    department: Optional[str] = Query(None, description="Filter by department"),
    location: Optional[str] = Query(None, description="Filter by location"),
    search: Optional[str] = Query(None, description="Search term in description/ID/location"),
    current_user: UserModel = Depends(get_current_user),
    service: ReportService = Depends(get_report_service)
):
    # Workers only see their own reports
    if current_user.role == UserRole.WORKER:
        return await service.list_reports(
            page=page,
            limit=limit,
            status=status,
            report_type=report_type,
            risk_level=risk_level,
            sif_precursor=sif_precursor,
            department=department,
            location=location,
            submitted_by=current_user.email,
            search=search
        )

    return await service.list_reports(
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


@router.get("/{report_id}", response_model=ReportResponse, summary="Get Safety Report Details")
async def get_report(
    report_id: str,
    current_user: UserModel = Depends(get_current_user),
    service: ReportService = Depends(get_report_service)
):
    return await service.get_report_by_id(report_id)


@router.put("/{report_id}", response_model=ReportResponse, summary="Update Safety Report")
async def update_report(
    report_id: str,
    update_in: ReportUpdate,
    current_user: UserModel = Depends(get_current_user),
    service: ReportService = Depends(get_report_service)
):
    return await service.update_report(report_id, update_in, current_user)


@router.patch("/{report_id}/status", response_model=ReportResponse, summary="Update Report Status Lifecycle")
async def update_status(
    report_id: str,
    status_in: ReportStatusUpdate,
    current_user: UserModel = Depends(require_roles([UserRole.SAFETY_OFFICER, UserRole.MANAGER, UserRole.ADMIN])),
    service: ReportService = Depends(get_report_service)
):
    return await service.update_report_status(report_id, status_in, current_user)


from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportStatusUpdate,
    ReportResponse,
    ReportListResponse,
    ActionItemCreate,
    ActionItemUpdate
)

@router.patch("/{report_id}/actions/{action_id}", response_model=ReportResponse, summary="Update Action Item Status")
async def update_action_item_status(
    report_id: str,
    action_id: str,
    action_update: ActionItemUpdate,
    current_user: UserModel = Depends(require_roles([UserRole.SAFETY_OFFICER, UserRole.MANAGER, UserRole.ADMIN])),
    service: ReportService = Depends(get_report_service)
):
    return await service.update_action_item(report_id, action_id, action_update, current_user)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Safety Report")
async def delete_report(
    report_id: str,
    current_user: UserModel = Depends(require_roles([UserRole.ADMIN])),
    service: ReportService = Depends(get_report_service)
):
    await service.delete_report(report_id, current_user)
    return None

