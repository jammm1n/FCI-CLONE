# FCI Investigation Platform

## Project Overview
AI-assisted financial crime investigation platform. Investigators log in, view assigned cases, and conduct AI-powered investigations via a chat interface with access to case data and a knowledge base.

There are two active workstreams:
1. **Existing platform (Phase 1 MVP)** — fully working. Do not modify existing files unless the task explicitly requires it.
2. **Data Ingestion Dashboard (active build)** — new feature slice being added to this codebase. See PRD below.

---

## Architecture
- **Backend:** FastAPI (`server/`) — fully implemented, running on port 8000
- **Frontend:** React 18 + Vite (`client/`) — functional, running on port 5173
- **Database:** MongoDB (local, port 27017)
- **AI:** Anthropic Claude API with tool use and SSE streaming
- **Styling:** Tailwind CSS 3 with custom `gold` (Binance #F0B90B) and `surface` (dark neutral) color scales

---

## Project Structure

```
fci-platform/
  server/
    config.py                    # Pydantic settings from .env
    database.py                  # PyMongo 4.16+ async (NOT Motor)
    main.py                      # App entry, lifespan, CORS, router registration
    routers/
      auth.py                    # POST /api/auth/login, GET /api/auth/me
      cases.py                   # GET /api/cases, GET /api/cases/{id}
      conversations.py           # Conversation CRUD, streaming, PDF export, images
      admin.py                   # POST /api/admin/reseed
      ingestion.py               # [TO BUILD] All ingestion endpoints
    services/
      ai_client.py               # Anthropic API wrapper (streaming + tool loop)
      conversation_manager.py    # Conversation lifecycle orchestration
      case_service.py            # Case CRUD
      knowledge_base.py          # Two-tier KB loader
      pdf_export.py              # PDF transcript generation
      icr/                       # [COPIED FROM TOOLKIT] C360 processing engine
        __init__.py
        address_manager.py
        constants.py
        elliptic_api.py
        file_detector.py
        health_check.py
        parser.py
        processor_registry.py
        uid_search.py
        utils.py
        validation.py
        processors/
          __init__.py, base.py, blocks.py, counterparty.py
          ctm_alerts.py, device.py, elliptic.py, failed_fiat.py
          ftm_alerts.py, privacy_coin.py, transaction_summary.py
          user_info_extended.py
      ingestion/                 # [TO BUILD] Ingestion service layer
        __init__.py
        ingestion_service.py     # Case CRUD + status management
        c360_processor.py        # Toolkit pipeline async wrapper
        elliptic_processor.py    # Elliptic API async wrapper
    models/
      schemas.py                 # Existing Pydantic models (do not modify)
      ingestion_schemas.py       # [TO BUILD] Ingestion Pydantic models

  client/
    src/
      main.jsx, App.jsx
      context/AuthContext.jsx
      services/
        api.js                   # Existing API calls (do not modify)
        ingestion_api.js         # [TO BUILD] All ingestion API calls
      hooks/
        useStreamingChat.js      # Existing hook
        useIngestionStatus.js    # [TO BUILD] Polling hook
      utils/formatters.js
      pages/
        LoginPage.jsx
        CaseListPage.jsx
        InvestigationPage.jsx
        FreeChatPage.jsx
        IngestionPage.jsx        # [TO BUILD]
      components/
        AppLayout.jsx            # Needs nav link added (one line)
        ProtectedRoute.jsx
        shared/                  # LoadingSpinner, MarkdownRenderer, ImageUpload, etc.
        cases/CaseCard.jsx
        investigation/           # All existing investigation components
        ingestion/               # [TO BUILD]
          CaseCreationForm.jsx
          IngestionHeader.jsx
          IngestionSection.jsx
          C360Section.jsx
          EllipticSection.jsx
          NotesSection.jsx
          AssembledOutputModal.jsx

  knowledge_base/
    core/                        # Tier 1 — loaded on startup
    reference/                   # Tier 2 — loaded on demand via tool calls
    preprocessing/               # [TO BUILD in Phase 2] Extraction prompts

  reference/toolkit/
    icr_router_reference.py      # READ-ONLY. Source of auto-population logic to port.

  scripts/
    seed_demo_data.py
    test_anthropic_api.py
    test_icr_import.py           # [TO BUILD] Toolkit validation script

  FCI-Ingestion-Dashboard-PRD.md  # Primary requirements document for ingestion work
```

---

## Data Ingestion Dashboard — Active Build

**Read `FCI-Ingestion-Dashboard-PRD.md` before doing any ingestion work.**

The PRD is the authoritative source for everything ingestion-related:
- Phase definitions and build order (Section 3 and 6.2)
- Database schema for `ingestion_cases` collection (Section 4)
- Full API contract with request/response shapes (Section 5)
- Detailed implementation specs including code patterns (Section 6)

**Current phase:** Phase 1 — Infrastructure + Toolkit Port

**Key rules for ingestion work:**
- The toolkit code in `server/services/icr/` is already copied and must not be modified
- `reference/toolkit/icr_router_reference.py` is read-only reference material — port logic from it, do not modify it
- `session_store.py` was intentionally excluded from the copied toolkit code — do not recreate it
- All processing state goes to MongoDB (`ingestion_cases` collection), not in-memory
- The toolkit pipeline is synchronous CPU-bound code — always wrap it with `asyncio.to_thread()` when calling from async FastAPI handlers
- Always read file bytes from `UploadFile` objects in the endpoint handler, before spawning any background task

---

## Existing Platform — Do Not Break

The existing investigation platform is fully working. The blast radius of the ingestion build on existing files is deliberately minimal:

| File | Allowed Change |
|------|---------------|
| `server/main.py` | Register ingestion router (one line) |
| `server/config.py` | Add `ELLIPTIC_API_KEY: str = ""` |
| `client/src/App.jsx` | Add `/ingest` route (one line) |
| `client/src/components/AppLayout.jsx` | Add "Ingest" nav link |
| `requirements.txt` | Add `openpyxl>=3.1.0` if not present |
| `.env.example` | Add `ELLIPTIC_API_KEY=` placeholder |

**No other existing files should be modified.**

---

## Case Data Schema (preprocessed_data)

Cases store a `preprocessed_data` dict. These keys map to UI tabs and markdown headers in the AI's `[CASE DATA]` injection.

```
l1_referral_narrative    → "L1 Referral Narrative"
hexa_dump                → "HEXA Dump (Full)"
kyc_id_document          → "KYC / ID Document"
c360_transaction_summary → "C360 Transaction Summary"
web_app_outputs          → "Web App Outputs"
elliptic_screening       → "Elliptic Screening"
prior_icr_summary        → "Prior ICR Summary"
le_kodex_extraction      → "LE / Kodex Extraction"
rfi_user_communication   → "RFI / User Communication"
case_intake_extraction   → "Case Intake Extraction"
osint_results            → "OSINT Results"
investigator_notes       → "Investigator Notes"
```

Defined in: `server/models/schemas.py` → `PreprocessedData`, `server/services/conversation_manager.py` → `_build_case_data_markdown()`, `client/src/components/investigation/CaseDataTabs.jsx` → `TAB_LABELS`

The ingestion dashboard assembles and writes these fields when Phase 5 integration is built. See PRD Section 4.6 for the field mapping from `ingestion_cases` to `preprocessed_data`.

---

## Key Conventions

- Dark theme throughout — `bg-surface-900` body, `bg-surface-800` panels, `gold-400` accents
- No state management library — React Context for auth only
- No localStorage — session state lives in memory only
- Enter sends messages in chat, Shift+Enter for newline
- Backend uses `KNOWLEDGE_BASE_PATH` in config (not `KNOWLEDGE_BASE_DIR`)
- PyMongo 4.16+ native async — NOT Motor
- All new Pydantic models use v2 syntax — `model_config = ConfigDict(...)`, not `class Config`
- Background tasks use `fastapi.BackgroundTasks`, not `asyncio.create_task`

---

## Running the App

```bash
# Terminal 1: Backend
cd server && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd client && npm run dev

# Seed data (once, requires MongoDB running)
python scripts/seed_demo_data.py
```

---

## Seed Data

- 2 users: `ben.investigator` (user_001), `demo.investigator` (user_002)
- 3 demo cases assigned to user_001
- To add cases: see `scripts/seed_demo_data.py` or insert directly into MongoDB `fci_platform.cases`