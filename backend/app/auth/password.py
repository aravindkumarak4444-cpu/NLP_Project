import hashlib
import bcrypt
import logging

logger = logging.getLogger("sif_backend")


def _prepare_password(password: str) -> bytes:
    """
    Pre-hashes password with SHA-256 to handle arbitrary password lengths securely
    and avoid bcrypt 72-byte truncation issues.
    """
    digest = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return digest.encode('utf-8')


def hash_password(password: str) -> str:
    """Hashes plain text password using bcrypt."""
    prep = _prepare_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prep, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against stored bcrypt hash."""
    try:
        prep = _prepare_password(plain_password)
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(prep, hashed_bytes)
    except Exception as e:
        logger.error(f"Error verifying password hash: {str(e)}")
        return False
