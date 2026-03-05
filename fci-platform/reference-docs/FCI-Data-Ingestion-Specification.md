# FCI Investigation Platform — Data Ingestion Specification

**Date:** 5 March 2026
**Status:** Planning / Pre-Development
**Purpose:** Define the data ingestion portal that replaces manual data collection. This document covers every data source, the upload interface for each, the backend processing pipeline, and the output format that feeds into the case data template for the investigation AI.

---

## 1. Overview

In Phase 2, the platform's landing page after login is the data ingestion portal, replacing the current case list of pre-staged demo cases. The investigator arrives here at the start of every new case and works through the data collection process before starting the AI-assisted investigation.

The ingestion portal accepts data from all case sources, processes each one independently, and assembles a structured case data template in the backend. When the investigator is satisfied that all available data has been ingested, they click "Start Investigation" and proceed to the investigation view with all data preprocessed and ready.

### 1.1 Design Principles

- **Separate upload zone per data type.** No dropdown selectors. Each data source has its own clearly labelled section. The investigator never has to tell the system what type of data they're uploading.
- **Process independently on submission.** Each upload triggers its own processing pipeline immediately. No waiting for everything to be collected before processing starts. Earlier uploads are often done by the time the last one is submitted.
- **Explicit "None" confirmation.** Every data source section must either have data uploaded or be explicitly marked as "None / Not Applicable" by the investigator. Empty sections are not allowed. This ensures the case data template explicitly states when a data source was not present, rather than leaving ambiguity.
- **One at a time for multi-entry sources.** Previous ICRs, RFIs, and similar sources where there may be multiple entries are uploaded individually. "Add another" button for multiples. The backend keeps them as distinct items. No concatenation of multiple cases or documents into a single paste.
- **Idiot-proof.** Clear labels, clear status indicators (empty, processing, complete, error), clear instructions. Investigators are under pressure and moving fast. The UI should never create doubt about what to do next.

### 1.2 Session Management

**One case at a time.** The investigator works a single case from ingestion through to export. No starting a second case while one is active. When the case is exported and marked complete, the investigator can start the next one.

**Case number is the session anchor.** The first thing the investigator enters is the HauDesk case number. This is the primary key for everything: all ingested data, all processed outputs, all conversation history, and the final export all belong to this case number. The case number is displayed prominently throughout the ingestion and investigation views so there is never ambiguity about which case is active.

**UID is a child of the case, not the session key.** After entering the case number, the investigator enters the subject UID (the user being investigated). In Phase 2, this is a single UID per case. The schema is designed so that a case can have multiple UIDs attached to it, but the multi-user ingestion workflow is deferred (see Section 9).

There is also a section to enter **co-conspirator or other suspect UIDs**. These are not full investigation subjects but are needed for:
- Kodex law enforcement processing (determining whether the subject is named directly).
- C360/UOL analysis (searching for transactions between the subject and known suspects).
- Cross-referencing across data sources.

The subject UID field is mandatory. Co-conspirator UIDs are optional and can be added at any point during ingestion.

---

## 2. Data Sources and Upload Zones

### 2.1 KYC Documents (Binance Admin)

**What the investigator does:** Screenshots the KYC document pages from Binance Admin and uploads the images.

**Upload zone:** Image upload area accepting multiple screenshots (paste, drag-drop, or file picker).

**Backend processing:**
- Sonnet API call with a dedicated prompt to extract every detail from the KYC document images.
- Output: structured markdown with all personal details, document type, document number, issuing country, dates, photo description, and any anomalies noted.

**Output in case template:** "KYC Document Summary" section.

**Notes:**
- Original images are not retained in the case data. The structured extraction is sufficient. The investigator can always return to Binance Admin for the originals.
- Processing is a single API call (or batched if many images).

---

### 2.2 C360 Spreadsheets

**What the investigator does:** Downloads spreadsheets from C360 (counterparty data, CTM alerts, failed fiat, block history, operations log, etc.) and uploads them all.

