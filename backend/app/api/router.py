from fastapi import APIRouter
from app.api.routes import auth, reports, analysis, dashboard, rules, patterns, health

api_router = APIRouter(prefix="/api/v1")

# Include business endpoints under /api/v1
api_router.include_router(auth.router)
api_router.include_router(reports.router)
api_router.include_router(analysis.router)
api_router.include_router(dashboard.router)
api_router.include_router(rules.router)
api_router.include_router(patterns.router)

# Health router directly accessible at /health as well as /api/v1/health
root_router = APIRouter()
root_router.include_router(health.router)
root_router.include_router(api_router)
