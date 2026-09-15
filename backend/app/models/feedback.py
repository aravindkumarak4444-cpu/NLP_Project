from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.report import SIFRiskLevel


class FeedbackModel(BaseModel):
    feedback_id: str
    report_id: str
    report_text: str
    original_ai_prediction: Optional[bool] = None
    original_confidence: Optional[float] = None
    familiarity_score: float = 1.0
    safety_context: str = "UNKNOWN"
    officer_final_label: bool
    final_risk: SIFRiskLevel = SIFRiskLevel.LOW
    hazard_category: Optional[str] = None
    unsafe_act: Optional[str] = None
    unsafe_condition: Optional[str] = None
    review_reason: Optional[str] = None
    reviewed_by: str
    reviewed_at: datetime
    status: str = "PENDING_TRAINING"  # PENDING_TRAINING, APPROVED_FOR_TRAINING, REJECTED