**Upload zone:** File upload area accepting .xlsx and .csv files. Multiple files at once.

**Additional input:** URL field for the UOL (User Operations Log). If not provided, a prominent message says: "UOL not provided. Full counterparty cross-referencing will not be available. Generate the UOL in C360 for a complete analysis."

**Backend processing:**
- The existing C360 Python processing pipeline, integrated into the platform backend.
- Produces: counterparty risk flags, device analysis, CTM alert summaries, failed fiat analysis, block history with parsed offboarding reasons, cross-referencing of flagged wallets against the operations log.
- Wallet addresses are extracted during processing and held for the Elliptic screening step.

**Output in case template:** "C360 Transaction Summary" section (and potentially multiple subsections depending on what data was available).

---

### 2.3 Elliptic Wallet Screening

**What the investigator does:** After C360 processing, the extracted wallet addresses are displayed. The investigator can:
- Review the list of wallets identified by the C360 pipeline.
- Add additional wallet addresses manually (e.g. addresses found in L1 chat narratives or other sources).
- Select which wallets to submit for screening.
- Click "Submit to Elliptic" (or this happens automatically as part of the C360 processing submission).

**Upload zone:** Not a traditional upload. This is a review and submit interface that appears after C360 processing completes. It shows the wallet list with checkboxes, a text input for adding extra addresses, and a submit button.

**Backend processing:**
- Elliptic API calls for each selected wallet. Code already exists from the current workflow.
- Results returned and formatted into structured markdown.

**Output in case template:** "Elliptic Wallet Screening Results" section.

**Notes:**
- If C360 hasn't been processed yet (no wallets extracted), this section shows as pending.
- Manual wallet entry is always available even without C360 data.

---

### 2.4 Hexa Dump / L1 Referral Text

**What the investigator does:** Copies the full Hexa dump from the case (the raw L1 referral data including case notes, the level one narrative, and system-generated fields) and pastes it in.

**Upload zone:** Large text paste area. Single submission.

**Backend processing:**
- Sonnet API call to restructure the raw text dump into clean, organised markdown.
- The raw Hexa dump is typically a mess of form fields, system metadata, and narrative text mixed together. The AI separates these into logical sections, strips noise, and produces a readable summary.
- This also reduces token usage for the investigation phase because clean markdown is far more token-efficient than a raw text dump.

**Output in case template:** "L1 Referral Narrative" section.

---

### 2.5 Previous ICRs

**What the investigator does:** For each prior ICR related to the subject, copies the full text and pastes it into the upload zone. Clicks "Add Another" for each additional ICR. Clicks "Submit" when all have been entered. If there are no prior ICRs, clicks "None."

**Upload zone:** Text paste area with "Add Another" and "Submit" buttons. Each entry is labelled (ICR 1, ICR 2, etc.).

**Backend processing:**
- Each ICR is processed as a separate Sonnet API call to extract key findings, decisions, and relevant context.
- The backend keeps them as distinct items, labelled and separated.
- A combined summary may be generated after all individual ICRs are processed, noting common themes or escalating patterns.

**Output in case template:** "Prior ICR Summary" section with clearly separated subsections per ICR.

**Notes:**
- Individual upload is critical. Concatenating multiple ICRs into one paste makes it difficult for the AI to determine which text belongs to which case.
- The "None" button injects an explicit statement into the case template: "No prior ICRs identified for this subject."

---

### 2.6 RFIs (Requests for Information)

**What the investigator does:** Same pattern as ICRs. Paste one RFI at a time. "Add Another" for multiples. "Submit" when done. "None" if no RFIs exist.

**Upload zone:** Text paste area with "Add Another" and "Submit" buttons.

**Backend processing:**
- Each RFI processed independently via Sonnet.
- Extracts the request, the response, any commitments made, and relevant timeline.

**Output in case template:** "RFI Summary" section with clearly separated subsections per RFI.

