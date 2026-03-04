"""
FCI Platform — Case Service

Simple CRUD operations for case records in MongoDB.
For the MVP, cases are pre-staged via the seed script.
This service retrieves them and manages status updates.
"""

import logging
from datetime import datetime, timezone

from server.database import get_database

logger = logging.getLogger(__name__)


async def get_cases(user_id: str | None = None) -> list[dict]:
    """
    Return all cases, optionally filtered by assigned user.

    Returns a list of case summary dicts (without full preprocessed_data)
    suitable for the case list view.
    """
    db = get_database()

    query = {}
    if user_id:
        query["assigned_to"] = user_id

    cursor = db.cases.find(
        query,
        {
            # Project only the fields needed for the case list
            "_id": 1,
            "case_type": 1,
            "status": 1,
            "subject_user_id": 1,
            "summary": 1,
            "conversation_id": 1,
            "created_at": 1,
        }
    )

    cases = []
    async for doc in cursor:
        cases.append({
            "case_id": doc["_id"],
            "case_type": doc.get("case_type", "unknown"),
            "status": doc.get("status", "open"),
            "subject_user_id": doc.get("subject_user_id", ""),
            "summary": doc.get("summary", ""),
            "conversation_id": doc.get("conversation_id"),
            "created_at": _format_dt(doc.get("created_at")),
        })

    return cases


async def get_case(case_id: str) -> dict | None:
    """
    Return full case details including preprocessed_data.

    Returns None if the case doesn't exist.
    """
    db = get_database()
    doc = await db.cases.find_one({"_id": case_id})

    if doc is None:
        return None

    return {
        "case_id": doc["_id"],
        "case_type": doc.get("case_type", "unknown"),
        "status": doc.get("status", "open"),
        "subject_user_id": doc.get("subject_user_id", ""),
        "summary": doc.get("summary", ""),
        "conversation_id": doc.get("conversation_id"),
        "created_at": _format_dt(doc.get("created_at")),
        "preprocessed_data": doc.get("preprocessed_data", {}),
    }


async def update_case_status(case_id: str, status: str) -> bool:
    """
    Update a case's status. Returns True if the case was found and updated.

    Valid statuses for MVP: open, in_progress, completed.
    """
    valid_statuses = {"open", "in_progress", "completed"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")

    db = get_database()
    result = await db.cases.update_one(
        {"_id": case_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}},
    )

    if result.matched_count == 0:
        return False

    logger.info("Case %s status updated to %s", case_id, status)
    return True


def _format_dt(dt) -> str | None:
    """Format a datetime to ISO string, handling None."""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)