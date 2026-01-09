"""Configuration management using Pydantic Settings."""

import logging
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Logger setup
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(..., description="PostgreSQL database URL for Neon DB")

    # OpenAI
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API port")
    api_rate_limit: int = Field(default=100, ge=1, description="API rate limit per IP per minute")

    # MCP
    mcp_enabled: bool = Field(default=True, description="Enable MCP server")
    mcp_port: int = Field(default=3000, ge=1, le=65535, description="MCP server port")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()

# Database engine and session
_engine: Optional[create_engine] = None
_session_factory: Optional[sessionmaker] = None


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        logger.info("Creating database engine")
        _engine = create_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            echo=False,
        )
    return _engine


def get_session_factory():
    """Get or create the database session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _session_factory


def create_db_tables():
    """Create all database tables."""
    engine = get_engine()
    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def init_logging():
    """Initialize logging configuration."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.setLevel(level)
    logger.info("Logging initialized at %s level", settings.log_level)
