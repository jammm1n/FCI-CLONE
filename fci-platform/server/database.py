"""
FCI Platform — Database Connection

Uses PyMongo 4.16's native async API (pymongo.asynchronous.AsyncMongoClient).
Motor is deprecated as of May 2025 — this is the official replacement.

The module provides connect/disconnect lifecycle functions called from
the FastAPI lifespan, and a get_database() accessor for services.
"""

import logging
from pymongo import AsyncMongoClient

from server.config import settings

logger = logging.getLogger(__name__)

_client: AsyncMongoClient | None = None
_db = None


async def connect_db():
    """Connect to MongoDB. Called on app startup."""
    global _client, _db
    _client = AsyncMongoClient(settings.MONGODB_URI)
    _db = _client[settings.MONGODB_DB_NAME]

    # Verify connection
    try:
        await _client.admin.command("ping")
        logger.info("Connected to MongoDB: %s / %s", settings.MONGODB_URI, settings.MONGODB_DB_NAME)
    except Exception as e:
        logger.error("Failed to connect to MongoDB: %s", e)
        raise


async def disconnect_db():
    """Disconnect from MongoDB. Called on app shutdown."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("Disconnected from MongoDB")


def get_database():
    """
    Get the database instance. Must be called after connect_db().

    Returns the PyMongo async database object, which supports
    the same collection/document API as Motor.
    """
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db