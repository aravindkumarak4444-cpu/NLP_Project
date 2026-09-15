from fastapi import APIRouter
from app.api.routes import (
    auth, reports, analysis, dashboard, rules, patterns, health, ml,
    notifications, reviews, feedback, audit, users, actions
)

api_router = APIRouter(prefix="/api/v1")

# Include business endpoints under /api/v1
api_router.include_router(auth.router)
api_router.include_router(reports.router)
api_router.include_router(analysis.router)
api_router.include_router(dashboard.router)
api_router.include_router(rules.router)
api_router.include_router(patterns.router)
api_router.include_router(ml.router)
api_router.include_router(notifications.router)
api_router.include_router(reviews.router)
api_router.include_router(feedback.router)
api_router.include_router(audit.router)
api_router.include_router(users.router)
api_router.include_router(actions.router)

# Health router directly accessible at /health as well as /api/v1/health
root_router = APIRouter()
root_router.include_router(health.router)
root_router.include_router(api_router)

