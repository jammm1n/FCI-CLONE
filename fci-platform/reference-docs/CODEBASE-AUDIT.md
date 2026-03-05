# FCI Investigation Platform — Codebase Audit

**Generated:** 2026-03-05
**Total source files:** 73 (excluding node_modules, .git, __pycache__, dist, package-lock.json)
**Total lines of code:** ~18,500 (4,234 backend Python, 2,511 frontend JS/JSX/CSS, 10,292 knowledge base)

---

## 1. Directory Tree

```
fci-platform/
├── .env                              # Environment variables (gitignored)
├── .env.example                      # Template: API keys, MongoDB URI, model config
├── .gitignore                        # Python, Node, IDE, OS ignores
├── BUG_HUNTING_BRIEFING.md           # Bug hunting notes (103 lines)
├── CLAUDE.md                         # AI assistant orientation document
├── CODEBASE-AUDIT.md                 # This file
├── DESIGN_UPDATE_STATUS.md           # Design implementation tracking
├── DOCUMENT_PIPELINE_SPEC.md         # Future document processing spec
├── requirements.txt                  # Python dependencies (11 packages)
│
├── client/                           # React 18 + Vite frontend
│   ├── .gitkeep
│   ├── DESIGN_SPEC.md                # Visual design specification (669 lines)
│   ├── index.html                    # Entry HTML with FOUC-prevention script
│   ├── package.json                  # NPM deps: react, react-router-dom, react-markdown
│   ├── package-lock.json             # (not audited)
│   ├── postcss.config.js             # PostCSS: tailwindcss + autoprefixer
│   ├── tailwind.config.js            # Custom surface/gold color scales, fonts, shadows
│   ├── vite.config.js                # Vite config with /api proxy to :8000
│   ├── dist/                         # Production build output (not audited)
│   └── src/
│       ├── main.jsx                  # React root: BrowserRouter > ThemeProvider > AuthProvider > App
│       ├── App.jsx                   # Route definitions (5 routes)
│       ├── index.css                 # Tailwind base + custom animations + scrollbar + prose
│       ├── context/
│       │   ├── AuthContext.jsx        # In-memory auth state (user, token, login, logout)
│       │   └── ThemeContext.jsx       # Dark/light mode toggle (localStorage 'fci-theme')
│       ├── hooks/
│       │   └── useStreamingChat.js    # Reusable SSE stream reader hook
│       ├── services/
│       │   └── api.js                 # All API calls (auth, cases, conversations, PDF, images, admin)
│       ├── utils/
│       │   └── formatters.js          # formatTimestamp, capitalize, statusColor, caseTypeColor
│       ├── pages/
│       │   ├── LoginPage.jsx          # Username-only login form
│       │   ├── CaseListPage.jsx       # Case cards grid + "Free Chat" link + reset button
│       │   ├── InvestigationPage.jsx  # Split-panel: case data (left) + chat (right)
│       │   └── FreeChatPage.jsx       # Free chat with sidebar + chat panel
│       └── components/
│           ├── AppLayout.jsx          # Global header (logo, nav, theme toggle, logout)
│           ├── ProtectedRoute.jsx     # Auth guard (redirects to /login)
│           ├── cases/
│           │   └── CaseCard.jsx       # Case summary card with status/type badges
│           ├── chat/
│           │   └── ChatSidebar.jsx    # Free chat conversation list + new chat button
│           ├── investigation/
│           │   ├── CaseHeader.jsx     # Case metadata header (subject, type, status)
│           │   ├── CaseDataTabs.jsx   # Tab bar for preprocessed_data sections
│           │   ├── CaseDataPanel.jsx  # Markdown-rendered case data content
│           │   ├── ChatMessageList.jsx # Scrollable message list with auto-scroll
│           │   ├── ChatMessage.jsx    # Individual message bubble + lightbox + tools footer
│           │   ├── ChatInput.jsx      # Textarea + image paste/drag/attach + send button
│           │   └── StreamingIndicator.jsx # Gold shimmer "Analyzing..." indicator
│           └── shared/
│               ├── DownloadPdfButton.jsx  # PDF export button with state feedback
│               ├── ImageUpload.jsx        # File input + thumbnail previews + remove
│               ├── LoadingSpinner.jsx     # Spinning border circle (sm/md/lg)
│               ├── MarkdownRenderer.jsx   # react-markdown with GFM + custom components
│               └── Skeleton.jsx           # Loading skeleton placeholder bar
│
├── server/                           # FastAPI backend
│   ├── __init__.py                   # Empty
│   ├── config.py                     # Pydantic Settings (env vars)
│   ├── database.py                   # PyMongo 4.16 async connection management
│   ├── main.py                       # FastAPI app, lifespan, CORS, router registration
│   ├── models/
│   │   ├── __init__.py               # Empty
│   │   └── schemas.py                # Pydantic v2 request/response models (190 lines)
│   ├── routers/
│   │   ├── __init__.py               # Empty
│   │   ├── admin.py                  # POST /api/admin/reseed — wipe + reseed demo data
│   │   ├── auth.py                   # POST /api/auth/login, GET /api/auth/me
│   │   ├── cases.py                  # GET /api/cases, GET /api/cases/{id}
│   │   └── conversations.py          # CRUD + streaming + PDF export + image serving
│   └── services/
│       ├── __init__.py               # Empty
│       ├── ai_client.py              # Anthropic API wrapper (streaming + non-streaming + tool loop)
│       ├── case_service.py           # Case CRUD (get_cases, get_case, update_case_status)
│       ├── conversation_manager.py   # Conversation lifecycle orchestration (751 lines)
│       ├── knowledge_base.py         # Two-tier KB: core (startup) + reference (tool calls)
│       └── pdf_export.py             # fpdf2-based PDF transcript generation
│
├── scripts/
│   ├── seed_demo_data.py             # Seeds 2 users + 5 cases (incl. markdown parser)
│   └── test_anthropic_api.py         # Standalone API test script
│
├── knowledge_base/
│   ├── core/                         # Tier 1: loaded into system prompt on startup
│   │   ├── SYSTEM-PROMPT.md          # Master system prompt (441 lines)
│   │   ├── decision-matrix.md        # Case outcome decision matrix
│   │   ├── icr-general-rules.md      # ICR investigation rules
│   │   ├── icr-steps-analysis.md     # ICR steps: analysis phase (1584 lines)
│   │   ├── icr-steps-decision.md     # ICR steps: decision phase
│   │   ├── icr-steps-post.md         # ICR steps: post-decision phase
│   │   ├── icr-steps-setup.md        # ICR steps: setup phase
│   │   ├── mlro-escalation-matrix.md # MLRO escalation criteria
│   │   ├── prompt-library.md         # Prompt templates for AI (1375 lines)
│   │   └── qc-submission-checklist.md # QC submission requirements
│   ├── reference-index.yaml          # YAML index of Tier 2 reference docs
│   └── reference/                    # Tier 2: available via get_reference_document tool
│       ├── CTM-on-chain-alerts-sop.md
│       ├── block-unblock-guidelines.md
│       ├── case-decision-archive.md
│       ├── fake-documents-guidelines.md
│       ├── ftm-sop.md
│       ├── gambling-legality-matrix.md
│       ├── mlro-escalation-decisions.md
│       └── scam-fraud-sop.md
│
├── data/
│   └── images/                       # Uploaded chat images (gitignored, persists across sessions)
│       └── conv_{id}/img_{id}.{ext}
│
└── demo_data/
    └── .gitkeep                      # Placeholder for future demo data files
```

---

## 2. Architecture Overview

### 2.1 System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Browser (React 18)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │ LoginPage│ │CaseList  │ │Investigation │ │  FreeChatPage    │  │
│  │          │ │  Page    │ │    Page       │ │                  │  │
│  └────┬─────┘ └────┬─────┘ └──────┬───────┘ └────────┬─────────┘  │
│       │             │              │                   │            │
│       └─────────────┴──────────────┴───────────────────┘            │
│                            │                                        │
│                     api.js (fetch)                                   │
│                            │                                        │
│              SSE (EventSource) for streaming                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │ Vite proxy /api → :8000
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (:8000)                           │
│                                                                     │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────────────┐ │
│  │   Routers   │  │    Services      │  │    Knowledge Base      │ │
│  │  auth.py    │  │  ai_client.py    │  │  core/ (10 .md files)  │ │
│  │  cases.py   │  │  conversation_   │  │  reference/ (8 files)  │ │
│  │  convers.py │──│  manager.py      │  │  reference-index.yaml  │ │
│  │  admin.py   │  │  case_service.py │  └────────────────────────┘ │
│  └─────────────┘  │  knowledge_base  │                             │
│                   │  pdf_export.py   │                             │
│                   └────────┬─────────┘                             │
│                            │                                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼                              ▼
┌──────────────────────┐      ┌──────────────────────────┐
│   MongoDB (:27017)   │      │   Anthropic Claude API   │
│   fci_platform DB    │      │   (claude-sonnet-4-6)    │
│                      │      │                          │
│   Collections:       │      │   - messages.create()    │
│   - users            │      │   - messages.stream()    │
│   - cases            │      │   - Tool use loop        │
│   - conversations    │      │   - Prompt caching       │
└──────────────────────┘      └──────────────────────────┘
```

### 2.2 Primary User Journey: Login → Case Selection → Investigation Chat

```
1. LOGIN
   Browser: POST /api/auth/login {username}
   Backend: Lookup user in MongoDB users collection
            Generate UUID token, store in _sessions dict
            Return {user_id, username, display_name, token}
   Frontend: Store user + token in AuthContext (memory only)
             Navigate to /cases

