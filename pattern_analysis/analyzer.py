import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR.parent / "data" / "sif_precursor.db"


ACTIVITY_KEYWORDS = {
    "Working at Height": [
        "working at height",
        "work at height",
        "height work",
        "scaffolding",
        "ladder",
    ],
    "Confined Space": [
        "confined space",
        "tank entry",
        "vessel entry",
        "manhole entry",
    ],
    "Lifting": [
        "lifting",
        "crane",
        "hoisting",
        "suspended load",
    ],
    "Hot Work": [
        "hot work",
        "welding",
        "cutting",
        "grinding",
    ],
    "Driving": [
        "driving",
        "vehicle",
        "road accident",
        "transport",
    ],
    "Excavation": [
        "excavation",
        "trenching",
        "trench",
    ],
}


LOCATION_KEYWORDS = {
    "Plant": [
        "plant",
        "refinery",
        "process plant",
    ],
    "Construction Site": [
        "construction site",
        "construction area",
    ],
    "Workshop": [
        "workshop",
        "maintenance shop",
    ],
    "Warehouse": [
        "warehouse",
        "storage area",
    ],
    "Offshore": [
        "offshore",
        "platform",
        "rig",
    ],
    "Road": [
        "road",
        "highway",
        "transport route",
    ],
}


BARRIER_KEYWORDS = {
    "PPE Failure": [
        "no ppe",
        "without ppe",
        "ppe not used",
        "ppe failure",
        "missing helmet",
        "missing harness",
    ],
    "Gas Monitoring Failure": [
        "gas monitor failed",
        "gas monitoring failure",
        "gas detector failed",
        "no gas monitoring",
    ],
    "Permit Failure": [
        "permit failure",
        "without permit",
        "permit not available",
        "permit violation",
    ],
    "Isolation Failure": [
        "isolation failure",
        "failed isolation",
        "isolation not done",
        "lockout failure",
    ],
    "Fall Protection Failure": [
        "no fall protection",
        "fall protection failure",
        "guardrail missing",
        "unguarded edge",
    ],
    "Procedure Failure": [
        "procedure not followed",
        "procedure failure",
        "unsafe procedure",
        "procedure violation",
    ],
}


NULL_VALUES = {
    "",
    "null",
    "none",
    "nan",
    "n/a",
    "na",
    "unknown",
    "-",
}


def _clean(value):
    """Clean missing values and extra spaces."""
    if value is None:
        return ""

    value = str(value).strip()

    if value.lower() in NULL_VALUES:
        return ""

    return re.sub(r"\s+", " ", value)


def _contains(text, keyword):
    return keyword.lower() in text.lower()


def _first_match(text, keyword_map):
    """Return the first matching category."""
    for category, keywords in keyword_map.items():
        for keyword in keywords:
            if _contains(text, keyword):
                return category

    return ""


def _all_matches(text, keyword_map):
    """Return all matching categories."""
    matches = []

    for category, keywords in keyword_map.items():
        for keyword in keywords:
            if _contains(text, keyword):
                matches.append(category)
                break

    return matches


def get_connection(db_path=None):
    """Create a SQLite connection."""
    db_path = Path(db_path or DEFAULT_DB_PATH)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row

    return connection


