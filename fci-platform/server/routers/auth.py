"""
FCI Platform — Auth Router

Username + password authentication. Users are seeded in MongoDB with
bcrypt-hashed passwords. Login returns a UUID session token stored
in-memory (dict). The token is sent as Bearer in subsequent requests.

Will be replaced by Okta OIDC in production.
"""

import logging
import uuid
from typing import Annotated

import bcrypt
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
    Login with username and password. Returns a session token.
    """
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    db = get_database()
    user = await db.users.find_one({"username": username})

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Verify password
    stored_hash = user.get("password_hash", "")
    if not stored_hash or not bcrypt.checkpw(
        password.encode("utf-8"), stored_hash.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password")

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