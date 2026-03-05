**Version:** 1.0 (Draft)
**Date:** March 2026
**Author:** Ben [Surname], Financial Crime Investigator, Level 2 Compliance
**Status:** Phase 1 MVP — Planning

---

## 1. Project Overview & Scope

### 1.1 Background

The Financial Crime Investigation (FCI) team at Binance Level 2 compliance investigates suspicious activity cases, with a target throughput of 10 cases per day. The current realistic throughput is approximately 6 cases per day, with each case taking 60–90 minutes using an AI-assisted workflow built over the past five weeks, down from 2–3 hours in a fully manual process.

The existing AI-assisted workflow relies on Binance's SAFU GPT platform (an internal ChatGPT-style interface) with a custom-built knowledge base of 17 documents, a continuously refined system prompt, and a separate Python web application for data preprocessing. While effective, this workflow is constrained by manual data collection, sequential processing across multiple chat sessions, and the limitations of a generic chat interface not designed for compliance investigation workflows.

Management has endorsed the development of a standalone investigation platform to replace the SAFU GPT interface, improve case throughput, and establish a foundation for further automation.

### 1.2 What We Are Building (Phase 1 MVP)

A working prototype demonstrating a custom AI-assisted investigation platform with:

- **A functional chat interface** connected to Anthropic's Claude API with tool use, replacing the SAFU GPT chat interface
- **A complete knowledge base** loaded server-side, with core documents injected into every conversation and reference documents (SOPs, guidelines) available to the AI on demand via tool calls against a structured index
- **Full conversation management** owned by our backend — conversation history, context assembly, and API orchestration handled server-side with storage in MongoDB
- **Pre-staged sanitised case data** in MongoDB, simulating the output of automated data ingestion that will be built in subsequent phases
- **A professional dashboard** with mock authentication, case selection, case data overview, and the chat interface
- **Streaming responses** for a responsive user experience (subject to API support confirmation)

### 1.3 What We Are Not Building (Deferred)

The following are explicitly out of scope for Phase 1 and will be addressed in subsequent phases:

- **Live data ingestion** — no live connections to C360, Binance Admin, HowDesk, Codex, or Elliptic. All case data is pre-staged.
- **Automated data preprocessing pipelines** — the existing C360 web app is used offline during demo preparation, not integrated into the platform
- **Codex PDF upload and processing** — the iterative PDF extraction pipeline is a strong Phase 2 feature but not required for the prototype
- **Audit trail / approval gates** — the existing workflow (copy output → paste into HowDesk case form → submit) provides a sufficient compliance audit trail. In-app approval mechanisms are deferred.
- **Real authentication** — mock auth (user selection or basic login) is sufficient for prototype demonstration
- **SAFU GPT knowledge base API integration** — all knowledge base content is served locally from the backend server
- **RAG / vector search infrastructure** — not required; the tool-based document retrieval pattern eliminates this need
- **Production deployment, scaling, or multi-user concurrency** — the prototype runs locally on a single workstation

### 1.4 Success Criteria

The prototype successfully demonstrates:

1. An investigator can select a pre-staged case and begin an AI-assisted investigation within seconds, with all case data already loaded
2. The AI correctly follows the investigation methodology, references the decision matrix, and produces case form outputs consistent with the existing SAFU GPT agent's quality
3. The AI retrieves reference documents (SOPs, guidelines) on demand when needed, without loading unnecessary material into context
4. A complete investigation conversation can be conducted within the model's context window (200K tokens) without degradation
5. The end-to-end experience of working through a case is faster and smoother than the current SAFU GPT workflow
6. The architecture is extensible — the same system can accommodate live data ingestion, additional tools, and real authentication in future phases without structural rework

---

## 2. Architecture Overview

### 2.1 System Components

The platform consists of four components:

| Component | Technology | Role |
|-----------|-----------|------|
| **Frontend** | React (Vite) + Tailwind CSS | Dashboard, chat interface, case data display |
| **Backend** | Python / FastAPI | API server, conversation management, AI orchestration, tool handling, knowledge base serving |
| **Database** | MongoDB Community Edition (local) | Case records, conversation history, user sessions |
| **AI Model** | Anthropic Claude (Opus / Sonnet) via API | Investigation assistant, document analysis, case form drafting |
| **Knowledge Base** | Markdown files on server filesystem | System prompt, core documents, reference documents (SOPs, guidelines) |

### 2.2 System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                       FRONTEND                          │
│              React (Vite) + Tailwind CSS                │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │  Login   │  │  Case Select  │  │  Chat Interface   │ │
│  │  (mock)  │  │  + Overview   │  │  + Case Data Panel│ │
│  └──────────┘  └──────────────┘  └───────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API (JSON)
                       │
┌──────────────────────┴──────────────────────────────────┐
│                       BACKEND                           │
│                  Python / FastAPI                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ Auth (mock)  │  │ Conversation │  │  Tool Handler  │ │
│  │              │  │  Manager     │  │  (KB retrieval)│ │
│  └──────────────┘  └──────┬───────┘  └───────┬───────┘ │
│                           │                   │         │
│  ┌──────────────┐  ┌──────┴───────┐  ┌───────┴───────┐ │
│  │ Case Data    │  │  AI Client   │  │  Knowledge    │ │
│  │ Service      │  │  (Anthropic) │  │  Base Loader  │ │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘ │
└─────────┼─────────────────┼───────────────────┼─────────┘
          │                 │                   │
    ┌─────┴─────┐    ┌─────┴──────┐   ┌────────┴────────┐
    │  MongoDB  │    │ Anthropic  │   │   Filesystem    │
    │  (local)  │    │ Claude API │   │  /knowledge_base│
    └───────────┘    └────────────┘   └─────────────────┘
```

### 2.3 Data Flow — Investigation Conversation

The following sequence describes the complete lifecycle of a single message exchange during an investigation:

**1. User sends a message** → Frontend sends `POST /api/chat` with `case_id`, `conversation_id`, and message content (text, or text + base64 image).

**2. Backend assembles the API payload:**
   - Retrieves the full conversation history from MongoDB
   - Loads the system prompt (cached in memory on server startup)
   - Loads the core knowledge base documents (cached in memory on server startup)
   - Loads the YAML reference document index (cached in memory on server startup)
   - Retrieves the pre-staged case data from MongoDB
   - Assembles the complete messages array: system prompt → case data (injected as first user/assistant exchange) → conversation history → new user message
   - Attaches tool definitions (reference document retrieval)

**3. Backend calls the Anthropic API** with the assembled payload.

**4. If the AI responds with a tool call** (e.g., requesting a reference document):
   - Backend reads the requested `.md` file from disk
   - Returns the file content as a tool result
   - Sends the updated messages (including tool call and result) back to the API
   - This loop repeats if the AI makes additional tool calls
   - The final text response is captured

**5. Backend stores the conversation turn** — the user message, any tool interactions, and the final assistant response are saved to MongoDB.

**6. Backend returns the response** to the frontend, which renders it in the chat interface.

### 2.4 Knowledge Base Architecture

The knowledge base is split into two tiers based on usage patterns:

**Tier 1 — Core Documents (loaded every conversation)**

Injected into the system prompt on every API call. These are documents the AI needs regardless of case type. Loaded from filesystem into server memory on startup. Approximate total: ~72,000 tokens.

Contents: system prompt, decision matrix, QC checklist, escalation rules, step-by-step case form guides, investigation methodology.

**Tier 2 — Reference Documents (available on demand via tool call)**

Not loaded by default. The AI receives a structured YAML index describing each document and what it covers. When the AI determines it needs a specific reference document during an investigation, it calls the `get_reference_document` tool. The backend reads the file from disk and returns the full content as a tool result, which then becomes part of the conversation context.

Contents: scam/fraud SOP, FTM SOP, CTM on-chain alerts SOP, block/unblock guidelines, fake documents guidelines, gambling legality matrix, MLRO escalation decisions, case decision archive.

This approach keeps the baseline context usage at ~75K tokens (core docs + YAML index), leaving ~125K tokens available for case data, conversation history, and any reference documents the AI retrieves during the investigation.

### 2.5 Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| Raw Anthropic API, not SAFU GPT API | Tool use support is essential for the knowledge base architecture. The Anthropic API is fully documented and can be developed against externally using a personal API key. SafuAPI deployment can be adopted later by changing the base URL. |
| Knowledge base on filesystem, not in database | SOPs and guidelines are static reference material. Filesystem storage is simpler, easier to update, and version-controllable. MongoDB is reserved for runtime data. |
| All core documents loaded upfront, reference docs via tool call | Core documents are needed on every case. Reference documents are case-type-dependent. Tool-based retrieval keeps context lean, gives the AI control over what it loads, and provides a clear record of which documents were consulted. |
| Conversation history in MongoDB, not in-memory | Conversations must survive server restarts and be queryable. MongoDB document model maps naturally to conversation turns. |
| Pre-staged case data for MVP | Live data ingestion requires API access to multiple Binance internal systems. Pre-staging eliminates this dependency and allows the prototype to demonstrate the investigation experience without blocked dependencies. |
| Build on Anthropic SDK directly | Enables development outside the Binance network. The SDK is well-documented, supports tool use, streaming, vision, and conversation management. The same code works against any Anthropic-compatible endpoint. |

---

## 3. API Contract

All endpoints are served by the FastAPI backend at `http://localhost:8000`. The frontend communicates exclusively through these endpoints. All request and response bodies are JSON unless otherwise noted.

