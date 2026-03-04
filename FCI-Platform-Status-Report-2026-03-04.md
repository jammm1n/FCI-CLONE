# FCI AI Investigation Platform — Build Status Report

**Date:** 4 March 2026
**Author:** Ben (Financial Crime Investigator, Level 2 Compliance, Binance)
**Purpose:** Complete handoff document to continue development in a new chat session. Contains everything needed to understand what has been built, what works, what remains, and how to pick up where we left off.

---

## 1. Project Summary

A standalone AI-assisted investigation platform for Binance Level 2 Financial Crime Investigators. Replaces the current SAFU GPT chat interface with a custom system offering full conversation control, tool-based knowledge retrieval, pre-staged case data, and a professional investigation dashboard.

**Tech stack:** Python/FastAPI backend, React (Vite) + Tailwind CSS frontend, MongoDB Community Edition (local), Anthropic Claude API (raw SDK).

**Full PRD:** Attached to the Claude Project as `FCI AI Investigation Platform — Product Requirements Document`. This contains the complete architecture, API contract, data models, knowledge base manifest, frontend layout specs, and build timeline. It is the authoritative reference for all design decisions.

---

## 2. Current Build Status — Where We Are

### PRD Timeline Position

The PRD defines a 14-day build in three phases:

- **Phase A (Days 1–5): Backend Core** — **COMPLETE**
- **Phase B (Days 4–10): Frontend** — **NOT STARTED**
- **Phase C (Days 10–14): Integration & Demo Prep** — **NOT STARTED**

The backend is feature-complete for MVP. All endpoints are implemented, tested via Postman, and returning correct responses. The server runs successfully. The next major block of work is the React frontend.

### What Has Been Built and Tested

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI server scaffold | ✅ Complete | Runs via `python -m uvicorn server.main:app --reload --port 8000` |
| MongoDB connection | ✅ Complete | PyMongo native async (`pymongo.asynchronous`), connects to `mongodb://localhost:27017` |
| Mock authentication | ✅ Complete | In-memory session store, UUID tokens, Bearer header auth |
| Case listing endpoint | ✅ Complete | `GET /api/cases` — returns cases assigned to logged-in user |
| Case detail endpoint | ✅ Complete | `GET /api/cases/{case_id}` — returns full case with preprocessed_data |
| Conversation creation | ✅ Complete | `POST /api/conversations` — creates conversation, injects case data, gets initial AI assessment |
| Message sending | ✅ Complete | `POST /api/conversations/{id}/messages` — full multi-turn with history |
| Conversation history | ✅ Complete | `GET /api/conversations/{id}/history` — returns visible messages only |
| Knowledge base loader | ✅ Complete | Two-tier: 11 core files loaded on startup (~72K tokens), 8 reference files via tool call |
| Tool call loop | ✅ Complete | `get_reference_document` tool with max 5 calls/turn safety limit |
| Prompt caching | ✅ Complete | System prompt cached via Anthropic cache_control, confirmed working |
| Token usage logging | ✅ Complete | Logs input/output/cache_created/cache_read on every API call |
| Image upload support | ✅ Built | Base64 → disk storage → Anthropic API image blocks. Not yet tested end-to-end |
| SSE streaming endpoint | ✅ Built | `stream=true` parameter on message endpoint. Not yet tested from a client |
| Health check | ✅ Complete | `GET /api/health` — reports MongoDB, KB status, token counts |
| KB index endpoint | ✅ Complete | `GET /api/knowledge-base/index` — returns reference document metadata |
| Seed script | ✅ Complete | Populates MongoDB with 2 users, 3 cases with realistic preprocessed data |
| API validation script | ✅ Complete | Standalone script confirming all Anthropic API capabilities work |

### What Has NOT Been Built

| Component | Status | PRD Reference |
|-----------|--------|---------------|
| React frontend (all views) | ❌ Not started | PRD Section 8 |
| Login page | ❌ Not started | PRD Section 8.1 |
| Case list page | ❌ Not started | PRD Section 8.2 |
| Investigation view (chat + case data panels) | ❌ Not started | PRD Section 8.3 |
| Markdown rendering in chat | ❌ Not started | PRD Section 8.3 |
| Image paste/upload UI | ❌ Not started | PRD Section 8.3 |
| Streaming response display in UI | ❌ Not started | PRD Section 8.3 |
| Streaming for conversation creation endpoint | ❌ Not started | Currently blocks until response complete |

