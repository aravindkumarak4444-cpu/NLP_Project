import logging
from datetime import timedelta
from fastapi import status
from app.database.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, LoginRequest
from app.models.user import UserModel
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.utils.ids import generate_user_id
from app.utils.timestamps import utc_now
from app.middleware.error_handler import APIException
from app.config import settings

logger = logging.getLogger("sif_backend")


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_in: UserCreate) -> UserResponse:
        # Check duplicate email
        existing_email = await self.user_repo.find_by_email(user_in.email)
        if existing_email:
            raise APIException(
                code="EMAIL_EXISTS",
                message="A user with this email address is already registered.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Check duplicate username
        existing_username = await self.user_repo.find_by_username(user_in.username)
        if existing_username:
            raise APIException(
                code="USERNAME_EXISTS",
                message="A user with this username is already registered.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user_id = generate_user_id()
        now = utc_now()
        hashed_pwd = hash_password(user_in.password)

        user_model = UserModel(
            user_id=user_id,
            username=user_in.username.lower(),
            email=user_in.email.lower(),
            full_name=user_in.full_name,
            role=user_in.role,
            department=user_in.department,
            hashed_password=hashed_pwd,
            is_active=True,
            created_at=now,
            updated_at=now
        )

        saved_user = await self.user_repo.create_user(user_model)
        logger.info(f"Registered new user: {saved_user.user_id} ({saved_user.email})")
        return UserResponse(**saved_user.model_dump())

    async def login_user(self, login_req: LoginRequest) -> Token:
        user = await self.user_repo.find_by_email(login_req.email)
        if not user:
            user = await self.user_repo.find_by_username(login_req.email)

        if not user:
            raise APIException(
                code="INVALID_CREDENTIALS",
                message="Invalid email or password credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        if not verify_password(login_req.password, user.hashed_password):
            raise APIException(
                code="INVALID_CREDENTIALS",
                message="Invalid email or password credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            raise APIException(
                code="USER_INACTIVE",
                message="User account is deactivated.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        token_data = {"sub": user.user_id, "role": user.role.value}
        access_token = create_access_token(data=token_data)

        logger.info(f"User logged in successfully: {user.user_id}")
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
