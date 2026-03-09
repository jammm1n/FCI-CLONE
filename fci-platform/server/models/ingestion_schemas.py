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
    'c360', 'elliptic', 'hexa_dump', 'raw_hex_dump', 'previous_icrs',
    'rfis', 'kyc', 'l1_victim', 'l1_suspect', 'kodex', 'investigator_notes',
]

# Sections that can be marked "none" (not applicable).
NONEABLE_SECTION_KEYS = [
    'elliptic', 'hexa_dump', 'raw_hex_dump', 'previous_icrs', 'rfis',
    'kyc', 'l1_victim', 'l1_suspect', 'kodex', 'investigator_notes',
]

# Sections that must be terminal (complete/none) before case is "ready".
# investigator_notes is always optional and never blocks readiness.
REQUIRED_TERMINAL_KEYS = [
    'c360', 'elliptic', 'hexa_dump', 'raw_hex_dump', 'previous_icrs',
    'rfis', 'kyc', 'l1_victim', 'l1_suspect', 'kodex',
]

# Terminal statuses — a section in one of these states is "done".
TERMINAL_STATUSES = {'complete', 'none'}


# ── Request Models ────────────────────────────────────────────────

class CreateIngestionCaseRequest(BaseModel):
    """POST /api/ingestion/cases"""
    case_id: str
    subject_uid: str = ''
    coconspirator_uids: list[str] = []
    case_mode: str = 'single'
    total_subjects: int = 1


class SetSubjectUidRequest(BaseModel):
    """PATCH /api/ingestion/cases/{case_id}/subjects/{index}/uid"""
    user_id: str


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


class TextSectionRequest(BaseModel):
    """PUT /api/ingestion/cases/{case_id}/sections/{key} — text with AI processing."""
    text: str


# ── Response Models ───────────────────────────────────────────────

class SectionStatus(BaseModel):
    """Lightweight section status for polling."""
    status: str
    updated_at: Optional[datetime] = None
    ai_status: Optional[str] = None
    ai_progress: Optional[dict] = None


class SubjectStatusSummary(BaseModel):
    """Per-subject summary for multi-user status polling."""
    index: int
    user_id: Optional[str] = None
    status: str
    sections_complete: int = 0
    sections_total: int = 0


class CaseStatusResponse(BaseModel):
    """GET /api/ingestion/cases/{case_id}/status — polling response."""
    case_id: str
    case_status: str
    sections: dict[str, SectionStatus]
    case_mode: Optional[str] = None
    current_subject_index: Optional[int] = None
    subjects: Optional[list[SubjectStatusSummary]] = None


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