2. CASE LIST
   Browser: GET /api/cases (Bearer token)
   Backend: Query cases collection where assigned_to = user_id
            Return case summaries (no preprocessed_data)
   Frontend: Render CaseCard grid

3. OPEN INVESTIGATION
   Browser: GET /api/cases/{caseId} (full detail with preprocessed_data)
   Frontend: Render left panel (CaseHeader + CaseDataTabs + CaseDataPanel)
             If case has conversation_id → load existing history
             If no conversation_id → create new:

   3a. CREATE CONVERSATION (instant, no AI):
       POST /api/conversations {case_id, mode: "case"}
       Backend: Create conversation doc with system_injected message
                (case data markdown), update case status to in_progress
       Frontend: Gets conversation_id back immediately

   3b. INITIAL ASSESSMENT (streaming):
       POST /api/conversations/{id}/messages {initial_assessment: true, stream: true}
       Backend: Rebuild API messages from stored history (includes case data)
                Stream response from Anthropic API
                Yield SSE events: content_delta → tool_use → done → stored
       Frontend: Display gold spinner → switch to streaming text on first delta
                 Accumulate text into assistant message bubble

4. SUBSEQUENT MESSAGES
   User types message (Enter to send) → POST /api/conversations/{id}/messages
   Backend: Append user message to API context, call Anthropic (streaming)
            Tool loop: if model calls get_reference_document, retrieve KB doc,
            send tool_result back, continue streaming
            After stream completes: store user msg + tool exchanges + AI msg in MongoDB
   Frontend: Optimistic user message → streaming assistant message → finalize on "stored"
```

### 2.3 Conversation State Management

- **MongoDB**: Single document per conversation in `conversations` collection. Messages embedded as array.
- **Message roles**: `system_injected` (case data, hidden), `user` (visible), `assistant` (visible), `tool_exchange` (hidden, stores API tool call/result pairs)
- **API reconstruction**: On every turn, `_rebuild_api_messages()` traverses the full stored message array and maps roles to Anthropic API format (system_injected → user, tool_exchange → original_role from `original_role` field)
- **Frontend state**: `useStreamingChat` hook holds `messages` array in React state. Messages have temporary IDs during streaming, replaced with server IDs on `stored` event.
- **No localStorage for session**: Auth token lives only in React state. Page refresh = logout.

---

## 3. Backend Documentation

### 3.1 `server/config.py` (44 lines)

**Purpose:** Application configuration via environment variables using pydantic-settings.

**Class: `Settings(BaseSettings)`**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `MONGODB_URI` | str | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | str | `fci_platform` | Database name |
| `ANTHROPIC_API_KEY` | str | `""` | Anthropic API key |
| `ANTHROPIC_MODEL` | str | `claude-sonnet-4-6` | Default model for AI calls |
| `ANTHROPIC_MAX_TOKENS` | int | `4096` | Max output tokens per API call |
| `MAX_TOOL_CALLS_PER_TURN` | int | `5` | Safety limit for reference doc lookups |
| `KNOWLEDGE_BASE_PATH` | str | `./knowledge_base` | Path to KB directory |
| `IMAGES_DIR` | str | `./data/images` | Path to uploaded image storage |
| `HOST` | str | `0.0.0.0` | Server host |
| `PORT` | int | `8000` | Server port |
| `LOG_LEVEL` | str | `INFO` | Logging level |

- Reads from `.env` file (latin-1 encoding, extra fields ignored)
- Exports singleton `settings` instance

**Dependencies:** `pydantic_settings.BaseSettings`

---

### 3.2 `server/database.py` (55 lines)

**Purpose:** MongoDB connection lifecycle management using PyMongo 4.16 native async.

**Functions:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `connect_db()` | `async def connect_db()` | Create `AsyncMongoClient`, verify with ping, store in module globals |
| `disconnect_db()` | `async def disconnect_db()` | Close client, clear globals |
| `get_database()` | `def get_database() -> Database` | Return database instance (raises `RuntimeError` if not connected) |

**Module-level state:** `_client: AsyncMongoClient | None`, `_db`

**Dependencies:** `pymongo.AsyncMongoClient`, `server.config.settings`

---

### 3.3 `server/main.py` (122 lines)

**Purpose:** FastAPI application entry point with lifespan management.

**Lifespan events (startup):**
1. Connect to MongoDB (`connect_db()`)
2. Load knowledge base into memory (`KnowledgeBase.load_on_startup()`)
3. Store KB instance in `app.state.knowledge_base`
4. Ensure images directory exists

**Lifespan events (shutdown):**
1. Disconnect from MongoDB (`disconnect_db()`)

**CORS configuration:** Allows origins `localhost:5173`, `localhost:3000`, `127.0.0.1:5173`

**Registered routers:** `admin`, `auth`, `cases`, `conversations`

**Endpoint:**

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/health` | No | Health check — MongoDB status + KB stats |

**Dependencies:** `fastapi`, `server.config`, `server.database`, `server.services.knowledge_base`, all routers

---

### 3.4 `server/models/schemas.py` (190 lines)

**Purpose:** Pydantic v2 models defining the API contract.

**Models:**

| Model | Used For | Key Fields |
|-------|----------|------------|
| `LoginRequest` | POST /auth/login body | `username: str` |
| `LoginResponse` | POST /auth/login response | `user_id, username, display_name, token` |
| `UserResponse` | GET /auth/me response | `user_id, username, display_name` |
| `TokenUsage` | Anthropic API token stats | `input_tokens, output_tokens` |
| `ToolUsedInfo` | Reference doc audit trail | `tool, document_id, document_title` |
| `CaseSummary` | Case list entry | `case_id, case_type, subject_user_id, status, summary, created_at, conversation_id` |
| `CaseListResponse` | GET /cases response | `cases: list[CaseSummary]` |
| `PreprocessedData` | Case data sections | 12 optional `str` fields (see Case Data Schema), `extra="allow"` |
| `CaseDetailResponse` | GET /cases/{id} response | Summary fields + `preprocessed_data` |
| `CreateConversationRequest` | POST /conversations body | `case_id: str | None`, `mode: str = "case"` |
| `CreateConversationResponse` | POST /conversations response | `conversation_id, case_id, mode` |
| `ConversationSummary` | Conversation list entry | `conversation_id, title, mode, case_id, updated_at, message_count` |
| `ConversationListResponse` | GET /conversations response | `conversations: list[ConversationSummary]` |
| `ImageInput` | Image in message body | `base64: str, media_type: str` |
| `SendMessageRequest` | POST /messages body | `content: str, images: list[ImageInput]` |
| `SendMessageResponse` | POST /messages response | `message_id, role, content, tools_used, token_usage, timestamp` |
| `MessageResponse` | Single message in history | `message_id, role, content, tools_used, images, timestamp` |
| `ConversationHistoryResponse` | GET /history response | `conversation_id, case_id, mode, title, messages` |
| `HealthResponse` | GET /health response | `status, mongodb, knowledge_base_loaded, core_documents_tokens, reference_documents_available` |
| `ReferenceDocumentInfo` | KB index entry | `id, title, covers, token_estimate` |
| `KnowledgeBaseIndexResponse` | KB index response | `reference_documents: list[ReferenceDocumentInfo]` |

**Dependencies:** `datetime`, `pydantic.BaseModel`, `pydantic.ConfigDict`

---

### 3.5 `server/routers/auth.py` (94 lines)

**Purpose:** Mock authentication — username-only login, UUID session tokens stored in-memory.

**Module-level state:** `_sessions: dict[str, dict]` — maps token → user dict

**Dependency function: `get_current_user(authorization: str | None) -> dict`**
- Extracts Bearer token from Authorization header
- Looks up in `_sessions`
- Returns user dict or raises 401
- Used by all other routers via `Depends(get_current_user)`

**Endpoints:**

