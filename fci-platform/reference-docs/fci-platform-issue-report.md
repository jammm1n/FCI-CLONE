# FCI Platform: Post-Testing Issue Report

**Date:** 10 March 2026
**Source:** First end-to-end case investigation on deployed platform
**Total issues identified:** 12

---

## Priority 0: Compliance Risk

### Group A: Data Integrity and Hallucination Prevention

**This must be fixed before any further case testing. A fabricated fact in a compliance case file is a showstopper.**

**Issue 11 -- AI fabricated counterparty wallet attribution**

The AI stated that a counterparty wallet was a "Binance clearing account" with no supporting data anywhere in the case. It used this fabricated attribution as a basis for risk mitigation. This is the most dangerous class of error the platform can produce: an incorrect retain decision could pass QC on false grounds.

**Required fix:**

- Add an explicit, high-priority instruction in the system prompt: never infer wallet ownership, never attribute wallets to entities unless the data explicitly states it, never fabricate mitigating factors.
- The "decide before writing" thinking step (see Issue 6 below) should require the AI to cite source data for every factual claim. If it cannot point to where in the provided data a fact originates, it cannot use it.
- Consider adding a self-verification instruction: "For every factual claim in your output, confirm you can identify where in the provided case data this comes from."

**Effort:** Prompt engineering, but high-care work. Needs testing across multiple case types to confirm it holds.

---

## Priority 1: Core Output Quality

### Group B: Investigation Prompt Architecture

Issues 6, 5, and 4 all affect the quality of the AI's case file output. They should be addressed together because they all touch the core investigation system prompt and output formatting instructions. Issue 6 is the structural change; Issues 5 and 4 layer on top.

**Issue 6 -- Narrative tone inconsistent with conclusion (unmitigated risk language)**

The AI produced a full case narrative and reached the correct decision (retain), but the language throughout left unmitigated risks. QC would reject this. When prompted to rewrite with more careful language, it did so successfully, proving the data and capability are there. The problem is the AI starts writing before it has committed to a conclusion.

**Required fix:**

- Restructure the investigation prompt to enforce a "decide first, then write" workflow.
- Before generating any output sections, the AI must use extended thinking to: review all case data, reach a preliminary decision (retain / off-board / RFI), identify the key factors supporting that decision.
- The writing phase is then governed by the decision: retain means every risk has a corresponding mitigation; off-board means risks are highlighted and justification builds progressively; RFI means information gaps are foregrounded.
- Increase thinking token budget to give the AI genuine reasoning space before output generation.

**Effort:** Significant prompt restructuring. This changes the core flow, so it needs careful testing. But it is not a large volume of text to change -- it is a structural addition to the prompt sequence.

**Issue 5 -- AI leaking internal document references in output**

The AI is citing internal rule numbers, decision matrix references, and knowledge base document names in case file output (e.g. "according to rule #4..."). This has been instructed against in the knowledge base but the guardrail is not strong enough.

**Required fix:**

- Harden the output formatting section of the system prompt with an explicit negative instruction: "Never reference internal document names, rule numbers, decision matrix entries, or knowledge base file names in any output intended for the case file."
- Add this as a check in the post-generation review step (if one exists) or in the "decide first" thinking phase from Issue 6.

**Effort:** Small prompt addition, but test across cases to confirm it sticks.

**Issue 4 -- Law enforcement section output too verbose**

The LE narrative section generated for the case file is too long. Needs to be more concise.

**Required fix:**

- Tighten the prompt instructions for the LE section specifically: set a target length or structural constraint (e.g. "summarise the law enforcement request in no more than 3-4 sentences covering: requesting agency, nature of request, relevant dates, and specific accounts or transactions referenced").
- May also benefit from a few-shot example of good vs bad LE section output in the prompt.

**Effort:** Small prompt tweak.

---

### Group C: Ingestion Pipeline

Issues 10 and 1 both relate to how data gets into the platform before the investigation AI sees it. They are independent of each other but both affect data quality at the point of ingestion.

**Issue 10 -- Hexa/HowDesk dump pre-processing adding unwanted AI analysis**

The ingestion pipeline runs an AI analysis step on the Hexa dump text. This is counterproductive because the investigation AI's job is to interpret this text, and the pre-processing is changing it before it arrives. The extra analysis layer is introducing noise.

**Required fix:**

- Remove the AI analysis step from Hexa dump ingestion entirely.
- Pass the raw Hexa text straight through into the case data. If the raw text is messy but readable, let the investigation AI handle it.
- If specific programmatic cleanup is needed later (stripping headers, normalising whitespace), that can be added as a non-AI processing step, but start with raw passthrough.

**Effort:** Removal of code, not addition. Quick to implement, but test that the investigation AI handles the raw format correctly.

**Issue 1 -- Codex PDF missing narrative detection**

Many Codex case PDFs downloaded from the system do not contain the actual case narrative. The narrative is embedded in a separate attachment (the original law enforcement request) that must be downloaded independently. The ingestion prompt currently does not detect or flag this.

**Required fix:**

- Update the Codex PDF ingestion prompt to identify when no substantive case narrative is present in the PDF.
- Flag this explicitly in the ingestion output report: "No case narrative found in this PDF. The narrative may be in the original law enforcement request attachment, which should be downloaded separately from Codex."
- The investigation AI can then inform the investigator which cases need their LE request attachment uploaded.

**Effort:** Prompt update on the ingestion side. Moderate -- needs to reliably distinguish "narrative present" from "narrative absent" across varied PDF formats.

---

## Priority 2: Workflow Improvements

### Group D: Chat Functionality

Issues 2, 8, 9, and 12 all relate to how the investigator interacts with the chat during a case. They are independent fixes but collectively improve the investigation workflow.