---

## 3. Backend File Inventory

All 9 backend Python files were produced in these chat sessions and should be in Ben's local project. They are also available in `/mnt/user-data/outputs/` in this environment.

### File List and Responsibilities

```
/server
├── main.py                          # App entry point, startup/shutdown, router registration
├── config.py                        # Pydantic Settings (env vars: API key, MongoDB URI, model, paths)
├── database.py                      # MongoDB connection (pymongo.asynchronous), get_database()
├── /routers
│   ├── auth.py                      # POST /api/auth/login, GET /api/auth/me, get_current_user dependency
│   ├── cases.py                     # GET /api/cases, GET /api/cases/{case_id}
│   └── conversations.py             # POST /api/conversations, POST .../messages, GET .../history
└── /services
    ├── ai_client.py                 # Anthropic API wrapper, tool call loop, streaming, prompt caching
    ├── conversation_manager.py      # Context assembly, history storage, MongoDB conversation CRUD
    └── case_service.py              # Case CRUD, status updates
```

### Key Implementation Details Per File

**`config.py`** — Uses `pydantic_settings.BaseSettings`. Key settings:
- `ANTHROPIC_MODEL`: defaults to `claude-sonnet-4-6` (Sonnet for dev, switch to Opus for demo)
- `ANTHROPIC_MAX_TOKENS`: 4096
- `MAX_TOOL_CALLS_PER_TURN`: 5
- `KNOWLEDGE_BASE_PATH`: `./knowledge_base`
- `IMAGES_DIR`: `./data/images`

**`database.py`** — Uses `pymongo.asynchronous.AsyncMongoClient` (NOT Motor — Motor is deprecated for PyMongo 4.x+). Single global client, database reference via `get_database()`. Connected/disconnected in `main.py` lifespan events.

**`main.py`** — FastAPI app with lifespan handler. On startup: connects MongoDB, loads knowledge base into `app.state.knowledge_base`, logs token counts. On shutdown: disconnects MongoDB. Registers three routers. Includes CORS middleware (allowing all origins for prototype).

**`auth.py`** — In-memory `_sessions` dict (token → user dict). `get_current_user` is a FastAPI `Depends` that extracts Bearer token from Authorization header. Sessions clear on server restart (requires re-login).

**`cases.py`** — Two endpoints. List endpoint projects only summary fields (no preprocessed_data). Detail endpoint returns full preprocessed_data markdown.

**`conversations.py`** — Three endpoints:
- `POST /api/conversations` — creates conversation, calls `conversation_manager.create_conversation()`, returns initial AI assessment. Currently non-streaming (blocks until response).
- `POST /api/conversations/{id}/messages` — supports `stream` boolean parameter. If `stream=true`, returns SSE `text/event-stream`. If `stream=false` (default), returns JSON.
- `GET /api/conversations/{id}/history` — returns visible messages only.

**`ai_client.py`** — Two main functions:
- `get_ai_response()` — synchronous (blocking) call with tool call loop. Handles `end_turn`, `tool_use`, and unexpected stop reasons.
- `get_ai_response_streaming()` — async generator yielding `content_delta`, `tool_use`, and `done` events. Also handles tool calls (falls back to non-streaming during tool loop, then resumes streaming for final response).
- Both use prompt caching: system prompt sent as `[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]`.
- Tool call loop caps at `MAX_TOOL_CALLS_PER_TURN` (5).
- Token logging includes `cache_creation_input_tokens` and `cache_read_input_tokens`.

**`conversation_manager.py`** — Core orchestration:
- `create_conversation()` — loads case data, assembles system prompt + case data injection message, calls AI for initial assessment, stores conversation in MongoDB with hidden `system_injected` message and visible assistant response.
- `send_message()` — retrieves full history from MongoDB, handles image base64 → disk storage, assembles messages array (all messages including hidden ones), calls AI, appends user message + any tool exchanges + assistant response to MongoDB.
- `get_conversation_history()` — filters to `visible: true` messages only.
- Initial assessment instruction explicitly tells AI NOT to use `get_reference_document` tool (prevents unnecessary second API call on conversation creation).
- Case data injected as first user message with role `system_injected` and `visible: false`.

