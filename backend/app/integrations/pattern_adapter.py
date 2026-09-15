import os
import sys
import logging
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
from app.models.report import ReportModel, PatternDataModel
from app.schemas.pattern import (
    PatternAnalysisResult,
    CategoryCount,
    TrendPoint,
    RepeatPattern
)

logger = logging.getLogger("sif_backend")

# Ensure pattern_analysis directory is on sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
pattern_dir = os.path.join(base_dir, "pattern_analysis")
if os.path.exists(pattern_dir) and pattern_dir not in sys.path:
    sys.path.insert(0, pattern_dir)

try:
    from analyzer import analyse_report, analyse_and_store_report, get_all_analyses
    MEMBER3_ANALYZER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Could not import Member 3 pattern analyzer: {str(e)}")
    MEMBER3_ANALYZER_AVAILABLE = False


class PatternAdapter:
    """
    Adapter interface connecting backend to Member 3's Pattern Analysis Engine.
    Executes report pattern analysis, stores in Member 3's SQLite DB, and returns normalized PatternDataModel.
    Also aggregates dataset-wide incident patterns for dashboard endpoints.
    """

    def analyze_single_report(
        self,
        report_text: str,
        report_id: Optional[str] = None,
        location: Optional[str] = None,
        department: Optional[str] = None
    ) -> PatternDataModel:
        """
        Invokes Member 3's analyzer to detect SIF precursor patterns for a report,
        stores the result in Member 3's SQLite DB, and returns a normalized PatternDataModel.
        """
        if MEMBER3_ANALYZER_AVAILABLE:
            try:
                res = analyse_and_store_report(
                    report_text=report_text,
                    report_id=report_id or "REPORT-UNKNOWN"
                )
                act = str(res.get("activity", ""))
                loc = str(res.get("location", location or ""))
                barr = str(res.get("barrier_failure", ""))
                patterns = list(res.get("precursor_patterns", []))
                sif_pot = bool(res.get("sif_potential", False))
                conf = float(res.get("confidence", 0.0))

                return PatternDataModel(
                    sif_potential=sif_pot,
                    confidence=conf,
                    activity=act,
                    location=loc,
                    barrier_failure=barr,
                    precursor_patterns=patterns,
                    hazard_pattern=act or "UNSPECIFIED",
                    location_pattern=loc or location,
                    department_pattern=department
                )
            except Exception as e:
                logger.error(f"Error executing Member 3 analyse_and_store_report: {str(e)}", exc_info=True)

        return PatternDataModel(
            sif_potential=False,
            confidence=0.0,
            activity="",
            location=location or "",
            barrier_failure="",
            precursor_patterns=[],
            hazard_pattern=None,
            location_pattern=location,
            department_pattern=department
        )

    def detect_patterns(self, reports: List[ReportModel]) -> PatternAnalysisResult:
        """
        Aggregates top hazards, unsafe acts, high-risk locations/departments,
        time-series SIF trends, and repeated incident patterns.
        """
        if not reports:
            # Check if Member 3's SQLite database has historical records
            if MEMBER3_ANALYZER_AVAILABLE:
                try:
                    sqlite_records = get_all_analyses()
                    if sqlite_records:
                        return self._aggregate_sqlite_records(sqlite_records)
                except Exception as e:
                    logger.warning(f"Failed to fetch SQLite records in detect_patterns: {str(e)}")

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

            if r.pattern_data:
                if r.pattern_data.activity:
                    hazards_counter[r.pattern_data.activity] += 1
                if r.pattern_data.location:
                    loc_counter[r.pattern_data.location] += 1

            if is_sif:
                loc_counter[r.location] += 1
                dept_counter[r.department] += 1

        def to_category_counts(counter: Counter, limit: int = 5) -> List[CategoryCount]:
            return [CategoryCount(name=k, count=v) for k, v in counter.most_common(limit)]

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

    def _aggregate_sqlite_records(self, sqlite_records: List[Dict[str, Any]]) -> PatternAnalysisResult:
        hazards_counter = Counter()
        loc_counter = Counter()
        barrier_counter = Counter()
        sif_count = 0

        for rec in sqlite_records:
            if rec.get("sif_potential"):
                sif_count += 1
            if rec.get("activity"):
                hazards_counter[rec["activity"]] += 1
            if rec.get("location"):
                loc_counter[rec["location"]] += 1
            if rec.get("barrier_failure"):
                barrier_counter[rec["barrier_failure"]] += 1

        def to_cat(counter: Counter, limit: int = 5) -> List[CategoryCount]:
            return [CategoryCount(name=k, count=v) for k, v in counter.most_common(limit)]

        return PatternAnalysisResult(
            top_hazards=to_cat(hazards_counter),
            top_unsafe_acts=[],
            top_unsafe_conditions=to_cat(barrier_counter),
            high_risk_locations=to_cat(loc_counter),
            high_risk_departments=[],
            sif_trends=[TrendPoint(period="CURRENT", total_reports=len(sqlite_records), sif_count=sif_count, sif_percentage=round((sif_count / len(sqlite_records)) * 100.0, 1) if sqlite_records else 0.0)],
            repeated_patterns=[]
        )
