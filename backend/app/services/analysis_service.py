import logging
from fastapi import status
from app.database.repositories.report_repository import ReportRepository
from app.integrations.ai_adapter import AIAdapter
from app.integrations.rule_adapter import RuleAdapter
from app.services.risk_service import RiskService
from app.services.recommendation_service import RecommendationService
from app.schemas.analysis import AnalysisResponse
from app.models.report import ReportStatus, PatternDataModel
from app.models.user import UserModel
from app.utils.timestamps import utc_now
from app.middleware.error_handler import APIException

logger = logging.getLogger("sif_backend")


class AnalysisService:
    def __init__(
        self,
        report_repo: ReportRepository,
        ai_adapter: AIAdapter,
        rule_adapter: RuleAdapter,
        risk_service: RiskService,
        recommendation_service: RecommendationService
    ):
        self.report_repo = report_repo
        self.ai_adapter = ai_adapter
        self.rule_adapter = rule_adapter
        self.risk_service = risk_service
        self.recommendation_service = recommendation_service

    async def analyze_report(self, report_id: str, user: UserModel) -> AnalysisResponse:
        report = await self.report_repo.find_by_id(report_id)
        if not report:
            raise APIException(
                code="REPORT_NOT_FOUND",
                message=f"Safety report with ID '{report_id}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        logger.info(f"Initiating AI/NLP Analysis Pipeline for report '{report_id}'...")

        # 1. AI Analysis
        try:
            ai_result = self.ai_adapter.analyze(report.description)
        except Exception as e:
            logger.error(f"AI Adapter execution failed for report '{report_id}': {str(e)}", exc_info=True)
            # Create graceful fallback AI result on complete failure
            from app.models.report import AIAnalysisModel
            ai_result = AIAnalysisModel(
                sif_precursor=False,
                confidence=0.0,
                hazard_category="UNCLASSIFIED",
                severity=2,
                evidence=[f"AI Service Execution Warning: {str(e)}"]
            )

        # 2. Life-Saving Rule Mapping
        rule_result = self.rule_adapter.map_rule(
            hazard_category=ai_result.hazard_category,
            unsafe_act=ai_result.unsafe_act,
            unsafe_condition=ai_result.unsafe_condition
        )

        # 3. SIF Risk Assessment
        risk_result = self.risk_service.calculate_risk(ai_result)

        # 4. Recommendation Generation
        recommendations_result = self.recommendation_service.generate_recommendations(
            ai_analysis=ai_result,
            risk_level=risk_result.level
        )

        # 5. Pattern Data setup
        pattern_data = PatternDataModel(
            hazard_pattern=ai_result.hazard_category,
            location_pattern=report.location,
            department_pattern=report.department
        )

        # 6. Save complete analysis into report document & update status
        update_dict = {
            "analysis": ai_result.model_dump(),
            "risk": risk_result.model_dump(),
            "life_saving_rule": rule_result.model_dump(),
            "recommendations": recommendations_result.model_dump(),
            "pattern_data": pattern_data.model_dump(),
            "status": ReportStatus.AI_ANALYZED if report.status == ReportStatus.SUBMITTED else report.status,
            "updated_at": utc_now()
        }

        updated_report = await self.report_repo.update_report(report_id, update_dict)
        logger.info(f"Analysis Pipeline completed for report '{report_id}'. SIF Precursor={ai_result.sif_precursor}, Risk Level={risk_result.level}")

        return AnalysisResponse(
            report_id=report_id,
            analysis=ai_result,
            risk=risk_result,
            life_saving_rule=rule_result,
            recommendations=recommendations_result,
            status="COMPLETED"
        )
