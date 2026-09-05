from app.database.repositories.report_repository import ReportRepository
from app.integrations.pattern_adapter import PatternAdapter
from app.schemas.pattern import PatternAnalysisResult


class PatternService:
    def __init__(self, report_repo: ReportRepository, pattern_adapter: PatternAdapter):
        self.report_repo = report_repo
        self.pattern_adapter = pattern_adapter

    async def get_pattern_analysis(self) -> PatternAnalysisResult:
        reports = await self.report_repo.get_all_reports_for_analytics()
        return self.pattern_adapter.detect_patterns(reports)
