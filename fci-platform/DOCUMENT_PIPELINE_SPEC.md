# Document Processing Pipeline — Architecture Spec

## Problem Statement

The current system sends all data (including images) directly into the main chat conversation context. This is inefficient:

- Images consume 1,000-5,000+ tokens each and must be resent on every subsequent API turn
- The prompt library (`knowledge_base/core/prompt-library.md`) is ~60KB and contains data extraction/processing prompts that are only needed during ingestion, not during interactive investigation
- Law enforcement cases can produce multiple PDFs, each up to 20 pages — far too large to inject raw into chat context
- As investigators upload more documents during a session, the main context balloons

## Proposed Architecture

### Separation of Concerns

Split the AI workload into two distinct pipelines:

```
                                  +---------------------------+
                                  |   PROCESSING PIPELINE     |
   Documents/Images/PDFs -------->|   (Separate API calls)    |
                                  |   Uses extraction prompts |
                                  |   Returns structured text |
                                  +------------+--------------+
                                               |
                                     condensed text summaries
                                               |
                                               v
                                  +---------------------------+
   Investigator messages -------->|   MAIN CHAT CONTEXT       |
                                  |   (Interactive API calls)  |
                                  |   Uses investigation       |
                                  |   prompts only             |
                                  +---------------------------+
```

### Pipeline 1: Document Processing (New)

Standalone API calls that process raw data and return condensed text. Each call uses a **task-specific extraction prompt** from the prompt library.

**Input types:**
- Screenshots/images (KYC docs, admin panels, Elliptic screenshots, C360 exports)
- PDFs (law enforcement documents, RFIs, court orders)
- Pasted raw data (spreadsheet data, alert tables, transaction lists)

**Output:** Structured text summary that gets injected into the main conversation as a `document_extraction` message.

### Pipeline 2: Main Chat (Existing, lightened)

Interactive conversation with the investigator. Receives only:
- Case preprocessed data (as now)
- Condensed document summaries (from Pipeline 1)
- Investigator messages (text only — no raw images/PDFs)
- Core knowledge base (minus extraction prompts)

---

## Prompt Library Split

The current `prompt-library.md` contains two categories that should be separated:

### Extraction Prompts (move to Pipeline 1)
These are standalone data processing prompts — they take raw input and produce a formatted summary. They do NOT need the investigation context.

| # | Prompt | Purpose | Pipeline Use |
|---|--------|---------|--------------|
| 1 | Transaction Analysis / Pass-Through | Summarize C360 transaction data | Process pasted C360 export |
| 2 | CTM Alerts Enhanced | Summarize crypto alert spreadsheet | Process CTM alert data |
| 3 | Account Blocks | Summarize block/unblock history | Process C360 status data |
| 4 | Prior ICR Analysis | Summarize prior investigations | Process Hexa template data |
| 5 | Scam Analysis (P2P) | Summarize HaoDesk L1 referral | Process L1 referral data |
| 6 | CTM Alerts (Standard) | Summarize CTM alert details | Process C360 CTM data |
| 7 | Privacy Coin Analysis | Summarize privacy coin activity | Process transaction data |
| 8 | Failed Fiat Transactions | Summarize failed deposits | Process C360 fiat data |
| 9 | Device and IP Analysis | Summarize device/IP data | Process C360 device data |
| 10 | RFI Summary | Summarize RFI responses | Process LE documents |
| 9E | Device & IP — Data Extraction | Extract structured data from screenshots | Process admin screenshots |
| 14E | Elliptic Top Addresses — Extraction | Extract data from Elliptic screenshots | Process Elliptic screenshots |
| 15E | Law Enforcement / Kodex — Extraction | Extract data from LE/Kodex documents | Process LE PDFs |
| 16E | RCM / Case Intake — Extraction | Extract data from case intake forms | Process intake screenshots |

### Investigation Prompts (keep in Pipeline 2 / main chat)
These require the full investigation context and interactive conversation.

