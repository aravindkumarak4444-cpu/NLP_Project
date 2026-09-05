from collections import Counter
from typing import List, Dict, Any
from app.database.repositories.report_repository import ReportRepository
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    RiskBreakdown,
    ActionMetrics,
)
from app.schemas.pattern import CategoryCount
from app.models.report import SIFRiskLevel, ActionStatus, ReportStatus


class DashboardService:
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    async def get_summary(self) -> DashboardSummaryResponse:
        reports = await self.report_repo.get_all_reports_for_analytics()

        total = len(reports)
        sif_count = 0

        risk_cnt = {
            SIFRiskLevel.LOW: 0,
            SIFRiskLevel.MEDIUM: 0,
            SIFRiskLevel.HIGH: 0,
            SIFRiskLevel.CRITICAL: 0
        }

        open_actions = 0
        in_prog_actions = 0
        resolved_actions = 0

        type_counter = Counter()
        dept_counter = Counter()
        loc_counter = Counter()

        for r in reports:
            type_counter[r.report_type.value] += 1
            dept_counter[r.department] += 1
            loc_counter[r.location] += 1

            if r.analysis and r.analysis.sif_precursor:
                sif_count += 1

            if r.risk and r.risk.level:
                risk_cnt[r.risk.level] += 1

            if r.actions:
                for act in r.actions:
                    if act.status == ActionStatus.PENDING:
                        open_actions += 1
                    elif act.status == ActionStatus.IN_PROGRESS:
                        in_prog_actions += 1
                    elif act.status == ActionStatus.COMPLETED:
                        resolved_actions += 1

        sif_pct = round((sif_count / total * 100.0), 1) if total > 0 else 0.0

        def to_cat_list(counter: Counter, limit: int = 5) -> List[CategoryCount]:
            return [CategoryCount(name=k, count=v) for k, v in counter.most_common(limit)]

        return DashboardSummaryResponse(
            total_reports=total,
            sif_precursor_count=sif_count,
            sif_precursor_percentage=sif_pct,
            risk_breakdown=RiskBreakdown(
                low=risk_cnt[SIFRiskLevel.LOW],
                medium=risk_cnt[SIFRiskLevel.MEDIUM],
                high=risk_cnt[SIFRiskLevel.HIGH],
                critical=risk_cnt[SIFRiskLevel.CRITICAL]
            ),
            actions=ActionMetrics(
                open_actions=open_actions,
                in_progress_actions=in_prog_actions,
                resolved_actions=resolved_actions
            ),
            reports_by_type=dict(type_counter),
            reports_by_department=to_cat_list(dept_counter),
            reports_by_location=to_cat_list(loc_counter)
        )