### 3.1 Authentication (Mock)

#### `POST /api/auth/login`

Mock authentication. Accepts a username and returns a session token. No password validation in the prototype.

**Request:**
```json
{
  "username": "ben.investigator"
}
```

**Response:**
```json
{
  "user_id": "user_001",
  "username": "ben.investigator",
  "display_name": "Ben",
  "token": "mock-session-token-uuid"
}
```

**Notes:** The token is returned in the response and must be sent as a `Bearer` token in the `Authorization` header on all subsequent requests. For the prototype, the backend generates a UUID and stores the session in MongoDB. No expiry, no password, no validation beyond checking the username exists in a hardcoded list.

#### `GET /api/auth/me`

Returns the current user based on the session token.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user_id": "user_001",
  "username": "ben.investigator",
  "display_name": "Ben"
}
```

---

### 3.2 Cases

#### `GET /api/cases`

Returns all available cases for the logged-in user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "cases": [
    {
      "case_id": "CASE-2026-0451",
      "case_type": "scam",
      "subject_user_id": "BIN-84729103",
      "status": "open",
      "summary": "Suspected romance scam — multiple outbound transfers to flagged counterparties",
      "created_at": "2026-03-01T09:00:00Z",
      "conversation_id": null
    }
  ]
}
```

**Notes:** `conversation_id` is `null` if no investigation conversation has been started for this case. `status` values for MVP: `open`, `in_progress`, `completed`.

#### `GET /api/cases/{case_id}`

Returns full case details including all pre-staged preprocessed data.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "case_id": "CASE-2026-0451",
  "case_type": "scam",
  "status": "open",
  "subject_user_id": "BIN-84729103",
  "summary": "Suspected romance scam — multiple outbound transfers to flagged counterparties",
  "conversation_id": null,
  "created_at": "2026-03-01T09:00:00Z",
  "preprocessed_data": {
    "c360_analysis": "## Counterparty Risk Summary\n...",
    "elliptic_analysis": "## Wallet Screening Results\n...",
    "previous_cases": "## Prior Investigations\n...",
    "chat_history_summary": "## L1 Customer Service Interactions\n...",
    "kyc_summary": "## KYC Information\n...",
    "law_enforcement": "## Law Enforcement Cases\n..."
  }
}
```

**Notes:** The `preprocessed_data` object contains markdown strings — each field represents one category of pre-processed case data. These are displayed in the frontend case overview panel and injected into the AI conversation context by the backend. For the MVP, all of this data is manually prepared from sanitised real cases and stored in MongoDB during demo setup. The field set may vary per case (e.g., not all cases have law enforcement data).

---

### 3.3 Conversations

#### `POST /api/conversations`

Creates a new investigation conversation for a case. This triggers the backend to assemble the initial context (system prompt, knowledge base, case data) and send the opening message to the AI, which will produce the initial case assessment.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "case_id": "CASE-2026-0451"
}
```

**Response:**
```json
{
  "conversation_id": "conv_abc123",
  "case_id": "CASE-2026-0451",
  "initial_response": {
    "role": "assistant",
    "content": "## Initial Case Assessment\n\nBased on the case data provided...",
    "tools_used": [],
    "token_usage": {
      "input_tokens": 78500,
      "output_tokens": 1200
    },
    "timestamp": "2026-03-01T09:05:00Z"
  }
}
```

**Notes:** When a conversation is created, the backend automatically injects all pre-staged case data into the conversation as a hidden context message (the user never sent it, but the AI sees it). The AI is instructed in the system prompt to begin with an initial assessment of the case. This means the investigator opens the chat and immediately sees the AI's first take on the case without having to prompt it. The case's `conversation_id` and `status` are updated in MongoDB.

#### `POST /api/conversations/{conversation_id}/messages`

Sends a new message in an existing conversation. This is the primary chat endpoint.

**Headers:** `Authorization: Bearer <token>`

**Request (text only):**
```json
{
  "content": "What does the counterparty transaction pattern suggest about the flow of funds?"
}
```

**Request (text with image):**
```json
{
  "content": "Here is the KYC document. Does the name match what we have on file?",
  "images": [
    {
      "base64": "/9j/4AAQSkZJRg...",
      "media_type": "image/jpeg"
    }
  ]
}
```

**Response (non-streaming):**
```json
{
  "message_id": "msg_xyz789",
  "role": "assistant",
  "content": "The counterparty transaction pattern shows...",
  "tools_used": [
    {
      "tool": "get_reference_document",
      "document_id": "scam-fraud-sop",
      "document_title": "Scam & Fraud Investigation SOP"
    }
  ],
  "token_usage": {
    "input_tokens": 82000,
    "output_tokens": 850
  },
  "timestamp": "2026-03-01T09:07:30Z"
}
```

**Response (streaming):** If streaming is enabled, this endpoint returns a `text/event-stream` response. Each event contains a chunk of the assistant's response:

```
data: {"type": "content_delta", "text": "The counterparty"}
data: {"type": "content_delta", "text": " transaction pattern"}
data: {"type": "tool_use", "tool": "get_reference_document", "document_id": "scam-fraud-sop"}
data: {"type": "content_delta", "text": " shows..."}
data: {"type": "done", "message_id": "msg_xyz789", "token_usage": {"input_tokens": 82000, "output_tokens": 850}}
```

**Notes:** The `tools_used` array tells the frontend which reference documents the AI consulted during this response. This is informational — it lets the investigator see what the AI referenced, which supports transparency and trust. The `images` array supports multiple images per message. Images are sent as base64 with their media type. The backend converts these into Anthropic API image content blocks.

#### `GET /api/conversations/{conversation_id}/history`