**`case_service.py`** — Simple CRUD. `get_cases()` with optional user_id filter, `get_case()` with full data, `update_case_status()`.

### Additional Files

| File | Purpose |
|------|---------|
| `test_anthropic_api.py` | Standalone validation script. Tests basic chat, tool use (full two-call loop), image input, streaming, and system prompt + tools together. Run separately, not part of the server. |
| `claude-code-scaffold-prompt.md` | The prompt used to scaffold the project directory structure, dependencies, and boilerplate via Claude Code. |
| `claude-code-testdata-prompt.md` | The prompt used to generate realistic seed/demo data for MongoDB via Claude Code. |

---

## 4. Environment Setup (Ben's Machine — Windows)

### Prerequisites Installed
- Python 3.13
- MongoDB Community Edition 8.2.5 (installed via MSI, running as a Windows service)
- MongoDB Compass (GUI client for inspecting data)

### Python Dependencies (in project)
- `fastapi`
- `uvicorn`
- `pymongo[asynchronous]` (NOT motor — motor is deprecated)
- `anthropic`
- `pydantic-settings`
- `pyyaml`

### Running the Server
```bash
cd <project-root>
python -m uvicorn server.main:app --reload --port 8000
```

Server logs on startup should show:
```
Knowledge base loaded: 361341 core chars, 8 reference documents
FCI Platform ready — http://0.0.0.0:8000
```

### Seeding the Database
```bash
python scripts/seed_demo_data.py
```
Creates: 2 users, 3 cases (CASE-2026-0451 scam, CASE-2026-0387 CTM, CASE-2026-0512 fraud).

### Environment Variables Required
```
ANTHROPIC_API_KEY=sk-ant-...
```
Set this before running the server. All other settings have working defaults.

---

## 5. Testing Workflow (Postman)

FastAPI's Swagger UI (`/docs`) doesn't show an Authorize button for the custom Bearer auth, so Postman is used for API testing.

### Step-by-step test flow:

**1. Login:**
```
POST http://localhost:8000/api/auth/login
Body: {"username": "ben.investigator"}
```
Save the `token` from the response.

**2. Set auth header on all subsequent requests:**
```
Authorization: Bearer <token>
```

**3. List cases:**
```
GET http://localhost:8000/api/cases
```

**4. Get case detail:**
```
GET http://localhost:8000/api/cases/CASE-2026-0451
```

**5. Create conversation (starts investigation):**
```
POST http://localhost:8000/api/conversations
Body: {"case_id": "CASE-2026-0451"}
```
Takes ~20-30 seconds. Returns `conversation_id` and `initial_response`.

**6. Send follow-up message (wait 60s for rate limit on free tier):**
```
POST http://localhost:8000/api/conversations/<conversation_id>/messages
Body: {"content": "Let's begin the ICR walkthrough in standard mode.", "stream": false}
```

**7. Get conversation history:**
```
GET http://localhost:8000/api/conversations/<conversation_id>/history
```

**Important:** Server restart clears the in-memory session store. You must re-login after every restart.

---

## 6. Prompt Caching — How It Works

The system prompt (~72K tokens of core knowledge base + ~1.5K YAML reference index) is sent with Anthropic's `cache_control: {"type": "ephemeral"}` flag.

**First API call in a conversation:**
- `cache_creation_input_tokens`: ~95,787 (system prompt written to cache)
- `cache_read_input_tokens`: 0
- `input_tokens`: ~2,318 (just the case data + user message)

**All subsequent API calls (within ~5 min cache TTL):**
- `cache_creation_input_tokens`: 0
- `cache_read_input_tokens`: ~95,787 (system prompt served from cache)
- `input_tokens`: ~3,000+ (case data + growing conversation history)

The cache dramatically reduces cost (90% reduction on cached tokens) and latency. The `input_tokens` field in the API response only counts non-cached tokens.

---

## 7. Known Issues and Constraints

