"""
Pydantic v2 models for all API request/response validation.

These models define the API contract between frontend and backend
as specified in PRD Section 3.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


# --- Auth ---

class LoginRequest(BaseModel):
    """POST /api/auth/login request body."""
    username: str


class LoginResponse(BaseModel):
    """POST /api/auth/login response body."""
    user_id: str
    username: str
    display_name: str
    token: str


class UserResponse(BaseModel):
    """GET /api/auth/me response body."""
    user_id: str
    username: str
    display_name: str


# --- Token & Tool Metadata ---

class TokenUsage(BaseModel):
    """Token usage stats returned from the Anthropic API."""
    input_tokens: int
    output_tokens: int


class ToolUsedInfo(BaseModel):
    """Metadata about a reference document retrieved during a response."""
    tool: str
    document_id: str
    document_title: str


# --- Cases ---

class CaseSummary(BaseModel):
    """Single case entry in the case list."""
    case_id: str
    case_name: str = ""
    case_type: str
    subject_user_id: str
    status: str
    summary: str
    created_at: datetime
    conversation_id: str | None = None
    case_mode: str | None = None
    total_subjects: int | None = None


class CaseListResponse(BaseModel):
    """GET /api/cases response body."""
    cases: list[CaseSummary]


class PreprocessedData(BaseModel):
    """Pre-staged case data fields populated from ingestion assembly.
    All optional — only sections with data are populated."""
    model_config = ConfigDict(extra="allow")

    # C360 sub-processors
    tx_summary: str | None = None
    user_profile: str | None = None
    privacy_coin: str | None = None
    counterparty: str | None = None
    device_ip: str | None = None
    failed_fiat: str | None = None
    ctm_alerts: str | None = None
    ftm_alerts: str | None = None
    account_blocks: str | None = None
    address_xref: str | None = None
    uid_search: str | None = None

    # Standalone sections
    elliptic_addresses: str | None = None
    elliptic: str | None = None
    l1_referral: str | None = None
    haoDesk: str | None = None
    kyc: str | None = None
    prior_icr: str | None = None
    rfi: str | None = None
    kodex: str | None = None
    l1_victim: str | None = None
    l1_suspect: str | None = None
    investigator_notes: str | None = None


class SubjectData(BaseModel):
    """Per-subject data in a multi-user case."""
    user_id: str
    label: str = ""
    preprocessed_data: PreprocessedData = PreprocessedData()


class CaseDetailResponse(BaseModel):
    """GET /api/cases/{case_id} response body."""
    case_id: str
    case_name: str = ""
    case_type: str
    status: str
    subject_user_id: str
    summary: str
    conversation_id: str | None = None
    created_at: datetime
    preprocessed_data: PreprocessedData
    assembled_case_data: str | None = None
    case_mode: str | None = None
    total_subjects: int | None = None
    subjects: list[SubjectData] = []


# --- Conversations ---

class CreateConversationRequest(BaseModel):
    """POST /api/conversations request body."""
    case_id: str | None = None
    mode: str = "case"


class CreateConversationResponse(BaseModel):
    """POST /api/conversations response body."""
    conversation_id: str
    case_id: str | None = None
    mode: str = "case"


class ConversationSummary(BaseModel):
    """Single conversation entry in the conversation list."""
    conversation_id: str
    title: str
    mode: str
    case_id: str | None = None
    updated_at: datetime
    message_count: int


class ConversationListResponse(BaseModel):
    """GET /api/conversations response body."""
    conversations: list[ConversationSummary]


class ImageInput(BaseModel):
    """A single image attached to a user message."""
    base64: str
    media_type: str


class SendMessageRequest(BaseModel):
    """POST /api/conversations/{id}/messages request body."""
    content: str
    images: list[ImageInput] = []


class SendMessageResponse(BaseModel):
    """POST /api/conversations/{id}/messages response body."""
    message_id: str
    role: str = "assistant"
    content: str
    tools_used: list[ToolUsedInfo] = []
    token_usage: TokenUsage
    timestamp: datetime


class MessageResponse(BaseModel):
    """A single message in conversation history."""
    message_id: str
    role: str
    content: str
    tools_used: list[ToolUsedInfo] = []
    images: list[dict] = []
    timestamp: datetime


class ConversationHistoryResponse(BaseModel):
    """GET /api/conversations/{id}/history response body."""
    conversation_id: str
    case_id: str | None = None
    mode: str = "case"
    title: str = ""
    messages: list[MessageResponse]


# --- Investigation State ---

class StepInfo(BaseModel):
    """State of a single investigation step."""
    step_number: int
    phase: str
    status: str
    summary: str | None = None
    completed_at: datetime | None = None


class InvestigationStateResponse(BaseModel):
    """GET /api/conversations/{id}/state response."""
    current_step: int
    phase: str
    steps: list[StepInfo]


class AdvanceStepResponse(BaseModel):
    """POST /api/conversations/{id}/advance-step response."""
    step: int
    phase: str
    summary: str


# --- System / Utility ---

class HealthResponse(BaseModel):
    """GET /api/health response body."""
    status: str
    mongodb: str
    knowledge_base_loaded: bool
    core_documents_tokens: int
    reference_documents_available: int


class ReferenceDocumentInfo(BaseModel):
    """A single entry in the knowledge base index."""
    id: str
    title: str
    covers: list[str]
    token_estimate: int


class KnowledgeBaseIndexResponse(BaseModel):
    """GET /api/knowledge-base/index response body."""
    reference_documents: list[ReferenceDocumentInfo]