Returns the full conversation history for display. Used when the frontend needs to reload a conversation (e.g., returning to a case in progress).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "conversation_id": "conv_abc123",
  "case_id": "CASE-2026-0451",
  "messages": [
    {
      "message_id": "msg_001",
      "role": "assistant",
      "content": "## Initial Case Assessment\n...",
      "tools_used": [],
      "timestamp": "2026-03-01T09:05:00Z"
    },
    {
      "message_id": "msg_002",
      "role": "user",
      "content": "What does the counterparty transaction pattern suggest?",
      "images": [],
      "timestamp": "2026-03-01T09:06:00Z"
    },
    {
      "message_id": "msg_003",
      "role": "assistant",
      "content": "The counterparty transaction pattern shows...",
      "tools_used": [{"tool": "get_reference_document", "document_id": "scam-fraud-sop", "document_title": "Scam & Fraud Investigation SOP"}],
      "timestamp": "2026-03-01T09:07:30Z"
    }
  ]
}
```

**Notes:** This returns only the messages the user should see. Hidden context messages (case data injection, system prompt) are not included. Images are returned as references, not full base64, to keep the payload manageable — the frontend can request full images separately if needed, or the images can be stored as references to uploaded files.

---

### 3.4 System / Utility

#### `GET /api/health`

Health check for the backend server.

**Response:**
```json
{
  "status": "ok",
  "mongodb": "connected",
  "knowledge_base_loaded": true,
  "core_documents_tokens": 72000,
  "reference_documents_available": 8
}
```

#### `GET /api/knowledge-base/index`

Returns the reference document index. Useful for debugging and for the frontend to display what reference material is available.

**Response:**
```json
{
  "reference_documents": [
    {
      "id": "scam-fraud-sop",
      "title": "Scam & Fraud Investigation SOP",
      "covers": [
        "First-party and third-party scam classification",
        "Victim vs willing participant indicators",
        "Romance scam, investment scam, impersonation patterns"
      ],
      "token_estimate": 8000
    }
  ]
}
```

---

## 4. Data Models

### 4.1 MongoDB Collections

The prototype uses three collections. Schemas are shown as the document structure stored in MongoDB.

#### Collection: `users`

Stores mock user records. Pre-populated during setup.

```json
{
  "_id": "user_001",
  "username": "ben.investigator",
  "display_name": "Ben",
  "created_at": "2026-03-01T00:00:00Z"
}
```

#### Collection: `cases`

Stores case records with pre-staged preprocessed data.

```json
{
  "_id": "CASE-2026-0451",
  "case_type": "scam",
  "status": "open",
  "subject_user_id": "BIN-84729103",
  "summary": "Suspected romance scam — multiple outbound transfers to flagged counterparties",
  "assigned_to": "user_001",
  "conversation_id": null,
  "preprocessed_data": {
    "c360_analysis": "## Counterparty Risk Summary\n...",
    "elliptic_analysis": "## Wallet Screening Results\n...",
    "previous_cases": "## Prior Investigations\n...",
    "chat_history_summary": "## L1 Customer Service Interactions\n...",
    "kyc_summary": "## KYC Information\n...",
    "law_enforcement": "## Law Enforcement Cases\n..."
  },
  "created_at": "2026-03-01T09:00:00Z",
  "updated_at": "2026-03-01T09:00:00Z"
}
```

**Notes:** `preprocessed_data` fields are all optional — not every case has every data type. Each field contains a markdown string representing the compressed, pre-processed output for that data category. For the MVP, these are manually prepared from sanitised real cases.

#### Collection: `conversations`

Stores conversation history as an array of turns within a single document.

```json
{
  "_id": "conv_abc123",
  "case_id": "CASE-2026-0451",
  "user_id": "user_001",
  "status": "active",
  "messages": [
    {
      "message_id": "msg_001",
      "role": "system_injected",
      "content": "[Hidden] Case data and context injection",
      "timestamp": "2026-03-01T09:05:00Z",
      "visible": false
    },
    {
      "message_id": "msg_002",
      "role": "assistant",
      "content": "## Initial Case Assessment\n...",
      "tools_used": [],
      "token_usage": {"input_tokens": 78500, "output_tokens": 1200},
      "timestamp": "2026-03-01T09:05:02Z",
      "visible": true
    },
    {
      "message_id": "msg_003",
      "role": "user",
      "content": "What does the counterparty pattern suggest?",
      "images": [
        {
          "image_id": "img_001",
          "media_type": "image/jpeg",
          "stored_path": "/data/images/conv_abc123/img_001.jpg"
        }
      ],
      "timestamp": "2026-03-01T09:06:00Z",
      "visible": true
    },
    {
      "message_id": "msg_004",
      "role": "assistant",
      "content": "The counterparty transaction pattern shows...",
      "tools_used": [
        {
          "tool": "get_reference_document",
          "document_id": "scam-fraud-sop",
          "document_title": "Scam & Fraud Investigation SOP"
        }
      ],
      "token_usage": {"input_tokens": 82000, "output_tokens": 850},
      "timestamp": "2026-03-01T09:07:30Z",
      "visible": true
    }
  ],
  "created_at": "2026-03-01T09:05:00Z",
  "updated_at": "2026-03-01T09:07:30Z"
}
```

**Notes on conversation storage:**

The entire conversation is stored as a single document with an embedded `messages` array. This is a deliberate choice for the prototype — it simplifies retrieval (one read to get the full history) and aligns with how the data is consumed (the backend needs the full history on every API call). For production scale with very long conversations, this could be refactored to a separate `messages` collection with an index on `conversation_id`, but for the MVP the embedded approach is simpler and faster.

The `visible` flag distinguishes between messages shown to the user in the frontend and hidden context injections (case data, system context). The `GET /api/conversations/{id}/history` endpoint filters to `visible: true` only.

The `tools_used` array on assistant messages records which reference documents the AI requested during that turn. This provides a lightweight audit trail of which SOPs and guidelines informed each response.

Images are stored as files on disk (not base64 in MongoDB) with a reference in the message. For the MVP, a simple `/data/images/{conversation_id}/` directory structure is sufficient. The base64 is written to disk when received and the path is stored in the message.

### 4.2 Filesystem Structure

```
/project-root
│
├── /server                         # FastAPI backend
│   ├── main.py                     # App entry point, startup events
│   ├── config.py                   # API keys, MongoDB URI, model settings
│   ├── /routers
│   │   ├── auth.py                 # Mock auth endpoints
│   │   ├── cases.py                # Case CRUD endpoints
│   │   └── conversations.py        # Chat + conversation endpoints
│   ├── /services
│   │   ├── ai_client.py            # Anthropic API wrapper, payload assembly
│   │   ├── conversation_manager.py # History retrieval, turn storage, context assembly
│   │   ├── knowledge_base.py       # Document loading, YAML index, tool handler
│   │   └── case_service.py         # Case data retrieval from MongoDB
│   └── /models
│       └── schemas.py              # Pydantic models for request/response validation
│
├── /knowledge_base
│   ├── /core                       # Tier 1: loaded every conversation
│   │   ├── system-prompt.md
│   │   ├── decision-matrix.md
│   │   ├── qc-checklist.md
│   │   ├── escalation-rules.md
│   │   └── case-form-guides.md
│   ├── /reference                  # Tier 2: available via tool call
│   │   ├── scam-fraud-sop.md
│   │   ├── ftm-sop.md
│   │   ├── CTM-on-chain-alerts-sop.md
│   │   ├── block-unblock-guidelines.md
│   │   ├── fake-documents-guidelines.md
│   │   ├── gambling-legality-matrix.md
│   │   ├── mlro-escalation-decisions.md
│   │   └── case-decision-archive.md
│   └── reference-index.yaml        # YAML index of reference documents
│
├── /client                         # React frontend
│   ├── /src
│   │   ├── /components
│   │   ├── /pages
│   │   ├── /services               # API client functions
│   │   └── App.jsx
│   ├── index.html
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── /data
│   └── /images                     # Uploaded images stored by conversation
│       └── /{conversation_id}/
│
└── /scripts
    └── seed_demo_data.py           # Script to populate MongoDB with demo cases and users
```

### 4.3 YAML Reference Index

The reference index file loaded on startup and included in the system prompt. This is what the AI uses to decide which documents to request.

```yaml
# /knowledge_base/reference-index.yaml

