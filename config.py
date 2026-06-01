"""Configuration management for MOOSE LOON AI Mentor Platform.

This module prefers `pydantic_settings.BaseSettings` when available but
falls back to a lightweight `os.environ`-based loader so that basic
operations (like DB table creation) don't require building heavy native
dependencies during early development.
"""

from typing import Optional
import os

try:
    from pydantic import ConfigDict
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        """Application settings loaded from environment variables."""

        MYSQL_HOST: str = "localhost"
        MYSQL_PORT: int = 3306
        MYSQL_USER: str = "root"
        MYSQL_PASSWORD: str = ""
        MYSQL_DATABASE: str = "moose_loon_ai"

        API_HOST: str = "0.0.0.0"
        API_PORT: int = 8000
        API_DEBUG: bool = False

        STREAMLIT_PORT: int = 8501

        SECRET_KEY: str = "your-secret-key-change-in-production"
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

        OPENAI_API_KEY: Optional[str] = None
        LLM_MODEL: str = "gpt-4"
        LLM_FAST_MODEL: str = "gpt-4o-mini"
        LLM_TEMPERATURE: float = 0.7

        CHROMA_DB_PATH: str = "./data/chroma_db"

        BILLING_CHECKOUT_BUILDER_URL: Optional[str] = None
        BILLING_CHECKOUT_PRO_URL: Optional[str] = None
        BILLING_CHECKOUT_TEAM_URL: Optional[str] = None

        ENVIRONMENT: str = "development"

        model_config = ConfigDict(env_file=".env", case_sensitive=True)

        @property
        def database_url(self) -> str:
            return (
                f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            )

        @property
        def is_production(self) -> bool:
            return self.ENVIRONMENT.lower() == "production"

        @property
        def is_development(self) -> bool:
            return self.ENVIRONMENT.lower() == "development"

    settings = Settings()
except Exception:
    # Fallback when pydantic is not installed / cannot be built.
    class _SimpleSettings:
        MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
        MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        MYSQL_USER = os.getenv("MYSQL_USER", "root")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
        MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "moose_loon_ai")

        API_HOST = os.getenv("API_HOST", "0.0.0.0")
        API_PORT = int(os.getenv("API_PORT", "8000"))
        API_DEBUG = os.getenv("API_DEBUG", "False") == "True"

        STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        ALGORITHM = os.getenv("ALGORITHM", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
        LLM_FAST_MODEL = os.getenv("LLM_FAST_MODEL", "gpt-4o-mini")
        LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

        CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

        BILLING_CHECKOUT_BUILDER_URL = os.getenv("BILLING_CHECKOUT_BUILDER_URL")
        BILLING_CHECKOUT_PRO_URL = os.getenv("BILLING_CHECKOUT_PRO_URL")
        BILLING_CHECKOUT_TEAM_URL = os.getenv("BILLING_CHECKOUT_TEAM_URL")

        ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

        @property
        def database_url(self) -> str:
            return (
                f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            )

        @property
        def is_production(self) -> bool:
            return self.ENVIRONMENT.lower() == "production"

        @property
        def is_development(self) -> bool:
            return self.ENVIRONMENT.lower() == "development"

    settings = _SimpleSettings()
