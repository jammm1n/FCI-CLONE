# FCI Investigation Platform

## Project Overview
AI-assisted financial crime investigation platform. Investigators log in, view assigned cases, and conduct AI-powered investigations via a chat interface with access to case data and a knowledge base.

The platform has two integrated subsystems:
1. **Investigation platform** — investigators view assigned cases and conduct AI-powered investigations via chat
2. **Data Ingestion Dashboard** — investigators create cases, upload/process data, then assemble and promote to investigations

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
      ingestion.py               # Ingestion endpoints (case CRUD, section processing, assembly)
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
      ingestion/                 # Ingestion service layer
        __init__.py
        ingestion_service.py     # Case CRUD, section management, assembly + case promotion
        c360_processor.py        # Toolkit pipeline async wrapper
        elliptic_processor.py    # Elliptic API async wrapper
        ai_processor.py          # AI prompt dispatch for all sections
        kodex_processor.py       # Kodex PDF extraction + AI pipeline
    models/
      schemas.py                 # Pydantic models (PreprocessedData, CaseSummary, etc.)
      ingestion_schemas.py       # Ingestion-specific Pydantic models

  client/
    src/
      main.jsx, App.jsx
      context/AuthContext.jsx
      services/
        api.js                   # Investigation API calls + case export
        ingestion_api.js         # Ingestion API calls
      hooks/
        useStreamingChat.js      # Streaming chat hook
        useIngestionStatus.js    # Ingestion polling hook
      utils/formatters.js
      pages/
        LoginPage.jsx
        CaseListPage.jsx
        InvestigationPage.jsx
        FreeChatPage.jsx
        IngestionPage.jsx        # Ingestion dashboard (single page, inline components)
      components/
        AppLayout.jsx
        ProtectedRoute.jsx
        shared/                  # LoadingSpinner, MarkdownRenderer, ImageUpload, etc.
        cases/CaseCard.jsx       # Case card with export button
        investigation/
          CaseDataTabs.jsx       # Two-tier tab system (groups + sub-tabs for C360)
          CaseDataPanel.jsx
          CaseHeader.jsx
          ChatMessageList.jsx
          ChatInput.jsx
          StreamingIndicator.jsx

  knowledge_base/
    core/                        # Tier 1 — loaded on startup
    reference/                   # Tier 2 — loaded on demand via tool calls
    prompts/                     # Ingestion extraction prompts (used by ai_processor.py)

  reference/toolkit/
    icr_router_reference.py      # READ-ONLY. Source of auto-population logic to port.

  scripts/
    seed_demo_data.py
    test_anthropic_api.py
    test_icr_import.py           # [TO BUILD] Toolkit validation script

  FCI-Ingestion-Dashboard-PRD.md  # Primary requirements document for ingestion work
```

---

## Data Ingestion Dashboard

The ingestion dashboard is fully built. All sections work with AI processing. Assembly creates a `cases` collection document and redirects to investigations.

**Flow:** Create case → upload/process sections → assemble → case appears in investigations list → open for AI-assisted investigation.

**Reference:** `FCI-Ingestion-Dashboard-PRD.md` for original requirements.

**Key rules for ingestion work:**
- The toolkit code in `server/services/icr/` is already copied and must not be modified
- `reference/toolkit/icr_router_reference.py` is read-only reference material — port logic from it, do not modify it
- `session_store.py` was intentionally excluded from the copied toolkit code — do not recreate it
- All processing state goes to MongoDB (`ingestion_cases` collection), not in-memory
- The toolkit pipeline is synchronous CPU-bound code — always wrap it with `asyncio.to_thread()` when calling from async FastAPI handlers
- Always read file bytes from `UploadFile` objects in the endpoint handler, before spawning any background task

---

## Case Data Schema (preprocessed_data)

Cases store a `preprocessed_data` dict populated by ingestion assembly. These keys map to UI tabs and markdown headers in the AI's `[CASE DATA]` injection.

```
# C360 sub-processors (from ingestion C360 pipeline)
tx_summary       → "Transaction Summary"
user_profile     → "User Profile"
privacy_coin     → "Privacy Coin Breakdown"
counterparty     → "Counterparty Analysis"
device_ip        → "Device & IP Analysis"
failed_fiat      → "Failed Fiat Withdrawals"
ctm_alerts       → "CTM Alerts"
ftm_alerts       → "FTM Alerts"
account_blocks   → "Account Blocks"
address_xref     → "Address Cross-Reference"
uid_search       → "UID Search Results"

# Standalone sections
elliptic_addresses → "Elliptic Screening Addresses"
elliptic_raw     → "Elliptic Screening Results" (tab-display only, NOT injected into chat)
elliptic         → "Elliptic Wallet Screening"  (AI analysis, injected into chat)
l1_referral      → "L1 Referral Narrative"
haoDesk          → "HaoDesk Case Data"
kyc              → "KYC Document Summary"
prior_icr        → "Prior ICR Summary"
rfi              → "RFI Summary"
kodex            → "Law Enforcement / Kodex"
l1_victim        → "L1 Victim Communications"
l1_suspect       → "L1 Suspect Communications"
investigator_notes → "Investigator Notes"
```

Defined in: `server/models/schemas.py` → `PreprocessedData`, `server/services/conversation_manager.py` → `_build_case_data_markdown()`, `client/src/components/investigation/CaseDataTabs.jsx` → `TAB_GROUPS`

The investigation page uses two-tier tabs: top-level groups (C360 expands into sub-tabs, others are single-content) showing only groups with data.

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
- Cases are created through the ingestion pipeline (no demo cases seeded)
- Run `python scripts/seed_demo_data.py` to seed users only