reference_documents:

  - id: scam-fraud-sop
    title: "Scam & Fraud Investigation SOP"
    filename: "scam-fraud-sop.md"
    covers:
      - First-party and third-party scam classification
      - Victim vs willing participant determination
      - Romance scam, investment scam, impersonation scam patterns
      - Refund eligibility criteria and process
      - Evidence thresholds for escalation to Level 3
    token_estimate: 8000

  - id: ftm-sop
    title: "Fiat Transaction Monitoring SOP"
    filename: "ftm-sop.md"
    covers:
      - Fiat deposit and withdrawal monitoring rules
      - Failed fiat transaction investigation procedures
      - Bank return and chargeback handling
      - Suspicious fiat activity indicators
    token_estimate: 7000

  - id: ctm-on-chain-alerts-sop
    title: "Crypto Transaction Monitoring — On-Chain Alerts SOP"
    filename: "CTM-on-chain-alerts-sop.md"
    covers:
      - On-chain alert triage and investigation
      - Wallet clustering and counterparty risk assessment
      - Interaction with sanctioned or high-risk entities
      - VASP-to-VASP transaction analysis
    token_estimate: 7000

  - id: block-unblock-guidelines
    title: "Account Block & Unblock Guidelines"
    filename: "block-unblock-guidelines.md"
    covers:
      - Grounds for full account block
      - Grounds for partial restriction
      - Offboarding criteria and process
      - Unblock request evaluation criteria
      - Block history interpretation
    token_estimate: 5000

  - id: fake-documents-guidelines
    title: "Fake Documents Detection Guidelines"
    filename: "fake-documents-guidelines.md"
    covers:
      - KYC document fraud indicators
      - Photo manipulation detection
      - Document consistency checks
      - Escalation process for suspected fake documents
    token_estimate: 4000

  - id: gambling-legality-matrix
    title: "Gambling Legality Matrix"
    filename: "gambling-legality-matrix.md"
    covers:
      - Jurisdiction-specific gambling legality status
      - Licensed vs unlicensed gambling platform identification
      - Regulatory treatment by country
      - Investigation approach for gambling-related cases
    token_estimate: 6000

  - id: mlro-escalation-decisions
    title: "MLRO Escalation Decisions"
    filename: "mlro-escalation-decisions.md"
    covers:
      - Criteria for MLRO escalation
      - Historical MLRO decision outcomes
      - SAR filing thresholds and considerations
      - Escalation documentation requirements
    token_estimate: 5000

  - id: case-decision-archive
    title: "Historical Case Decision Archive"
    filename: "case-decision-archive.md"
    covers:
      - Past QC decisions and management rationale
      - Edge case rulings by case type
      - Precedent decisions for recurring scenarios
      - Common QC failure patterns and corrections
    token_estimate: 15000
```

**Notes:** The `covers` descriptions should be refined once the actual document contents are reviewed — the AI uses these to decide whether to request a document, so accuracy matters. The `token_estimate` values help the AI (and the backend, in future) make informed decisions about context budget when multiple documents are being considered.

---

## 5. Conversation Flow

This section describes the complete lifecycle of an investigation conversation, from case selection through to the final response. This is the core logic of the backend and the most complex part of the system.

### 5.1 Starting an Investigation

When the investigator selects a case and clicks "Start Investigation", the following sequence executes:

```
Investigator clicks "Start Investigation" on CASE-2026-0451
        │
        ▼
Frontend: POST /api/conversations  { case_id: "CASE-2026-0451" }
        │
        ▼
Backend: conversation_manager.create_conversation()
        │
        ├── 1. Load case from MongoDB (including preprocessed_data)
        │
        ├── 2. Assemble the initial API payload:
        │       ┌─────────────────────────────────────────────┐
        │       │ SYSTEM PROMPT                                │
        │       │  - system-prompt.md content                  │
        │       │  - decision-matrix.md content                │
        │       │  - qc-checklist.md content                   │
        │       │  - escalation-rules.md content               │
        │       │  - case-form-guides.md content               │
        │       │  - reference-index.yaml (formatted as text)  │
        │       │  [All cached in memory — no disk reads]      │
        │       └─────────────────────────────────────────────┘
        │       ┌─────────────────────────────────────────────┐
        │       │ MESSAGES ARRAY                               │
        │       │  [0] role: "user"                            │
        │       │      content: "[CASE DATA]\n{all fields     │
        │       │      from preprocessed_data, concatenated    │
        │       │      as markdown}\n\nPlease begin your       │
        │       │      initial assessment of this case."       │
        │       └─────────────────────────────────────────────┘
        │       ┌─────────────────────────────────────────────┐
        │       │ TOOLS                                        │
        │       │  - get_reference_document(document_id: str)  │
        │       └─────────────────────────────────────────────┘
        │
        ├── 3. Call Anthropic API
        │
        ├── 4. Handle tool calls (if AI requests reference docs)
        │       └── Loop: call API → tool response → call API
        │           until final text response received
        │
        ├── 5. Store conversation in MongoDB:
        │       - Hidden context message (case data injection, visible: false)
        │       - Assistant's initial assessment (visible: true)
        │
        ├── 6. Update case status to "in_progress"
        │       Update case conversation_id
        │
        └── 7. Return initial_response to frontend
                │
                ▼
        Frontend renders the AI's initial case assessment in the chat
```

### 5.2 Sending a Message (Standard Turn)

Each subsequent message follows this sequence:

```
Investigator types a message (optionally pastes/uploads images)
        │
        ▼
Frontend: POST /api/conversations/{id}/messages
          { content: "...", images: [...] }
        │
        ▼
Backend: conversation_manager.send_message()
        │
        ├── 1. Retrieve conversation from MongoDB
        │       (full messages array including hidden context)
        │
        ├── 2. Assemble the API payload:
        │       ┌─────────────────────────────────────────────┐
        │       │ SYSTEM PROMPT (same as initial — from cache) │
        │       └─────────────────────────────────────────────┘
        │       ┌─────────────────────────────────────────────┐
        │       │ MESSAGES ARRAY                               │
        │       │  [0] Hidden case data message (from DB)      │
        │       │  [1] Assistant initial assessment (from DB)  │
        │       │  [2] User message (from DB)                  │
        │       │  [3] Assistant response (from DB)            │
        │       │  ... all previous turns from DB ...          │
        │       │  [N] New user message (from request)         │
        │       │      - text content block                    │
        │       │      - image content blocks (if any)         │
        │       └─────────────────────────────────────────────┘
        │       ┌─────────────────────────────────────────────┐
        │       │ TOOLS (same as initial)                      │
        │       └─────────────────────────────────────────────┘
        │
        ├── 3. Call Anthropic API (with streaming if supported)
        │
        ├── 4. Handle tool calls (if any — same loop as initial)
        │
        ├── 5. Append new messages to conversation in MongoDB:
        │       - User message (visible: true)
        │       - Any tool interactions (visible: false)
        │       - Assistant response (visible: true)
        │
        └── 6. Return response to frontend
                │
                ▼
        Frontend appends the AI response to the chat display
```

### 5.3 Tool Call Handling (Reference Document Retrieval)

When the AI decides it needs a reference document, the API returns a `tool_use` stop reason instead of a text response. The backend must handle this transparently:

```
API Response: stop_reason = "tool_use"
        │
        ▼
Backend detects tool_use in response
        │
        ├── Extract tool call: get_reference_document(document_id="scam-fraud-sop")
        │
        ├── Look up filename from reference-index.yaml
        │
        ├── Read /knowledge_base/reference/scam-fraud-sop.md from disk
        │
        ├── Append to messages array:
        │       - The assistant's tool_use message (as returned by API)
        │       - A tool_result message containing the document content
        │
        ├── Call Anthropic API again with updated messages
        │
        └── If response is another tool_use → repeat loop
            If response is text → return as final response
