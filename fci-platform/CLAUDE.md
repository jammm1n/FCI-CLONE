# FCI Investigation Platform

## Project Overview
AI-assisted financial crime investigation platform (Phase 1 MVP). Investigators log in, view assigned cases, and conduct AI-powered investigations via a chat interface with access to case data and a knowledge base.

## Architecture
- **Backend:** FastAPI (`server/`) — fully implemented, running on port 8000
- **Frontend:** React 18 + Vite (`client/`) — functional, running on port 5173
- **Database:** MongoDB (local, port 27017)
- **AI:** Anthropic Claude API with tool use and SSE streaming
- **Styling:** Tailwind CSS 3 with custom `gold` (Binance #F0B90B) and `surface` (dark neutral) color scales

## Project Structure
```
fci-platform/
  server/             # FastAPI backend (complete)
    config.py         # Pydantic settings from .env
    database.py       # PyMongo 4.16+ async (NOT Motor)
    main.py           # App entry, lifespan, CORS
    routers/          # auth.py, cases.py, conversations.py
    services/         # ai_client.py, conversation_manager.py, case_service.py, knowledge_base.py
    models/schemas.py # Pydantic v2 models
  client/             # React frontend
    src/
      main.jsx, App.jsx
      context/AuthContext.jsx
      services/api.js
      utils/formatters.js
      pages/            # LoginPage, CaseListPage, InvestigationPage
      components/
        AppLayout.jsx, ProtectedRoute.jsx
        shared/         # LoadingSpinner, MarkdownRenderer, ImageUpload
        cases/          # CaseCard
        investigation/  # CaseHeader, CaseDataTabs, CaseDataPanel,
                        # ChatMessageList, ChatMessage, ChatInput, StreamingIndicator
  knowledge_base/     # core/ (10 .md files) + reference/ (8 .md files)
  scripts/seed_demo_data.py
```

## Current State
- Backend: fully working — auth, cases, conversations with streaming SSE
- Frontend: fully styled with Binance Dark + Gold design (see `client/DESIGN_SPEC.md`)
- Seed data: 2 users (`ben.investigator` = user_001, `demo.investigator` = user_002), 3 demo cases
- Streaming chat works end-to-end
- Resizable split-panel investigation view (drag handle between case data and chat)
- Split loading: case data panel renders immediately, chat shows gold spinner during AI initial assessment

## Case Data Schema (preprocessed_data)
Cases store a `preprocessed_data` dict with sections matching the real case package template.
These keys map to UI tabs (left panel) and to markdown headers in the AI's `[CASE DATA]` injection.

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

All fields are optional (not every case has every section). The schema is defined in:
- `server/models/schemas.py` → `PreprocessedData` model
- `server/services/conversation_manager.py` → `section_map` in `_build_case_data_markdown()`
- `client/src/components/investigation/CaseDataTabs.jsx` → `TAB_LABELS`

To add a new demo case: see `scripts/seed_demo_data.py` for the structure, or insert directly
into MongoDB `fci_platform.cases` collection. Cases are assigned to users via `assigned_to` field
(e.g., `"user_001"` for ben.investigator). Two sanitised real-case templates are at `/demo-1.md`
and `/demo-2.md` in the repo root — these need to be converted into the schema above.

## Future: Document Processing Pipeline
See `DOCUMENT_PIPELINE_SPEC.md` for the full architecture spec. Key idea:
- Separate extraction prompts (data processing) from investigation prompts (main chat)
- Documents/images/PDFs processed via standalone API calls, condensed to text summaries
- Only summaries injected into main chat context — saves massive token overhead
- Multi-stage PDF flow for LE cases: individual summaries → consolidated summary
- NOT for the current demo sprint — current demo uses direct image passing in chat

## Key Conventions
- Dark theme throughout — `bg-surface-900` body, `bg-surface-800` panels
- No state management library — React Context for auth only
- No localStorage — session state lives in memory
- Enter sends messages, Shift+Enter for newline
- Backend uses `KNOWLEDGE_BASE_PATH` in config (not `KNOWLEDGE_BASE_DIR`)
- PyMongo 4.16+ native async — NOT Motor

## Running the App
```bash
# Terminal 1: Backend
cd server && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd client && npm run dev

# Seed data (once, requires MongoDB running)
python scripts/seed_demo_data.py
```
