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
    ANTHROPIC_BASE_URL: str | None = None  # Custom proxy (e.g., LiteLLM). None = default Anthropic endpoint
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
    1: {"model": settings.ANTHROPIC_MODEL, "docs": ["icr-steps-setup"]},
    2: {"model": settings.ANTHROPIC_MODEL, "docs": ["icr-steps-analysis"]},  # TODO: revert to ONESHOT_MODEL for production
    3: {"model": settings.ANTHROPIC_MODEL, "docs": ["icr-steps-decision", "decision-matrix", "mlro-escalation-matrix"]},
    4: {"model": settings.ANTHROPIC_MODEL, "docs": ["icr-steps-post", "mlro-escalation-matrix"]},
    5: {"model": settings.ANTHROPIC_MODEL, "docs": ["qc-full-checklist"]},  # TODO: revert to ONESHOT_MODEL for production
    "summary": {"model": settings.ANTHROPIC_MODEL},  # TODO: revert to ONESHOT_MODEL for production
}

STEP_PHASES = {1: "setup", 2: "analysis", 3: "decision", 4: "post", 5: "qc_check"}


# ---------------------------------------------------------------------------
# Multi-user step configuration — 9 investigation blocks
# Block-based structure: each block covers a subset of ICR steps.
# ---------------------------------------------------------------------------

MULTI_USER_STEP_CONFIG = {
    1: {
        "phase": "setup",
        "label": "Identity & Account Overview",
        "steps_covered": [1, 2, 3],
        "model": settings.ONESHOT_MODEL,
        "docs": ["icr-steps-setup"],
    },
    2: {
        "phase": "setup",
        "label": "Case History & Context",
        "steps_covered": [4, 5, 6],
        "model": settings.ONESHOT_MODEL,
        "docs": ["icr-steps-setup"],
    },
    3: {
        "phase": "analysis",
        "label": "Transaction & Alert Analysis",
        "steps_covered": [7, 8],
        "model": settings.ONESHOT_MODEL,
        "docs": ["icr-steps-analysis"],
    },
    4: {
        "phase": "analysis",
        "label": "On-Chain Analysis",
        "steps_covered": [9, 10, 11],
        "model": settings.ONESHOT_MODEL,
        "docs": ["icr-steps-analysis"],
    },
    5: {
        "phase": "analysis",
        "label": "Counterparty & Device Analysis",
        "steps_covered": [12, 13, 14],
        "model": settings.ONESHOT_MODEL,
        "docs": ["icr-steps-analysis"],
    },
    6: {
        "phase": "analysis",
        "label": "Communications & OSINT",
        "steps_covered": [15, 16, 17, 18, 19],
        "model": settings.ONESHOT_MODEL,
        "docs": ["icr-steps-analysis", "icr-steps-decision"],
    },
    7: {
        "phase": "summary",
        "label": "Summary of Unusual Activity",
        "steps_covered": [20],
        "model": settings.ONESHOT_MODEL,
        "docs": ["icr-steps-decision"],
    },
    8: {
        "phase": "decision",
        "label": "Decision & Recommendation",
        "steps_covered": [21],
        "model": settings.ONESHOT_MODEL,
        "docs": ["icr-steps-decision", "decision-matrix", "mlro-escalation-matrix"],
    },
    9: {
        "phase": "qc_check",
        "label": "QC Check",
        "steps_covered": [],
        "model": settings.ONESHOT_MODEL,
        "docs": ["qc-full-checklist"],
    },
    "summary": {
        "model": settings.ONESHOT_MODEL,
    },
}

MULTI_USER_STEP_PHASES = {
    1: "setup", 2: "setup", 3: "analysis", 4: "analysis",
    5: "analysis", 6: "analysis", 7: "summary", 8: "decision", 9: "qc_check",
}

# Sentinel constants for block-to-data mapping
ALL_SECTIONS = "all"      # Inject all case data sections (unfiltered)
NO_INJECTION = "none"     # No case data injected for this block

MULTI_USER_BLOCK_DATA = {
    1: ALL_SECTIONS,
    2: ["l1_referral", "haoDesk", "prior_icr", "kodex", "l1_victim", "l1_suspect"],
    3: ["tx_summary", "ctm_alerts", "ftm_alerts"],
    4: ["elliptic", "address_xref", "privacy_coin"],
    5: ["counterparty", "failed_fiat", "device_ip"],
    6: ["investigator_notes", "rfi"],
    7: ["tx_summary"],
    8: NO_INJECTION,
    9: NO_INJECTION,
}