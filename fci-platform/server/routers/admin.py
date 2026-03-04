"""
FCI Platform — Admin Router (Demo Only)

Single endpoint to wipe and reseed the database for demo/dev use.
Delete this file for production.
"""

import asyncio
import logging
import shutil
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from server.routers.auth import get_current_user
from server.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/reseed")
async def reseed_database(user: dict = Depends(get_current_user)):
    """Wipe all data and re-run the seed script. Demo/dev only."""
    logger.warning("Reseed requested by user %s", user.get("user_id"))

    # 1. Clear uploaded images
    images_dir = Path(settings.IMAGES_DIR)
    if images_dir.exists():
        shutil.rmtree(images_dir)
        images_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Cleared images directory")

    # 2. Run seed script in a thread (asyncio subprocess not supported on Windows)
    seed_script = Path("scripts/seed_demo_data.py")
    if not seed_script.exists():
        raise HTTPException(status_code=500, detail="Seed script not found")

    result = await asyncio.to_thread(
        subprocess.run,
        [sys.executable, str(seed_script)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error("Seed script failed (rc=%d): %s", result.returncode, result.stderr)
        raise HTTPException(status_code=500, detail="Seed script failed")

    logger.info("Reseed complete: %s", result.stdout.strip())
    return {"status": "reseeded"}
