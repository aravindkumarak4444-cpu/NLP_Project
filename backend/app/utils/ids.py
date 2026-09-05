import uuid
from datetime import datetime, timezone


def generate_report_id(prefix: str = "NM") -> str:
    """Generates unique report ID format (e.g. NM-2026-8A3F1)."""
    year = datetime.now(timezone.utc).year
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{year}-{short_uuid}"


def generate_action_id() -> str:
    """Generates unique action ID (e.g. ACT-8A3F1B)."""
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"ACT-{short_uuid}"


def generate_user_id() -> str:
    """Generates unique user ID (e.g. USR-8A3F1B)."""
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"USR-{short_uuid}"


def generate_uuid() -> str:
    """Generates standard UUID string."""
    return str(uuid.uuid4())