### Rate Limiting (Critical for Development)
Ben's personal Anthropic API key is on the free/basic tier: **30,000 input tokens per minute**. Since the system prompt alone is ~96K tokens, the first call in a conversation consumes the entire minute's budget. Subsequent calls within the same minute will hit 429 errors.

**Workaround:** Wait 60 seconds between API calls during development. Once the cache is warm, subsequent calls only send ~3K fresh tokens and process much faster.

**Resolution options:**
- Upgrade to Anthropic's paid tier ($5 — significantly higher limits)
- Use colleague's API key if they have a higher tier
- When deployed to Binance network via SafuAPI, rate limits will be different

### Server Restart Clears Sessions
The mock auth stores sessions in an in-memory dict. Any server restart (including `--reload` triggering) requires a new login call.

### Streaming Not Yet Tested From Client
The SSE streaming endpoint exists in the backend but hasn't been tested with an actual EventSource client. It needs validation with the React frontend or a test script.

### Conversation Creation Is Not Streaming
`POST /api/conversations` currently blocks until the initial AI assessment is complete (~20-30 seconds). This should be converted to streaming for a better user experience, but is functional as-is for the prototype.

---

## 8. Architectural Decisions Made During Development

These decisions were made during the build sessions and supplement the PRD's Appendix A:

| # | Decision | Rationale |
|---|----------|-----------|
| 12 | PyMongo native async, not Motor | Motor is deprecated for PyMongo 4.x+. `pymongo[asynchronous]` is the supported async driver. Import: `from pymongo.asynchronous import AsyncMongoClient`. |
| 13 | Prompt caching via Anthropic `cache_control` | System prompt is ~96K tokens. Caching reduces cost by 90% and improves latency on all calls after the first. Applied to both streaming and non-streaming code paths. |
| 14 | Initial assessment instruction explicitly prohibits tool use | Prevents the AI from proactively calling `get_reference_document` on the first turn, which would trigger a second ~96K token API call within the same minute and hit rate limits. The AI works from case data + core knowledge for the initial assessment. |
| 15 | Tool call messages stored as hidden `tool_exchange` entries | When the AI makes tool calls, the intermediate messages (tool_use + tool_result) are stored in MongoDB with `visible: false` and `role: "tool_exchange"`. They're included in API calls (the model needs to see them) but hidden from the frontend. |
| 16 | Images stored on disk at `./data/images/{conversation_id}/` | Base64 received from client is decoded and written to disk. The MongoDB message stores the file path, not the base64. Images are re-encoded to base64 when assembling API payloads. |
| 17 | Token usage includes cache metrics in all response paths | All 5 return/yield points in ai_client.py include `cache_creation_input_tokens` and `cache_read_input_tokens` alongside standard `input_tokens` and `output_tokens`. |

---

## 9. Knowledge Base Files on Disk

The knowledge base directory structure on Ben's machine:

```
/knowledge_base
├── /core                              # Tier 1: loaded every conversation (~72K tokens)
│   ├── SYSTEM-PROMPT.md
│   ├── icr-general-rules.md
│   ├── mlro-escalation-matrix.md
│   ├── qc-submission-checklist.md
│   ├── decision-matrix.md
│   ├── icr-steps-setup.md
│   ├── icr-steps-analysis.md
│   ├── icr-steps-decision.md
│   ├── icr-steps-post.md
│   └── prompt-library.md
├── /reference                         # Tier 2: available via tool call (~57K tokens)
│   ├── scam-fraud-sop.md
│   ├── ftm-sop.md
│   ├── CTM-on-chain-alerts-sop.md
│   ├── block-unblock-guidelines.md
│   ├── fake-documents-guidelines.md
│   ├── gambling-legality-matrix.md
│   ├── mlro-escalation-decisions.md
│   └── case-decision-archive.md
└── reference-index.yaml               # YAML index for tool-based retrieval
```

All 11 core files (324,093 chars / ~72K tokens) are loaded into memory on server startup and concatenated into the system prompt. All 8 reference files are indexed in `reference-index.yaml` and served on demand when the AI calls `get_reference_document`.

---

## 10. Database State (MongoDB)

**Database name:** `fci_platform`

