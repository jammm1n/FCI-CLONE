# FCI Investigation Platform — Data Ingestion Dashboard
## Product Requirements Document

**Version:** 1.0  
**Date:** March 2026  
**Status:** Phase 1 — Active Development  
**Author:** Ben — Financial Crime Investigator, Level 2 Compliance

---

## Table of Contents

1. [Overview & Scope](#1-overview--scope)
2. [Architecture](#2-architecture)
3. [Phase Definitions](#3-phase-definitions)
4. [Database Schema](#4-database-schema)
5. [API Contract](#5-api-contract)
6. [Phase 1 Build Specification](#6-phase-1-build-specification)
7. [Phase 2 — AI Text Modules (Summary)](#7-phase-2--ai-text-modules)
8. [Phase 3 — Communications Modules (Summary)](#8-phase-3--communications-modules)
9. [Phase 4 — Kodex PDF Pipeline (Summary)](#9-phase-4--kodex-pdf-pipeline)
10. [Phase 5 — Integration and Handoff (Summary)](#10-phase-5--integration-and-handoff)
11. [Open Questions](#11-open-questions)

---

## 1. Overview & Scope

### 1.1 Purpose

The Data Ingestion Dashboard replaces the current manual case data collection workflow. Investigators currently spend 15–20 minutes per case gathering spreadsheets from C360, screening wallets in Elliptic, copying Kodex PDFs, and pasting text from multiple sources before they can begin an AI-assisted investigation. The ingestion dashboard automates this pipeline.

The output of the ingestion dashboard is a single assembled case data markdown document — the same format the existing investigation platform already consumes. When the investigator clicks "Start Investigation," this document is written into the platform's MongoDB `cases` collection and the investigation begins exactly as it does today with pre-staged demo data.

### 1.2 What We Are Building

A new `IngestionPage` inside the existing `fci-platform` codebase. The investigator workflow is:

1. Log in to the existing platform (auth unchanged)
2. Navigate to `/ingest` (new route)
3. Enter a HowDesk case number and subject UID
4. Upload all C360 spreadsheets at once (bulk upload, identical behaviour to the existing toolkit)
5. Review extracted wallet addresses, add any manual addresses, submit to Elliptic
6. Complete additional data modules in subsequent phases
7. Click "Start Investigation" — assembled markdown is written to MongoDB and the investigator is navigated to the existing investigation view

### 1.3 Integration Point with the Existing Platform

The existing `fci-platform` seeds demo data into the MongoDB `cases` collection via `scripts/seed_demo_data.py`. Each case document has a `preprocessed_data` dict with optional markdown fields. The investigation conversation manager reads these fields and assembles them into the initial AI context.

The ingestion dashboard replaces the seed script. When the investigator completes ingestion, the backend writes the assembled case data to the `cases` collection in the exact same format. No changes to the investigation view, conversation manager, AI client, or knowledge base are required in any phase.

**The integration point is the `cases` collection. Nothing else changes in the existing platform.**

### 1.4 What Is Out of Scope (All Phases)

- Changes to the investigation view, chat interface, or conversation manager
- Changes to the knowledge base or AI client
- Live API connections to HowDesk or Binance Admin
- Real authentication (mock auth continues throughout)
- Production deployment or multi-user concurrency
- OSINT integration

### 1.5 Success Criteria

| Phase | Definition of Success |
|-------|----------------------|
| Phase 1 | Investigator uploads a full set of C360 spreadsheets, sees all 10 processor outputs in the dashboard, reviews and submits wallet addresses to Elliptic, and views the assembled case data markdown. Output quality matches the existing toolkit. |
| Phase 2 | All text-based AI modules operational (Hexa dump, ICRs, RFIs, KYC images). Investigator can complete ingestion without needing Phase 3–4 sources. |
| Phase 3 | L1 Victim and Suspect communications operational including image upload, translation, and batching. |
| Phase 4 | Kodex PDF pipeline operational. Multi-stage processing handles multi-page PDFs correctly. |
| Phase 5 | End-to-end flow from login → ingest → investigate works without any manual steps. Ingestion is the post-login landing page. |

---

## 2. Architecture

### 2.1 Approach: Feature Slice Inside Existing Platform

The ingestion dashboard is built as a new feature slice within the existing `fci-platform` codebase. It is not a separate application. It shares:

- The existing React/Vite frontend (same build, same server)
- The existing FastAPI backend (same process, new router registered)
- The existing MongoDB instance (`fci_platform` database, new collection)
- The existing mock authentication system (zero changes)
- The existing design system (Tailwind config, surface/gold colour scales, all components)

"Standalone testing" means navigating to `/ingest` in the browser. There is no separate server to run, no separate database, and no merge to perform later. When Phase 5 is complete and ingestion becomes the landing page, the change is a single redirect in the auth flow.

### 2.2 Blast Radius on Existing Code

The following existing files are modified. No other existing files are touched in Phase 1.

| File | Change | Risk |
|------|--------|------|
| `server/main.py` | +1 line: register ingestion router | Zero — adding a router cannot break existing routes |
| `requirements.txt` | Add `openpyxl>=3.1.0` if not already present | Zero |
| `client/src/App.jsx` | +1 route: `/ingest` → `IngestionPage` | Zero — adding a route cannot break existing routes |
| `client/src/components/AppLayout.jsx` | Add "Ingest" nav link in header | Minimal — visual addition only |
| `server/config.py` | Add `ELLIPTIC_API_KEY: str = ""` setting | Zero |
| `.env.example` | Add `ELLIPTIC_API_KEY=` placeholder | Zero |

### 2.3 New File Structure

All new files are additive. No existing files are deleted or structurally modified.

#### Backend — New Files

```
server/routers/ingestion.py                        All ingestion API endpoints

server/services/icr/                               Copied from toolkit (see 2.4)
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
    __init__.py
    base.py
    blocks.py
    counterparty.py
    ctm_alerts.py
    device.py
    elliptic.py
    failed_fiat.py
    ftm_alerts.py
    privacy_coin.py
    transaction_summary.py
    user_info_extended.py

server/services/ingestion/__init__.py
server/services/ingestion/ingestion_service.py     Case CRUD + status management
server/services/ingestion/c360_processor.py        Toolkit pipeline wrapper
server/services/ingestion/elliptic_processor.py    Elliptic API wrapper

server/models/ingestion_schemas.py                 Pydantic models
```

#### Frontend — New Files

```
client/src/pages/IngestionPage.jsx
client/src/components/ingestion/CaseCreationForm.jsx
client/src/components/ingestion/IngestionHeader.jsx
client/src/components/ingestion/IngestionSection.jsx    Reusable status wrapper
client/src/components/ingestion/C360Section.jsx
client/src/components/ingestion/EllipticSection.jsx
client/src/components/ingestion/NotesSection.jsx
client/src/components/ingestion/AssembledOutputModal.jsx
client/src/hooks/useIngestionStatus.js                  Status polling hook
client/src/services/ingestion_api.js                    All ingestion API calls
```

### 2.4 Toolkit Import Strategy

The toolkit's `backend/services/icr/` directory is copied directly into `server/services/icr/`. This is a deliberate copy, not a git submodule or symlink. The toolkit is the source of truth during its own development. Once the toolkit is stable, the copy is taken once and lives in the platform codebase.

#### Files NOT Copied

| File | Reason for Exclusion |
|------|---------------------|
| `session_store.py` | Replaced entirely by MongoDB. The ingestion service writes processing state directly to the `ingestion_cases` collection. No in-memory session management required. |
| `field_discovery.py` | Optional SQLite-based field usage logging. No impact on processing output. Include or exclude at your discretion. If excluded, verify nothing in the copied files imports it. |

> **Note:** After copying, verify no file in the copied directory imports `session_store` or `field_discovery`. The toolkit's `health_check.py` imports `processor_registry` (not `session_store`) — this is fine.

#### Dependencies

Add to `requirements.txt` if not already present: `openpyxl>=3.1.0`

All other dependencies used by the toolkit (`csv`, `io`, `json`, `threading`, etc.) are Python standard library.

### 2.5 System Diagram

```
Browser (React 18)
  LoginPage | CaseListPage | InvestigationPage | IngestionPage (NEW)
       │
       │  Vite proxy /api → :8000
       ▼
FastAPI Backend (:8000)
  Existing: auth.py, cases.py, conversations.py, admin.py
  New:      ingestion.py ─────────────────────────────────────┐
                                                               │
  New services:                                               │
    ingestion_service.py                                      │
    c360_processor.py ──── services/icr/ (toolkit) ◄──────── ┘
    elliptic_processor.py ─ services/icr/elliptic_api.py
       │                              │
  ┌────┴──────────────┐   ┌──────────┴──────────────┐
  │ MongoDB (:27017)  │   │ External APIs            │
  │ fci_platform DB   │   │ Elliptic AML (Phase 1)   │
  │ - users           │   │ Anthropic Claude (Ph 2+) │
  │ - cases           │   └─────────────────────────┘
  │ - conversations   │
  │ - ingestion_cases │
  │   (NEW)           │
  └───────────────────┘
```

---

## 3. Phase Definitions

| Phase | Name | Scope Summary | Definition of Done |
|-------|------|---------------|-------------------|
| 1 | Infrastructure + Toolkit Port | Repo scaffolding, IngestionPage shell, case creation, C360 bulk upload + full toolkit processing (all 10 processors), Elliptic address review + screening, Investigator Notes, assembled output display | Investigator completes a full C360 + Elliptic workflow and views the assembled case data markdown |
| 2 | AI Text Modules | Hexa dump restructuring, Previous ICR extraction (multi-entry), RFI extraction (multi-entry), KYC document image extraction. New IngestionAIClient service. Preprocessing prompt library. | All text/image AI modules operational; investigator can complete ingestion for standard cases without Phase 3–4 sources |
| 3 | Communications Modules | L1 Victim communications (text + images, batching, translation). L1 Suspect communications (same pattern). | Both comms sections operational with full translation and image handling |
| 4 | Kodex PDF Pipeline | Multi-stage PDF processing: parallel per-document extraction, consolidation call, page chunking for large PDFs | Investigator uploads Kodex PDFs and receives a consolidated LE summary |
| 5 | Integration + Handoff | "Start Investigation" writes assembled markdown to `cases` collection. Navigation to investigation view. Ingestion becomes the post-login landing page. | End-to-end flow: login → ingest → investigate works without any manual steps |

> **Note:** Sections 7–10 of this PRD contain phase summaries for Phases 2–5. Full technical specifications for each phase will be written as addendum documents before development of that phase begins.

---

## 4. Database Schema

### 4.1 New Collection: `ingestion_cases`

The HowDesk case number is the primary key (`_id`). One document per case.

#### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `_id` | String | HowDesk case number (e.g. `CASE-2026-0451`). Primary key. |
| `status` | String | Case lifecycle state: `ingesting` \| `ready` \| `investigating` \| `completed` \| `archived` |
| `created_by` | String | References `users._id` |
| `subject_uid` | String | The Binance UID being investigated. Mandatory. |
| `coconspirator_uids` | Array\<String\> | Optional. Used by UID search and Kodex extraction. |
| `sections` | Object | One key per data source. See Section 4.2. |
| `assembled_case_data` | String \| null | Final assembled markdown. Set by the `/assemble` endpoint. |
| `created_at` | DateTime | UTC timestamp of case creation |
| `updated_at` | DateTime | UTC timestamp of last update to any field |
| `completed_at` | DateTime \| null | Set when status transitions to `completed` |

### 4.2 Sections Object

Every section follows the same base structure. Additional fields are noted per section.

#### `c360` section

| Field | Type | Notes |
|-------|------|-------|
| `status` | String | `empty` \| `processing` \| `complete` \| `error` |
| `output` | String \| null | Full assembled markdown from all 10 processors |
| `wallet_addresses` | Array\<Object\> | `[{address, source}]` — extracted for Elliptic review |
| `files_uploaded` | Integer | Count of files received |
| `detected_file_types` | Array\<String\> | e.g. `["IT", "BP", "CTM_ALERTS", ...]` |
| `warnings` | Array\<Object\> | `[{level, message}]` from `health_check.py` |
| `error_message` | String \| null | Set on processing failure |
| `updated_at` | DateTime \| null | Last update timestamp |

#### `elliptic` section

| Field | Type | Notes |
|-------|------|-------|
| `status` | String | `empty` \| `processing` \| `complete` \| `error` \| `none` |
| `output` | String \| null | Markdown report from Elliptic API |
| `wallet_addresses` | Array\<String\> | Final list submitted (C360-extracted + manual) |
| `manual_addresses` | Array\<String\> | Investigator-added addresses |
| `error_message` | String \| null | Set on API failure |
| `updated_at` | DateTime \| null | Last update timestamp |

#### `hexa_dump`, `kyc`, `l1_victim`, `l1_suspect` sections (Phase 2/3)

| Field | Type | Notes |
|-------|------|-------|
| `status` | String | `empty` \| `processing` \| `complete` \| `error` \| `none` |
| `output` | String \| null | AI-generated markdown |
| `error_message` | String \| null | |
| `updated_at` | DateTime \| null | |

#### `previous_icrs` and `rfis` sections (Phase 2)

| Field | Type | Notes |
|-------|------|-------|
| `status` | String | `empty` \| `processing` \| `complete` \| `error` \| `none` |
| `items` | Array\<Object\> | `[{item_id, raw_text, output, status, created_at}]` — one per uploaded entry |
| `output` | String \| null | Assembled output of all individual entries |
| `error_message` | String \| null | |
| `updated_at` | DateTime \| null | |

#### `kodex` section (Phase 4)

| Field | Type | Notes |
|-------|------|-------|
| `status` | String | `empty` \| `processing` \| `complete` \| `error` \| `none` |
| `items` | Array\<Object\> | `[{item_id, filename, individual_summary, status, created_at}]` — one per PDF |
| `output` | String \| null | Consolidated summary from Stage 2 consolidation call |
| `error_message` | String \| null | |
| `updated_at` | DateTime \| null | |

#### `investigator_notes` section

| Field | Type | Notes |
|-------|------|-------|
| `status` | String | `empty` \| `complete` — no processing, no `none` option |
| `output` | String \| null | Freeform text, passed through as-is |
| `updated_at` | DateTime \| null | |

### 4.3 Section State Machine

| State | Visual | Meaning | Sections That Can Enter |
|-------|--------|---------|------------------------|
| `empty` | Grey circle ○ | No data submitted, not marked None | All sections on creation |
| `processing` | Gold spinner ◐ | Background task running | `c360`, `elliptic`, all AI sections |
| `complete` | Green dot ● | Processing succeeded, output available | All sections |
| `error` | Red dot ✗ | Processing failed, error message available | `c360`, `elliptic`, all AI sections |
| `none` | Grey tick ✓ None | Investigator confirmed not applicable | `elliptic`, `hexa_dump`, `previous_icrs`, `rfis`, `kyc`, `l1_victim`, `l1_suspect`, `kodex` |

State transitions:
- `empty` → `processing` → `complete` or `error`
- `empty` → `none`
- `error` → `processing` (retry)
- `none` → `empty` (undo)
- No undo from `complete` in Phase 1

### 4.4 Case Lifecycle States

| Status | Meaning | Transition Trigger |
|--------|---------|-------------------|
| `ingesting` | Case created, data being collected | Set on case creation |
| `ready` | All sections terminal, awaiting Start Investigation | Set automatically when last section reaches `complete` or `none` |
| `investigating` | Handed off to investigation platform | Set by `/assemble` endpoint (Phase 5) |
| `completed` | Investigation finished and exported | Set by investigation platform |
| `archived` | Hidden from active UI, retained for audit | Manual or automated after completion |

> **Note:** `investigator_notes` is always optional and never blocks the `ready` state. All other sections must be `complete` or `none` before status transitions to `ready`.

### 4.5 One Active Case Per Investigator

The backend enforces a single active case per investigator. On `POST /api/ingestion/cases`:

- If the investigator has an existing case in `ingesting` or `ready` state, the request is rejected with 409 Conflict and the existing `case_id` is returned in the response.
- The frontend hides the creation form when an active case exists, but the backend is the authoritative guard.
- To start a new case, the existing case must be in `investigating`, `completed`, or `archived` state.

### 4.6 Relationship to the `cases` Collection (Phase 5)

In Phase 5, the `/assemble` endpoint writes a new document to the existing `cases` collection. Field mapping:

| `ingestion_cases` field | `cases.preprocessed_data` field |
|------------------------|--------------------------------|
| `sections.c360.output` | `c360_transaction_summary` |
| `sections.elliptic.output` | `elliptic_screening` |
| `sections.hexa_dump.output` | `hexa_dump` |
| `sections.previous_icrs.output` | `prior_icr_summary` |
| `sections.rfis.output` | `rfi_user_communication` |
| `sections.kyc.output` | `kyc_id_document` |
| `sections.l1_victim.output` | `l1_referral_narrative` |
| `sections.l1_suspect.output` | `l1_suspect_comms` |
| `sections.kodex.output` | `le_kodex_extraction` |
| `sections.investigator_notes.output` | `investigator_notes` |

In Phases 1–4, the assembled case data is displayed in the UI as a copyable markdown block for manual QA. The investigator can paste it into the existing platform to validate quality before Phase 5 automated integration is built.

### 4.7 Indexes

```javascript
// Primary key index is automatic on _id
db.ingestion_cases.createIndex({ "created_by": 1, "status": 1 })
// Enables: find active case for investigator (one-at-a-time enforcement)
```

---

## 5. API Contract

All endpoints are prefixed `/api/ingestion/`. All require Bearer token authentication via the existing `get_current_user` dependency from `server/routers/auth.py`. No changes to the authentication system.

### 5.1 Case Management Endpoints

---

#### `POST /api/ingestion/cases`

Create a new ingestion case. Rejected if the investigator has an existing active case.

**Request Body**
```json
{
  "case_id": "CASE-2026-0451",
  "subject_uid": "BIN-84729103",
  "coconspirator_uids": []
}
```

**Response 201 — Created**
```json
{
  "case_id": "CASE-2026-0451",
  "status": "ingesting",
  "subject_uid": "BIN-84729103",
  "sections": { "...each section with status: empty..." }
}
```

**Response 409 — Active Case Exists**
```json
{ "detail": "Active case exists", "existing_case_id": "CASE-2026-0450" }
```

**Response 409 — Case ID Already Exists**
```json
{ "detail": "Case CASE-2026-0451 already exists" }
```

---

#### `GET /api/ingestion/cases/active`

Returns the investigator's current active case if one exists. Called on page load to resume an interrupted session.

**Response 200 — Active Case Found**
```json
{
  "case_id": "CASE-2026-0451",
  "status": "ingesting",
  "subject_uid": "BIN-84729103",
  "sections": { "...full section data..." }
}
```

**Response 200 — No Active Case**
```json
{ "case_id": null }
```

---

#### `GET /api/ingestion/cases/{case_id}`

Full case document. Used after initial load or after an action that requires full section data.

**Response 200** — Full `ingestion_cases` document as defined in Section 4.

---

#### `GET /api/ingestion/cases/{case_id}/status`

Lightweight status snapshot for polling. Returns only section statuses and timestamps, not outputs. Designed to be called every 2.5 seconds.

**Response 200**
```json
{
  "case_id": "CASE-2026-0451",
  "case_status": "ingesting",
  "sections": {
    "c360":               { "status": "processing", "updated_at": "2026-03-05T10:05:00Z" },
    "elliptic":           { "status": "empty",      "updated_at": null },
    "hexa_dump":          { "status": "empty",      "updated_at": null },
    "previous_icrs":      { "status": "empty",      "updated_at": null },
    "rfis":               { "status": "empty",      "updated_at": null },
    "kyc":                { "status": "empty",      "updated_at": null },
    "l1_victim":          { "status": "empty",      "updated_at": null },
    "l1_suspect":         { "status": "empty",      "updated_at": null },
    "kodex":              { "status": "empty",      "updated_at": null },
    "investigator_notes": { "status": "empty",      "updated_at": null }
  }
}
```

---

### 5.2 C360 Processing Endpoints

---

#### `POST /api/ingestion/cases/{case_id}/c360`

Upload C360 spreadsheet files. Triggers background processing immediately and returns 202 Accepted. Poll `/status` to track completion.

**Request** — `multipart/form-data`
- `files`: one or more `.xlsx` or `.csv` files
- `subject_uid`: string

**Response 202 — Accepted**
```json
{
  "accepted": true,
  "files_received": 12,
  "section_status": "processing",
  "message": "Processing started. Poll /status for updates."
}
```

**Response 400 — Invalid File Type**
```json
{ "detail": "Only .xlsx and .csv files are accepted" }
```

**Response 409 — Already Processing or Complete**
```json
{ "detail": "C360 section is already complete. Reprocessing not supported in Phase 1." }
```

**Background Processing — MongoDB Updates**
- On task start: `sections.c360.status = processing`
- On success: `status = complete`, `output = markdown`, `wallet_addresses = [...]`, `detected_file_types = [...]`, `warnings = [...]`
- On failure: `status = error`, `error_message = exception text`

---

#### `GET /api/ingestion/cases/{case_id}/c360`

Returns the C360 section output after processing is complete.

**Response 200**
```json
{
  "status": "complete",
  "output": "### Transaction Summary\n\n...",
  "detected_file_types": ["IT", "BP", "CTM_ALERTS", "FTM_ALERTS", "BLOCKS"],
  "undetected_files": [],
  "warnings": [],
  "wallet_addresses": [
    { "address": "1A1zP1...", "source": "ADDR_VALUE" },
    { "address": "bc1qxy...", "source": "ADDR_EXPOSED" }
  ],
  "updated_at": "2026-03-05T10:07:00Z"
}
```

---

### 5.3 Elliptic Endpoints

---

#### `GET /api/ingestion/cases/{case_id}/elliptic/addresses`

Returns the combined address list (C360-extracted + manual) for the investigator to review before submitting.

**Response 200**
```json
{
  "c360_addresses": [
    { "address": "1A1zP1...", "source": "ADDR_VALUE" },
    { "address": "bc1qxy...", "source": "ADDR_EXPOSED" }
  ],
  "manual_addresses": [],
  "total": 2
}
```

**Response 400 — C360 Not Complete**
```json
{ "detail": "C360 processing must complete before Elliptic screening" }
```

---

#### `POST /api/ingestion/cases/{case_id}/elliptic/addresses`

Add or replace manual wallet addresses. Replaces the entire `manual_addresses` list.

**Request Body**
```json
{ "manual_addresses": ["bc1qxy2k...", "0x4e83..."] }
```

**Response 200**
```json
{ "manual_addresses": ["bc1qxy2k...", "0x4e83..."], "total_addresses": 4 }
```

---

#### `POST /api/ingestion/cases/{case_id}/elliptic/submit`

Submit the confirmed address list to Elliptic. Triggers background processing.

**Request Body**
```json
{
  "addresses": ["1A1zP1...", "bc1qxy...", "bc1qxy2k..."],
  "customer_id": "BIN-84729103"
}
```

**Response 202**
```json
{ "accepted": true, "addresses_submitted": 3, "section_status": "processing" }
```

---

#### `GET /api/ingestion/cases/{case_id}/elliptic`

Returns the Elliptic section output after screening is complete.

**Response 200**
```json
{
  "status": "complete",
  "output": "## Elliptic Wallet Screening Results\n\n...",
  "addresses_screened": 3,
  "updated_at": "2026-03-05T10:12:00Z"
}
```

---

### 5.4 Utility Endpoints

---

#### `POST /api/ingestion/cases/{case_id}/sections/{section_key}/none`

Mark a section as not applicable.

Valid `section_key` values: `elliptic`, `hexa_dump`, `previous_icrs`, `rfis`, `kyc`, `l1_victim`, `l1_suspect`, `kodex`

> `c360` and `investigator_notes` cannot be marked None. `c360` is core required. `investigator_notes` is always optional and has its own save endpoint.

**Response 200**
```json
{ "section": "kodex", "status": "none" }
```

---

#### `PUT /api/ingestion/cases/{case_id}/notes`

Save investigator notes. No AI processing — pure pass-through. Empty string accepted (clears notes, resets status to `empty`).

**Request Body**
```json
{ "notes": "Subject appears to be part of a coordinated group..." }
```

**Response 200**
```json
{ "status": "complete", "updated_at": "2026-03-05T10:20:00Z" }
```

---

#### `POST /api/ingestion/cases/{case_id}/assemble`

Assemble all section outputs into the final case data markdown document. Can only be called when all non-notes sections are in terminal state (`complete` or `none`).

**Phase 1 behaviour:** Stores `assembled_case_data` in MongoDB and returns the markdown for display.  
**Phase 5 behaviour:** Additionally writes to the `cases` collection and returns `case_id` for navigation.

**Response 200**
```json
{
  "assembled_case_data": "# Case Data: CASE-2026-0451\n\n## Subject Information\n...",
  "sections_included": ["c360", "elliptic"],
  "sections_none": ["hexa_dump", "previous_icrs", "rfis", "kyc", "l1_victim", "l1_suspect", "kodex"]
}
```

**Response 409 — Sections Not Complete**
```json
{
  "detail": "Cannot assemble: sections not complete",
  "incomplete_sections": ["c360"]
}
```

---

### 5.5 Phase 2–4 Endpoint Stubs

Full request/response specifications will be written in each phase's PRD addendum.

| Phase | Method | Path | Purpose |
|-------|--------|------|---------|
| 2 | POST | `/cases/{id}/hexa` | Submit Hexa dump text for AI restructuring |
| 2 | POST | `/cases/{id}/icrs` | Add one ICR text entry, trigger AI extraction |
| 2 | DELETE | `/cases/{id}/icrs/{icr_id}` | Remove an ICR entry |
| 2 | POST | `/cases/{id}/rfis` | Add one RFI text entry, trigger AI extraction |
| 2 | DELETE | `/cases/{id}/rfis/{rfi_id}` | Remove an RFI entry |
| 2 | POST | `/cases/{id}/kyc` | Upload KYC images for AI extraction |
| 3 | POST | `/cases/{id}/l1-victim` | Submit L1 victim comms (text + images) |
| 3 | POST | `/cases/{id}/l1-suspect` | Submit L1 suspect comms (text + images) |
| 4 | POST | `/cases/{id}/kodex` | Upload Kodex PDFs, trigger multi-stage pipeline |
| 5 | PATCH | `/cases/{id}/assemble` | Extended: write to `cases` collection, return investigation URL |

### 5.6 Standard Error Responses

| HTTP Code | Meaning |
|-----------|---------|
| 400 | Bad request — invalid input, wrong file type, malformed request body |
| 401 | Unauthenticated — missing or invalid Bearer token |
| 404 | Not found — `case_id` does not exist |
| 409 | Conflict — active case exists, section already processing, sections not complete for assembly |
| 422 | Pydantic validation failure — request body fails schema validation |
| 500 | Internal server error — processing failure, MongoDB error, external API failure |

---

## 6. Phase 1 Build Specification

### 6.1 Scope

Phase 1 delivers: case creation and active case resumption, C360 bulk upload with full 10-processor toolkit pipeline, Elliptic address review and screening, Investigator Notes, and assembled output display.

Phase 1 sections not yet functional (Hexa dump, ICRs, RFIs, KYC, L1 comms, Kodex) are present in the UI as locked placeholder cards labelled "Available in a future phase." They are not hidden — their presence communicates the complete roadmap to stakeholders during demos.

### 6.2 Build Order

Backend must be fully built and endpoint-tested before frontend work begins. The toolkit import must be validated before writing any service code.

1. Copy `services/icr/` from toolkit into `server/services/icr/` (excluding `session_store.py`)
2. Run toolkit validation script — confirm all imports resolve and one processor executes successfully
3. Add `openpyxl` to `requirements.txt` if not present; `pip install -r requirements.txt`
4. Add `ELLIPTIC_API_KEY` to `server/config.py` and `.env.example`
5. Create `server/models/ingestion_schemas.py`
6. Create `server/services/ingestion/__init__.py`
7. Create `server/services/ingestion/ingestion_service.py`
8. Create `server/services/ingestion/c360_processor.py`
9. Create `server/services/ingestion/elliptic_processor.py`
10. Create `server/routers/ingestion.py`
11. Register router in `server/main.py` (one line)
12. Test all backend endpoints with curl or Postman before writing frontend
13. Create `client/src/services/ingestion_api.js`
14. Create `client/src/hooks/useIngestionStatus.js`
15. Create ingestion components: `CaseCreationForm`, `IngestionSection`, `C360Section`, `EllipticSection`, `NotesSection`, `AssembledOutputModal`, `IngestionHeader`
16. Create `client/src/pages/IngestionPage.jsx`
17. Add route to `client/src/App.jsx` (one line)
18. Add "Ingest" nav link to `client/src/components/AppLayout.jsx`

### 6.3 Toolkit Validation Script

Before writing any ingestion service code, validate the copied toolkit. This script is throwaway — delete after the check passes.

```python
# scripts/test_icr_import.py
import sys
sys.path.insert(0, '.')

from server.services.icr.parser import parse_uploaded_file
from server.services.icr.file_detector import classify_files
from server.services.icr.processor_registry import discover_processors

# Test with any real spreadsheet file
with open('test_data/sample_spreadsheet.xlsx', 'rb') as f:
    content = f.read()

parsed = [parse_uploaded_file('sample_spreadsheet.xlsx', content)]
detected, undetected, uol_data = classify_files(parsed)
print(f'Detected file types: {list(detected.keys())}')

processors = discover_processors()
print(f'Processors found: {[p.id for p in processors]}')
# Expected: tx_summary, user_profile, privacy_coin, counterparty, device,
#           elliptic, fiat, ctm, ftm, blocks  (10 total)
```

### 6.4 `ingestion_service.py`

Responsibilities: case CRUD, section status updates, active case enforcement, ready-state detection, and assembly.

#### Key Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_ingestion_case` | `async (case_id, subject_uid, coconspirator_uids, created_by) → dict` | Creates `ingestion_cases` document. Raises `ValueError` if investigator has active case or `case_id` exists. |
| `get_active_case` | `async (user_id) → dict \| None` | Returns active `ingesting`/`ready` case for user, or None. |
| `get_case` | `async (case_id) → dict` | Returns full case document. Raises `ValueError` if not found. |
| `get_case_status` | `async (case_id) → dict` | Returns lightweight `{case_id, case_status, sections: {key: {status, updated_at}}}` |
| `update_section` | `async (case_id, section_key, status, output=None, error=None, extra_fields=None)` | Atomic section update via `$set`. After each update, calls `_check_ready_state()` to auto-transition case to `ready` if all sections are terminal. |
| `mark_section_none` | `async (case_id, section_key)` | Sets section status to `none`. Triggers ready check. |
| `save_notes` | `async (case_id, notes_text) → dict` | Sets `investigator_notes.output` and status. Empty string resets to `empty`. |
| `assemble_case_data` | `async (case_id) → str` | Validates all non-notes sections are terminal. Assembles ordered markdown. Writes to `assembled_case_data`. Returns markdown string. |

#### Assembly Section Order

The `assemble_case_data` function builds the markdown in this fixed order. Sections marked `none` produce an explicit absence statement rather than being omitted.

| Section Key | Markdown Heading | None Statement |
|-------------|-----------------|----------------|
| `c360` | `## C360 Transaction Summary` | `C360 data not provided.` |
| `elliptic` | `## Elliptic Wallet Screening Results` | `No wallet screening performed.` |
| `hexa_dump` | `## L1 Referral Narrative` | `No L1 referral data provided.` |
| `previous_icrs` | `## Prior ICR Summary` | `No prior ICRs identified for this subject.` |
| `rfis` | `## RFI Summary` | `No RFIs on record for this subject.` |
| `kyc` | `## KYC Document Summary` | `KYC documents not provided.` |
| `l1_victim` | `## L1 Victim Communications Summary` | `No victim communications available.` |
| `l1_suspect` | `## L1 Suspect Communications Summary` | `No suspect communications available.` |
| `kodex` | `## Law Enforcement / Kodex Summary` | `No law enforcement cases identified.` |
| `investigator_notes` | `## Investigator Notes` | `No additional notes.` |

> The assembled document must include all 10 sections in this order, even when some are `none`. The investigation AI must never have to guess whether data is missing or simply not loaded.

### 6.5 `c360_processor.py`

Thin async wrapper around the synchronous toolkit pipeline. The toolkit is CPU-bound synchronous Python and must run in a thread pool to avoid blocking the FastAPI event loop.

```python
import asyncio
from server.services.icr.parser import parse_uploaded_file
from server.services.icr.file_detector import classify_files
from server.services.icr.processor_registry import discover_processors
from server.services.icr.health_check import run_health_check

async def process_c360_files(files_bytes: list, params: dict) -> dict:
    # files_bytes = [(filename, bytes), ...]
    # Read file bytes BEFORE spawning background task — UploadFile objects
    # are closed by the time a background task executes.
    return await asyncio.to_thread(_run_sync_pipeline, files_bytes, params)

def _run_sync_pipeline(files_bytes, params):
    parsed = [parse_uploaded_file(name, content) for name, content in files_bytes]
    detected, undetected, uol_data = classify_files(parsed)
    params = _auto_populate_params(detected, uol_data, params)
    warnings = run_health_check(detected, undetected, uol_data)
    processors = discover_processors()
    context = {'uol_data': uol_data}
    output_parts, wallet_addresses = [], []

    for p in processors:
        if p.should_run(list(detected.keys()), params):
            result = p.process(detected, params, context)
            if result.has_data:
                output_parts.append(f'### {p.label}\n\n{result.content}')
            if p.id == 'elliptic' and result.metadata:
                wallet_addresses = [
                    {'address': a, 'source': info.get('source')}
                    for a, info in result.metadata.get('addresses', {}).items()
                ]

    return {
        'output': '\n\n---\n\n'.join(output_parts),
        'wallet_addresses': wallet_addresses,
        'detected_file_types': list(detected.keys()),
        'undetected_files': undetected,
        'warnings': [{'level': w['level'], 'message': w['message']} for w in warnings]
    }
```

#### Params Auto-Population

All auto-population happens server-side from the uploaded spreadsheets. Any param that cannot be auto-populated is left as an empty string — processors with unmet required fields simply do not run.

| Param Key | Auto-Populated From | Source Column |
|-----------|--------------------|--------------| 
| `devices_used` | `USER_INFO_FIAT_PARTNERS` | `No. of Device Used` |
| `ip_locations` | `USER_INFO_FIAT_PARTNERS` | `IP location Used` |
| `sys_langs` | `USER_INFO_FIAT_PARTNERS` | `System Language used` |
| `it_count` | `CP_SUMMARY` | `Internal CP User Count` |
| `device_link_count` | `DEVICE_LINK_SUMMARY` | `Device Linked User Count` |
| `nationality` | `USER_INFO` | `nationality` |
| `residence` | `USER_INFO` | `residency` |
| `subject_uid` | Case document (always available) | — |
| `account_type` | Not from spreadsheets | Defaults to `"individual"` |

#### Background Task Pattern in Router

> **Critical:** Files must be read in the endpoint handler, not inside the background task. `UploadFile` objects are closed by the time the background task executes. Always pass bytes, never file objects.

```python
@router.post('/cases/{case_id}/c360', status_code=202)
async def upload_c360(
    case_id: str,
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    # Read files HERE — before spawning background task
    files_bytes = [(f.filename, await f.read()) for f in files]
    params = {'subject_uid': case['subject_uid']}
    background_tasks.add_task(_process_c360_background, case_id, files_bytes, params)
    return {'accepted': True, 'files_received': len(files), 'section_status': 'processing'}


async def _process_c360_background(case_id: str, files_bytes: list, params: dict):
    try:
        await ingestion_service.update_section(case_id, 'c360', 'processing')
        result = await c360_processor.process_c360_files(files_bytes, params)
        await ingestion_service.update_section(
            case_id, 'c360', 'complete',
            output=result['output'],
            extra_fields={
                'wallet_addresses': result['wallet_addresses'],
                'detected_file_types': result['detected_file_types'],
                'warnings': result['warnings']
            }
        )
    except Exception as e:
        await ingestion_service.update_section(case_id, 'c360', 'error', error=str(e))
```

### 6.6 `elliptic_processor.py`

Wraps the toolkit's `elliptic_api.py`. The toolkit's `EllipticApiClient` and result formatting are used directly.

```python
import asyncio
from server.services.icr.elliptic_api import EllipticApiClient
from server.config import settings

async def screen_addresses(addresses: list, customer_id: str) -> dict:
    return await asyncio.to_thread(_run_elliptic_sync, addresses, customer_id)

def _run_elliptic_sync(addresses, customer_id):
    client = EllipticApiClient(api_key=settings.ELLIPTIC_API_KEY)
    results = []
    for entry in addresses:
        address = entry if isinstance(entry, str) else entry['address']
        result = client.screen_address(address, customer_id)
        results.append(result)
    output_markdown = client.generate_markdown_report(results)
    return {
        'output': output_markdown,
        'addresses_screened': len(results)
    }
```

> **Note:** Review `elliptic_api.py` before implementing. Confirm: (1) the demo mode flag and how to disable it for real API calls, (2) the expected API key format for the constructor, (3) the exact method names for `screen_address` and `generate_markdown_report` — these names are assumed based on the toolkit audit.

### 6.7 `ingestion_schemas.py`

All Pydantic v2 models for the ingestion API. Follows the same patterns as `server/models/schemas.py`.

```python
from pydantic import BaseModel
from datetime import datetime

class CreateIngestionCaseRequest(BaseModel):
    case_id: str
    subject_uid: str
    coconspirator_uids: list[str] = []

class SectionStatusItem(BaseModel):
    status: str
    updated_at: datetime | None = None

class CaseStatusResponse(BaseModel):
    case_id: str
    case_status: str
    sections: dict[str, SectionStatusItem]

class AddManualAddressesRequest(BaseModel):
    manual_addresses: list[str]

class SubmitEllipticRequest(BaseModel):
    addresses: list[str]
    customer_id: str

class SaveNotesRequest(BaseModel):
    notes: str

class AssembleResponse(BaseModel):
    assembled_case_data: str
    sections_included: list[str]
    sections_none: list[str]
```

### 6.8 `useIngestionStatus` Hook

The polling hook. Components never call the status API directly — they consume this hook. The hook stops polling automatically when all sections reach a terminal state. It exposes `resumePolling` for retry scenarios.

```javascript
// client/src/hooks/useIngestionStatus.js
import { useState, useEffect, useRef, useCallback } from 'react'
import { getIngestionCaseStatus } from '../services/ingestion_api'

const TERMINAL = ['complete', 'error', 'none']
const INTERVAL_MS = 2500

export function useIngestionStatus(caseId, { enabled = true } = {}) {
  const [sections, setSections]     = useState({})
  const [caseStatus, setCaseStatus] = useState(null)
  const [error, setError]           = useState(null)
  const intervalRef = useRef(null)

  const allTerminal = useCallback((data) => {
    if (!data || !Object.keys(data).length) return false
    return Object.entries(data).every(([key, val]) =>
      key === 'investigator_notes' || TERMINAL.includes(val.status)
    )
  }, [])

  const poll = useCallback(async () => {
    if (!caseId) return
    try {
      const data = await getIngestionCaseStatus(caseId)
      setSections(data.sections)
      setCaseStatus(data.case_status)
      setError(null)
      if (allTerminal(data.sections)) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    } catch (err) {
      setError(err.message)
    }
  }, [caseId, allTerminal])

  useEffect(() => {
    if (!enabled || !caseId) return
    poll()
    intervalRef.current = setInterval(poll, INTERVAL_MS)
    return () => clearInterval(intervalRef.current)
  }, [enabled, caseId, poll])

  const resumePolling = useCallback(() => {
    if (intervalRef.current) return
    intervalRef.current = setInterval(poll, INTERVAL_MS)
  }, [poll])

  return { sections, caseStatus, error, resumePolling }
}
```

### 6.9 `IngestionPage` Structure

The page renders in two modes depending on whether the investigator has an active case. On mount it calls `GET /api/ingestion/cases/active` to determine which mode to enter.

#### Mode 1: No Active Case — `CaseCreationForm`

```
CaseCreationForm
  Title: "New Investigation"
  Input: Case Number     (HowDesk reference, e.g. CASE-2026-0451)
  Input: Subject UID     (e.g. BIN-84729103)
  Input: Co-conspirator UIDs  (comma-separated, optional)
  Note:  "Co-conspirator UIDs can be added at any time during ingestion"
  Button: "Create Case"
```

#### Mode 2: Active Case — Full Ingestion Dashboard

```
IngestionHeader
  Case number (prominent, gold)
  Subject UID
  Case status badge  (ingesting / ready)

IngestionSectionGrid  (2 columns ≥1280px, 1 column smaller)
  C360Section
  EllipticSection        (rendered only when sections.c360.status === 'complete')
  NotesSection
  [Locked placeholder cards for all Phase 2–4 sections]

AssembleBar  (sticky bottom, visible when caseStatus === 'ready')
  "All data collected — ready to start investigation"
  Button: "Assemble Case Data →"
```

### 6.10 `IngestionSection` Component

Every section is wrapped by this component. It handles the status indicator, None button, error display, and locked placeholder state. Section content is passed as children.

#### Props

| Prop | Type | Description |
|------|------|-------------|
| `title` | string | Section display name |
| `sectionKey` | string | Matches MongoDB section key |
| `status` | string | From `useIngestionStatus` hook |
| `allowNone` | boolean | `false` for `c360` and `investigator_notes` |
| `locked` | boolean | `true` for Phase 2+ sections |
| `lockedLabel` | string | e.g. `"Available in Phase 2"` |
| `onMarkNone` | function | Called when investigator clicks None |
| `errorMessage` | string \| null | |
| `children` | ReactNode | The section's actual content |

#### Rendering by Status

| Status | What the Section Shows |
|--------|----------------------|
| `empty` | Section content fully interactive. None button visible if `allowNone`. |
| `processing` | Gold spinner. "Processing..." text. Section content greyed out and non-interactive. |
| `complete` | Green dot. Summary line (e.g. "12 files processed, 8 types detected"). "View Output" toggle → collapsible markdown panel. |
| `error` | Red dot. Error message text. "Retry" button re-enables section content for re-upload. |
| `none` | Grey tick. "Marked as not applicable." Undo link restores to `empty`. |
| `locked` | Full card at 40% opacity, no interaction. `lockedLabel` shown in place of status indicator. |

### 6.11 `C360Section` Component

```
C360Section
  Drop zone
    Label:   "Drop all C360 spreadsheets here, or click to browse"
    Accepts: .xlsx, .csv — multiple files
    Drag-over state: gold highlighted border
  File list (appears as files are added)
    Each file: filename + size + remove button
  Button: "Process Files"  (disabled until ≥1 file added)

  [After processing complete]
    "12 files processed"
    Detected types: chip list  (IT, BP, CTM_ALERTS, etc.)
    Warnings: amber text if any health check warnings present
    "{k} wallet addresses extracted for Elliptic review"
    "View Full Output" toggle → collapsible markdown
```

On "Process Files" click: `POST /api/ingestion/cases/{id}/c360` with FormData. Section transitions to `processing`. Polling hook picks up status changes. When status becomes `complete`, fetch full output via `GET /c360` and display summary.

### 6.12 `EllipticSection` Component

The Elliptic section is only rendered when `sections.c360.status === 'complete'`. This is enforced in the parent component.

```
EllipticSection
  Address table
    Columns: ✓ checkbox | Address | Source (ADDR_VALUE / ADDR_EXPOSED / Manual)
    All addresses pre-selected by default
    Investigator can deselect individual addresses
  Manual address input
    Textarea: "Add additional wallet addresses (one per line)"
    Button: "Add Addresses"  → POST /elliptic/addresses, refreshes table
  Button: "Submit to Elliptic"  (disabled if no addresses selected)

  [After screening complete]
    "{n} addresses screened"
    "View Elliptic Report" toggle → collapsible markdown
```

### 6.13 `NotesSection` Component

```
NotesSection
  Label: "Investigator Notes (Optional)"
  Textarea: freeform text, full width, min-height 100px
  Auto-saves on blur with 500ms debounce
  Inline save confirmation: "Saved ✓"  (shown for 2 seconds after save)
  No None button — notes are always optional
```

On blur: `PUT /api/ingestion/cases/{id}/notes`. Status transitions to `complete` on first save, back to `empty` if cleared.

### 6.14 `AssembledOutputModal` Component

Modal opened by the "Assemble Case Data" button in the `AssembleBar`. Calls `POST /api/ingestion/cases/{id}/assemble`, then displays the result.

```
AssembledOutputModal
  Title: "Case Data — CASE-2026-0451"
  Summary: "{X} sections included, {Y} marked None"
  Scrollable markdown output (full height)
  Button: "Copy to Clipboard"
  Button: "Download as .txt"
  Note: "Phase 5: This button will navigate directly to the investigation."
  Close button
```

### 6.15 `ingestion_api.js`

All ingestion API calls. Follows the same pattern as `client/src/services/api.js` — fetch with Bearer token, throw on non-200, return parsed JSON.

```javascript
// client/src/services/ingestion_api.js
const BASE = '/api/ingestion'

export async function createIngestionCase(caseId, subjectUid, coconspiratorUids, token)
export async function getActiveCaseSummary(token)
export async function getIngestionCase(caseId, token)
export async function getIngestionCaseStatus(caseId, token)
export async function uploadC360Files(caseId, files, subjectUid, token)
export async function getC360Output(caseId, token)
export async function getEllipticAddresses(caseId, token)
export async function addManualAddresses(caseId, addresses, token)
export async function submitToElliptic(caseId, addresses, customerId, token)
export async function getEllipticOutput(caseId, token)
export async function markSectionNone(caseId, sectionKey, token)
export async function saveNotes(caseId, notes, token)
export async function assembleCaseData(caseId, token)
```

### 6.16 Phase 1 Definition of Done

All of the following must be true before Phase 1 is considered complete and Phase 2 development begins.

- [ ] Investigator can create a new case with a case number and subject UID
- [ ] Investigator cannot create a second case while one is active (409 returned, frontend shows existing case)
- [ ] Page reload resumes the active case — no lost state, no re-upload required
- [ ] Investigator can upload 1 to 20+ C360 spreadsheet files at once via drag-drop or file picker
- [ ] All 10 processors run and produce output matching the quality of the existing standalone toolkit
- [ ] Auto-population of params from spreadsheet data works correctly (`devices_used`, `ip_locations`, `sys_langs`, `it_count`, `nationality`, `residence` where spreadsheets provide them)
- [ ] Health check warnings are surfaced in the C360 section summary
- [ ] Wallet addresses are extracted from C360 output and displayed in the Elliptic section with correct source labels
- [ ] Investigator can add manual wallet addresses to the Elliptic list
- [ ] Investigator can submit selected addresses to Elliptic and view screening results
- [ ] Investigator can mark Elliptic as None
- [ ] Investigator Notes can be saved and are included in the assembled output
- [ ] Assemble is disabled until C360 and Elliptic are both terminal (complete or none)
- [ ] Assembling produces correct markdown matching the assembly order in Section 6.4
- [ ] Assembled markdown is displayed in the modal and copyable to clipboard
- [ ] All Phase 2–4 sections are visible in the UI as locked placeholder cards
- [ ] The existing investigation view, case list, free chat, and all other platform features are fully unaffected

---

## 7. Phase 2 — AI Text Modules

> Full specification to be written as an addendum before Phase 2 development begins.

Phase 2 adds AI-powered text processing modules: Hexa dump restructuring, previous ICR extraction (one entry at a time, multiple entries supported), RFI extraction (same pattern as ICRs), and KYC document image extraction.

### New Service: `IngestionAIClient`

A dedicated service at `server/services/ingestion/ingestion_ai_client.py`. Separate from the investigation platform's `ai_client.py`. Handles standalone preprocessing API calls with no conversation state and no tool use. Pattern: prompt + input → markdown output.

### New Knowledge Base Directory

```
knowledge_base/preprocessing/
  kyc-extraction.md          Extract all personal details from KYC document images
  hexa-restructure.md        Restructure raw Hexa dump text into clean organised markdown
  icr-extraction.md          Extract key findings and decisions from a single prior ICR
  rfi-extraction.md          Extract the request, response, commitments and timeline from a single RFI
```

These prompts are loaded on startup by the ingestion service. They are entirely separate from the investigation prompts in the main system prompt.

> All Phase 2 preprocessing calls are standalone — no conversation history, no knowledge base, no tool use. Input in, markdown out.

---

## 8. Phase 3 — Communications Modules

> Full specification to be written as an addendum before Phase 3 development begins.

Phase 3 adds L1 Victim and L1 Suspect communications. Both sections accept a text paste area (chat transcript) and an image upload area (screenshots) as independent inputs within the same section.

### Key Additions Beyond Phase 2 Pattern

- Image upload alongside text input (reusing the existing `ImageUpload` component from the platform)
- Automatic filtering of images under 20KB (avatar icons, UI elements — not evidence)
- Batching logic: if image volume exceeds a single API call, the backend splits into multiple calls and merges outputs
- Translation: the extraction prompt instructs the AI to translate all non-English content to English inline
- Video flag: the prompt notes any references to video files that require manual investigator review

### Preprocessing Prompts Required

```
knowledge_base/preprocessing/
  l1-victim-comms.md         Translate, narrate, and describe images from victim communications
  l1-suspect-comms.md        Translate, narrate, and describe images from suspect communications
```

---

## 9. Phase 4 — Kodex PDF Pipeline

> Full specification to be written as an addendum before Phase 4 development begins.

Phase 4 implements the multi-stage Kodex PDF processing pipeline as designed in `DOCUMENT_PIPELINE_SPEC.md`.

### Processing Stages

1. **Stage 1 — Individual PDF processing (parallel).** One API call per PDF, using the Kodex extraction prompt. Each call produces an individual summary (~500 words). All Stage 1 calls run concurrently via `asyncio.gather`.

2. **Stage 2 — Consolidation.** One API call merging all individual summaries into a single final LE summary. The consolidation prompt emphasises deduplication, chronological ordering, key entities, and relevance to the specific case (using subject UID and co-conspirator UIDs).

3. **Page chunking (if required).** PDFs exceeding context limits are split across multiple Stage 1 calls. Outputs are merged before Stage 2.

### Subject UID Provision

The subject UID and co-conspirator UIDs (from the case document) are provided to both Stage 1 and Stage 2 prompts so the AI can determine whether the subject is named directly in each LE case.

### Preprocessing Prompt Required

```
knowledge_base/preprocessing/
  kodex-pdf-extraction.md    Extract key findings from a single Kodex law enforcement PDF
```

---

## 10. Phase 5 — Integration and Handoff

> Full specification to be written as an addendum before Phase 5 development begins.

Phase 5 connects the ingestion dashboard to the investigation platform.

### Changes in Phase 5

- The `POST /api/ingestion/cases/{id}/assemble` endpoint is extended. After assembling the markdown, it writes a new document to the `cases` collection (see Section 4.6 for field mapping), updates the ingestion case status to `investigating`, and returns the `case_id` and a navigation URL.

- The `AssembledOutputModal` is replaced by a navigation action: clicking "Start Investigation" navigates the browser to `/investigation/{case_id}` where the existing investigation view loads exactly as it does today with pre-staged data.

- The ingestion page becomes the default landing page after login. The current case list becomes a secondary view accessible from the nav. Investigators with no active case see the case creation form. Investigators with an active case resume it automatically.

---

## 11. Open Questions

| Question | Impact | Resolve By |
|----------|--------|-----------|
| Does `health_check.py` have any hidden dependency on `session_store`? | Build order — must confirm before Step 1 | Toolkit copy validation (build Step 2) |
| Is `openpyxl` already in `requirements.txt`? | Minor — one line addition if not | Check before install step |
| Does `elliptic_api.py` have a demo mode flag? How is it disabled for real API calls? | Phase 1 Elliptic testing | Review `elliptic_api.py` before writing `elliptic_processor.py` |
| Should `field_discovery.py` SQLite logging be included in the copied `services/icr/`? | No functional impact on output | Decision at build time (Step 1) |
| What is the Elliptic API key format expected by `elliptic_api.py`? | Config setup | Review `elliptic_api.py` constructor |
| Maximum number of C360 files a real case produces? | File list UI rendering and upload payload size | Ask team; toolkit already handles this so no code risk |
| Should co-conspirator UIDs auto-feed into the UID search? | Phase 1 UX detail — UID search uses the same UIDs as Elliptic but is a separate feature | Decide before building `EllipticSection` |
| Does the Vite dev server proxy handle `multipart/form-data` uploads to `:8000` correctly? | C360 upload endpoint | Test early in Phase 1 — known to work for JSON, worth confirming for multipart |
