# Prompt Architecture Report

**Date:** 2026-03-06
**Status:** Planning — no code changes yet

---

## 1. Current State

All 17 prompts live in `knowledge_base/core/prompt-library.md` and are loaded into the system prompt for every conversation (both free chat and case investigations). This made sense when all analysis was done interactively in the chat. With the ingestion dashboard handling data processing upstream, the prompt library needs to be split by context.

---

## 2. Complete Prompt Inventory

| # | Name | Trigger Data | Category |
|---|------|-------------|----------|
| 1 | Transaction Analysis / Pass-Through | C360 IO Summary, IO Count, Trade Summary | C360 Ingestion |
| 2 | CTM Alerts Enhanced | Raw crypto transaction spreadsheet | Free Chat Only |
| 3 | Account Blocks | C360 Block/Unblock Details | C360 Ingestion |
| 4 | Prior ICR Analysis | Hexa Template: Prior ICR section | Future Ingestion Module |
| 5 | Scam Analysis (P2P) | HaoDesk L1 Referral | Future Ingestion Module |
| 6 | CTM Alerts (Standard) | C360 Lifetime CTM Alert Details | C360 Ingestion |
| 7 | Privacy Coin Analysis | C360 Privacy Inbound/Outbound | C360 Ingestion |
| 8 | Failed Fiat Transactions | C360 Lifetime Failed Fiat Details | C360 Ingestion |
| 9 | Device and IP Analysis | C360 Device Analysis + nationality/residence | Being Merged (see Section 4) |
| 10 | RFI Summary | Hexa Template: RFI section | Future Ingestion Module |
| 11 | Summary of Investigation | All completed investigation sections | Meta — Case Assembly |
| 12 | Internal Counterparty Analysis | C360 IT + BP + P2P spreadsheets + Hexa text | Free Chat / Investigation (NOT ingestion — uses Hexa text) |
| 13 | KYB Summary (Corporate) | Company KYC/KYB screenshots | Future Ingestion Module |
| 9E | Device & IP — Data Extraction | Web app device output + nationality/residence | Being Merged (see Section 4) |
| 14E | Elliptic Top Addresses — Extraction | Elliptic batch screening results | Future Ingestion Module |
| 15E | Law Enforcement / Kodex — Extraction | Kodex case screenshots | Future Ingestion Module |
| 16E | RCM / Case Intake — Extraction | Scam/fraud case package from SSO | Future Ingestion Module |

---

## 3. C360 Processor → Prompt Mapping (Confirmed)

These 8 processors run automatically after C360 file upload. Each processor's raw output is sent to its corresponding prompt for AI summarisation. The AI output is what gets stored in the case file — raw processor output is not included in the final document.

| Processor ID | Processor Label | Prompt | Notes |
|---|---|---|---|
| `tx_summary` | Transaction Summary | **Prompt 1** | Direct match. IO Summary, IO Count, Trade Summary data. |
| `privacy_coin` | Privacy Coin Breakdown | **Prompt 7** | Direct match. |
| `counterparty` | Internal Counterparty | **Prompt 19** (NEW) | Rewritten for ingestion. Prompt 12 stays in free chat (uses Hexa text). |
| `device` | Device & IP Analysis | **New merged prompt** | Combines 9 + 9E. See Section 4. |
| `fiat` | Failed Fiat Withdrawals | **Prompt 8** | Direct match. |
| `ctm` | CTM Alerts | **Prompt 6** (Standard) | NOT Prompt 2 (Enhanced), which is for free chat. |
| `ftm` | FTM Alerts | **New prompt** | Adapted from Prompt 6. See Section 4. |
| `blocks` | Account Blocks | **Prompt 3** | Direct match. |

### C360 processors with NO AI processing

| Processor ID | Reason |
|---|---|
| `user_profile` | Short text summary — passed through as raw text. KYC/KYB is a separate future module. |
| `elliptic` | Intermediate data (address extraction for wallet pipeline). Excluded from C360 case file output entirely. |
| `elliptic` | This processor only extracts wallet addresses for the Elliptic API batch CSV. The AI processing (Prompt 14E) applies to the Elliptic API *screening results*, which is a separate pipeline. |

---

## 4. New Prompts Required

### 4a. Merged Device & IP Prompt (replaces Prompts 9 and 9E)

**Problem:** Prompt 9 produces a narrative but is thin on data points. Prompt 9E extracts comprehensive structured data but outputs labeled sections with bullets — not suitable for direct inclusion in the case file.

**Solution:** A single merged prompt that:
- Extracts ALL data points from 9E (headline figures, location frequency, language summary, VPN usage, shared UIDs with full listing, sanctioned/restricted jurisdiction check)
- Presents everything as **narrative prose paragraphs** (like Prompt 9)
- **No opinions or risk assessment** — purely factual data presentation
- Output is ICR-ready text that reduces cognitive load in the case file

**Status:** Needs to be written before implementation.

### 4b. FTM Alerts Prompt

**Problem:** No FTM-specific prompt exists in the library. FTM (Fiat Transaction Monitoring) alerts have a different structure and focus than CTM (Crypto Transaction Monitoring) alerts.