**Notes:**
- Same separation logic as ICRs. One at a time, never concatenated.
- "None" injects: "No RFIs on record for this subject."

---

### 2.7 Kodex Law Enforcement Cases

**What the investigator does:** Downloads PDF exports from Kodex for any law enforcement cases involving the subject. Uploads them one at a time or as a batch.

**Upload zone:** PDF file upload area. Multiple files accepted. "None" button if no LE cases exist.

**Backend processing:**
- PDF extraction pipeline (to be built). Iterative approach for inconsistent Kodex PDF formats.
- The subject UID (entered at the top of the page) is provided to the extraction prompt so the AI can determine whether the subject is named directly in the LE case.
- Co-conspirator UIDs are also provided for cross-referencing.
- Each PDF processed separately.

**Output in case template:** "Law Enforcement / Kodex Summary" section.

**Notes:**
- Kodex has no API. PDFs are the only export option. This will remain a manual upload for the foreseeable future.
- "None" injects: "No law enforcement cases identified in Kodex for this subject."

---

### 2.8 L1 Communications — Victim

**What the investigator does:** Copies the chat history from HauDesk for the victim's communications and pastes the text. Separately uploads relevant images (screenshots sent by the victim within the chat or in the L1 case file).

**Upload zone:** Two areas within this section:
1. **Text paste area** for the chat transcript. When copied from HauDesk, images are stripped but placeholder text remains (e.g. "image uploaded by user, 69KB").
2. **Image upload area** for screenshots extracted from the chat or the L1 case file. The investigator pastes or drops the relevant images here.

**Backend processing:**
- Images below ~20KB are automatically stripped (these are avatar icons and UI elements, not evidence).
- Sonnet API call with dedicated prompt:
  - Translate all foreign language content to English.
  - Build a chronological narrative of the victim's account of events.
  - Describe what each image shows and flag which ones are evidentially important.
  - Note any financial amounts, transaction references, wallet addresses, or platform names mentioned.
  - Flag any references to video files that require manual review by the investigator.
- If the volume of images is too large for a single API call, the backend batches them automatically (e.g. text + first 10 images in call 1, remaining images in call 2, merge outputs).

**Output in case template:** "L1 Victim Communications Summary" section.

**Notes:**
- Videos embedded in the chat cannot be processed. The output template includes a standard note: "Check with the investigator: are there any video files from the victim? Video content must be reviewed manually."
- The L1 case file (customer service portal) may contain additional victim submissions and screenshots beyond the chat. These go in the same upload zone.

---

### 2.9 L1 Communications — Suspect

**What the investigator does:** Same as victim communications, but for the suspect's chat history if one exists.

**Upload zone:** Same layout as victim: text paste area + image upload area.

**Backend processing:** Same pipeline as victim communications, with the prompt adjusted to focus on the suspect's account and behaviour.

**Output in case template:** "L1 Suspect Communications Summary" section.

**Notes:**
- Not all cases have suspect communications. "None" button if not applicable.
- "None" injects: "No suspect communications available for this case."

---

### 2.10 Investigator Notes (Optional)

**What the investigator does:** Adds any additional context, observations, or notes they want the investigation AI to be aware of. This is freeform text.

**Upload zone:** Text area. Optional. No processing.

**Output in case template:** "Investigator Notes" section (passed through as-is, no AI processing).

---

