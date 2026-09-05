from typing import List, Dict, Any
from pydantic import BaseModel


class CategoryCount(BaseModel):
    name: str
    count: int


class TrendPoint(BaseModel):
    period: str
    total_reports: int
    sif_count: int
    sif_percentage: float


class RepeatPattern(BaseModel):
    pattern_type: str
    description: str
    affected_entity: str
    occurrence_count: int


class PatternAnalysisResult(BaseModel):
    top_hazards: List[CategoryCount]
    top_unsafe_acts: List[CategoryCount]
    top_unsafe_conditions: List[CategoryCount]
    high_risk_locations: List[CategoryCount]
    high_risk_departments: List[CategoryCount]
    sif_trends: List[TrendPoint]
    repeated_patterns: List[RepeatPattern]
