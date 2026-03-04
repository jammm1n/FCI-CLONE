# FCI Investigation Platform

## Project Overview
AI-assisted financial crime investigation platform (Phase 1 MVP). Investigators log in, view assigned cases, and conduct AI-powered investigations via a chat interface with access to case data and a knowledge base.

## Architecture
- **Backend:** FastAPI (`server/`) — fully implemented, running on port 8000
- **Frontend:** React 18 + Vite (`client/`) — functional, running on port 5173
- **Database:** MongoDB (local, port 27017)
- **AI:** Anthropic Claude API with tool use and SSE streaming
- **Styling:** Tailwind CSS 3 with custom `primary` (blue) and `surface` (slate) color scales

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

## Active Task: Frontend Design Overhaul
See `client/DESIGN_SPEC.md` for the complete design specification. This is a comprehensive visual overhaul to make the dashboard look like a premium SaaS product. Key areas:

- **Light/dark mode** — ThemeContext with system detection + manual toggle + localStorage persistence
- **Typography** — Inter font, bump all font sizes (text-xs/text-sm → text-base for body)
- **Animations** — fade-in-up on messages, staggered card animations, shimmer loading, blinking streaming cursor, smooth page transitions
- **Polished components** — gradient buttons, glass-effect header, rounded-2xl bubbles, auto-growing textarea, proper drag handle with grip indicator
- **Badge system** — consistent ring-based badges for case types and statuses in both themes
- **Shadows & depth** — custom soft shadow scale, glow effects on hover
- **Skeleton loading** — replace spinners with skeleton placeholders
- **Two new files only:** ThemeContext.jsx and Skeleton.jsx. Everything else is styling updates.

Follow the implementation order in Section 10 of the spec for maximum impact at each step.

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
