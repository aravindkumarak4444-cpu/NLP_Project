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


async def seed_initial_users():
    try:
        from app.database.connection import db_manager
        if db_manager.db is None:
            return
        from app.database.repositories.user_repository import UserRepository
        from app.services.auth_service import AuthService
        from app.schemas.user import UserCreate
        from app.models.user import UserRole
        from app.auth.password import hash_password, verify_password

        repo = UserRepository(db_manager.db)
        auth_service = AuthService(repo)

        test_user = await repo.find_by_email("test@example.com")
        if not test_user:
            try:
                await auth_service.register_user(UserCreate(
                    username="testuser",
                    email="test@example.com",
                    password="Test@12345",
                    full_name="Test User",
                    role=UserRole.SAFETY_OFFICER,
                    department="HSE Department"
                ))
                logger.info("Seeded default test user account: testuser (test@example.com)")
            except Exception as e:
                logger.debug(f"Test user seed skipped: {e}")
        else:
            if not verify_password("Test@12345", test_user.hashed_password):
                await repo.update_user(test_user.user_id, {"hashed_password": hash_password("Test@12345")})
                logger.info("Updated testuser password to match default credentials")

        admin_user = await repo.find_by_email("admin@oil.in")
        if not admin_user:
            try:
                await auth_service.register_user(UserCreate(
                    username="admin",
                    email="admin@oil.in",
                    password="password123",
                    full_name="HSE Administrator",
                    role=UserRole.ADMIN,
                    department="Safety Management"
                ))
                logger.info("Seeded default admin user account: admin (admin@oil.in)")
            except Exception as e:
                logger.debug(f"Admin user seed skipped: {e}")
        else:
            if not verify_password("password123", admin_user.hashed_password):
                await repo.update_user(admin_user.user_id, {"hashed_password": hash_password("password123")})
                logger.info("Updated admin password to match default credentials")
    except Exception as e:
        logger.warning(f"Initial user seeding skipped: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application Startup and Shutdown Lifecycle."""
    logger.info("Initializing FastAPI Backend for OIL SIF Precursor Detection...")
    await connect_to_mongo()
    await seed_initial_users()
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
origins = settings.FRONTEND_URL if isinstance(settings.FRONTEND_URL, list) else [str(settings.FRONTEND_URL)]
default_origins = [
    "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174",
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://10.218.117.130:5173", "http://10.218.117.130:5174", "http://10.218.117.130:3000"
]
for orig in default_origins:
    if orig not in origins:
        origins.append(orig)


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
