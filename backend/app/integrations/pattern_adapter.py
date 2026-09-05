import logging
from typing import List, Dict, Any
from collections import Counter, defaultdict
from datetime import datetime
from app.models.report import ReportModel
from app.schemas.pattern import (
    PatternAnalysisResult,
    CategoryCount,
    TrendPoint,
    RepeatPattern
)

logger = logging.getLogger("sif_backend")


class PatternAdapter:
    """
    Adapter interface connecting backend to Member 3's Pattern Analysis Engine.
    Aggregates top hazards, unsafe acts/conditions, high-risk locations/departments,
    time-series SIF precursor trends, and repeated incident patterns.
    """

    def detect_patterns(self, reports: List[ReportModel]) -> PatternAnalysisResult:
        if not reports:
            return PatternAnalysisResult(
                top_hazards=[],
                top_unsafe_acts=[],
                top_unsafe_conditions=[],
                high_risk_locations=[],
                high_risk_departments=[],
                sif_trends=[],
                repeated_patterns=[]
            )

        hazards_counter = Counter()
        acts_counter = Counter()
        conditions_counter = Counter()
        loc_counter = Counter()
        dept_counter = Counter()

        monthly_totals = defaultdict(int)
        monthly_sif = defaultdict(int)

        location_hazard_map = defaultdict(lambda: defaultdict(int))

        for r in reports:
            # Grouping by YYYY-MM period
            period = r.created_at.strftime("%Y-%m")
            monthly_totals[period] += 1

            is_sif = False
            if r.analysis:
                if r.analysis.sif_precursor:
                    is_sif = True
                    monthly_sif[period] += 1

                hazards_counter[r.analysis.hazard_category] += 1
                if r.analysis.unsafe_act:
                    acts_counter[r.analysis.unsafe_act] += 1
                if r.analysis.unsafe_condition:
                    conditions_counter[r.analysis.unsafe_condition] += 1

                location_hazard_map[r.location][r.analysis.hazard_category] += 1

            if is_sif:
                loc_counter[r.location] += 1
                dept_counter[r.department] += 1

        # Format Top categories
        def to_category_counts(counter: Counter, limit: int = 5) -> List[CategoryCount]:
            return [CategoryCount(name=k, count=v) for k, v in counter.most_common(limit)]

        # Format Trends
        trends: List[TrendPoint] = []
        for period in sorted(monthly_totals.keys()):
            total = monthly_totals[period]
            sif_cnt = monthly_sif[period]
            pct = round((sif_cnt / total) * 100.0, 1) if total > 0 else 0.0
            trends.append(TrendPoint(
                period=period,
                total_reports=total,
                sif_count=sif_cnt,
                sif_percentage=pct
            ))

        # Repeat pattern detection
        repeated: List[RepeatPattern] = []
        for loc, hz_map in location_hazard_map.items():
            for hz, cnt in hz_map.items():
                if cnt >= 2 and hz != "GENERAL_SAFETY":
                    repeated.append(RepeatPattern(
                        pattern_type="REPEATED_LOCATION_HAZARD",
                        description=f"Multiple incidents ({cnt}) involving {hz} reported at location {loc}.",
                        affected_entity=loc,
                        occurrence_count=cnt
                    ))

        return PatternAnalysisResult(
            top_hazards=to_category_counts(hazards_counter),
            top_unsafe_acts=to_category_counts(acts_counter),
            top_unsafe_conditions=to_category_counts(conditions_counter),
            high_risk_locations=to_category_counts(loc_counter),
            high_risk_departments=to_category_counts(dept_counter),
            sif_trends=trends,
            repeated_patterns=repeated
        )
