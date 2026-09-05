from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.report import (
    AIAnalysisModel,
    RiskAssessmentModel,
    LifeSavingRuleModel,
    RecommendationsModel
)


class AnalysisResponse(BaseModel):
    report_id: str
    analysis: AIAnalysisModel
    risk: RiskAssessmentModel
    life_saving_rule: LifeSavingRuleModel
    recommendations: RecommendationsModel
    status: str = "COMPLETED"


class AIStatusResponse(BaseModel):
    mode: str
    model_loaded: bool
    model_path: Optional[str] = None
    reason: Optional[str] = None

