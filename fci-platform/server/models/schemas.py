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
    case_type: str
    subject_user_id: str
    status: str
    summary: str
    created_at: datetime
    conversation_id: str | None = None


class CaseListResponse(BaseModel):
    """GET /api/cases response body."""
    cases: list[CaseSummary]


class PreprocessedData(BaseModel):
    """Pre-staged case data fields. All optional — not every case has every type."""
    model_config = ConfigDict(extra="allow")

    c360_analysis: str | None = None
    elliptic_analysis: str | None = None
    previous_cases: str | None = None
    chat_history_summary: str | None = None
    kyc_summary: str | None = None
    law_enforcement: str | None = None


class CaseDetailResponse(BaseModel):
    """GET /api/cases/{case_id} response body."""
    case_id: str
    case_type: str
    status: str
    subject_user_id: str
    summary: str
    conversation_id: str | None = None
    created_at: datetime
    preprocessed_data: PreprocessedData


# --- Conversations ---

class CreateConversationRequest(BaseModel):
    """POST /api/conversations request body."""
    case_id: str


class InitialResponse(BaseModel):
    """The AI's initial case assessment returned when a conversation is created."""
    role: str = "assistant"
    content: str
    tools_used: list[ToolUsedInfo] = []
    token_usage: TokenUsage
    timestamp: datetime


class CreateConversationResponse(BaseModel):
    """POST /api/conversations response body."""
    conversation_id: str
    case_id: str
    initial_response: InitialResponse


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
    case_id: str
    messages: list[MessageResponse]


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
