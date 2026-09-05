from fastapi import APIRouter, Depends
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.pattern import PatternAnalysisResult
from app.services.dashboard_service import DashboardService
from app.services.pattern_service import PatternService
from app.integrations.pattern_adapter import PatternAdapter
from app.database.connection import get_database
from app.database.repositories.report_repository import ReportRepository
from app.auth.dependencies import get_current_user
from app.models.user import UserModel

router = APIRouter(prefix="/dashboard", tags=["HSE Dashboard & Analytics"])


def get_dashboard_service(db=Depends(get_database)) -> DashboardService:
    repo = ReportRepository(db)
    return DashboardService(repo)


def get_pattern_service(db=Depends(get_database)) -> PatternService:
    repo = ReportRepository(db)
    adapter = PatternAdapter()
    return PatternService(repo, adapter)


@router.get("/summary", response_model=DashboardSummaryResponse, summary="Get Dashboard Overview Summary")
async def get_summary(
    current_user: UserModel = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    return await service.get_summary()


@router.get("/trends", summary="Get SIF Precursor Trends")
async def get_trends(
    current_user: UserModel = Depends(get_current_user),
    pattern_service: PatternService = Depends(get_pattern_service)
):
    result = await pattern_service.get_pattern_analysis()
    return {"sif_trends": result.sif_trends}


@router.get("/patterns", response_model=PatternAnalysisResult, summary="Get Deep Pattern Analysis")
async def get_patterns(
    current_user: UserModel = Depends(get_current_user),
    pattern_service: PatternService = Depends(get_pattern_service)
):
    return await pattern_service.get_pattern_analysis()