| # | Prompt | Purpose |
|---|--------|---------|
| 11 | Summary of Investigation and Activity | Draft the final investigation narrative |
| 12 | Internal Counterparty Analysis | Analyse counterparty patterns |
| 13 | KYB Summary (Corporate Accounts) | Analyse corporate entity data |

**Context savings:** Removing ~14 extraction prompts from the main chat system prompt could save 40,000+ tokens per conversation turn.

---

## PDF Processing Flow (Law Enforcement Cases)

LE cases are the most complex — multiple PDFs, each up to 20 pages. Direct ingestion is impossible.

### Multi-stage summarisation:

```
Stage 1: Individual PDF Processing (parallel)
  PDF 1 (20 pages) ---> API call with LE extraction prompt ---> Summary 1 (~500 words)
  PDF 2 (15 pages) ---> API call with LE extraction prompt ---> Summary 2 (~500 words)
  PDF 3 (8 pages)  ---> API call with LE extraction prompt ---> Summary 3 (~500 words)

Stage 2: Consolidation
  [Summary 1 + Summary 2 + Summary 3] ---> API call ---> Final LE Summary (~800 words)

Stage 3: Injection
  Final LE Summary ---> added to main chat context as document_extraction message
```

### Implementation considerations:
- Stage 1 calls can run in **parallel** (independent documents)
- Each Stage 1 call may need to process the PDF in **page chunks** if the PDF exceeds context limits (send pages 1-10, then 11-20, then combine)
- Stage 2 prompt should emphasise: deduplication, chronological ordering, key dates/entities, and relevance to the specific case
- The final summary is what the investigator and main chat AI both see
- Individual PDF summaries should be stored in MongoDB for audit trail / drill-down

---

## Backend Architecture

### New endpoint
```
POST /api/conversations/{id}/process-document
Content-Type: multipart/form-data

Fields:
  - file: The document (image, PDF)
  - document_type: "kyc" | "admin_screenshot" | "elliptic" | "le_document" | "c360_export" | "general"
  - description: Optional user description
```

### New service: `document_processor.py`
```python
class DocumentProcessor:
    """
    Processes documents through extraction prompts outside the main chat context.

    Methods:
        process_image(image_b64, media_type, document_type) -> str
        process_pdf(pdf_bytes, document_type) -> str
        process_pdf_multi(pdf_list) -> str  # multi-stage LE flow
        process_raw_data(text, document_type) -> str

    Each method:
        1. Selects the appropriate extraction prompt
        2. Makes standalone API call(s)
        3. Returns condensed text summary
    """
```

### New knowledge base directory
```
knowledge_base/
  core/                    # Main chat system prompt + investigation guidance
    prompt-library.md      # SLIMMED — only investigation prompts (11, 12, 13)
  extraction/              # NEW — extraction prompts for Pipeline 1
    transaction-analysis.md
    ctm-alerts.md
    account-blocks.md
    ...etc
  reference/               # Unchanged — tool-callable reference docs
```

---

## Frontend Architecture

### Left panel: new "Documents" tab
- Sits alongside the existing data tabs (C360, Elliptic, KYC, etc.)
- Drag-and-drop zone for files
- Shows processing status (uploading → processing → done)
- Lists processed documents with their summaries
- Click to expand and see the full extracted text

### Chat panel changes
- Remove image upload from chat input (or keep as secondary option)
- When a document is processed, show a system message in chat: "Document processed: [type] — [brief description]"
- The AI automatically has access to the extracted summary in subsequent turns

---

## Priority for Implementation

This is NOT for the current demo sprint. The current demo uses direct image passing in chat context, which is functional.

### Phase 1 (Current — Demo)
- Images sent directly in chat context (**done**)
- All prompts in main system prompt (**done**)

### Phase 2 (Post-Demo)
- Build `document_processor.py` service
- Split prompt library into extraction vs investigation
- Add `/process-document` endpoint
- Add Documents tab to left panel
- Single-image and single-PDF processing

### Phase 3 (Full Pipeline)
- Multi-PDF LE processing flow (parallel + consolidation)
- Raw data paste processing (spreadsheets, alert tables)
- Automatic prompt selection based on document type detection
- Processing queue with status tracking
- Audit trail in MongoDB
