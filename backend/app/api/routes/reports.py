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


@router.post("/{report_id}/actions", response_model=ReportResponse, summary="Add Corrective Action Item")
async def add_action_item(
    report_id: str,
    action_in: ActionItemCreate,
    current_user: UserModel = Depends(require_roles([UserRole.SAFETY_OFFICER, UserRole.MANAGER, UserRole.ADMIN])),
    service: ReportService = Depends(get_report_service)
):
    return await service.add_action_item(report_id, action_in, current_user)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Safety Report")
async def delete_report(
    report_id: str,
    current_user: UserModel = Depends(require_roles([UserRole.ADMIN])),
    service: ReportService = Depends(get_report_service)
):
    await service.delete_report(report_id, current_user)
    return None