**Solution:** Adapt Prompt 6 (CTM Standard) as a starting point, creating a separate prompt so it can be independently tuned as real FTM data flows through the system.

**Status:** Needs to be written before implementation.

---

## 5. Future Ingestion Module Prompts

These prompts will be wired to their respective ingestion modules as those modules are built. They are NOT part of the C360 pipeline.

| Prompt | Future Module | Input Source |
|---|---|---|
| 4 — Prior ICR Analysis | Prior ICR section | Hexa template data (text input) |
| 5 — Scam Analysis (P2P) | L1 Referral / Case Intake | HaoDesk referral data |
| 10 — RFI Summary | RFI section | Hexa template data (text input) |
| 13 — KYB Summary | KYC/KYB module | Admin screenshots (image analysis) |
| 14E — Elliptic Extraction | Elliptic section | Elliptic API screening results |
| 15E — LE / Kodex Extraction | Law Enforcement section | Kodex screenshots (image analysis) |
| 16E — RCM / Case Intake | Case Intake section | SSO scam/fraud package |

### Elliptic Note
The Elliptic pipeline has a gap: C360 extracts addresses → Elliptic API screens them → [MISSING: AI processing via 14E] → case file. This will be wired when the Elliptic API key is available and the response format can be tested. No stub code needed now — just this documented note.

---

## 6. Meta Prompt

| Prompt | Purpose | When It Runs |
|---|---|---|
| 11 — Summary of Investigation | Executive summary of the entire case | At assembly time, after all sections are populated. Runs on the assembled output of all other sections. |

This prompt stays available in both free chat and case investigation contexts. It is not tied to any single ingestion module.

---

## 7. System Prompt Split

Currently one system prompt contains all 17 prompts. Going forward, two distinct prompt configurations:

### Free Chat
- **Keeps ALL prompts** (1-16E)
- Used for ad-hoc analysis where the investigator pastes raw data directly
- Prompt 2 (CTM Enhanced) is primarily used here

### Case Investigation Chat
- **Removes prompts handled by ingestion:** 1, 3, 6, 7, 8, 12, plus the new Device/IP and FTM prompts
- These sections arrive pre-processed — the AI doesn't need instructions to process them again
- **Retains:** Prompt 11 (Summary), Prompt 2 (ad-hoc analysis), and any prompts for modules not yet built
- As each new ingestion module goes live, its corresponding prompt migrates out of the case investigation system prompt

### Migration Plan
Prompts are removed from the case investigation system prompt **only when their ingestion module is live and tested**. This is incremental — the case chat can still process raw data for any section that hasn't been automated yet.

| Phase | Prompts Removed from Case Chat |
|---|---|
| C360 AI layer goes live | 1, 3, 6, 7, 8, 12, new Device/IP, new FTM |
| Elliptic module goes live | 14E |
| LE/Kodex module goes live | 15E |
| KYC/KYB module goes live | 13 |
| Prior ICR module goes live | 4 |
| RFI module goes live | 10 |
| Case Intake module goes live | 5, 16E |
| Prompt 9, 9E | Replaced by merged prompt — remove both from all contexts |

---

## 8. Implementation Order (C360 AI Layer)

1. Write the two new prompts (merged Device/IP, FTM) — **DONE, see Section 9**
2. Modify `c360_processor.py` to return per-processor output (not one assembled blob)
3. Create `server/services/ingestion/ai_processor.py` — takes raw processor output + prompt, calls Claude API, returns narrative
4. Wire the pipeline: raw processing completes → AI calls fire sequentially → results stored to `ingestion_cases` document
5. Update assembly to use AI-processed output instead of raw output
6. Update frontend status indicators for the AI processing step

---

## 9. New Prompts (Draft)

**IMPORTANT:** These prompts are stored here for reference only. They must NOT be added to `knowledge_base/core/prompt-library.md` until the system prompt split is implemented — that file is loaded live into the investigation chat system prompt and any changes affect downstream behaviour immediately.

---

### Prompt 17: DEVICE & IP ANALYSIS — INGESTION

**Replaces:** Prompts 9 + 9E (blended into one for the ingestion pipeline)

**Trigger Data:** Raw output from the Device & IP Analysis processor (DEVICE_MAIN, DEVICE_SUM, DEVICE_LINK data), plus the user's nationality and country of residence (auto-populated from C360/UOL).

**Exact Prompt:**