def init_db(db_path=None):
    """Create the pattern_analysis table."""
    connection = get_connection(db_path)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS pattern_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT,
            report_text TEXT NOT NULL,
            sif_potential INTEGER NOT NULL,
            confidence REAL NOT NULL,
            activity TEXT,
            location TEXT,
            barrier_failure TEXT,
            precursor_patterns TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pattern_report_id
        ON pattern_analysis(report_id)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pattern_sif
        ON pattern_analysis(sif_potential)
        """
    )

    connection.commit()
    connection.close()


def analyse_report(report_text):
    """
    Analyse a safety report and identify possible SIF precursor patterns.

    This is a baseline rule-based analyser.
    """

    text = _clean(report_text)

    if not text:
        return {
            "status": "empty_report",
            "sif_potential": False,
            "confidence": 0.0,
            "activity": "",
            "location": "",
            "barrier_failure": "",
            "precursor_patterns": [],
        }

    activities = _all_matches(text, ACTIVITY_KEYWORDS)
    locations = _all_matches(text, LOCATION_KEYWORDS)
    barriers = _all_matches(text, BARRIER_KEYWORDS)

    confidence = 0.20

    if activities:
        confidence += 0.15

    if barriers:
        confidence += min(0.45, 0.20 * len(barriers))

    high_risk_activities = {
        "Working at Height",
        "Confined Space",
        "Lifting",
    }

    if any(activity in high_risk_activities for activity in activities):
        confidence += 0.20

    confidence = min(confidence, 0.99)

    precursor_patterns = []

    for activity in activities:
        precursor_patterns.append(
            f"Activity: {activity}"
        )

    for barrier in barriers:
        precursor_patterns.append(
            f"Barrier Failure: {barrier}"
        )

    for location in locations:
        precursor_patterns.append(
            f"Location: {location}"
        )

    return {
        "status": "analysed",
        "sif_potential": confidence >= 0.50,
        "confidence": round(confidence, 2),
        "activity": activities[0] if activities else "",
        "location": locations[0] if locations else "",
        "barrier_failure": barriers[0] if barriers else "",
        "precursor_patterns": precursor_patterns,
    }


def analyse_and_store_report(
    report_text,
    report_id=None,
    db_path=None,
):
    """Analyse a report and store the result in SQLite."""

    result = analyse_report(report_text)

    if result["status"] == "empty_report":
        return {
            "stored": False,
            **result,
        }

    init_db(db_path)

    connection = get_connection(db_path)

    cursor = connection.execute(
        """
        INSERT INTO pattern_analysis (
            report_id,
            report_text,
            sif_potential,
            confidence,
            activity,
            location,
            barrier_failure,
            precursor_patterns,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _clean(report_id),
            _clean(report_text),
            int(result["sif_potential"]),
            result["confidence"],
            result["activity"],
            result["location"],
            result["barrier_failure"],
            json.dumps(result["precursor_patterns"]),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    connection.commit()

    analysis_id = cursor.lastrowid

    connection.close()

    return {
        "stored": True,
        "analysis_id": analysis_id,
        **result,
    }


def _row_to_dict(row):
    """Convert SQLite row into a normal Python dictionary."""

    if row is None:
        return None

    result = dict(row)

    result["sif_potential"] = bool(result["sif_potential"])

    try:
        result["precursor_patterns"] = json.loads(
            result["precursor_patterns"]
        )
    except (TypeError, json.JSONDecodeError):
        result["precursor_patterns"] = []

    return result


def get_analysis_by_id(analysis_id, db_path=None):
    """Get one analysis result from SQLite."""

    init_db(db_path)

    connection = get_connection(db_path)

    row = connection.execute(
        """
        SELECT *
        FROM pattern_analysis
        WHERE id = ?
        """,
        (analysis_id,),
    ).fetchone()

    connection.close()

    return _row_to_dict(row)


def get_all_analyses(db_path=None):
    """Get all analysis results."""

    init_db(db_path)

    connection = get_connection(db_path)

    rows = connection.execute(
        """
        SELECT *
        FROM pattern_analysis
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [_row_to_dict(row) for row in rows]


if __name__ == "__main__":

    init_db()

    sample_report = """
    Worker was working at height on a plant structure.
    No fall protection was used and the required permit was not available.
    """

    result = analyse_and_store_report(
        sample_report,
        report_id="SIF-DEMO-001",
    )

    print(json.dumps(result, indent=4))

    print("\nAll stored analyses:")

    print(
        json.dumps(
            get_all_analyses(),
            indent=4,
        )
    )