from fastapi import APIRouter, Depends
from app.schemas.pattern import PatternAnalysisResult
from app.services.pattern_service import PatternService
from app.integrations.pattern_adapter import PatternAdapter
from app.database.connection import get_database
from app.database.repositories.report_repository import ReportRepository
from app.auth.dependencies import get_current_user
from app.models.user import UserModel

router = APIRouter(prefix="/patterns", tags=["Pattern Detection"])


def get_pattern_service(db=Depends(get_database)) -> PatternService:
    repo = ReportRepository(db)
    adapter = PatternAdapter()
    return PatternService(repo, adapter)


@router.get("", response_model=PatternAnalysisResult, summary="Get Incident Pattern Analysis")
async def get_patterns(
    current_user: UserModel = Depends(get_current_user),
    service: PatternService = Depends(get_pattern_service)
):
    return await service.get_pattern_analysis()