> You are a data extraction and presentation tool. You produce factual narrative text only. No risk assessment, no opinions, no recommendations, no mitigation statements. Present every data point; do not omit or summarize counts without listing the underlying data.
>
> **INPUT:** The raw Device & IP Analysis data for a user under investigation. The user's nationality is [NATIONALITY] and country of residence is [RESIDENCE].
>
> **ACTION:** Parse the device and IP data and present ALL of the following information as clean narrative paragraphs. Every data point listed below must appear in the output.
>
> **Paragraph 1 — Overview and Access Profile:**
> State the total number of distinct devices used, distinct IP locations accessed from, and distinct system languages detected. State the primary access country with its login count and percentage of total logins. State whether the primary access country matches or does not match the user's known nationality ([NATIONALITY]) and country of residence ([RESIDENCE]). State the primary system language with its session count and whether it is consistent or inconsistent with the user's nationality and country of residence.
>
> **Paragraph 2 — Access Locations and VPN:**
> List each country the user accessed from, sorted by frequency (highest first), with the total login count per country. For the top 3 countries by volume, include the leading cities with their login counts. State the VPN usage as a percentage and absolute count (e.g., "VPN was used for X% of total accesses, Y of Z operations"). If timezone data is available, state the timezones with session counts.
>
> **Paragraph 3 — Jurisdictional Exposure:**
> Check all access locations against the following lists:
> Sanctioned jurisdictions: North Korea, Cuba, Iran, Crimea, Donetsk People's Republic, Luhansk People's Republic.
> Restricted jurisdictions: Canada, Netherlands, United States, Belarus, Russia.
> If access from any sanctioned jurisdiction was detected, state the country, login count, and percentage of total activity. If access from any restricted jurisdiction was detected, state the country, login count, and percentage of total activity. United States access must always be stated separately with its own count and percentage, regardless of other restricted jurisdictions. If no access from sanctioned or restricted jurisdictions was detected, state both facts explicitly (e.g., "The user has not accessed from any sanctioned jurisdiction. The user has not accessed from any restricted jurisdiction.").
>
> **Paragraph 4 — Shared Device Identifiers:**
> If any UIDs share device identifiers (UUIDs, IPs, or FaceVideo IDs) with the subject, list EVERY UID individually. Do not summarize as a count without listing them. For each shared UID, state the type of sharing (UUID, IP, FaceVideo), and include any available context: KYC status, offboarded status and reason, blocked status, ICR cases, LE/Kodex requests, nationality, and residence. If counterparties from Internal Transfer, Binance Pay, or P2P data also share device identifiers, list those UIDs separately with the shared identifier types. If no shared device identifiers were detected, state this explicitly.
>
> **FORMAT:**
> 3-4 narrative paragraphs as described above. Clean prose suitable for direct inclusion in an ICR case file. No headings, no bullets, no labeled sections, no markdown formatting. Approximately 150-300 words total depending on data volume.
>
> All dates must use YYYY-MM-DD format. All USD amounts must use a leading $ and commas for thousands separators.
>
> **COMPLETENESS CHECK:** All four paragraph topics must be addressed. If data for any topic is not present in the input, state what is absent rather than omitting the paragraph.
>
> **NO CITATIONS:** No source brackets, reference numbers, or grounding citations under any circumstances.

---

### Prompt 18: FTM ALERTS — INGESTION

**Replaces:** Nothing (new prompt — no FTM prompt existed previously)

**Trigger Data:** Raw output from the FTM Alerts processor (FTM_ALERTS data — rule-triggered fiat transaction monitoring alerts with rule codes, transaction types, amounts, counterparties, and addresses).

**Exact Prompt:**

> **C — Context**
> You are summarizing Fiat Transaction Monitoring (FTM) alert data for a compliance case file. FTM alerts are rule-triggered alerts on fiat-side activity including deposits, withdrawals, and internal transfers. The data includes rule codes with descriptions, USD amounts, transaction types, counterparty IDs, wallet addresses, and timestamps.
>
> **R — Role**
> Act as a Senior Compliance Analyst specializing in fiat transaction monitoring.
>
> **A — Action (strict rules)**
> 1. State the total number of FTM alerts and the total USD value flagged.
> 2. Report the date range covered by the alerts only if start and end dates are explicitly present in the data.
> 3. Identify the top 1-3 rule codes by flagged USD value. For each, state: the rule code, the rule name and platform, the alert count, and the total USD flagged under that rule.
> 4. State the number of distinct transaction types observed and name them (e.g., deposit, withdrawal, internal transfer).
> 5. If counterparty data is present, state the number of distinct counterparties and identify the top counterparty by USD volume. If any alerts have no counterparty (external transactions), state the count and USD total for external transactions.
> 6. If address data is present, state the number of distinct addresses and identify the top 1-3 addresses by USD value with their associated rule codes and transaction types.
> 7. Describe any clear patterns that are explicitly supported by the data (e.g., concentration of alerts under a single rule code, clustering of alerts around specific dates, repeated flagging of the same counterparty or address).
> 8. All local currency amounts must include USD equivalent in square brackets.
> 9. End with this exact final sentence: "This is a summary of the provided FTM alert data and requires manual verification against the underlying fiat transaction monitoring records."
>
> **F — Format**
> Single paragraph, 80-120 words, full sentences, no bullets. If the data volume requires it (more than 10 distinct rule codes or more than 5 distinct counterparties), a second paragraph is permitted to cover the additional detail.
>
> **T — Target Audience**
> Internal Compliance, FCI, and external regulators.
>
> **Constraints:**
> Do not infer or estimate any values not explicitly present in the data. Do not use internal rule code abbreviations without the full rule name. Do not speculate on the reason for the alerts or assess risk. Report facts only.
>
> **NO CITATIONS:** No source brackets, reference numbers, or grounding citations under any circumstances.
