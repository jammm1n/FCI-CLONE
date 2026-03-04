"""
FCI Platform — Auth Router (Mock)

Mock authentication for the prototype. No passwords, no expiry.
Users are pre-seeded in MongoDB. Login returns a UUID session token
stored in-memory (dict). The token is sent as Bearer in subsequent requests.

For the MVP, this is intentionally simple. Real auth is deferred.
"""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException

from server.database import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory session store: token → user dict
# This is fine for a single-process prototype. Clears on restart.
_sessions: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Dependency: extract current user from Authorization header
# ---------------------------------------------------------------------------

async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """
    FastAPI dependency that extracts and validates the session token.
    Returns the user dict or raises 401.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    # Expect "Bearer <token>"
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use: Bearer <token>")

    token = parts[1]
    user = _sessions.get(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")

    return user


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/login")
async def login(body: dict):
    """
    Mock login. Accepts {"username": "..."}, returns a session token.
    No password required for the prototype.
    """
    username = body.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    db = get_database()
    user = await db.users.find_one({"username": username})

    if user is None:
        raise HTTPException(status_code=404, detail=f"User not found: {username}")

    # Generate session token
    token = str(uuid.uuid4())
    user_data = {
        "user_id": user["_id"],
        "username": user["username"],
        "display_name": user.get("display_name", user["username"]),
    }
    _sessions[token] = user_data

    logger.info("User logged in: %s (token: %s...)", username, token[:8])

    return {
        **user_data,
        "token": token,
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the current user based on their session token."""
    return current_user