```

**Important:** The tool call loop must have a safety limit (e.g., maximum 5 tool calls per turn) to prevent infinite loops. In practice, the AI will rarely call more than 2 reference documents in a single turn.

**Context window consideration:** Each retrieved reference document adds to the conversation's token count permanently (it becomes part of the messages history). The backend should track cumulative token usage from the API's `usage` response field. For the MVP, log a warning if total input tokens exceed 150K (75% of the 200K window). This gives early visibility into whether context is becoming a constraint.

### 5.4 Resuming a Conversation

When an investigator returns to a case that already has an active conversation:

```
Frontend: GET /api/cases → finds case with conversation_id != null
Frontend: GET /api/conversations/{id}/history → renders chat history
Investigator continues chatting → normal message flow (5.2)
```

No special handling needed — the full history is in MongoDB, the backend reassembles the complete context on every message.

### 5.5 Context Assembly Summary

For clarity, here is exactly what goes into each Anthropic API call:

| Payload component | Source | Approximate tokens |
|---|---|---|
| System prompt (Anthropic `system` parameter) | Cached from `/knowledge_base/core/` on startup | ~72,000 |
| Reference document index | Cached from `reference-index.yaml` on startup | ~1,500 |
| Case data (first message in array) | From MongoDB case record | ~10,000–20,000 |
| Conversation history | From MongoDB conversation record | Grows per turn (~500–2,000 per exchange) |
| Retrieved reference documents (if any) | From tool call results in history | ~4,000–15,000 per document |
| New user message | From current request | Variable |
| **Typical total at conversation start** | | **~85,000–95,000** |
| **Typical total mid-investigation (15 turns, 1 ref doc loaded)** | | **~110,000–130,000** |

This leaves comfortable headroom within a 200K context window for even complex investigations.

---

## 6. Tool Use Specification

### 6.1 Tool Definition

The following tool definition is sent with every Anthropic API call. It follows the Anthropic tool use specification.

```python
TOOLS = [
    {
        "name": "get_reference_document",
        "description": (
            "Retrieve a reference document from the knowledge base. "
            "Use this tool when you need detailed procedural guidance, "
            "SOP requirements, or historical decision precedents that are "
            "not covered by your core knowledge. Consult the reference "
            "document index in your system prompt to identify the correct "
            "document_id. Only request documents that are directly relevant "
            "to the current investigation question or case form section."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": (
                        "The unique identifier of the reference document "
                        "to retrieve, as listed in the reference document index."
                    )
                }
            },
            "required": ["document_id"]
        }
    }
]
```

### 6.2 Tool Handler Implementation

```python
# /server/services/knowledge_base.py

import yaml
from pathlib import Path

class KnowledgeBase:
    def __init__(self, base_path: str = "./knowledge_base"):
        self.base_path = Path(base_path)
        self.core_content: str = ""
        self.reference_index: list[dict] = []
        self.reference_index_text: str = ""

    def load_on_startup(self):
        """Load core documents and reference index into memory."""
        # Load all core documents
        core_parts = []
        core_dir = self.base_path / "core"
        for filepath in sorted(core_dir.glob("*.md")):
            content = filepath.read_text(encoding="utf-8")
            core_parts.append(f"# {filepath.stem.upper()}\n\n{content}")
        self.core_content = "\n\n---\n\n".join(core_parts)

        # Load reference index
        index_path = self.base_path / "reference-index.yaml"
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = yaml.safe_load(f)
        self.reference_index = index_data["reference_documents"]

        # Format index as text for system prompt injection
        lines = ["## REFERENCE DOCUMENT INDEX",
                 "",
                 "The following reference documents are available via the "
                 "get_reference_document tool. Review the coverage descriptions "
                 "to determine which document is relevant before requesting it.",
                 ""]
        for doc in self.reference_index:
            lines.append(f"### {doc['title']}")
            lines.append(f"- **ID:** `{doc['id']}`")
            lines.append(f"- **Covers:**")
            for item in doc["covers"]:
                lines.append(f"  - {item}")
            lines.append(f"- **Approximate size:** {doc['token_estimate']:,} tokens")
            lines.append("")
        self.reference_index_text = "\n".join(lines)

    def get_system_prompt(self) -> str:
        """Return the complete system prompt: core docs + reference index."""
        return f"{self.core_content}\n\n---\n\n{self.reference_index_text}"

    def get_reference_document(self, document_id: str) -> str:
        """Retrieve a reference document by ID. Called by the tool handler."""
        # Validate document_id against index
        valid_ids = {doc["id"]: doc["filename"] for doc in self.reference_index}
        if document_id not in valid_ids:
            return f"Error: Unknown document ID '{document_id}'. Valid IDs: {', '.join(valid_ids.keys())}"

        filepath = self.base_path / "reference" / valid_ids[document_id]
        if not filepath.exists():
            return f"Error: Document file not found for '{document_id}'."

        return filepath.read_text(encoding="utf-8")
```

### 6.3 Tool Call Processing Loop

```python
# /server/services/ai_client.py (relevant excerpt)

import anthropic

MAX_TOOL_CALLS_PER_TURN = 5

