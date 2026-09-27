from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "AetherMind Multimodal AI"
    VERSION: str = "3.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Host & Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS Allowed Origins
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/aethermind_v3",
        description="Async PostgreSQL connection string"
    )

    # JWT & Authentication Security
    SECRET_KEY: str = "aethermind-enterprise-jwt-secret-key-super-secure-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days
    REMEMBER_ME_EXPIRE_DAYS: int = 30

    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    # Redis Cache & Broker
    REDIS_URL: str = "redis://localhost:6379/0"

    # Supabase Object Storage
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "aethermind-assets"

    # Multimodal Providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_GEMINI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""

    # OAuth & Clerk Auth Configuration
    CLERK_SECRET_KEY: str = "sk_test_mock_clerk_secret_key_aethermind"
    CLERK_PUBLISHABLE_KEY: str = "pk_test_mock_clerk_publishable_key"
    CLERK_ISSUER_URL: str = "https://clerk.aethermind.ai"
    MICROSOFT_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

