from fastapi import APIRouter, Depends, status
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.database.connection import get_database
from app.database.repositories.user_repository import UserRepository
from app.auth.dependencies import get_current_user
from app.models.user import UserModel

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db=Depends(get_database)) -> AuthService:
    repo = UserRepository(db)
    return AuthService(repo)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register User")
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register_user(user_in)


@router.post("/login", response_model=Token, summary="User Login")
async def login(
    login_req: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login_user(login_req)


@router.get("/me", response_model=UserResponse, summary="Get Current User Profile")
async def me(current_user: UserModel = Depends(get_current_user)):
    return UserResponse(**current_user.model_dump())