**Issue 9 -- AI hitting output token limit mid-response**

The investigation output is long enough that it hits the max_tokens ceiling on the API response. The AI stops mid-sentence and the investigator has to manually prompt "carry on."

**Required fix (two parts):**

- Immediate: check the current max_tokens setting on the API call and increase it. Sonnet and Opus both support 8192 output tokens; with extended thinking enabled, higher limits may be available.
- Proper: add backend logic to detect when a response has `stop_reason: "max_tokens"` (rather than `end_turn`) and automatically continue the generation. Stitch the continuation together and deliver it as one complete message to the frontend.

**Effort:** The config change is one line. The auto-continuation logic is a small backend addition.

**Issue 2 -- In-chat PDF upload during investigation**

When the AI identifies missing context (e.g. a Codex case narrative), the investigator needs to upload a PDF directly into the chat. The platform already handles images in conversation -- PDF upload just needs the backend to convert PDF pages to images (code already exists in the ingestion pipeline) and pass them through the existing image handling path.

**Required fix:**

- Accept PDF as a file type in the chat input (frontend file type filter change).
- Backend receives the PDF, converts pages to images using existing conversion code.
- Images are included in the next API message via the existing image handling flow.

**Effort:** Small. The heavy lifting (PDF-to-image, image-to-API) is already built. This is wiring, not new capability.

**Issue 8 -- Clipboard paste support in chat input**

No support for Cmd+V / Ctrl+V paste into the chat. Currently requires clicking the attach button and going through the file upload flow. Screenshots from clipboard should paste directly.

**Required fix:**

- Add paste event listener to the chat input area.
- Handle image data from clipboard (screenshot paste).
- Ideally also handle pasted text that might include formatting.

**Effort:** Standard frontend work. Not complex, but needs testing across browsers.

**Issue 12 -- Bullet points and formatting stripped from pasted or ingested text**

When text is pasted into the chat or passed through ingestion (especially relevant now that the Hexa AI step is being removed), bullet points and list formatting are stripped. The text arrives as flat, unstructured content.

**Required fix:**

- Investigate where the stripping occurs: frontend input handling, backend processing, or MongoDB storage.
- If the source text contains bullet characters, list markers, or markdown-style formatting, these should be preserved as-is into the context.
- This may be a plain text vs rich text handling issue. At minimum, markdown-compatible list markers and line breaks should survive the pipeline.

**Effort:** Depends on where the stripping happens. Could be a quick fix if it is a single sanitisation step, or more involved if multiple stages are stripping formatting.

---

## Priority 3: UI and Access

### Group E: Data Accessibility

**Issue 3 -- Elliptic screening CSV not accessible from case view**

After completing data ingestion, the Elliptic screening CSV is only available during the ingestion flow. If the investigator misses it or needs it later, there is no way to retrieve it. It needs to be surfaced as a downloadable file in the main case view.

**Required fix:**

- Store the Elliptic CSV path (or the file itself) as part of the case data in MongoDB.
- Add a download link or button in the case file view UI.

**Effort:** Small. This is surfacing an existing artifact, not generating new data.

**Issue 7 -- Extended thinking not properly contained in follow-up messages**

During the structured investigation flow, the AI's thinking blocks are correctly rendered in a collapsible dropdown. In free chat after the structured process completes, thinking content bleeds into the main response text instead of being separated.

**Required fix:**

- The frontend thinking block parser needs to apply consistently to all assistant messages, not just those generated during the structured investigation phase.

**Effort:** Small frontend fix. Likely a conditional that needs to be removed or broadened.

---

## Summary Table

| # | Issue | Group | Priority | Type | Effort |
|---|-------|-------|----------|------|--------|
| 11 | Fabricated wallet attribution | A | P0 | Prompt | High-care |
| 6 | Narrative tone vs conclusion | B | P1 | Prompt architecture | Significant |
| 5 | Internal doc references in output | B | P1 | Prompt | Small |
| 4 | LE section too verbose | B | P1 | Prompt | Small |
| 10 | Hexa pre-processing adds AI analysis | C | P1 | Ingestion pipeline | Quick |
| 1 | Codex PDF missing narrative | C | P1 | Ingestion prompt | Moderate |
| 9 | Token limit mid-response | D | P2 | Backend config + logic | Small-moderate |
| 2 | In-chat PDF upload | D | P2 | Backend + frontend | Small |
| 8 | Clipboard paste in chat | D | P2 | Frontend | Small |
| 12 | Formatting stripped from text | D | P2 | Investigation needed | Unknown |
| 3 | Elliptic CSV in case view | E | P3 | Frontend + backend | Small |
| 7 | Thinking blocks in free chat | E | P3 | Frontend | Small |

---

## Recommended Fix Order

**Session 1: Prompt overhaul (Issues 11, 6, 5, 4)**

Start with Issue 11 (hallucination guardrails) as the foundation. Then build Issue 6 (decide-first architecture) which structurally prevents many of the problems 11 addresses. Layer Issues 5 and 4 on top as output formatting constraints. Test the full prompt suite against 2-3 varied case types before moving on.

**Session 2: Ingestion pipeline (Issues 10, 1)**

Remove the Hexa AI analysis step (Issue 10) first since it is a deletion. Then update the Codex ingestion prompt (Issue 1). Test both with representative data.

**Session 3: Chat and workflow (Issues 9, 2, 8, 12)**

Start with Issue 9 (token limit) as it is partially a config change. Then Issue 2 (PDF upload in chat) since it unlocks the workflow for missing Codex narratives. Issue 8 (clipboard paste) and Issue 12 (formatting preservation) round out the chat improvements.

**Session 4: Polish (Issues 3, 7)**

Surface the Elliptic CSV in case view. Fix the thinking block rendering in free chat. Both are quick, isolated changes.
