"""
FCI Platform — Cases Router

Endpoints for listing and viewing investigation cases.
Cases are pre-staged in MongoDB via the seed script.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from server.routers.auth import get_current_user
from server.services import case_service

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("")
async def list_cases(
    include_archived: bool = False,
    current_user: dict = Depends(get_current_user),
):
    """
    Return all cases assigned to the current user.
    Archived cases excluded by default; pass ?include_archived=true to include.
    """
    cases = await case_service.get_cases(
        user_id=current_user["user_id"],
        include_archived=include_archived,
    )
    return {"cases": cases}


@router.patch("/{case_id}/archive")
async def archive_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Set a case's status to archived."""
    updated = await case_service.update_case_status(case_id, "archived")
    if not updated:
        raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")
    return {"status": "archived"}


@router.get("/{case_id}")
async def get_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """
    Return full case details including preprocessed data.
    Used when opening the Investigation view.
    """
    case = await case_service.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")
    return case


@router.get("/{case_id}/export")
async def export_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Serve assembled markdown as a downloadable .md file."""
    case = await case_service.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")
    markdown = case.get("assembled_case_data", "")
    if not markdown:
        raise HTTPException(status_code=404, detail="No assembled data for this case")
    return PlainTextResponse(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{case_id}.md"'},
    )