**Collections:**
- `users` — 2 records (ben.investigator / user_001, demo.investigator / user_002)
- `cases` — 3 records:
  - CASE-2026-0451 (scam — romance scam, assigned to user_001)
  - CASE-2026-0387 (CTM — on-chain alerts, assigned to user_001)
  - CASE-2026-0512 (fraud — fake documents, assigned to user_001)
- `conversations` — any conversations created during testing (can be cleared by re-running seed script)

Each case contains realistic preprocessed_data markdown fields (c360_analysis, elliptic_analysis, previous_cases, chat_history_summary, kyc_summary, and optionally law_enforcement, fake_documents).

---

## 11. What To Do Next

### Immediate Next Step: Frontend Build (PRD Phase B)

The React frontend is the entire remaining deliverable. The PRD Section 8 contains the complete specification including wireframes, component breakdown, and state management approach.

**Recommended build order:**

1. **Scaffold Vite + React + Tailwind project** in `/client`
2. **Build API client service** — functions wrapping fetch calls to all backend endpoints, auth token management in React context
3. **Login page** — simple username input, stores token in React state (not localStorage per PRD)
4. **Case list page** — fetch cases, display as cards with Open/Continue buttons
5. **Investigation view layout** — two-panel split (case data left, chat right)
6. **Case data panel** — tabbed display of preprocessed_data markdown, using react-markdown
7. **Chat interface** — message list, input box, send button, markdown rendering in AI responses
8. **Streaming display** — wire up EventSource for SSE streaming responses
9. **Image upload** — paste handler + file picker, base64 conversion, thumbnail preview
10. **Polish** — loading states, error handling, scroll behaviour, responsive layout

### Backend Items Still Pending

- **Test streaming from an actual client** (EventSource or SSE library)
- **Test image upload end-to-end** (send base64 image in a message, verify it reaches the AI)
- **Test tool call retrieval during conversation** (send a message that should trigger the AI to request a reference document — e.g., ask about scam classification specifics that require the SOP)
- **Convert conversation creation to streaming** (nice-to-have for UX, not blocking)

### Demo Data Preparation (PRD Phase C, Days 11-12)

The 3 seed cases have realistic preprocessed data but may need refinement after full investigations are run through them. The sanitisation and quality of demo data directly impacts the demo — this should not be left to the last day.

---

## 12. Key Decisions Already Made (Do Not Relitigate)

Carried forward from the PRD and development sessions:

1. Raw Anthropic API, not SAFU GPT wrapper — tool use support required
2. Two-tier knowledge base — 11 core files loaded every call, 8 reference via tool call
3. No RAG or vector search — tool-based retrieval with AI-controlled document loading
4. Pre-staged case data for MVP — no live API connections
5. Mock auth — in-memory session store, no real authentication
6. Conversation as single MongoDB document — embedded messages array with visible flag
7. Images stored on disk — base64 written to filesystem, path in MongoDB
8. No audit trail / approval gates in MVP — existing HowDesk workflow provides trail
9. Build on personal laptop with personal API key — deploy to Binance later
10. Use Sonnet for development/testing, Opus for demo
11. PyMongo native async, not Motor (Motor is deprecated)
12. Prompt caching on system prompt (confirmed working, 90% cost reduction)
13. Initial assessment explicitly prohibits tool use (prevents rate limit issues)
14. Tool call messages stored as hidden `tool_exchange` entries in MongoDB

---

## 13. Reference Files in This Project

| File | Location | Purpose |
|------|----------|---------|
| PRD Context Document | Claude Project file | Background, current workflow, what exists, constraints |
| PRD | Claude Project file | Full product requirements, API contract, data models, build timeline |
| This status report | Output from current session | Handoff document for continuing in a new chat |
| All backend .py files | `/mnt/user-data/outputs/` and Ben's local machine | Production-ready backend code |
| `claude-code-scaffold-prompt.md` | `/mnt/user-data/outputs/` | Prompt used to scaffold project structure |
| `claude-code-testdata-prompt.md` | `/mnt/user-data/outputs/` | Prompt used to generate seed data |
| `test_anthropic_api.py` | `/mnt/user-data/outputs/` | API capability validation script |