## 3. Ingestion Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  FCI Investigation Platform              Data Ingestion      Ben ⏻  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Case Number: [ CASE-2026-0451  ]                                  │
│  Subject UID: [ BIN-84729103    ]                                  │
│  Co-conspirator UIDs: [ Add UID... ] [UID-1] [UID-2]              │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ KYC Documents                               ○ Empty         │   │
│  │ Upload screenshots from Binance Admin       [Upload] [None] │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ C360 Spreadsheets                           ● Complete      │   │
│  │ Upload .xlsx/.csv files from C360           [3 files]       │   │
│  │ UOL URL: [https://...]                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Elliptic Screening                          ◐ Processing    │   │
│  │ 5 wallets identified, 2 manually added                      │   │
│  │ [Submit to Elliptic]                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Hexa Dump / L1 Referral                     ○ Empty         │   │
│  │ Paste the full Hexa dump text               [Paste] [None]  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Previous ICRs                               ● 2 uploaded    │   │
│  │ [ICR 1 ✓] [ICR 2 ✓] [Add Another] [Submit]                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ RFIs                                        ✓ None          │   │
│  │ No RFIs on record                                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Kodex Law Enforcement                       ○ Empty         │   │
│  │ Upload PDFs from Kodex                      [Upload] [None] │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ L1 Victim Communications                    ● Complete      │   │
│  │ Chat text: ✓  Images: 4 uploaded                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ L1 Suspect Communications                   ✓ None          │   │
│  │ No suspect communications available                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Investigator Notes (Optional)                               │   │
│  │ [Text area...]                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│                    [ Start Investigation → ]                        │
│                                                                     │
│  "Start Investigation" is disabled until all sections are either    │
│  completed or marked as "None".                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Processing Architecture

### 4.1 Per-Source Processing

Each data source has its own processing pipeline. They run independently and can execute in parallel where the investigator has uploaded multiple sources.

| Source | Processing Method | Model | Approximate Tokens |
|--------|------------------|-------|-------------------|
| KYC Documents | AI image extraction | Sonnet | Low (few images) |
| C360 Spreadsheets | Python pipeline (existing code) | None (deterministic) | N/A |
| Elliptic | API call (existing code) | None (API response) | N/A |
| Hexa Dump | AI text restructuring | Sonnet | Medium |
| Previous ICRs | AI extraction per ICR | Sonnet | Medium per ICR |
| RFIs | AI extraction per RFI | Sonnet | Medium per RFI |
| Kodex PDFs | PDF extraction pipeline | Sonnet | Medium-High per PDF |
| L1 Victim Comms | AI translation + summary | Sonnet | High (text + images) |
| L1 Suspect Comms | AI translation + summary | Sonnet | High (text + images) |
| Investigator Notes | Pass-through | None | N/A |

### 4.2 Output Assembly

Each pipeline produces a markdown section. These are stored individually in the case record in MongoDB (similar to the current `preprocessed_data` field structure) and assembled into the full case data template when the investigation begins.

The case data template is the structured markdown document injected into the AI conversation at the start of the investigation. It includes every section in order, with explicit "None" statements for any source that was marked as not applicable.

### 4.3 Processing Prompts

Each AI-powered pipeline needs a dedicated processing prompt. These prompts are separate from the investigation prompts in the prompt library. They are preprocessing prompts focused on extraction and structuring, not investigation analysis.

These prompts should be stored alongside the knowledge base, possibly in a `/knowledge_base/preprocessing/` directory:

```
/knowledge_base/preprocessing/
├── kyc-extraction-prompt.md
├── hexa-restructure-prompt.md
├── icr-extraction-prompt.md
├── rfi-extraction-prompt.md
├── kodex-pdf-extraction-prompt.md
├── l1-victim-comms-prompt.md
└── l1-suspect-comms-prompt.md
```

---

## 5. Status Tracking and "Start Investigation" Gate

### 5.1 Section States

Every ingestion section has one of these states:

| State | Meaning | Visual |
|-------|---------|--------|
| Empty | No data uploaded and not marked as None | Grey circle ○ |
| Processing | Data uploaded, backend processing in progress | Half circle ◐ or spinner |
| Complete | Processing finished successfully | Green filled circle ● |
| None | Investigator confirmed this source is not applicable | Checkmark ✓ None |
| Error | Processing failed | Red circle with message |

### 5.2 Start Investigation Gate

The "Start Investigation" button is disabled until every section is either Complete or None. No empty sections are allowed.

This ensures:
- The case data template is complete before the investigation starts.
- The AI knows definitively which data sources were available and which were not.
- There is no ambiguity about missing data.

---

## 6. Case Data Template (Assembled Output)

When the investigator clicks "Start Investigation," the backend assembles the full case data template from all processed sections. This template is the markdown document injected into the investigation conversation as the hidden case data message.

The template follows a standard structure regardless of case type:

```markdown
# Case Data: [Case Number]

## Subject Information
- **Case Number:** CASE-2026-0451
- **Subject UID:** BIN-84729103
- **Co-conspirator UIDs:** [list or "None identified"]

## KYC Document Summary
[Extracted KYC data or "KYC documents not provided"]

## L1 Referral Narrative
[Restructured Hexa dump or "No L1 referral data provided"]

## C360 Transaction Summary
[C360 pipeline output or "C360 data not provided"]

## Elliptic Wallet Screening Results
[Elliptic results or "No wallet screening performed"]

## Prior ICR Summary
[Individual ICR summaries or "No prior ICRs identified for this subject"]

## RFI Summary
[Individual RFI summaries or "No RFIs on record for this subject"]

## Law Enforcement / Kodex Summary
[Kodex extraction results or "No law enforcement cases identified in Kodex for this subject"]

## L1 Victim Communications Summary
[Translation, narrative, image descriptions, video flags or "No victim communications available"]

## L1 Suspect Communications Summary
[Translation, narrative, image descriptions, video flags or "No suspect communications available"]

## Investigator Notes
[Freeform notes or "No additional notes"]
```

This is what the investigation AI sees when the case begins. Every section is present, every absence is explicitly stated. The AI never has to guess whether data is missing or just hasn't been loaded.

---

## 7. Integration with Block Architecture

The case data template (Section 6) is reinjected fresh at the start of each investigation block, as described in the Blocked Investigation Architecture document. The full template goes in every time. It does not change between blocks. The block summaries are appended alongside it, not merged into it.

The data ingestion system is built and tested standalone before being connected to the investigation platform (see Section 10).

---

## 8. Case Lifecycle and Audit Trail

### 8.1 Case States

| Status | Meaning |
|--------|---------|
| ingesting | Case number entered, data being collected and processed |
| ready | All sections complete or marked None, waiting to start investigation |
| investigating | Active investigation in progress (blocked architecture) |
| completed | Investigation finished, transcript exported |
| archived | Retained for audit, hidden from active UI |

### 8.2 One Case at a Time

The backend enforces single active case per investigator. If an investigator attempts to create a new case while one is in `ingesting`, `ready`, or `investigating` state, the backend rejects it. The frontend hides the option, but the backend is the real guard.

To start a new case, the current case must be in `completed` or `archived` state.

### 8.3 Audit Trail

All case data is retained permanently. If an investigator deletes a conversation from their UI, it is soft-deleted: flagged as hidden in their view but the underlying data stays in MongoDB.

The full audit record for every case includes:
- The case number and all associated UIDs.
- All raw ingested data (or references to uploaded files).
- All processed markdown outputs from each pipeline.
- Every block transcript, including hidden system messages and tool exchanges.
- Every block summary generated by Opus.
- Every image uploaded during ingestion or investigation.
- The final exported transcript.
- Timestamps and investigator ID on every action.

### 8.4 Database Schema

The case record uses the case number as its primary key. UIDs are children of the case.

```json
{
  "_id": "CASE-2026-0451",
  "status": "investigating",
  "created_by": "user_001",
  "subject_uids": ["BIN-84729103"],
  "coconspirator_uids": ["BIN-22341098"],
  "ingestion": {
    "kyc": { "status": "complete", "output": "## KYC Document Summary\n..." },
    "c360": { "status": "complete", "output": "## C360 Transaction Summary\n..." },
    "elliptic": { "status": "complete", "output": "## Elliptic Results\n..." },
    "hexa_dump": { "status": "none", "output": "No L1 referral data provided" },
    "previous_icrs": { "status": "complete", "count": 2, "output": "## Prior ICR Summary\n..." },
    "rfis": { "status": "none", "output": "No RFIs on record for this subject" },
    "kodex": { "status": "complete", "output": "## Law Enforcement Summary\n..." },
    "l1_victim": { "status": "complete", "output": "## L1 Victim Communications\n..." },
    "l1_suspect": { "status": "none", "output": "No suspect communications available" },
    "investigator_notes": { "status": "empty", "output": "" }
  },
  "assembled_case_data": "# Case Data: CASE-2026-0451\n\n## Subject Information\n...",
  "conversation_id": "conv_abc123",
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-05T11:30:00Z",
  "completed_at": null,
  "archived_at": null
}
```

Note that `subject_uids` is an array even though Phase 2 only supports a single entry. This means multi-user support can be added later without changing the schema structure.

---

## 9. Multi-User Cases (Deferred — Phase 3+)

Some cases involve multiple users (e.g. four subjects in a coordinated fraud ring). The current architecture is designed to support this in the future without structural changes.

**What's already in place:**
- Case number is the session anchor, not UID. A case can have multiple UIDs.
- `subject_uids` is an array in the database schema.
- The case data template is assembled per case, not per UID.

**What would need to be built:**
- A "Multi-user" toggle on the ingestion page. The investigator selects how many subjects.
- The ingestion pipeline repeats for each UID: separate KYC, C360, Elliptic, and communications per user.
- The case data template extends with per-user sections: "User 1: BIN-84729103" with their complete dataset, "User 2: BIN-22341098" with theirs, and so on.
- A cross-user analysis section at the end: shared counterparties, transactions between subjects, shared devices/IPs. The C360 pipeline may surface some of this automatically if all users' data is processed together.
- Context window implications need to be evaluated. Four users' worth of case data could be 40-60K tokens. Combined with the system prompt and block documents, this may push towards the context limit even with the block architecture. May require additional summarisation or a tiered approach where the AI focuses on one user at a time within each block.

**Not built in Phase 2.** Single-user workflow only. Multi-user is additive: the schema supports it, the ingestion pipeline repeats, the template extends. No structural rewrites required.

---

## 10. Integration with Investigation Platform

The data ingestion system should be built and tested as a standalone system initially. The input is raw data from the investigator. The output is a complete case data markdown document.

This can be validated independently by taking the output markdown and pasting it into the existing platform as pre-staged case data, then running an investigation to check the quality. That's the integration test before any actual integration code is written.

When the ingestion system is producing reliable, well-structured output, connecting it to the platform is straightforward. The assembled case data markdown is the same format the conversation manager already expects in the `preprocessed_data` field. The integration replaces "loaded from MongoDB seed data" with "generated by the ingestion pipeline."

---

## 11. Open Questions

- **Image batching thresholds.** At what point does the L1 communications pipeline need to split images across multiple API calls? Need to test with real case data to establish practical limits.
- **Kodex PDF extraction reliability.** Kodex PDF formats vary. The extraction pipeline will need iterative refinement. How much can we rely on consistent formatting vs needing robust error handling?
- **C360 pipeline integration effort.** The existing Python web app processes spreadsheets. How much refactoring is needed to run this as a backend service rather than a standalone app? May be minimal if the core functions can be imported directly.
- **Elliptic automatic vs manual submission.** Should Elliptic screening run automatically after C360 processing, or should the investigator always review and confirm the wallet list first? The manual review step is safer but slower.
- **UOL format.** Is the UOL always a URL, or is it sometimes a downloaded file? The upload zone needs to accommodate whichever format investigators use.
- **Maximum ICR/RFI count.** Is there a practical limit to how many prior ICRs or RFIs a single case might have? This affects the UI layout and the backend's ability to process them all efficiently.

---

*This document should be read alongside the Blocked Investigation Architecture document and the main PRD. Together they define the complete Phase 2 specification.*
