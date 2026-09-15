from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.report import SIFRiskLevel


class ReviewModel(BaseModel):
    review_id: str
    report_id: str
    officer_id: str
    officer_name: str
    decision: str  # ACCEPT, REJECT, CORRECT
    raw_prediction: Optional[bool] = None
    raw_confidence: Optional[float] = None
    corrected_sif: Optional[bool] = None
    corrected_risk: Optional[SIFRiskLevel] = None
    corrected_hazard: Optional[str] = None
    corrected_unsafe_act: Optional[str] = None
    corrected_unsafe_condition: Optional[str] = None
    correction_reason: Optional[str] = None
    created_at: datetime
