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
- Frontend: fully functional but visually raw/unstyled
- Seed data: 2 users (`ben.investigator`, `demo.investigator`), 3 cases (scam, CTM, fraud)
- Streaming chat works end-to-end
- Resizable split-panel investigation view (drag handle between case data and chat)

## Active Task: Frontend Design Overhaul (Binance Dark + Gold)
See `client/DESIGN_SPEC.md` for the complete design specification (v3). Binance-inspired dark-luxury aesthetic: dark surfaces, warm gold accents, Plus Jakarta Sans typography, atmospheric depth. Key areas:

- **Light/dark mode** — ThemeContext with system detection + manual toggle + localStorage (dark default)
- **Typography** — Plus Jakarta Sans (NOT Inter — banned as generic), JetBrains Mono for code
- **Colour system** — `surface` scale (cool-neutral darks, #0B0E11 to #F5F6F7), `gold` scale centered on Binance #F0B90B
- **Status colours** — Binance palette: #0ECB81 green, #F6465D red, #1E9CF4 blue
- **Hero moment** — Gold shimmer sweep on AI streaming indicator ("Analyzing...")
- **Animations** — orchestrated login sequence, staggered cards, gold-shimmer keyframes, panel slide-ins
- **Polished components** — gold gradient buttons (dark text on gold), glass-effect header, gold hover glows, gold active tabs
- **Atmospheric backgrounds** — radial gradient + dot-grid on login, grain texture on case data panel
- **Badge system** — ring-based badges; "In Progress" uses gold accent, "Open" uses Binance emerald
- **Shadows & depth** — stronger values for dark mode, `glow-gold` / `glow-gold-lg` accent shadows
- **Two new files only:** ThemeContext.jsx and Skeleton.jsx. Everything else is styling updates.

Follow the implementation order in Section 14 of the spec for maximum impact at each step.

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
