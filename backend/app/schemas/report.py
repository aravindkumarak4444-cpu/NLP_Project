from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.report import (
    ReportType,
    ReportStatus,
    SIFRiskLevel,
    ActionStatus,
    AIAnalysisModel,
    RiskAssessmentModel,
    LifeSavingRuleModel,
    RecommendationsModel,
    PatternDataModel,
    ActionItemModel
)


class ReportCreate(BaseModel):
    report_type: ReportType
    description: str = Field(..., min_length=10, max_length=5000)
    location: str = Field(..., min_length=2, max_length=200)
    department: str = Field(..., min_length=2, max_length=100)


class ReportUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    location: Optional[str] = Field(None, min_length=2, max_length=200)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    report_type: Optional[ReportType] = None


class ReportStatusUpdate(BaseModel):
    status: ReportStatus
    reason: Optional[str] = None


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=3, max_length=1000)
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None


class ActionItemUpdate(BaseModel):
    status: ActionStatus
    assigned_to: Optional[str] = None


class ReportResponse(BaseModel):
    report_id: str
    report_type: ReportType
    description: str
    location: str
    department: str
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    status: ReportStatus

    analysis: Optional[AIAnalysisModel] = None
    risk: Optional[RiskAssessmentModel] = None
    life_saving_rule: Optional[LifeSavingRuleModel] = None
    recommendations: Optional[RecommendationsModel] = None
    pattern_data: Optional[PatternDataModel] = None
    actions: List[ActionItemModel] = Field(default_factory=list)


class ReportListResponse(BaseModel):
    items: List[ReportResponse]
    total: int
    page: int
    limit: int
    total_pages: int
