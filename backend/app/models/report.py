from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    UNSAFE_ACT = "UNSAFE_ACT"
    UNSAFE_CONDITION = "UNSAFE_CONDITION"
    NEAR_MISS = "NEAR_MISS"


class ReportStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    AI_ANALYZED = "AI_ANALYZED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    ACTION_ASSIGNED = "ACTION_ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"


class SIFRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class ActionItemModel(BaseModel):
    action_id: str
    description: str
    assigned_to: Optional[str] = None
    status: ActionStatus = ActionStatus.PENDING
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class AIAnalysisModel(BaseModel):
    sif_precursor: bool = False
    confidence: float = 0.0
    hazard_category: str = "UNKNOWN"
    unsafe_act: Optional[str] = None
    unsafe_condition: Optional[str] = None
    severity: int = 1
    evidence: List[str] = Field(default_factory=list)
    model_source: str = "FALLBACK"
    raw_prediction: Optional[bool] = None
    raw_confidence: Optional[float] = None
    context_type: str = "UNKNOWN"
    context_adjustment_reason: Optional[str] = None
    training_familiarity: float = 1.0
    is_novel: bool = False


class RiskAssessmentModel(BaseModel):
    score: int = 1
    level: SIFRiskLevel = SIFRiskLevel.LOW
    likelihood: int = 1
    severity: int = 1


class LifeSavingRuleModel(BaseModel):
    rule_id: str = "RULE_NONE"
    rule_name: str = "None Applicable"
    description: str = "No mandatory Life-Saving Rule breach detected."


class RecommendationsModel(BaseModel):
    immediate_actions: List[str] = Field(default_factory=list)
    preventive_actions: List[str] = Field(default_factory=list)
    verification_actions: List[str] = Field(default_factory=list)


class PatternDataModel(BaseModel):
    sif_potential: bool = False
    confidence: float = 0.0
    activity: str = ""
    location: str = ""
    barrier_failure: str = ""
    precursor_patterns: List[str] = Field(default_factory=list)
    hazard_pattern: Optional[str] = None
    location_pattern: Optional[str] = None
    department_pattern: Optional[str] = None


class ReportModel(BaseModel):
    report_id: str
    report_type: ReportType
    description: str
    location: str
    department: str
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    status: ReportStatus = ReportStatus.SUBMITTED

    analysis: Optional[AIAnalysisModel] = None
    risk: Optional[RiskAssessmentModel] = None
    life_saving_rule: Optional[LifeSavingRuleModel] = None
    recommendations: Optional[RecommendationsModel] = None
    pattern_data: Optional[PatternDataModel] = None
    actions: List[ActionItemModel] = Field(default_factory=list)
