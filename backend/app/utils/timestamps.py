from datetime import datetime, timezone


def utc_now() -> datetime:
    """Returns current UTC datetime formatted correctly."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Returns current UTC ISO timestamp string."""
    return utc_now().isoformat()
