import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field, AliasChoices


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "OIL SIF Precursor Detection API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "oil_sif"

    JWT_SECRET: str = Field(
        default="super_secret_sif_precursor_key_change_in_production_2026",
        validation_alias=AliasChoices("JWT_SECRET", "JWT_SECRET_KEY", "SECRET_KEY")
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM", "ALGORITHM")
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=480,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "TOKEN_EXPIRE_MINUTES")
    )

    FRONTEND_URL: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]
    MODEL_PATH: str = "ml/models/model.pkl"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("FRONTEND_URL", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173"]


settings = Settings()
