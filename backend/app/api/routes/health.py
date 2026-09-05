import logging
from fastapi import APIRouter, Response, status
from app.database.connection import db_manager

logger = logging.getLogger("sif_backend")

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
async def health_check(response: Response):
    """
    System Health Check Endpoint.
    Verifies database connectivity and service readiness.
    """
    db_status = "unavailable"
    is_healthy = False

    if db_manager.client is not None and db_manager.db is not None:
        try:
            await db_manager.client.admin.command('ping')
            db_status = "connected"
            is_healthy = True
        except Exception as e:
            logger.warning(f"Database ping failed in health check: {str(e)}")
            db_status = "unavailable"

    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "degraded",
            "database": db_status
        }

    return {
        "status": "healthy",
        "database": db_status
    }