async def get_ai_response(
    client: anthropic.Anthropic,
    system_prompt: str,
    messages: list[dict],
    tools: list[dict],
    knowledge_base: KnowledgeBase,
    model: str = "claude-sonnet-4-20250514"
) -> dict:
    """
    Send messages to the Anthropic API and handle tool calls.
    Returns the final assistant response and metadata.
    """
    tools_used = []
    tool_call_count = 0

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=tools
        )

        # If the response is a final text response, we're done
        if response.stop_reason == "end_turn":
            assistant_text = ""
            for block in response.content:
                if block.type == "text":
                    assistant_text += block.text
            return {
                "content": assistant_text,
                "tools_used": tools_used,
                "token_usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        # If the response contains tool use, handle it
        if response.stop_reason == "tool_use":
            tool_call_count += 1
            if tool_call_count > MAX_TOOL_CALLS_PER_TURN:
                # Safety limit reached — force a text response
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": "Maximum reference documents reached for this turn. "
                               "Please provide your response with the information available."
                })
                continue

            # Append the assistant's tool use message
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call in the response
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "get_reference_document":
                        doc_id = block.input["document_id"]
                        doc_content = knowledge_base.get_reference_document(doc_id)

                        # Track which documents were used
                        doc_meta = next(
                            (d for d in knowledge_base.reference_index if d["id"] == doc_id),
                            None
                        )
                        tools_used.append({
                            "tool": "get_reference_document",
                            "document_id": doc_id,
                            "document_title": doc_meta["title"] if doc_meta else doc_id
                        })

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": doc_content
                        })

            # Append tool results and loop back for the next API call
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason — return whatever we have
            assistant_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    assistant_text += block.text
            return {
                "content": assistant_text or "[No response generated]",
                "tools_used": tools_used,
                "token_usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
```

### 6.4 Future Tool Expansion

The tool system is designed to be extensible. Additional tools that could be added in subsequent phases without architectural changes:

| Tool | Phase | Purpose |
|------|-------|---------|
| `get_reference_document` | MVP (Phase 1) | Retrieve SOPs and guidelines on demand |
| `search_case_decisions` | Phase 2 | Search the case decision archive by keyword or case type, returning relevant excerpts rather than the full document |
| `screen_wallet` | Phase 2 | Call the Elliptic API to screen a wallet address in real time |
| `get_user_profile` | Phase 2+ | Fetch user details from Binance Admin API |
| `get_transaction_history` | Phase 2+ | Query C360 data via API |
| `submit_case_section` | Phase 3+ | Write a completed section directly to HowDesk (requires HowDesk API) |

Each new tool follows the same pattern: define the tool schema, add a handler function, register it in the tools array. The AI sees the new tool, understands when to use it from the description, and calls it when appropriate. No changes to the conversation flow or frontend required.

---

## 7. Knowledge Base File Manifest

### 7.1 Tier 1 — Core Documents (Loaded Every Conversation)

These files are loaded into server memory on startup and injected into the system prompt on every API call. They are organised on disk mirroring the original directory structure.

**System Prompt**

| File | Source Dir | Description | Est. Tokens |
|------|-----------|-------------|-------------|
| `SYSTEM-PROMPT.md` | Root | Master investigation methodology, AI persona, behavioural instructions, output format requirements | ~7,900 |

**FCI-CORE (3 files)**

| File | Description | Est. Tokens |
|------|-------------|-------------|
| `icr-general-rules.md` | General investigation case review rules and standards | Part of ~11,000 |
| `mlro-escalation-matrix.md` | MLRO escalation criteria matrix | Part of ~11,000 |
| `qc-submission-checklist.md` | Quality control checklist for case submission — AI uses this to self-verify outputs | Part of ~11,000 |

**FCI-LOOKUP (1 file)**

| File | Description | Est. Tokens |
|------|-------------|-------------|
| `decision-matrix.md` | Case classification rules derived from QC feedback and management decisions. The primary decision-making reference. | ~6,900 |

**FCI-PROCEDURES (4 files)**

| File | Description | Est. Tokens |
|------|-------------|-------------|
| `icr-steps-setup.md` | Step-by-step guide: case setup phase | Part of ~34,700 |
| `icr-steps-analysis.md` | Step-by-step guide: case analysis phase | Part of ~34,700 |
| `icr-steps-decision.md` | Step-by-step guide: decision and classification phase | Part of ~34,700 |
| `icr-steps-post.md` | Step-by-step guide: post-decision actions and submission | Part of ~34,700 |

**FCI-PROMPTS (1 file)**

| File | Description | Est. Tokens |
|------|-------------|-------------|
| `prompt-library.md` | Library of specialist prompts used by the AI during different investigation phases | ~11,100 |

**Tier 1 Total: 11 files, ~71,600 tokens**

**Filesystem layout on server:**
```
/knowledge_base/core/
├── SYSTEM-PROMPT.md
├── icr-general-rules.md
├── mlro-escalation-matrix.md
├── qc-submission-checklist.md
├── decision-matrix.md
├── icr-steps-setup.md
├── icr-steps-analysis.md
├── icr-steps-decision.md
├── icr-steps-post.md
└── prompt-library.md
```

All 11 files are flattened into a single `/core/` directory on the server regardless of their original directory structure. The original directory names (FCI-CORE, FCI-LOOKUP, etc.) are organisational categories, not meaningful boundaries for the AI. Flattening simplifies the loader — it reads every `.md` file in `/core/` and concatenates them.

### 7.2 Tier 2 — Reference Documents (Available via Tool Call)

These files are stored in `/knowledge_base/reference/` and served on demand when the AI calls the `get_reference_document` tool. They are indexed in `reference-index.yaml`.

| File | Description | Est. Tokens |
|------|-------------|-------------|
| `scam-fraud-sop.md` | Comprehensive SOP for investigating scam and fraud cases | ~8,000 |
| `ftm-sop.md` | Fiat Transaction Monitoring investigation procedures | ~7,000 |
| `CTM-on-chain-alerts-sop.md` | Crypto Transaction Monitoring on-chain alert SOP | ~7,000 |
| `block-unblock-guidelines.md` | Account blocking, unblocking, and offboarding rules | ~5,000 |
| `fake-documents-guidelines.md` | KYC document fraud detection guidance | ~4,000 |
| `gambling-legality-matrix.md` | Jurisdiction-specific gambling legality reference | ~6,000 |
| `mlro-escalation-decisions.md` | MLRO escalation criteria and historical outcomes | ~5,000 |
| `case-decision-archive.md` | Archive of past QC decisions and edge case rulings | ~15,000 |

**Total Tier 2:** ~57,000 tokens across 8 documents. Typically 0–2 documents are loaded per investigation, adding 0–20,000 tokens to the conversation context.

### 7.3 Configuration File

| File | Location | Purpose |
|------|----------|---------|
| `reference-index.yaml` | `/knowledge_base/reference-index.yaml` | Structured index of all Tier 2 documents with coverage descriptions. Loaded into memory on startup and appended to the system prompt. |

---

## 8. Frontend Layout & Components

The frontend is a single-page React application (Vite + Tailwind CSS) with three primary views. The design should be clean and professional — this is a tool for compliance investigators, not a consumer product. Prioritise clarity and information density over visual flair.

### 8.1 View 1 — Login

A simple login screen. For the MVP, this is a username input (no password) or a dropdown of pre-configured users.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│               FCI Investigation Platform                │
│                                                         │
│            ┌──────────────────────────┐                 │
│            │  Username                │                 │
│            └──────────────────────────┘                 │
│                                                         │
│                   [ Log In ]                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:** `LoginPage`, `LoginForm`

**Behaviour:** On successful login, store the session token in React state (not localStorage) and navigate to the Case List view.

### 8.2 View 2 — Case List

Displays all available cases for the logged-in user. Each case shows summary information and status.

```
┌─────────────────────────────────────────────────────────┐
│  FCI Investigation Platform          Logged in: Ben  ⏻  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Your Cases                                             │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ CASE-2026-0451  │ Scam  │ Open                     │ │
│  │ Suspected romance scam — multiple outbound          │ │
│  │ transfers to flagged counterparties                  │ │
│  │                              [ Open Case ]          │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ CASE-2026-0387  │ CTM   │ In Progress              │ │
│  │ On-chain alerts — interactions with sanctioned       │ │
│  │ wallet cluster                                       │ │
│  │                            [ Continue Case ]        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:** `CaseListPage`, `CaseCard`

**Behaviour:** "Open Case" navigates to the Investigation view and triggers `POST /api/conversations` to start a new investigation. "Continue Case" navigates to the Investigation view and loads the existing conversation via `GET /api/conversations/{id}/history`.

### 8.3 View 3 — Investigation (Primary Working View)

This is where the investigator spends their time. It consists of two panels: a case data panel on the left and the chat interface on the right.

```
┌─────────────────────────────────────────────────────────────────────┐
│  FCI Investigation Platform     CASE-2026-0451 (Scam)     Ben  ⏻   │
├───────────────────────────┬─────────────────────────────────────────┤
│                           │                                         │
│  CASE DATA                │  INVESTIGATION CHAT                     │
│                           │                                         │
│  ┌─ Subject ────────────┐ │  ┌─────────────────────────────────┐   │
│  │ User: BIN-84729103   │ │  │ AI: ## Initial Case Assessment  │   │
│  │ KYC: Verified        │ │  │                                 │   │
│  │ Status: Active       │ │  │ Based on the case data, this    │   │
│  └──────────────────────┘ │  │ presents as a likely romance    │   │
│                           │  │ scam scenario...                │   │
│  ┌─ Tabs ───────────────┐ │  │                                 │   │
│  │ C360 │ Elliptic │ LE │ │  │ Ref docs used: [none]          │   │
│  ├──────────────────────┤ │  └─────────────────────────────────┘   │
│  │                      │ │                                         │
│  │ ## Counterparty Risk │ │  ┌─────────────────────────────────┐   │
│  │                      │ │  │ You: What does the counterparty │   │
│  │ 3 flagged counter-   │ │  │ transaction pattern suggest?    │   │
│  │ parties identified:  │ │  └─────────────────────────────────┘   │
│  │ - 0x3f2...a8c (high) │ │                                         │
│  │ - 0x91b...d4f (med)  │ │  ┌─────────────────────────────────┐   │
│  │ ...                  │ │  │ AI: The pattern shows...        │   │
│  │                      │ │  │                                 │   │
│  │                      │ │  │ Ref docs used:                  │   │
│  │                      │ │  │  📄 Scam & Fraud SOP            │   │
│  │                      │ │  └─────────────────────────────────┘   │
│  │                      │ │                                         │
│  └──────────────────────┘ │  ┌─────────────────────────────────┐   │
│                           │  │ [📎 Upload] Type a message...   │   │
│                           │  │                          [Send] │   │
│                           │  └─────────────────────────────────┘   │
└───────────────────────────┴─────────────────────────────────────────┘
```

**Left Panel — Case Data:**

| Component | Description |
|-----------|-------------|
| `CaseHeader` | Subject user ID, KYC status, account status — always visible |
| `CaseDataTabs` | Tabbed navigation for different data categories |
| `CaseDataPanel` | Renders the markdown content for the selected tab |

The tabs map directly to the `preprocessed_data` fields from the case record: C360 Analysis, Elliptic Analysis, Previous Cases, Chat History, KYC, Law Enforcement. Each tab renders its markdown content. Tabs with no data are hidden.

**Right Panel — Chat Interface:**

| Component | Description |
|-----------|-------------|
| `ChatMessageList` | Scrollable list of messages, auto-scrolls to bottom |
| `ChatMessage` | Single message bubble. User messages right-aligned, AI messages left-aligned. AI messages show `tools_used` as a subtle footer (e.g., "Referenced: Scam & Fraud SOP"). |
| `ChatInput` | Text input with send button and image upload. Supports paste (for screenshots) and file picker (for images). Multi-line input. |
| `StreamingIndicator` | Visual indicator when waiting for / receiving a streaming AI response |

**Behaviour notes:**

- The chat should support markdown rendering in AI responses (headers, bold, lists, code blocks). Libraries like `react-markdown` handle this.
- Image uploads should show a thumbnail preview before sending.
- When an AI response is streaming, show tokens appearing in real time. If streaming is not available, show a typing/loading indicator.
- The case data panel is read-only — it displays the pre-staged data for reference. The investigator reads from it while working in the chat.
- The panel split should be resizable (or at minimum, a sensible default like 35/65 or 40/60).

### 8.4 Shared Components

| Component | Description |
|-----------|-------------|
| `AppLayout` | Top navigation bar with app name, current case ID and type, user name, logout |
| `MarkdownRenderer` | Reusable component for rendering markdown content (used in both case data panel and chat messages) |
| `ImageUpload` | Handles paste events, file picker, base64 conversion, and thumbnail preview |
| `LoadingSpinner` | Used while API calls are in flight |

### 8.5 Frontend State Management

For the MVP, React's built-in state management (`useState`, `useContext`) is sufficient. No Redux or external state library needed.

| State | Scope | Description |
|-------|-------|-------------|
| Auth token + user | App-level (Context) | Set on login, cleared on logout, included in all API calls |
| Case list | CaseListPage | Fetched on mount, refreshed on navigation back |
| Current case | Investigation view | Fetched when a case is opened |
| Conversation messages | Investigation view | Fetched on load (existing conversation) or initialised on creation. New messages appended as they arrive. |
| Chat input | ChatInput component | Local state for the current message draft and pending image uploads |

---

## 9. Pre-Staged Demo Data

### 9.1 Requirements

The prototype requires a minimum of 2–3 pre-staged cases to demonstrate the system. These cases should:

- Cover at least two different case types (e.g., scam and CTM) to demonstrate the AI adapting its approach and requesting different reference documents
- Contain realistic preprocessed data in all relevant categories
- Be fully sanitised — no real user data, wallet addresses, or identifiable information
- Be complex enough to sustain a full investigation conversation (15–25 turns)

### 9.2 Preparation Process

For each demo case:

1. **Select a real case** that has already been investigated and closed
2. **Run the case data through the existing workflow** — process C360 spreadsheets through the existing web app, screen wallets in Elliptic, extract LE data, summarise L1 chat history, compile previous cases
3. **Sanitise all outputs** — replace real user IDs, wallet addresses, names, transaction amounts, dates, and any other identifying information with fictional equivalents. The data structure and patterns must remain realistic.
4. **Store the sanitised outputs** as the `preprocessed_data` fields in the case's MongoDB record
5. **Prepare a brief case summary** for the case list display

### 9.3 Seed Script

A Python script (`/scripts/seed_demo_data.py`) populates MongoDB with demo data:

```python
"""
Seed script for FCI Investigation Platform demo data.

Populates MongoDB with:
- Mock user accounts
- Pre-staged sanitised case records with preprocessed data

Usage: python scripts/seed_demo_data.py
"""

from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "fci_platform"

def seed():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Clear existing data
    db.users.drop()
    db.cases.drop()
    db.conversations.drop()

    # Seed users
    db.users.insert_many([
        {
            "_id": "user_001",
            "username": "ben.investigator",
            "display_name": "Ben",
            "created_at": datetime.utcnow()
        },
        {
            "_id": "user_002",
            "username": "demo.investigator",
            "display_name": "Demo User",
            "created_at": datetime.utcnow()
        }
    ])

    # Seed cases — preprocessed_data loaded from files
    # In practice, each case's data would be loaded from
    # sanitised markdown files prepared during demo setup
    db.cases.insert_many([
        {
            "_id": "CASE-2026-0451",
            "case_type": "scam",
            "status": "open",
            "subject_user_id": "BIN-84729103",
            "summary": "Suspected romance scam — multiple outbound "
                       "transfers to flagged counterparties",
            "assigned_to": "user_001",
            "conversation_id": None,
            "preprocessed_data": {
                "c360_analysis": load_file("demo_data/case_0451/c360.md"),
                "elliptic_analysis": load_file("demo_data/case_0451/elliptic.md"),
                "previous_cases": load_file("demo_data/case_0451/previous.md"),
                "chat_history_summary": load_file("demo_data/case_0451/chat.md"),
                "kyc_summary": load_file("demo_data/case_0451/kyc.md"),
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Additional cases follow the same pattern
    ])

    print(f"Seeded {db.users.count_documents({})} users")
    print(f"Seeded {db.cases.count_documents({})} cases")

def load_file(path: str) -> str:
    """Load a markdown file as a string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    seed()
```

### 9.4 Demo Data Directory Structure

```
/demo_data
├── /case_0451                  # Scam case
│   ├── c360.md
│   ├── elliptic.md
│   ├── previous.md
│   ├── chat.md
│   └── kyc.md
├── /case_0387                  # CTM case
│   ├── c360.md
│   ├── elliptic.md
│   ├── law_enforcement.md
│   └── kyc.md
└── /case_0512                  # Fraud case (optional third case)
    ├── c360.md
    ├── elliptic.md
    ├── fake_documents.md
    └── kyc.md
```

---

## 10. Build Sequence & Timeline

### 10.1 Phase Overview

The two-week build is divided into three phases. The first phase must be complete before the second can begin meaningfully. The third phase is integration and polish.

| Phase | Days | Focus | Owner |
|-------|------|-------|-------|
| **Phase A: Backend Core** | Days 1–5 | FastAPI server, MongoDB, conversation management, AI integration with tool use | Ben |
| **Phase B: Frontend** | Days 4–10 | React app, all three views, chat interface, API integration | Colleague (with API contract from Phase A) |
| **Phase C: Integration & Demo Prep** | Days 10–14 | End-to-end testing, demo case preparation, bug fixes, polish | Both |

Note the overlap: the frontend can begin on Day 4 once the API contract is stable and a basic version of the backend is returning responses. The colleague can mock API responses before the backend is complete.

### 10.2 Phase A — Backend Core (Days 1–5)

**Day 1: Foundation + API validation**
- Scaffold the FastAPI project structure (routers, services, models)
- Set up MongoDB connection (Motor async driver)
- Test Anthropic API: basic chat, image input, streaming, tool use
- Confirm all API capabilities work before building on them
- **Milestone:** Successful API call with tool use returning a reference document

**Day 2: Knowledge base + system prompt assembly**
- Implement `KnowledgeBase` class (load core docs, load reference index, tool handler)
- Build the system prompt assembly (core docs + reference index)
- Implement the `get_reference_document` tool and processing loop
- Test: send a message that should trigger a document retrieval, verify the full loop
- **Milestone:** Complete system prompt + tool call working end-to-end via script

**Day 3: Conversation management**
- Implement conversation storage in MongoDB (create, append, retrieve)
- Build the context assembly logic (system prompt + case data + history + new message)
- Implement the full message send flow: retrieve history → assemble → call API → handle tools → store → return
- Test: multi-turn conversation via script, verify history builds correctly
- **Milestone:** Full multi-turn investigation conversation working via terminal/script

**Day 4: API endpoints**
- Implement all REST endpoints: auth, cases, conversations, health
- Wire endpoints to the services built on Days 2–3
- Handle image uploads (receive base64, store to disk, include in API calls)
- Test all endpoints via curl or Postman
- **Deliverable:** API contract document finalised and handed to colleague
- **Milestone:** All endpoints returning correct responses, colleague can begin frontend

**Day 5: Streaming + edge cases**
- Implement streaming response support (SSE from FastAPI)
- Handle error cases: API timeouts, tool call failures, invalid inputs
- Add token usage logging and context window monitoring
- Test with realistic case data volumes
- **Milestone:** Backend feature-complete for MVP

### 10.3 Phase B — Frontend (Days 4–10)

**Days 4–5: Scaffold + Login + Case List**
- Scaffold Vite + React + Tailwind project
- Build `LoginPage` (mock auth against backend)
- Build `CaseListPage` with `CaseCard` components
- Set up API client service and auth context
- Can use mocked API responses if backend isn't ready
- **Milestone:** Can log in and see case list

**Days 6–7: Investigation View — Case Data Panel**
- Build the two-panel layout (case data left, chat right)
- Implement `CaseDataTabs` and `CaseDataPanel`
- Render markdown content from case data
- **Milestone:** Can open a case and see preprocessed data in tabs

**Days 8–9: Investigation View — Chat Interface**
- Build `ChatMessageList`, `ChatMessage`, `ChatInput`
- Implement message sending via API
- Render markdown in AI responses
- Display tool usage footer on AI messages
- Implement image paste/upload with preview
- **Milestone:** Can have a full conversation with the AI through the UI

**Day 10: Streaming + Polish**
- Wire up SSE streaming for real-time response display
- Add loading states, error handling, scroll behaviour
- Responsive layout adjustments
- **Milestone:** Frontend feature-complete for MVP

### 10.4 Phase C — Integration & Demo Prep (Days 10–14)

**Days 10–11: End-to-end integration**
- Connect frontend to live backend
- Test complete flows: login → case list → open case → full investigation
- Fix integration bugs (data format mismatches, timing issues, error handling)

**Days 11–12: Demo data preparation**
- Select 2–3 real cases for demonstration
- Process through existing workflow (C360 app, Elliptic, etc.)
- Sanitise all data
- Write seed script, populate MongoDB
- Run full investigation on each demo case to verify quality

**Days 13–14: Polish and demo rehearsal**
- UI polish (spacing, colours, typography)
- Fix any issues found during demo case walkthroughs
- Prepare demo script (what to show, in what order, what to say)
- Rehearse the demonstration
- **Milestone:** Demo-ready prototype

### 10.5 Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Anthropic API doesn't support streaming through SafuAPI proxy | Demo feels slower (responses appear all at once) | Build with streaming, fall back to full response + loading indicator. Test on Day 1. |
| Context window fills up on complex cases | Investigation degrades or fails mid-conversation | Monitor token usage. Move borderline Tier 1 docs to Tier 2. Test with largest demo case early. |
| Colleague unavailable or frontend delayed | No visual demo | Backend works standalone — can demo via terminal or minimal HTML page. Prioritise backend. |
| SAFU GPT API key delayed | Cannot demo inside Binance network | Build and demo using personal Anthropic API key on personal laptop. Architecture is identical. |
| Demo cases too simple to show system value | Demo doesn't impress | Select at least one complex case (multiple case types, multiple data sources, edge case requiring reference doc lookup). |
| Tool use doesn't work as expected | AI can't retrieve reference documents | Fall back to static loading by case type (the simple mapping approach). Test tool use on Day 1. |

---

## Appendix A: Decisions Log

Decisions made during the planning process, recorded for reference.

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | Raw Anthropic API, not SAFU GPT Plus API | Tool use support required. Anthropic SDK enables development outside Binance network. SafuAPI Direct can be used later by changing base URL. | Mar 2026 |
| 2 | Knowledge base on filesystem, not MongoDB | Static reference material. Simpler, easier to update, no database overhead. | Mar 2026 |
| 3 | Two-tier knowledge base: core (always loaded) + reference (tool call) | Manages context window budget. Core docs ~72K tokens always loaded. Reference docs ~57K available on demand. Keeps baseline under 100K tokens. | Mar 2026 |
| 4 | YAML index for reference documents | Gives the AI structured information about available documents without loading them. Enables intelligent, targeted retrieval. | Mar 2026 |
| 5 | No audit trail / approval gates in MVP | Existing HowDesk submission process provides compliance audit trail. In-app audit deferred until direct submission is implemented. | Mar 2026 |
| 6 | Pre-staged case data, no live data pipelines | Eliminates dependency on internal API access for the prototype. Demonstrates the investigation experience without blocked dependencies. | Mar 2026 |
| 7 | No RAG or vector search | MongoDB Community lacks native vector search. Tool-based retrieval is simpler and more reliable. SAFU GPT knowledge base API not needed. | Mar 2026 |
| 8 | Mock authentication | Real auth is unnecessary for a prototype demonstration. Simple user selection sufficient. | Mar 2026 |
| 9 | Conversation stored as single MongoDB document | Simplifies retrieval — one read for full history. Adequate for prototype conversation lengths (20–30 turns). | Mar 2026 |
| 10 | Load all core documents upfront, no step-based loading | Later investigation steps reference earlier findings. Conclusion and QC steps need full visibility. Step tracking adds orchestration complexity not justified for MVP. | Mar 2026 |
| 11 | Build on personal laptop with personal API key, deploy to Binance later | Enables development outside Binance network. Identical architecture — only base URL and API key change. | Mar 2026 |

---

## Appendix B: Open Items

Items requiring action or decisions before or during development.

| # | Item | Action Required | Priority |
|---|------|-----------------|----------|
| 1 | Confirm exact model deployment name for Opus on SafuAPI | Send test request to `claude-opus-4-20250514-v1` deployment, verify response | High — but does not block development on personal API key |
| 2 | Test streaming support on SafuAPI Claude endpoint | Send request with `stream: true`, check if SSE response is returned | Medium — fallback is non-streaming |
| 3 | Test tool use support on SafuAPI Direct | Send request with tool definitions, verify tool_use responses | High — if unsupported, fall back to static document loading |
| 4 | ~~Finalise Tier 1 / Tier 2 document split~~ | **RESOLVED.** 11 files (root + FCI-CORE + FCI-LOOKUP + FCI-PROCEDURES + FCI-PROMPTS) are Tier 1. 8 files (FCI-REFERENCE) are Tier 2. | — |
| 5 | Write accurate `covers` descriptions for YAML index | Review each reference document, write descriptions the AI can use to decide relevance | High — directly impacts retrieval quality |
| 6 | Prepare and sanitise 2–3 demo cases | Select closed cases, run through existing pipeline, sanitise all data | High — required by Day 11 |
| 7 | KYC image handling for conversation start | Design how KYC screenshots are included in the initial context — pre-staged in case data for MVP, upload flow for production | Medium — can pre-stage for demo |
| 8 | Confirm SafuAPI context window limit | Check whether 200K is the ceiling or if extended context is available via the Binance deployment | Medium — architectural implications if only 200K |
| 9 | Request SafuAPI key and WAF whitelisting | Submit JIRA ticket per documentation, engage SAFU API support | High — required for Binance network deployment |