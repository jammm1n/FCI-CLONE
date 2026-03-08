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

    # Elliptic API
    ELLIPTIC_API_KEY: str = ""

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

    # One-shot mode
    ONESHOT_MODEL: str = "claude-opus-4-6"
    ONESHOT_THINKING_ENABLED: bool = True
    ONESHOT_THINKING_BUDGET: int = 10000
    ONESHOT_MAX_TOKENS: int = 16000

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


# ---------------------------------------------------------------------------
# Step configuration — per-step model and document injection list
# Used by knowledge_base.get_step_system_prompt() to assemble the correct
# system prompt for each investigation step.
# ---------------------------------------------------------------------------

STEP_CONFIG = {
    1: {"model": "claude-sonnet-4-6", "docs": ["icr-steps-setup"]},
    2: {"model": "claude-sonnet-4-6", "docs": ["icr-steps-analysis"]},  # TODO: revert to opus for production
    3: {"model": "claude-sonnet-4-6", "docs": ["icr-steps-decision", "decision-matrix", "mlro-escalation-matrix"]},
    4: {"model": "claude-sonnet-4-6", "docs": ["icr-steps-post", "mlro-escalation-matrix"]},
    5: {"model": "claude-sonnet-4-6", "docs": ["qc-full-checklist"]},  # TODO: revert to opus for production
    "summary": {"model": "claude-sonnet-4-6"},  # TODO: revert to opus for production
}

STEP_PHASES = {1: "setup", 2: "analysis", 3: "decision", 4: "post", 5: "qc_check"}