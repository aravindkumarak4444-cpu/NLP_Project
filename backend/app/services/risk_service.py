import logging
from typing import Tuple
from app.models.report import SIFRiskLevel, RiskAssessmentModel, AIAnalysisModel

logger = logging.getLogger("sif_backend")


class RiskService:
    """
    Risk Assessment Engine for SIF Precursors.
    
    Decouples AI Model Confidence from SIF Risk Assessment.
    Uses standard Oil & Gas 5x5 Risk Matrix Methodology:
    Risk Score = Severity (1-5) * Likelihood (1-5)
    
    Risk Levels:
    - LOW: Score 1 - 4
    - MEDIUM: Score 5 - 9
    - HIGH: Score 10 - 15
    - CRITICAL: Score 16 - 25
    """

    def calculate_risk(
        self,
        ai_analysis: AIAnalysisModel,
        likelihood_override: int = None
    ) -> RiskAssessmentModel:
        severity = ai_analysis.severity if ai_analysis.severity is not None else 2

        # Override severity and likelihood for compliant / prevented reports
        ctx_type = getattr(ai_analysis, "context_type", "UNKNOWN")
        if ctx_type in ["SAFE_COMPLIANCE", "PREVENTED_EVENT"]:
            severity = min(severity, 2)
            likelihood = 1
        elif likelihood_override and 1 <= likelihood_override <= 5:
            likelihood = likelihood_override
        else:
            if ai_analysis.sif_precursor:
                likelihood = 4 if severity >= 4 else 3
            else:
                likelihood = 2 if severity >= 3 else 1

        # Enforce range limits [1..5]
        severity = max(1, min(5, severity))
        likelihood = max(1, min(5, likelihood))

        risk_score = severity * likelihood

        # Map to Risk Level
        if risk_score >= 16:
            level = SIFRiskLevel.CRITICAL
        elif risk_score >= 10:
            level = SIFRiskLevel.HIGH
        elif risk_score >= 5:
            level = SIFRiskLevel.MEDIUM
        else:
            level = SIFRiskLevel.LOW

        logger.info(f"Calculated Risk: Severity={severity}, Likelihood={likelihood}, Score={risk_score}, Level={level}")

        return RiskAssessmentModel(
            score=risk_score,
            level=level,
            likelihood=likelihood,
            severity=severity
        )

