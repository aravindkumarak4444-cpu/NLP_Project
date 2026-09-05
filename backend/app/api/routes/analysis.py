from fastapi import APIRouter, Depends, status
from app.schemas.analysis import AnalysisResponse, AIStatusResponse
from app.services.analysis_service import AnalysisService
from app.database.connection import get_database
from app.database.repositories.report_repository import ReportRepository
from app.integrations.ai_adapter import AIAdapter
from app.integrations.rule_adapter import RuleAdapter
from app.services.risk_service import RiskService
from app.services.recommendation_service import RecommendationService
from app.auth.dependencies import get_current_user
from app.models.user import UserModel

router = APIRouter(prefix="/analysis", tags=["AI Analysis Pipeline"])


def get_analysis_service(db=Depends(get_database)) -> AnalysisService:
    report_repo = ReportRepository(db)
    ai_adapter = AIAdapter()
    rule_adapter = RuleAdapter()
    risk_service = RiskService()
    recommendation_service = RecommendationService()
    return AnalysisService(
        report_repo=report_repo,
        ai_adapter=ai_adapter,
        rule_adapter=rule_adapter,
        risk_service=risk_service,
        recommendation_service=recommendation_service
    )


@router.get("/status", response_model=AIStatusResponse, summary="Get AI Engine & Model Status")
async def get_ai_status():
    """
    Returns current AI engine operational mode and model status:
    - REAL_MODEL (ml/models/model.pkl)
    - PREDICT_SCRIPT (ai_model/src/predict.py)
    - FALLBACK (Domain NLP baseline engine)
    """
    adapter = AIAdapter()
    return AIStatusResponse(**adapter.get_status())


@router.post("/{report_id}", response_model=AnalysisResponse, status_code=status.HTTP_200_OK, summary="Run AI/NLP Pipeline Analysis")
async def analyze_report(
    report_id: str,
    current_user: UserModel = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service)
):
    return await service.analyze_report(report_id, current_user)