| Method | Path | Auth | Request | Response | Description |
|--------|------|------|---------|----------|-------------|
| POST | `/api/auth/login` | No | `{username: str}` | `{user_id, username, display_name, token}` | Lookup user in MongoDB, generate session token |
| GET | `/api/auth/me` | Yes | — | `{user_id, username, display_name}` | Return current user from session |

**Database:** Reads `users` collection (`find_one` by username)

---

### 3.6 `server/routers/cases.py` (34 lines)

**Purpose:** Case listing and detail retrieval.

**Endpoints:**

| Method | Path | Auth | Request | Response | Description |
|--------|------|------|---------|----------|-------------|
| GET | `/api/cases` | Yes | — | `{cases: [...]}` | List cases assigned to current user (summary only, no preprocessed_data) |
| GET | `/api/cases/{case_id}` | Yes | — | Full case detail | Get case with all preprocessed_data sections |

**Dependencies:** `server.services.case_service`

---

### 3.7 `server/routers/admin.py` (54 lines)

**Purpose:** Demo/dev only — wipe and reseed database.

**Endpoints:**

| Method | Path | Auth | Request | Response | Description |
|--------|------|------|---------|----------|-------------|
| POST | `/api/admin/reseed` | Yes | — | `{status: "reseeded"}` | Clear images dir, run `seed_demo_data.py` via subprocess |

**Note:** Uses `asyncio.to_thread(subprocess.run, ...)` because `asyncio.create_subprocess_exec` is not supported on Windows.

---

### 3.8 `server/routers/conversations.py` (357 lines)

**Purpose:** Conversation CRUD, message sending (streaming + non-streaming), PDF export, image serving.

**Endpoints:**

| Method | Path | Auth | Request | Response | Description |
|--------|------|------|---------|----------|-------------|
| POST | `/api/conversations` | Yes | `{case_id?, mode}` | `{conversation_id, case_id, mode}` | Create conversation (no AI call) |
| POST | `/api/conversations/{id}/messages` | Yes | `{content, images?, stream?, initial_assessment?}` | SSE stream or JSON | Send message, get AI response |
| GET | `/api/conversations/{id}/history` | Yes | — | `{conversation_id, case_id, mode, title, messages}` | Get visible message history |
| GET | `/api/conversations` | Yes | `?mode=free_chat` | `{conversations: [...]}` | List user's conversations |
| GET | `/api/conversations/{id}/export/pdf` | Yes | — | PDF blob | Export conversation as PDF |
| GET | `/api/conversations/{id}/images/{image_id}` | **No** | — | Image file | Serve stored image |
| DELETE | `/api/conversations/{id}` | Yes | — | `{status: "deleted"}` | Delete conversation |

**Streaming flow (SSE):**
1. Router creates `event_generator()` async generator
2. Iterates `conversation_manager.send_message_streaming()`
3. Yields SSE events: `content_delta`, `tool_use`, `done`, `error`
4. After `done`: calls `store_streamed_response()` to persist to MongoDB
5. Yields final `stored` event with message_id
6. Wraps in `EventSourceResponse` from `sse-starlette`

**Error handling:** Catches `ValueError` (→ 400), `RateLimitError` (→ 429), generic `Exception` (→ error SSE event)

