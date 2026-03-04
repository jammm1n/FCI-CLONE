"""
FCI Platform — Application Entry Point

FastAPI app with lifespan events that:
- Connect to MongoDB on startup
- Load the knowledge base into memory on startup
- Disconnect from MongoDB on shutdown

Run with: uvicorn server.main:app --reload
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config import settings
from server.database import connect_db, disconnect_db, get_database
from server.services.knowledge_base import KnowledgeBase
from server.routers import admin, auth, cases, conversations

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""

    # --- Startup ---
    logger.info("Starting FCI Investigation Platform")

    # Connect to MongoDB
    await connect_db()

    # Load knowledge base
    kb = KnowledgeBase(base_path=settings.KNOWLEDGE_BASE_PATH)
    kb.load_on_startup()
    app.state.knowledge_base = kb
    logger.info(
        "Knowledge base loaded: %d core chars, %d reference documents",
        len(kb.core_content),
        len(kb.reference_index),
    )

    # Ensure images directory exists
    Path(settings.IMAGES_DIR).mkdir(parents=True, exist_ok=True)

    logger.info("FCI Platform ready — http://%s:%d", settings.HOST, settings.PORT)

    yield

    # --- Shutdown ---
    logger.info("Shutting down FCI Platform")
    await disconnect_db()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FCI Investigation Platform",
    description="AI-assisted financial crime investigation platform — Phase 1 MVP",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(conversations.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["system"])
async def health_check():
    """Health check endpoint. Verifies MongoDB connection and KB status."""
    kb: KnowledgeBase = app.state.knowledge_base

    # Check MongoDB
    mongo_status = "disconnected"
    try:
        db = get_database()
        await db.command("ping")
        mongo_status = "connected"
    except Exception:
        mongo_status = "error"

    return {
        "status": "ok" if mongo_status == "connected" else "degraded",
        "mongodb": mongo_status,
        "knowledge_base_loaded": bool(kb.core_content),
        "core_documents_chars": len(kb.core_content),
        "reference_documents_available": len(kb.reference_index),
    }