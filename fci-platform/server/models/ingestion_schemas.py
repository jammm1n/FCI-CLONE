"""
Pydantic v2 models for the Data Ingestion Dashboard.

These models define the API contract for all ingestion endpoints
as specified in FCI-Ingestion-Dashboard-PRD Section 5.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


# ── Section Keys ──────────────────────────────────────────────────

# All section keys in the ingestion case document.
ALL_SECTION_KEYS = [
    'c360', 'elliptic', 'hexa_dump', 'previous_icrs', 'rfis',
    'kyc', 'l1_victim', 'l1_suspect', 'kodex', 'investigator_notes',
]

# Sections that can be marked "none" (not applicable).
NONEABLE_SECTION_KEYS = [
    'elliptic', 'hexa_dump', 'previous_icrs', 'rfis',
    'kyc', 'l1_victim', 'l1_suspect', 'kodex',
]

# Sections that must be terminal (complete/none) before case is "ready".
# investigator_notes is always optional and never blocks readiness.
REQUIRED_TERMINAL_KEYS = [
    'c360', 'elliptic', 'hexa_dump', 'previous_icrs', 'rfis',
    'kyc', 'l1_victim', 'l1_suspect', 'kodex',
]

# Terminal statuses — a section in one of these states is "done".
TERMINAL_STATUSES = {'complete', 'none'}


# ── Request Models ────────────────────────────────────────────────

class CreateIngestionCaseRequest(BaseModel):
    """POST /api/ingestion/cases"""
    case_id: str
    subject_uid: str = ''
    coconspirator_uids: list[str] = []


class ManualAddressesRequest(BaseModel):
    """POST /api/ingestion/cases/{case_id}/elliptic/addresses"""
    manual_addresses: list[str] = []


class EllipticSubmitRequest(BaseModel):
    """POST /api/ingestion/cases/{case_id}/elliptic/submit"""
    addresses: list[str]
    customer_id: str


class NotesRequest(BaseModel):
    """PUT /api/ingestion/cases/{case_id}/notes"""
    notes: str


# ── Response Models ───────────────────────────────────────────────

class SectionStatus(BaseModel):
    """Lightweight section status for polling."""
    status: str
    updated_at: Optional[datetime] = None


class CaseStatusResponse(BaseModel):
    """GET /api/ingestion/cases/{case_id}/status — polling response."""
    case_id: str
    case_status: str
    sections: dict[str, SectionStatus]


class C360UploadResponse(BaseModel):
    """POST /api/ingestion/cases/{case_id}/c360 — 202 Accepted."""
    accepted: bool = True
    files_received: int
    section_status: str = 'processing'
    message: str = 'Processing started. Poll /status for updates.'


class EllipticSubmitResponse(BaseModel):
    """POST /api/ingestion/cases/{case_id}/elliptic/submit — 202 Accepted."""
    accepted: bool = True
    addresses_submitted: int
    section_status: str = 'processing'


class AssembleResponse(BaseModel):
    """POST /api/ingestion/cases/{case_id}/assemble"""
    assembled_case_data: str
    sections_included: list[str]
    sections_none: list[str]