**Image endpoint:** Unauthenticated (images referenced by `<img src>` which can't send Bearer tokens). Security by obscurity (random IDs). Serves via `FileResponse`.

---

### 3.9 `server/services/ai_client.py` (558 lines)

**Purpose:** Core Anthropic API integration layer — wraps message creation, tool call loops, and streaming.

**Constants:**
- `TOOLS`: Single tool definition — `get_reference_document(document_id: str)` — sent with every API call

**Singleton:** `_client: AsyncAnthropic | None`, created on first use with `max_retries=3`

**Functions:**

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `get_client()` | — | `AsyncAnthropic` | Get or create singleton client |
| `_process_tool_calls(response_content, knowledge_base)` | Content blocks, KB | `(tool_results, tools_used)` | Extract tool_use blocks, call `kb.get_reference_document()`, return results + audit metadata |
| `_extract_text(response_content)` | Content blocks | `str` | Join all text blocks |
| `get_ai_response(system_prompt, messages, knowledge_base, model?)` | — | `dict` | Non-streaming: loop API calls until `end_turn`, handle tool calls (max 5/turn) |
| `get_ai_response_streaming(system_prompt, messages, knowledge_base, model?)` | — | `AsyncGenerator[dict]` | Streaming: yield `content_delta` chunks, handle tool calls between streams |
| `_serialize_content(content_blocks)` | SDK objects | `list[dict]` | Convert SDK `TextBlock`/`ToolUseBlock` to plain dicts for API re-submission |
| `build_image_content_block(base64_data, media_type)` | — | `dict` | Build Anthropic image content block |
| `build_user_message_content(text, images?)` | — | `str | list[dict]` | Build user message content (plain string or image+text blocks) |

**Anthropic API parameters:**
- `system`: Array with single text block + `cache_control: {"type": "ephemeral"}` (prompt caching)
- `tools`: `TOOLS` array (get_reference_document)
- `max_tokens`: from `settings.ANTHROPIC_MAX_TOKENS` (4096)
- `model`: from `settings.ANTHROPIC_MODEL` (defaults to claude-sonnet-4-6)

**Tool call loop logic:**
1. Call API (streaming or non-streaming)
2. If `stop_reason == "end_turn"` → return/yield final result
3. If `stop_reason == "tool_use"` → process tool calls, append assistant + tool_result messages, increment counter
4. If counter > `MAX_TOOL_CALLS_PER_TURN` (5) → force model to respond with available info
5. Loop back to step 1

**Token usage logging:** Logs `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` on every API call

---

### 3.10 `server/services/conversation_manager.py` (751 lines)

**Purpose:** Orchestration layer managing conversation lifecycle — creation, message sending, history retrieval, storage.

**Functions:**

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `create_conversation(user_id, knowledge_base, case_id?, mode?)` | — | `dict` | Create conversation doc. Case mode: load case, build case data markdown, store system_injected message, update case status. Free chat: empty doc. Returns existing conv if case already has one. |
| `send_message(conversation_id, content, knowledge_base, images?)` | — | `dict` | Non-streaming: rebuild API messages, call AI, store user + tool + assistant messages |
| `send_message_streaming(conversation_id, content, knowledge_base, images?, is_initial_assessment?)` | — | `AsyncGenerator` | Streaming: rebuild API messages, yield events from `get_ai_response_streaming()`. For initial_assessment: no new user message appended. |
| `store_streamed_response(conversation_id, user_content, user_images, ai_content, tools_used, token_usage, tool_call_messages, is_initial_assessment?)` | — | `dict` | Persist streamed turn to MongoDB. Skip user message for initial_assessment. Auto-generate title for free_chat on first message. |
| `get_history(conversation_id)` | — | `dict` | Return visible messages only (filter `visible: True`). |
| `list_conversations(user_id, mode?)` | — | `list[dict]` | List conversations sorted by `updated_at` desc, with visible message count. |
| `delete_conversation(conversation_id, user_id)` | — | `None` | Delete conversation, verify ownership. |
| `_rebuild_api_messages(stored_messages)` | `list[dict]` | `list[dict]` | Reconstruct Anthropic API messages array from stored history. Maps roles: system_injected→user, tool_exchange→original_role. Reloads images from disk for user messages. |
| `_build_case_data_markdown(case)` | `dict` | `str` | Build markdown document from preprocessed_data. Maps 12 field keys to display headers. |
| `_store_images(conversation_id, images)` | — | `list[dict]` | Decode base64, save to disk at `{IMAGES_DIR}/{conv_id}/{img_id}.{ext}`, return references. |
| `_generate_title(content)` | `str` | `str` | Heuristic title from first sentence or first 50 chars. |
| `_generate_id(prefix)` | `str` | `str` | `{prefix}_{uuid4_hex[:12]}` |
| `_now()` | — | `datetime` | UTC now |

**Database interactions:**
- `conversations.find_one({"_id": conversation_id})` — retrieve conversation
- `conversations.insert_one(conversation_doc)` — create conversation
- `conversations.update_one({"_id": id}, {"$push": {"messages": {"$each": [...]}}, "$set": {"updated_at": now}})` — append messages
- `conversations.update_one({"_id": id}, {"$set": {"title": title}})` — set auto-generated title
- `conversations.find(query).sort("updated_at", -1)` — list conversations
- `conversations.delete_one({"_id": id, "user_id": user_id})` — delete with ownership check
- `cases.find_one({"_id": case_id})` — load case for conversation creation
- `cases.update_one({"_id": case_id}, {"$set": {"conversation_id": ..., "status": "in_progress"}})` — link conversation to case

---

### 3.11 `server/services/case_service.py` (111 lines)

**Purpose:** Case CRUD operations.

**Functions:**

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `get_cases(user_id?)` | Optional filter | `list[dict]` | List cases (summary projection, no preprocessed_data) |
| `get_case(case_id)` | Case ID | `dict | None` | Full case detail including preprocessed_data |
| `update_case_status(case_id, status)` | Case ID, new status | `bool` | Update status (valid: open, in_progress, completed) |
| `_format_dt(dt)` | datetime or None | `str | None` | ISO format helper |

**Database:** Reads/writes `cases` collection.

---

### 3.12 `server/services/knowledge_base.py` (82 lines)

**Purpose:** Two-tier knowledge base — core docs loaded on startup, reference docs available via tool calls.

**Class: `KnowledgeBase`**

| Method | Description |
|--------|-------------|
| `__init__(base_path)` | Initialize with path, empty state |
| `load_on_startup()` | Load all `core/*.md` files into `core_content` (sorted, concatenated with headers). Parse `reference-index.yaml` into `reference_index` list. Format index as text for system prompt. |
| `get_system_prompt()` | Return `core_content + reference_index_text` |
| `get_reference_document(document_id)` | Validate ID against index, read file from `reference/` directory, return content or error string |

**State:**
- `core_content: str` — concatenated core documents (~10K lines)
- `reference_index: list[dict]` — parsed YAML index (8 entries)
- `reference_index_text: str` — formatted index for system prompt injection

**Singleton:** Module-level `knowledge_base = KnowledgeBase()` (but app uses the one stored in `app.state`)

---

### 3.13 `server/services/pdf_export.py` (281 lines)

**Purpose:** Server-side PDF generation using fpdf2.

**Class: `TranscriptPDF(FPDF)`**
- Custom header: "FCI Investigation Platform" + "Case Transcript" + gold accent line
- Custom footer: "CONFIDENTIAL" + page number

**Functions:**

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `generate_conversation_pdf(conversation, case_doc?, images_dir?)` | Conversation doc, optional case, images path | `bytes` | Generate PDF: metadata table, gold separator, iterate visible messages, render user text plain / assistant text as markdown→HTML via `write_html()`. Embed images from disk. |
| `build_pdf_filename(conversation, case_doc?)` | — | `str` | `FCI-{case_id}-transcript-{date}.pdf` or `FCI-chat-{short_id}-{date}.pdf` |
| `_md_to_html(text)` | Markdown string | HTML string | Convert markdown to HTML (tables, fenced_code, nl2br) |
| `_sanitize_text(text)` | String | String | Replace Unicode chars (em dash, smart quotes, etc.) for latin-1 encoding |

**Dependencies:** `fpdf2`, `markdown`

---

### 3.14 `scripts/seed_demo_data.py` (928 lines)

**Purpose:** Seeds MongoDB with demo data — 2 users and 5 cases.

**Key functions:**
- `parse_case_markdown(filepath)` — Parse `## N. SECTION TITLE` markdown files into preprocessed_data dict
- `_clean_content(content, section_key)` — Post-process raw case data: strip tool preamble, remove template instructions, convert form fields to tables, promote known headings
- `_convert_kv_runs_to_tables(content)` — Convert runs of 3+ `Key: Value` lines to markdown tables
- `_reformat_l1_header(content)` — Convert L1 referral form dump to clean table + narrative
- `seed()` — Drop collections, insert users + cases, verify

**Demo data:**
- 2 users: `ben.investigator` (user_001), `demo.investigator` (user_002)
- 5 cases:
  - CASE-2026-0451: Scam (romance scam, inline data)
  - CASE-2026-0387: CTM (sanctions exposure, inline data)
  - CASE-2026-0512: Fraud (account anomalies, inline data)
  - CASE-2026-0784: LE (Los Halcones, parsed from demo-1.md)
  - CASE-2026-0091: LE (Los Lobos, parsed from demo-2.md)

---

### 3.15 `scripts/test_anthropic_api.py` (573 lines)

**Purpose:** Standalone test script for Anthropic API integration testing. Not part of the production application.

---

## 4. Frontend Documentation

### 4.1 `client/src/main.jsx` (19 lines)

**Purpose:** React application root. Renders `<BrowserRouter>` > `<ThemeProvider>` > `<AuthProvider>` > `<App />` into `#root`.

---

### 4.2 `client/src/App.jsx` (53 lines)

**Purpose:** Route definitions.

**Routes:**

| Path | Component | Auth Required |
|------|-----------|---------------|
| `/login` | `LoginPage` | No |
| `/cases` | `CaseListPage` | Yes |
| `/investigation/:caseId` | `InvestigationPage` | Yes |
| `/chat` | `FreeChatPage` | Yes |
| `/chat/:conversationId` | `FreeChatPage` | Yes |
| `*` | Redirect to `/cases` or `/login` | — |

---

### 4.3 `client/src/context/AuthContext.jsx` (43 lines)

**Purpose:** In-memory authentication state.

**State:** `user` (object or null), `token` (string or null)

**Exposed values:** `{ user, token, isAuthenticated, login, logout }`

- `login(username)`: Calls `api.login()`, stores user + token in state
- `logout()`: Clears state, navigates to `/login`
- No localStorage — session is lost on page refresh

---

### 4.4 `client/src/context/ThemeContext.jsx` (44 lines)

**Purpose:** Dark/light mode toggle.

**State:** `theme` ('dark' | 'light')

**Behavior:**
- Initial theme: from localStorage `fci-theme`, then system preference, then default to 'dark'
- `useLayoutEffect` applies theme class to `<html>` before paint
- Stores preference in localStorage

**Exposed values:** `{ theme, isDark, toggleTheme }`

---

### 4.5 `client/src/services/api.js` (176 lines)

**Purpose:** All HTTP calls to the backend API.

**Helper functions:**
- `authHeaders(token)` — Returns headers with `Content-Type` + `Authorization: Bearer`
- `handleResponse(res)` — Parse JSON, throw on non-OK responses

**API functions:**

| Function | Method | Path | Description |
|----------|--------|------|-------------|
| `login(username)` | POST | `/api/auth/login` | Login |
| `getMe(token)` | GET | `/api/auth/me` | Get current user |
| `getCases(token)` | GET | `/api/cases` | List cases |
| `getCase(token, caseId)` | GET | `/api/cases/{caseId}` | Get case detail |
| `createConversation(token, caseId?, mode?)` | POST | `/api/conversations` | Create conversation |
| `sendMessage(token, convId, content, images?, stream?, initialAssessment?)` | POST | `/api/conversations/{id}/messages` | Send message (returns raw Response for streaming) |
| `getConversationHistory(token, convId)` | GET | `/api/conversations/{id}/history` | Get visible history |
| `getConversations(token, mode?)` | GET | `/api/conversations?mode=` | List conversations |
| `deleteConversation(token, convId)` | DELETE | `/api/conversations/{id}` | Delete conversation |
| `exportPdf(token, convId)` | GET | `/api/conversations/{id}/export/pdf` | Download PDF (blob → auto-download via `<a>` click) |
| `imageUrl(convId, imageId)` | — | `/api/conversations/{id}/images/{imageId}` | Build image URL (no fetch, just URL construction) |
| `reseedDatabase(token)` | POST | `/api/admin/reseed` | Reset demo data |
| `getHealth()` | GET | `/api/health` | Health check |

---

### 4.6 `client/src/hooks/useStreamingChat.js` (195 lines)

**Purpose:** Reusable hook for SSE-streaming chat, shared by InvestigationPage and FreeChatPage.

**State:** `messages`, `conversationId`, `sending`, `aiLoading`

**Returns:** `{ messages, setMessages, conversationId, setConversationId, sending, aiLoading, loadHistory, sendMessage, triggerInitialAssessment }`

**Key methods:**
- `readStream(response, streamMsgId)` — Read SSE from `response.body`, parse `content_delta`, `tool_use`, `stored`, `error` events, update messages state
- `loadHistory(convId)` — Fetch existing conversation history from API
- `triggerInitialAssessment(convId)` — Send initial assessment request (no user message), show gold spinner then streaming text
- `sendMessage(content, images?)` — Optimistic user message + streaming assistant response

**SSE parsing:** Manual parsing of `data:` lines from `ReadableStream` (not using `EventSource` — uses `fetch` + body reader for POST support).

---

### 4.7 `client/src/pages/LoginPage.jsx` (122 lines)

**Purpose:** Username-only login form.

**Props:** None

**State:** `username`, `error`, `loading`

**Behavior:** Submit → `auth.login(username)` → navigate to `/cases`. No password field.

**Design:** Centered card with gold gradient accent bar, radial gradient background, dot-grid pattern overlay.

---

### 4.8 `client/src/pages/CaseListPage.jsx` (119 lines)

**Purpose:** Display assigned cases in a card list.

**State:** `cases`, `loading`, `error`

**API calls:** `getCases(token)` on mount

**Child components:** `AppLayout`, `CaseCard`, `LoadingSpinner`, `ResetDemoButton` (internal)

**ResetDemoButton:** Calls `api.reseedDatabase(token)` then `logout()`. Confirmation dialog.

---

### 4.9 `client/src/pages/InvestigationPage.jsx` (208 lines)

**Purpose:** Main investigation view — split-panel with draggable divider.

**URL params:** `caseId` from `/investigation/:caseId`

**State:** `caseData`, `activeTab`, `caseLoading`, `error`, `leftWidth` (percentage, default 35%)

**Uses:** `useStreamingChat(token)` hook for chat state

**Initialization flow (useEffect):**
1. Fetch case detail
2. Set first available tab
3. Set `caseLoading = false` (left panel renders immediately)
4. If existing conversation → `loadHistory()`
5. If new case → `createConversation()` then `triggerInitialAssessment()`

**Drag handle:** Mouse events to resize left/right panels (min 20%, max 60%)

**Layout:** Left panel (case data: CaseHeader + CaseDataTabs + CaseDataPanel) | Gold drag handle | Right panel (chat: DownloadPdfButton + ChatMessageList + StreamingIndicator + ChatInput)

---

### 4.10 `client/src/pages/FreeChatPage.jsx` (231 lines)

**Purpose:** Free chat mode with sidebar conversation history.

**URL params:** `conversationId` (optional) from `/chat/:conversationId`

**State:** `sidebarConversations`

**Uses:** `useStreamingChat(token)` hook

**Key behavior:**
- First message: create `free_chat` conversation via API, then send message + stream response (duplicates SSE reading logic from hook for first-message edge case due to timing)
- Subsequent messages: use hook's `sendMessage()`
- Sidebar: lists free_chat conversations, supports delete
- New chat: clears state, navigates to `/chat`

---

### 4.11 `client/src/components/AppLayout.jsx` (85 lines)

**Purpose:** Global page layout — header bar + main content area.

**Props:** `{ children, caseInfo? }`

**Features:**
- Frosted glass header with blur effect
- Back button (shown when `caseInfo` provided)
- App title (links to /cases)
- Case ID + type badge (when on investigation page)
- Free chat nav icon, theme toggle, user display name, logout button

---

### 4.12 `client/src/components/ProtectedRoute.jsx` (12 lines)

**Purpose:** Auth guard. Redirects to `/login` if `!isAuthenticated`.

---

### 4.13 `client/src/components/cases/CaseCard.jsx` (66 lines)

**Purpose:** Single case card in the case list.

**Props:** `{ caseData, index }`

**Features:** Case ID (monospace), case type badge (color-coded), status badge (color-coded), summary (2-line clamp), subject user ID, creation date. Click navigates to `/investigation/{case_id}`. Button says "Continue" if conversation exists, "Open Case" if not. Staggered animation on index.

---

### 4.14 `client/src/components/chat/ChatSidebar.jsx` (65 lines)

**Purpose:** Conversation list sidebar for free chat.

**Props:** `{ conversations, activeId, onNewChat, onDelete }`

**Features:** "New Chat" button, scrollable conversation list with active highlighting, delete button (appears on hover, calls `onDelete`).

---

### 4.15 `client/src/components/investigation/CaseHeader.jsx` (24 lines)

**Purpose:** Case metadata header above the data tabs.

**Props:** `{ caseData }`

**Displays:** Subject user ID, case type badge, status badge, summary.

---

### 4.16 `client/src/components/investigation/CaseDataTabs.jsx` (40 lines)

**Purpose:** Tab bar for selecting preprocessed_data sections.

**Props:** `{ preprocessedData, activeTab, onTabChange }`

**Constant `TAB_LABELS`:** Maps 12 preprocessed_data keys to short display labels.

**Behavior:** Only renders tabs that have data. Gold underline on active tab.

---

### 4.17 `client/src/components/investigation/CaseDataPanel.jsx` (24 lines)

**Purpose:** Renders the selected case data tab content as markdown.

**Props:** `{ content, activeTab }`

**Uses:** `MarkdownRenderer` component. Shows placeholder icon + text when no tab selected.

---

### 4.18 `client/src/components/investigation/ChatMessageList.jsx` (58 lines)

**Purpose:** Scrollable list of chat messages with auto-scroll to bottom.

**Props:** `{ messages, aiLoading, emptyStateText, maxWidth, conversationId }`

**Features:**
- Empty state: gold-ringed dual spinner (when aiLoading) or chat icon + text
- Auto-scrolls to bottom on new messages via `useRef` + `scrollIntoView`
- 5% horizontal padding (inline styles)

---

### 4.19 `client/src/components/investigation/ChatMessage.jsx` (186 lines)

**Purpose:** Single message bubble (user or assistant).

**Props:** `{ message, conversationId }`

**Features:**
- **User messages:** Right-aligned, max-w-[75%], gold-tinted background, whitespace-pre-wrap text
- **Assistant messages:** Full-width, surface background, rendered as markdown via `MarkdownRenderer`
- **Image thumbnails:** For user messages with images. Falls back to `imageUrl(conversationId, img.image_id)` when `img.preview` is missing (after session refresh)
- **Lightbox:** Click thumbnail → full-size overlay portalled to `document.body` via `createPortal`. All inline styles (avoids Tailwind parent constraints). Download button + close button. Escape key closes.
- **Streaming cursor:** Blinking gold cursor character (`&#9612;`) when `isStreaming`
- **Tools used footer:** Lists referenced documents with gold-colored text

**Internal component `Lightbox`:** Fixed overlay with backdrop blur, image centered, download via fetch→blob→createObjectURL→click, close on backdrop click or Escape.

---

### 4.20 `client/src/components/investigation/ChatInput.jsx` (157 lines)

**Purpose:** Chat input area — textarea with image support.

**Props:** `{ onSend, disabled, maxWidth }`

**State:** `text`, `images`, `dragOver`

**Features:**
- Enter sends, Shift+Enter for newline
- Image paste (clipboard), drag-and-drop, and file picker
- Thumbnail previews above textarea (via `ImageUpload` component)
- Send button inside textarea container (bottom-right)
- Attach button inside textarea container (bottom-left)
- Drop zone indicator ("Drop image here")

**Internal function `fileToBase64(file)`:** Returns `{base64, media_type, preview}` using FileReader.

---

### 4.21 `client/src/components/investigation/StreamingIndicator.jsx` (21 lines)

**Purpose:** Gold shimmer "Analyzing..." pill shown while sending.

**Props:** None

**Design:** Three pulsing gold dots + "Analyzing..." text, with gold shimmer overlay animation.

---

### 4.22 `client/src/components/shared/DownloadPdfButton.jsx` (85 lines)

**Purpose:** PDF export button with visual state feedback.

**Props:** `{ conversationId, disabled }`

**State:** `state` — 'idle' | 'generating' | 'done' | 'error'

**Behavior:** Click → set 'generating' → call `exportPdf()` → 'done' (2s) → 'idle'. Different icon + label for each state. Uses auth token from context.

---

### 4.23 `client/src/components/shared/ImageUpload.jsx` (103 lines)

**Purpose:** Image file input + thumbnail management.

**Props:** `{ images, onImagesChange, showButton, showThumbnails }`

**Features:** Hidden file input, attach button (paperclip icon), thumbnails with hover-remove button. `fileToBase64()` converts files.

---

### 4.24 `client/src/components/shared/LoadingSpinner.jsx` (13 lines)

**Purpose:** Generic loading spinner.

**Props:** `{ size, className }` — size: 'sm' | 'md' | 'lg'

---

### 4.25 `client/src/components/shared/MarkdownRenderer.jsx` (55 lines)

**Purpose:** Markdown rendering using react-markdown with remark-gfm.

**Props:** `{ content, className }`

**Custom components:** table (rounded border container), th (surface bg), td (bordered), h2, h3, code (inline vs block detection via className), pre (surface bg with overflow).

---

### 4.26 `client/src/components/shared/Skeleton.jsx` (3 lines)

**Purpose:** Loading skeleton placeholder.

**Props:** `{ className }`

**Renders:** `<div>` with shimmer animation.

---

### 4.27 `client/src/utils/formatters.js` (73 lines)

**Purpose:** Formatting utilities.

**Functions:**

| Function | Description |
|----------|-------------|
| `formatTimestamp(isoString)` | Format to `dd MMM yyyy, HH:mm` (en-GB locale) |
| `formatTokens(count)` | Format number with K suffix |
| `capitalize(str)` | Capitalize first letter |
| `statusColor(status)` | Return Tailwind badge classes for case status (open→emerald, in_progress→gold, etc.) |
| `caseTypeColor(caseType)` | Return Tailwind badge classes for case type (scam→red, ctm→amber, ftm→blue, fraud→purple) |

---

## 5. API Contract (As-Built)

### Authentication

All endpoints except `/api/health`, `/api/auth/login`, and `/api/conversations/{id}/images/{image_id}` require:
```
Authorization: Bearer {session_token}
```

### Endpoints

#### `POST /api/auth/login`

```
Request:  {"username": "ben.investigator"}
Response: {"user_id": "user_001", "username": "ben.investigator",
           "display_name": "Ben", "token": "uuid-string"}
Errors:   400 (no username), 404 (user not found)
```

#### `GET /api/auth/me`

```
Response: {"user_id": "user_001", "username": "ben.investigator", "display_name": "Ben"}
Errors:   401 (invalid/missing token)
```

#### `GET /api/cases`

```
Response: {"cases": [
  {"case_id": "CASE-2026-0451", "case_type": "scam", "status": "open",
   "subject_user_id": "BIN-84729103", "summary": "...",
   "conversation_id": null, "created_at": "2026-03-01T09:00:00+00:00"}
]}
```

#### `GET /api/cases/{case_id}`

```
Response: {"case_id": "...", "case_type": "...", "status": "...",
           "subject_user_id": "...", "summary": "...",
           "conversation_id": "conv_abc123" | null,
           "created_at": "...",
           "preprocessed_data": {
             "l1_referral_narrative": "...",
             "c360_transaction_summary": "...",
             ...
           }}
Errors:   404 (case not found)
```

#### `POST /api/conversations`

```
Request:  {"case_id": "CASE-2026-0451", "mode": "case"}
          or {"mode": "free_chat"}
Response: {"conversation_id": "conv_abc123", "case_id": "...", "mode": "case"}
Errors:   400 (missing case_id for case mode, case not found)
```

#### `POST /api/conversations/{conversation_id}/messages`

```
Request:  {"content": "What do the transactions suggest?",
           "images": [{"base64": "...", "media_type": "image/png"}],
           "stream": true,
           "initial_assessment": false}

Streaming Response (SSE):
  data: {"type": "content_delta", "text": "The transaction"}
  data: {"type": "content_delta", "text": " pattern shows"}
  data: {"type": "tool_use", "tool": "get_reference_document",
         "document_id": "scam-fraud-sop", "document_title": "Scam & Fraud SOP"}
  data: {"type": "content_delta", "text": " according to the SOP..."}
  data: {"type": "done", "message_id": null, "token_usage": {"input_tokens": 5000, "output_tokens": 800}}
  data: {"type": "stored", "message_id": "msg_abc123def456"}

Non-streaming Response (stream: false):
  {"message_id": "msg_abc", "role": "assistant", "content": "...",
   "tools_used": [...], "token_usage": {...}, "timestamp": "..."}

Errors:   400 (empty content), 429 (rate limited)
```

#### `GET /api/conversations/{conversation_id}/history`

```
Response: {"conversation_id": "conv_abc123", "case_id": "...",
           "mode": "case", "title": "",
           "messages": [
             {"message_id": "msg_001", "role": "assistant",
              "content": "...", "tools_used": [...],
              "timestamp": "2026-03-01T09:05:00+00:00"},
             {"message_id": "msg_002", "role": "user",
              "content": "...", "images": [...],
              "timestamp": "..."}
           ]}
Errors:   404 (conversation not found)
```

#### `GET /api/conversations?mode=free_chat`

```
Response: {"conversations": [
  {"conversation_id": "conv_abc", "title": "Question about sanctions",
   "mode": "free_chat", "case_id": null,
   "updated_at": "...", "message_count": 4}
]}
```

#### `DELETE /api/conversations/{conversation_id}`

```
Response: {"status": "deleted"}
Errors:   404 (not found or not owned)
```

#### `GET /api/conversations/{conversation_id}/export/pdf`

```
Response: application/pdf blob
Headers:  Content-Disposition: attachment; filename="FCI-CASE-2026-0451-transcript-2026-03-05.pdf"
Errors:   404 (not found), 403 (not authorized), 400 (no messages)
```

#### `GET /api/conversations/{conversation_id}/images/{image_id}`

```
Auth:     NONE (unauthenticated — image IDs are random/unguessable)
Response: Image file (image/jpeg, image/png, etc.)
Errors:   404 (not found)
```

#### `POST /api/admin/reseed`

```
Response: {"status": "reseeded"}
Errors:   500 (seed script not found or failed)
```

#### `GET /api/health`

```
Auth:     NONE
Response: {"status": "ok", "mongodb": "connected",
           "knowledge_base_loaded": true,
           "core_documents_chars": 45000,
           "reference_documents_available": 8}
```

---

## 6. Data Models

### 6.1 MongoDB Collections

#### `users` Collection

```json
{
  "_id": "user_001",
  "username": "ben.investigator",
  "display_name": "Ben",
  "created_at": ISODate("2026-01-15T00:00:00Z")
}
```

No indexes beyond default `_id`.

#### `cases` Collection

```json
{
  "_id": "CASE-2026-0451",
  "case_type": "scam",
  "status": "open",
  "subject_user_id": "BIN-84729103",
  "summary": "Suspected romance scam — ...",
  "assigned_to": "user_001",
  "conversation_id": null,
  "preprocessed_data": {
    "l1_referral_narrative": "## L1 Customer Service Interactions...",
    "hexa_dump": null,
    "kyc_id_document": "## KYC Information...",
    "c360_transaction_summary": "## Counterparty Risk Summary...",
    "web_app_outputs": null,
    "elliptic_screening": "## Wallet Screening Results...",
    "prior_icr_summary": "## Prior Investigations...",
    "le_kodex_extraction": null,
    "rfi_user_communication": null,
    "case_intake_extraction": null,
    "osint_results": null,
    "investigator_notes": null
  },
  "created_at": ISODate("2026-03-01T09:00:00Z"),
  "updated_at": ISODate("2026-03-01T09:00:00Z")
}
```

No indexes beyond default `_id`. Cases are queried by `assigned_to` and `_id`.

#### `conversations` Collection

```json
{
  "_id": "conv_abc123def456",
  "case_id": "CASE-2026-0451",
  "user_id": "user_001",
  "mode": "case",
  "title": "",
  "status": "active",
  "messages": [
    {
      "message_id": "msg_001abc",
      "role": "system_injected",
      "content": "[CASE DATA]\n\n...",
      "timestamp": ISODate("..."),
      "visible": false
    },
    {
      "message_id": "msg_002def",
      "role": "assistant",
      "content": "## Initial Assessment\n\nThis case...",
      "tools_used": [],
      "token_usage": {"input_tokens": 12000, "output_tokens": 800},
      "timestamp": ISODate("..."),
      "visible": true
    },
    {
      "message_id": "msg_003ghi",
      "role": "user",
      "content": "What about the transaction pattern?",
      "images": [
        {
          "image_id": "img_abc123",
          "media_type": "image/png",
          "stored_path": "./data/images/conv_abc123/img_abc123.png"
        }
      ],
      "timestamp": ISODate("..."),
      "visible": true
    },
    {
      "message_id": "msg_004jkl",
      "role": "tool_exchange",
      "content": [{"type": "tool_use", "id": "...", "name": "get_reference_document", "input": {"document_id": "scam-fraud-sop"}}],
      "original_role": "assistant",
      "timestamp": ISODate("..."),
      "visible": false
    },
    {
      "message_id": "msg_005mno",
      "role": "tool_exchange",
      "content": [{"type": "tool_result", "tool_use_id": "...", "content": "...SOP content..."}],
      "original_role": "user",
      "timestamp": ISODate("..."),
      "visible": false
    },
    {
      "message_id": "msg_006pqr",
      "role": "assistant",
      "content": "According to the Scam & Fraud SOP...",
      "tools_used": [{"tool": "get_reference_document", "document_id": "scam-fraud-sop", "document_title": "Scam & Fraud Investigation SOP"}],
      "token_usage": {"input_tokens": 18000, "output_tokens": 1200},
      "timestamp": ISODate("..."),
      "visible": true
    }
  ],
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

No indexes beyond default `_id`. Conversations are queried by `_id`, `user_id`, and `mode`.

### 6.2 In-Memory State

| Location | Variable | Type | Description |
|----------|----------|------|-------------|
| `server/routers/auth.py` | `_sessions` | `dict[str, dict]` | Token → user mapping. Clears on server restart. |
| `server/services/ai_client.py` | `_client` | `AsyncAnthropic | None` | Anthropic client singleton |
| `server/database.py` | `_client`, `_db` | Module globals | MongoDB connection |
| `server/main.py` | `app.state.knowledge_base` | `KnowledgeBase` | Loaded KB instance |

---

## 7. Knowledge Base Architecture

### 7.1 Disk Structure

```
knowledge_base/
├── core/           # Tier 1 — loaded into memory on startup
│   ├── SYSTEM-PROMPT.md          (441 lines) — Master system prompt defining AI persona and behavior
│   ├── decision-matrix.md        (134 lines) — Case outcome decision criteria
│   ├── icr-general-rules.md      (572 lines) — Investigation rules and procedures
│   ├── icr-steps-analysis.md     (1584 lines) — Detailed analysis phase steps
│   ├── icr-steps-decision.md     (739 lines) — Decision phase steps
│   ├── icr-steps-post.md         (411 lines) — Post-decision phase steps
│   ├── icr-steps-setup.md        (629 lines) — Case setup phase steps
│   ├── mlro-escalation-matrix.md (97 lines) — MLRO escalation criteria
│   ├── prompt-library.md         (1375 lines) — ICR form section prompts
│   └── qc-submission-checklist.md (511 lines) — QC requirements
├── reference-index.yaml          (87 lines) — Index of Tier 2 documents
└── reference/      # Tier 2 — available via get_reference_document tool call
    ├── CTM-on-chain-alerts-sop.md      (365 lines, ~7K tokens)
    ├── block-unblock-guidelines.md     (138 lines, ~5K tokens)
    ├── case-decision-archive.md        (544 lines, ~15K tokens)
    ├── fake-documents-guidelines.md    (60 lines, ~4K tokens)
    ├── ftm-sop.md                      (460 lines, ~7K tokens)
    ├── gambling-legality-matrix.md     (896 lines, ~6K tokens)
    ├── mlro-escalation-decisions.md    (1049 lines, ~5K tokens)
    └── scam-fraud-sop.md              (200 lines, ~8K tokens)
```

### 7.2 Loading Behavior

**Tier 1 (Startup):**
- `KnowledgeBase.load_on_startup()` reads all `core/*.md` files (sorted alphabetically)
- Each file prefixed with `# {FILENAME_STEM_UPPER}` header
- Files joined with `\n\n---\n\n` separator
- Result stored in `core_content` string

**Tier 2 (On Demand):**
- `reference-index.yaml` parsed on startup → `reference_index` list
- Index formatted as text → `reference_index_text` (appended to system prompt)
- Documents loaded only when AI calls `get_reference_document(document_id)`
- `KnowledgeBase.get_reference_document()` validates ID against index, reads file

### 7.3 Tool Definition Sent to Anthropic API

```json
{
  "name": "get_reference_document",
  "description": "Retrieve a reference document from the knowledge base. Use this tool when you need detailed procedural guidance, SOP requirements, or historical decision precedents...",
  "input_schema": {
    "type": "object",
    "properties": {
      "document_id": {
        "type": "string",
        "description": "The unique identifier of the reference document to retrieve, as listed in the reference document index."
      }
    },
    "required": ["document_id"]
  }
}
```

### 7.4 Reference Index Structure (from YAML)

```yaml
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
  # ... 7 more entries
```

8 reference documents total, with estimated token counts ranging from 4,000 to 15,000.

### 7.5 Startup Logging

On startup, `main.py` logs:
```
Knowledge base loaded: {N} core chars, {M} reference documents
```

---

## 8. Configuration and Environment

### 8.1 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | `""` | Anthropic API key (must be set) |
| `ANTHROPIC_MODEL` | No | `claude-sonnet-4-6` | Model ID |
| `MONGODB_URI` | No | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | No | `fci_platform` | Database name |

Other settings (HOST, PORT, LOG_LEVEL, etc.) have sensible defaults and rarely need overriding.

### 8.2 Config Files

| File | Format | Description |
|------|--------|-------------|
| `.env` | Key=Value | Runtime environment variables (gitignored) |
| `.env.example` | Key=Value | Template with placeholder values |
| `client/vite.config.js` | JS | Vite dev server config + API proxy |
| `client/tailwind.config.js` | JS | Custom color scales, fonts, shadows |
| `client/postcss.config.js` | JS | PostCSS plugins (tailwindcss, autoprefixer) |
| `requirements.txt` | pip | Python dependencies |
| `client/package.json` | JSON | NPM dependencies |

### 8.3 Setup from Scratch

```bash
# 1. Prerequisites
# - Python 3.11+
# - Node.js 18+
# - MongoDB running on localhost:27017

# 2. Clone and configure
cd fci-platform
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY=sk-ant-...

# 3. Backend setup
pip install -r requirements.txt

# 4. Frontend setup
cd client
npm install
cd ..

# 5. Seed demo data
python scripts/seed_demo_data.py

# 6. Run backend (Terminal 1)
cd server && uvicorn main:app --reload --port 8000

# 7. Run frontend (Terminal 2)
cd client && npm run dev

# 8. Open http://localhost:5173
# Login as: ben.investigator
```

### 8.4 Required API Keys

- **Anthropic API key** — required for AI functionality. Set as `ANTHROPIC_API_KEY` in `.env`.
- No other API keys required.

---

## 9. Features Inventory

### 9.1 Working Features

| Feature | Description |
|---------|-------------|
| **Mock authentication** | Username-only login, UUID session tokens, in-memory session store |
| **Case management** | List assigned cases, view case detail with 12-section preprocessed data |
| **Case data viewer** | Tabbed panel with markdown rendering for each data section |
| **AI investigation chat** | Streaming SSE chat with Claude, full context assembly |
| **Initial assessment** | Automatic AI case analysis on first conversation creation |
| **Knowledge base (Tier 1)** | 10 core documents loaded into system prompt |
| **Knowledge base (Tier 2)** | 8 reference documents available via tool calls, with audit trail |
| **Prompt caching** | System prompt sent with `cache_control: ephemeral` for Anthropic caching |
| **Tool call loop** | AI can call `get_reference_document` up to 5 times per turn |
| **Streaming responses** | Real-time text streaming via SSE, tool use notifications mid-stream |
| **Image upload** | Paste, drag-drop, or file picker. Images sent as base64 to Anthropic API |
| **Image persistence** | Images saved to disk, thumbnails persist across sessions via server endpoint |
| **Image lightbox** | Click thumbnail for full-size overlay with download button |
| **PDF export** | Server-side PDF generation with metadata, markdown rendering, embedded images |
| **Free chat mode** | Conversations without cases, with sidebar history |
| **Chat history** | Conversation history persisted in MongoDB, loadable on return |
| **Auto-generated titles** | Free chat conversations get titles from first user message |
| **Dark/light mode** | Toggle with localStorage persistence, FOUC prevention |
| **Resizable panels** | Draggable divider between case data and chat panels |
| **Split loading** | Case data renders immediately, chat shows spinner during AI processing |
| **Demo data reset** | Button to wipe and reseed all demo data |
| **Rate limit handling** | Auto-retry (3x) on Anthropic 429s, user-facing error messages |
| **Skeleton loading** | Loading placeholders while fetching data |

### 9.2 Partially Implemented

| Feature | Status |
|---------|--------|
| **Case status updates** | `update_case_status()` exists in backend but no frontend trigger except auto-set to `in_progress` on conversation creation |
| **HealthResponse schema** | Schema says `core_documents_tokens` but endpoint returns `core_documents_chars` |

### 9.3 Stubbed/Placeholder

| Feature | Status |
|---------|--------|
| **Document processing pipeline** | Spec exists (`DOCUMENT_PIPELINE_SPEC.md`) but not implemented. Current approach uses direct image passing in chat. |
| **demo_data/ directory** | Empty with `.gitkeep` |

### 9.4 Known Issues / Observations

| Issue | Details |
|-------|---------|
| **FreeChatPage duplicates SSE reading logic** | The first-message handler in `FreeChatPage.jsx` duplicates the SSE stream reading from `useStreamingChat.js` hook, rather than reusing it. This is due to a timing issue where `conversationId` isn't set in the hook's ref when the first message is sent. |
| **Image double-storage on streaming** | In `send_message_streaming()`, images are stored via `_store_images()`. Then in `store_streamed_response()`, `_store_images()` is called again if `user_images` is truthy. This could result in duplicate image files on disk. |
| **No pagination** | Case list, conversation history, and sidebar all load all records. Fine for demo but won't scale. |
| **Session lost on refresh** | Auth is in-memory only. Any page refresh logs the user out. |
| **No HTTPS** | Development only — no TLS configuration |
| **HealthResponse mismatch** | Schema defines `core_documents_tokens` but the `/api/health` endpoint returns `core_documents_chars` |
| **Unauthenticated image endpoint** | `GET /api/conversations/{id}/images/{image_id}` has no auth — acceptable for demo (random IDs) but not production |

---

## 10. Dependencies Manifest

### 10.1 Backend (Python)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi[standard]` | 0.135.1 | Web framework |
| `uvicorn[standard]` | 0.41.0 | ASGI server |
| `anthropic` | 0.84.0 | Anthropic Claude API client |
| `pymongo` | 4.16.0 | MongoDB driver (native async) |
| `pydantic` | 2.12.5 | Data validation |
| `pydantic-settings` | >=2.7.0 | Settings management from env vars |
| `pyyaml` | >=6.0.2 | YAML parsing (reference index) |
| `python-dotenv` | >=1.0.1 | .env file loading |
| `sse-starlette` | 3.2.0 | Server-Sent Events for FastAPI |
| `fpdf2` | >=2.8.0 | PDF generation |
| `markdown` | >=3.5 | Markdown→HTML conversion (for PDF) |

### 10.2 Frontend (Node.js)

**Dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | ^18 | UI framework |
| `react-dom` | ^18 | React DOM renderer |
| `react-markdown` | ^9 | Markdown rendering component |
| `react-router-dom` | ^6 | Client-side routing |
| `remark-gfm` | ^4 | GitHub Flavored Markdown plugin |

**Dev Dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| `@vitejs/plugin-react` | ^4 | Vite React plugin |
| `autoprefixer` | ^10 | CSS vendor prefixing |
| `postcss` | ^8 | CSS processing |
| `tailwindcss` | ^3 | Utility-first CSS framework |
| `vite` | ^5 | Build tool / dev server |

### 10.3 System Dependencies

| Dependency | Expected Version |
|------------|-----------------|
| Python | 3.11+ |
| Node.js | 18+ |
| MongoDB | 7.x (local, port 27017) |

---

## 11. File-by-File Reference

| File Path | Type | Lines | Purpose |
|-----------|------|-------|---------|
| `.env.example` | Config | 4 | Environment variable template |
| `.gitignore` | Config | 32 | Git ignore rules |
| `BUG_HUNTING_BRIEFING.md` | Doc | 103 | Bug hunting instructions |
| `CLAUDE.md` | Doc | 216 | AI assistant orientation |
| `DESIGN_UPDATE_STATUS.md` | Doc | 112 | Design implementation status |
| `DOCUMENT_PIPELINE_SPEC.md` | Doc | 206 | Future document processing spec |
| `requirements.txt` | Config | 11 | Python dependencies |
| `client/DESIGN_SPEC.md` | Doc | 669 | Visual design specification |
| `client/index.html` | HTML | 24 | Entry HTML with theme script |
| `client/package.json` | Config | 25 | NPM dependencies |
| `client/postcss.config.js` | Config | 6 | PostCSS plugins |
| `client/tailwind.config.js` | Config | 55 | Tailwind theme customization |
| `client/vite.config.js` | Config | 15 | Vite dev server + API proxy |
| `client/src/main.jsx` | JSX | 19 | React app root |
| `client/src/App.jsx` | JSX | 53 | Route definitions |
| `client/src/index.css` | CSS | 231 | Tailwind base + custom animations |
| `client/src/context/AuthContext.jsx` | JSX | 43 | Auth state (in-memory) |
| `client/src/context/ThemeContext.jsx` | JSX | 44 | Dark/light mode toggle |
| `client/src/hooks/useStreamingChat.js` | JS | 195 | SSE streaming chat hook |
| `client/src/services/api.js` | JS | 176 | All API calls |
| `client/src/utils/formatters.js` | JS | 73 | Formatting utilities |
| `client/src/pages/LoginPage.jsx` | JSX | 122 | Login page |
| `client/src/pages/CaseListPage.jsx` | JSX | 119 | Case list page |
| `client/src/pages/InvestigationPage.jsx` | JSX | 208 | Investigation split-panel page |
| `client/src/pages/FreeChatPage.jsx` | JSX | 231 | Free chat page |
| `client/src/components/AppLayout.jsx` | JSX | 85 | Global layout + header |
| `client/src/components/ProtectedRoute.jsx` | JSX | 12 | Auth guard |
| `client/src/components/cases/CaseCard.jsx` | JSX | 66 | Case summary card |
| `client/src/components/chat/ChatSidebar.jsx` | JSX | 65 | Free chat conversation list |
| `client/src/components/investigation/CaseHeader.jsx` | JSX | 24 | Case metadata header |
| `client/src/components/investigation/CaseDataTabs.jsx` | JSX | 40 | Data section tab bar |
| `client/src/components/investigation/CaseDataPanel.jsx` | JSX | 24 | Markdown data panel |
| `client/src/components/investigation/ChatMessageList.jsx` | JSX | 58 | Scrollable message list |
| `client/src/components/investigation/ChatMessage.jsx` | JSX | 186 | Message bubble + lightbox |
| `client/src/components/investigation/ChatInput.jsx` | JSX | 157 | Chat input + image handling |
| `client/src/components/investigation/StreamingIndicator.jsx` | JSX | 21 | Gold shimmer indicator |
| `client/src/components/shared/DownloadPdfButton.jsx` | JSX | 85 | PDF export button |
| `client/src/components/shared/ImageUpload.jsx` | JSX | 103 | Image upload component |
| `client/src/components/shared/LoadingSpinner.jsx` | JSX | 13 | Loading spinner |
| `client/src/components/shared/MarkdownRenderer.jsx` | JSX | 55 | Markdown renderer |
| `client/src/components/shared/Skeleton.jsx` | JSX | 3 | Skeleton placeholder |
| `server/__init__.py` | Python | 0 | Package init |
| `server/config.py` | Python | 44 | Configuration |
| `server/database.py` | Python | 55 | MongoDB connection |
| `server/main.py` | Python | 122 | FastAPI app entry |
| `server/models/__init__.py` | Python | 0 | Package init |
| `server/models/schemas.py` | Python | 190 | Pydantic models |
| `server/routers/__init__.py` | Python | 0 | Package init |
| `server/routers/admin.py` | Python | 54 | Admin reseed endpoint |
| `server/routers/auth.py` | Python | 94 | Auth endpoints |
| `server/routers/cases.py` | Python | 34 | Case endpoints |
| `server/routers/conversations.py` | Python | 357 | Conversation endpoints |
| `server/services/__init__.py` | Python | 0 | Package init |
| `server/services/ai_client.py` | Python | 558 | Anthropic API wrapper |
| `server/services/case_service.py` | Python | 111 | Case CRUD |
| `server/services/conversation_manager.py` | Python | 751 | Conversation orchestration |
| `server/services/knowledge_base.py` | Python | 82 | Two-tier knowledge base |
| `server/services/pdf_export.py` | Python | 281 | PDF generation |
| `scripts/seed_demo_data.py` | Python | 928 | Demo data seeder |
| `scripts/test_anthropic_api.py` | Python | 573 | API test script |
| `knowledge_base/reference-index.yaml` | YAML | 87 | Reference document index |
| `knowledge_base/core/SYSTEM-PROMPT.md` | MD | 441 | Master system prompt |
| `knowledge_base/core/decision-matrix.md` | MD | 134 | Case decision matrix |
| `knowledge_base/core/icr-general-rules.md` | MD | 572 | ICR rules |
| `knowledge_base/core/icr-steps-analysis.md` | MD | 1584 | Analysis phase steps |
| `knowledge_base/core/icr-steps-decision.md` | MD | 739 | Decision phase steps |
| `knowledge_base/core/icr-steps-post.md` | MD | 411 | Post-decision steps |
| `knowledge_base/core/icr-steps-setup.md` | MD | 629 | Setup phase steps |
| `knowledge_base/core/mlro-escalation-matrix.md` | MD | 97 | MLRO escalation criteria |
| `knowledge_base/core/prompt-library.md` | MD | 1375 | ICR form prompts |
| `knowledge_base/core/qc-submission-checklist.md` | MD | 511 | QC checklist |
| `knowledge_base/reference/CTM-on-chain-alerts-sop.md` | MD | 365 | CTM on-chain alerts SOP |
| `knowledge_base/reference/block-unblock-guidelines.md` | MD | 138 | Block/unblock guidelines |
| `knowledge_base/reference/case-decision-archive.md` | MD | 544 | Historical decisions |
| `knowledge_base/reference/fake-documents-guidelines.md` | MD | 60 | Fake document detection |
| `knowledge_base/reference/ftm-sop.md` | MD | 460 | Fiat TM SOP |
| `knowledge_base/reference/gambling-legality-matrix.md` | MD | 896 | Gambling legality |
| `knowledge_base/reference/mlro-escalation-decisions.md` | MD | 1049 | MLRO decisions |
| `knowledge_base/reference/scam-fraud-sop.md` | MD | 200 | Scam/fraud SOP |
