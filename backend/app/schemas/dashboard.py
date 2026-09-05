from typing import List, Dict, Any
from pydantic import BaseModel
from app.schemas.pattern import CategoryCount, TrendPoint


class RiskBreakdown(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class ActionMetrics(BaseModel):
    open_actions: int = 0
    in_progress_actions: int = 0
    resolved_actions: int = 0


class DashboardSummaryResponse(BaseModel):
    total_reports: int
    sif_precursor_count: int
    sif_precursor_percentage: float
    risk_breakdown: RiskBreakdown
    actions: ActionMetrics
    reports_by_type: Dict[str, int]
    reports_by_department: List[CategoryCount]
    reports_by_location: List[CategoryCount]
