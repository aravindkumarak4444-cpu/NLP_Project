import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.api.router import root_router
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.middleware.error_handler import (
    APIException,
    custom_api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.middleware.rate_limit import RateLimitMiddleware

# Setup structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("sif_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application Startup and Shutdown Lifecycle."""
    logger.info("Initializing FastAPI Backend for OIL SIF Precursor Detection...")
    await connect_to_mongo()
    yield
    logger.info("Shutting down FastAPI Backend...")
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="Secure, Scalable AI/NLP Engine API for Serious Injury & Fatality (SIF) Precursor Detection in Oil & Gas Safety Reports.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
origins = settings.FRONTEND_URL if isinstance(settings.FRONTEND_URL, list) else [settings.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Rate Limit Middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

# Exception Handlers
app.add_exception_handler(APIException, custom_api_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register Routers
app.include_router(root_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
