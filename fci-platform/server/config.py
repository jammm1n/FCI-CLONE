"""
FCI Platform — Configuration

All settings loaded from environment variables with sensible defaults.
Uses pydantic-settings for validation and type coercion.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, loaded from environment variables."""

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "fci_platform"

    # Anthropic API
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"  # Sonnet for dev, Opus for demo
    ANTHROPIC_MAX_TOKENS: int = 4096

    # Tool use limits
    MAX_TOOL_CALLS_PER_TURN: int = 5

    # Knowledge base
    KNOWLEDGE_BASE_PATH: str = "./knowledge_base"

    # Image storage
    IMAGES_DIR: str = "./data/images"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton instance
settings = Settings()