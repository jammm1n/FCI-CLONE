# Free Chat Implementation Plan

## Overview
Add a differentiated Free Chat mode with its own system prompt, access to all processing prompts via tool calls, and the same core knowledge base as Case Investigation.

## Current State
- `KnowledgeBase` loads all `core/*.md` + `reference-index.yaml` on startup
- `get_system_prompt()` returns one blob for both modes (no mode awareness)
- `get_reference_document(id)` resolves from `reference/` only
- `conversation_manager.py` supports `mode="free_chat"` (stored in MongoDB) but both modes get identical AI behavior
- Frontend `FreeChatPage.jsx` is fully functional — no changes needed
- `SYSTEM-PROMPT.md` lives in `core/` and gets globbed into every conversation

## Architecture Decisions
1. **Same core KB for both modes** — general rules, step docs, decision matrix, QC checklist, escalation matrix
2. **Different system prompts** — case investigation vs free chat
3. **System prompts moved out of `core/`** — `core/` = shared only
4. **All ingestion prompts accessible via `get_prompt` tool call** — no duplication
5. **Global rules prepended to every prompt fetch** — self-contained execution
6. **Both tools available to both modes** — `get_reference_document` + `get_prompt`

## Target File Structure

```
knowledge_base/
  system-prompt-case.md           # MOVED from core/SYSTEM-PROMPT.md
  system-prompt-free-chat.md      # NEW
  reference-index.yaml            # Existing (14 documents)
  prompt-index.yaml               # NEW — indexes all 18 prompt files
  core/                           # Shared — loaded for ALL modes
    decision-matrix.md
    icr-general-rules.md
    icr-steps-setup.md
    icr-steps-analysis.md
    icr-steps-decision.md
    icr-steps-post.md
    mlro-escalation-matrix.md
    qc-submission-checklist.md
  reference/                      # On demand via get_reference_document
    (14 files — 8 SOPs + 4 prompts + archive + escalation decisions)
  prompts/                        # On demand via get_prompt
    _global-rules.md              # Prepended to every prompt fetch
    prompt-01-transaction-analysis.md
    prompt-03-account-blocks.md
    prompt-04-prior-icr.md
    prompt-06-ctm-alerts.md
    prompt-07-privacy-coin.md
    prompt-08-failed-fiat.md
    prompt-10-rfi-summary.md
    prompt-13-kyc-document.md
    prompt-15e-kodex-per-case.md
    prompt-15e-kodex-summary.md
    prompt-17-device-ip-ingestion.md
    prompt-18-ftm-alerts-ingestion.md
    prompt-19-counterparty-ingestion.md
    prompt-20-l1-referral.md
    prompt-21-haoDesk-cleanup.md
    prompt-22-rfi-document-review.md
    prompt-23-l1-communications.md
```

## Changes — Execution Order

### Step 1: Move system prompt out of core/

**Action:** Rename `knowledge_base/core/SYSTEM-PROMPT.md` → `knowledge_base/system-prompt-case.md`

No content changes. Just move the file so `core/` only contains shared documents.

### Step 2: Write `knowledge_base/system-prompt-free-chat.md`

New file. Content should include:

```markdown
# SYSTEM PROMPT — FREE CHAT MODE
---
### IDENTITY & ROLE
You are FCI-GPT, a Senior Compliance Investigator Copilot
operating in ad-hoc mode. You assist Binance L2 investigators
with any task on demand: processing raw data into ICR-ready
output, answering procedural questions, running QC checks,
and walking through any part of a case file.

You do NOT follow a sequential investigation workflow in this
mode. Respond directly to whatever the investigator needs.
---
### DOCUMENT HIERARCHY (Priority Order)
[Same as case investigation — copy from system-prompt-case.md]
---
### VOICE & TONE
[Same as case investigation — copy from system-prompt-case.md]
---
### AD-HOC MODE BEHAVIOR

**Data Processing:**
When the investigator pastes raw data (C360, Elliptic screenshots,
device/IP output, communications, etc.):
1. Identify the data type and the corresponding ICR section
2. If a processing prompt is available in the prompt index,
   fetch it via `get_prompt("prompt-id")` and execute it
3. Apply the output format spec from the relevant step document
4. Output ICR-ready text suitable for direct copy-paste

**QC Checks:**
When asked to QC-check pasted ICR text:
1. Identify the section(s) being checked
2. Apply the relevant QC parameters from qc-submission-checklist.md
3. Apply step-specific rules from the relevant step document
4. Report findings with specific references

**Procedural Questions:**
When asked "how do I handle X?":
1. Consult the relevant step document, general rules, and decision matrix
2. If an SOP is needed, fetch it from the reference tier
3. Provide a clear, actionable answer

**Multi-User / Partial Case Work:**
Investigators may process data for additional users in a multi-user
case without creating a full ingestion case. Treat each data paste
as standalone — apply the same rules and output specs as if it were
part of a full investigation.
---
### PROCESSING PROMPT INDEX
The following processing prompts are available via the `get_prompt`
tool. When the investigator pastes data matching a prompt's trigger,
fetch and execute the prompt. Global formatting rules are
automatically included with every prompt.

[Injected from prompt-index.yaml at runtime — same format as
reference index]
---
### OPERATIONAL OVERRIDE HANDLING
[Same as case investigation — copy from system-prompt-case.md]
---
### FCI / FCMI TERMINOLOGY
[Same as case investigation — copy from system-prompt-case.md]
```

Note: The shared sections (Document Hierarchy, Voice & Tone, Override Handling, Terminology) should be copied verbatim from `system-prompt-case.md`. Do NOT reference the other file — each system prompt must be self-contained since only one is loaded per mode.

### Step 3: Write `knowledge_base/prompt-index.yaml`

New file. Must list all 18 prompt files from `knowledge_base/prompts/`.

```yaml
# Prompt Index
# Available to the AI via get_prompt tool calls.
# Global rules (_global-rules.md) are automatically prepended.

processing_prompts:

  - id: tx-analysis
    title: "Transaction Analysis / Pass-Through & Rapid Movement"
    filename: "prompt-01-transaction-analysis.md"
    covers:
      - C360 transaction summary data processing
      - Fund movement narrative, velocity assessment, negative confirmations
      - Single paragraph ~80-100 words for ICR Transaction Overview
    token_estimate: 500

  - id: account-blocks
    title: "Account Blocks Summary"
    filename: "prompt-03-account-blocks.md"
    covers:
      - Lifetime block/unblock details from C360
      - Chronological block/unblock actions with timestamps
    token_estimate: 300

  - id: prior-icr
    title: "Prior ICR Analysis"
    filename: "prompt-04-prior-icr.md"
    covers:
      - Prior and in-progress ICR review data
      - Consolidated summary paragraph ~60-75 words
    token_estimate: 300

  - id: ctm-alerts
    title: "CTM Alerts (Standard)"
    filename: "prompt-06-ctm-alerts.md"
    covers:
      - Lifetime CTM alert details from C360
      - Single paragraph 60-80 words with entity attributions
    token_estimate: 400

  - id: privacy-coin
    title: "Privacy Coin Analysis"
    filename: "prompt-07-privacy-coin.md"
    covers:
      - Privacy coin transaction data (XMR, ZEC, DASH)
      - Summary paragraph 50-70 words with AML/CFT risk statement
    token_estimate: 300

  - id: failed-fiat
    title: "Failed Fiat Transactions"
    filename: "prompt-08-failed-fiat.md"
    covers:
      - Failed fiat withdrawal/deposit data
      - Analysis paragraph with error reasons and fraud flags
    token_estimate: 300

  - id: rfi-summary
    title: "RFI Summary"
    filename: "prompt-10-rfi-summary.md"
    covers:
      - RFI history data from Hexa template
      - 50-60 word summary of RFI types and responses
    token_estimate: 300

  - id: kyc-document
    title: "KYC Document Extraction"
    filename: "prompt-13-kyc-document.md"
    covers:
      - KYC document images (passport, ID, POA)
      - Structured extraction of identity and address details
    token_estimate: 400

  - id: kodex-per-case
    title: "Kodex Per-Case Extraction"
    filename: "prompt-15e-kodex-per-case.md"
    covers:
      - Individual Kodex/LE case PDF extraction
      - Structured case data (authority, dates, targets, request type)
    token_estimate: 500

  - id: kodex-summary
    title: "Kodex Cross-Case Summary"
    filename: "prompt-15e-kodex-summary.md"
    covers:
      - Summary across multiple Kodex cases
      - LE case table and risk classification
    token_estimate: 400

  - id: device-ip
    title: "Device & IP Analysis"
    filename: "prompt-17-device-ip-ingestion.md"
    covers:
      - Web app device/IP output processing
      - Six-section structured extraction (headline figures, location, language, VPN, shared devices, sanctioned jurisdictions)
    token_estimate: 600

  - id: ftm-alerts
    title: "FTM Alerts"
    filename: "prompt-18-ftm-alerts-ingestion.md"
    covers:
      - Fiat Transaction Monitoring alert data
      - Alert summary with patterns and risk indicators
    token_estimate: 400

  - id: counterparty-ingestion
    title: "Counterparty Analysis (Ingestion)"
    filename: "prompt-19-counterparty-ingestion.md"
    covers:
      - C360 counterparty spreadsheet processing
      - Risk flag extraction, clean CP summary, P2P totals
    token_estimate: 500

  - id: l1-referral
    title: "L1 Referral Narrative Cleanup"
    filename: "prompt-20-l1-referral.md"
    covers:
      - Raw L1 referral text (hexa_dump) cleanup
      - Organized, readable English summary
    token_estimate: 300

  - id: haoDesk-cleanup
    title: "HaoDesk Case Data Cleanup"
    filename: "prompt-21-haoDesk-cleanup.md"
    covers:
      - Raw HaoDesk hex dump cleanup
      - Structured case data extraction
    token_estimate: 300

  - id: rfi-document-review
    title: "RFI Document Review"
    filename: "prompt-22-rfi-document-review.md"
    covers:
      - RFI response document analysis (images + text)
      - Evidence assessment and compliance relevance
    token_estimate: 400

  - id: l1-communications
    title: "L1 Communications Processing"
    filename: "prompt-23-l1-communications.md"
    covers:
      - Victim and suspect communications (text + screenshots)
      - Translation, chronological summary, scam/fraud enhancement
    token_estimate: 400
```

**Important:** Read each prompt file to verify the token estimates and coverage descriptions are accurate. The estimates above are rough — adjust based on actual file sizes.

### Step 4: Edit `server/services/knowledge_base.py`

Current file is 82 lines. Changes:

**`__init__`** — add new instance variables:
```python
self.case_system_prompt: str = ""
self.free_chat_system_prompt: str = ""
self.prompt_index: list[dict] = []
self.prompt_index_text: str = ""
self.global_rules: str = ""
```

**`load_on_startup()`** — restructure:
```python
def load_on_startup(self):
    # 1. Load mode-specific system prompts (from KB root, NOT core/)
    case_sp = self.base_path / "system-prompt-case.md"
    if case_sp.exists():
        self.case_system_prompt = case_sp.read_text(encoding="utf-8")

    free_sp = self.base_path / "system-prompt-free-chat.md"
    if free_sp.exists():
        self.free_chat_system_prompt = free_sp.read_text(encoding="utf-8")

    # 2. Load shared core documents (everything in core/)
    core_parts = []
    core_dir = self.base_path / "core"
    if core_dir.exists():
        for filepath in sorted(core_dir.glob("*.md")):
            content = filepath.read_text(encoding="utf-8")
            core_parts.append(f"# {filepath.stem.upper()}\n\n{content}")
    self.core_content = "\n\n---\n\n".join(core_parts)

    # 3. Load reference index (existing logic, unchanged)
    # ... existing code ...

    # 4. Load prompt index
    prompt_index_path = self.base_path / "prompt-index.yaml"
    if prompt_index_path.exists():
        with open(prompt_index_path, "r", encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)
        self.prompt_index = prompt_data.get("processing_prompts", [])
    else:
        self.prompt_index = []

    # Format prompt index as text for system prompt injection
    # (same structure as reference index)
    p_lines = [
        "## PROCESSING PROMPT INDEX",
        "",
        "The following processing prompts are available via the "
        "get_prompt tool. When data is pasted that matches a prompt's "
        "trigger, fetch and execute the prompt. Global formatting rules "
        "are automatically included.",
        "",
    ]
    for doc in self.prompt_index:
        p_lines.append(f"### {doc['title']}")
        p_lines.append(f"- **ID:** `{doc['id']}`")
        p_lines.append("- **Covers:**")
        for item in doc["covers"]:
            p_lines.append(f"  - {item}")
        p_lines.append(f"- **Approximate size:** {doc['token_estimate']:,} tokens")
        p_lines.append("")
    self.prompt_index_text = "\n".join(p_lines)

    # 5. Load global rules for prompt prepending
    global_rules_path = self.base_path / "prompts" / "_global-rules.md"
    if global_rules_path.exists():
        self.global_rules = global_rules_path.read_text(encoding="utf-8")
```

**`get_system_prompt(mode)`** — add mode parameter:
```python
def get_system_prompt(self, mode: str = "case") -> str:
    """Return the complete system prompt for the given mode."""
    if mode == "free_chat":
        return (
            f"{self.free_chat_system_prompt}\n\n---\n\n"
            f"{self.core_content}\n\n---\n\n"
            f"{self.reference_index_text}\n\n---\n\n"
            f"{self.prompt_index_text}"
        )
    else:
        return (
            f"{self.case_system_prompt}\n\n---\n\n"
            f"{self.core_content}\n\n---\n\n"
            f"{self.reference_index_text}"
        )
```

**`get_prompt(prompt_id)`** — new method:
```python
def get_prompt(self, prompt_id: str) -> str:
    """Retrieve a processing prompt by ID, with global rules prepended."""
    valid_ids = {p["id"]: p["filename"] for p in self.prompt_index}
    if prompt_id not in valid_ids:
        return f"Error: Unknown prompt ID '{prompt_id}'. Valid IDs: {', '.join(valid_ids.keys())}"

    filepath = self.base_path / "prompts" / valid_ids[prompt_id]
    if not filepath.exists():
        return f"Error: Prompt file not found for '{prompt_id}'."

    prompt_content = filepath.read_text(encoding="utf-8")

    # Prepend global rules for self-contained execution
    if self.global_rules:
        return f"{self.global_rules}\n\n---\n\n{prompt_content}"
    return prompt_content
```

### Step 5: Edit `server/services/ai_client.py`

**`TOOLS` list** — add second tool:
```python
TOOLS = [
    {
        "name": "get_reference_document",
        # ... existing definition unchanged ...
    },
    {
        "name": "get_prompt",
        "description": (
            "Retrieve a data processing prompt from the prompt library. "
            "Use this tool when you need to process raw data pasted by "
            "the investigator (e.g., C360 transaction data, device/IP "
            "output, Elliptic screenshots, communications). The prompt "
            "will include formatting rules automatically. Consult the "
            "processing prompt index in your system prompt to identify "
            "the correct prompt_id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt_id": {
                    "type": "string",
                    "description": (
                        "The unique identifier of the processing prompt "
                        "to retrieve, as listed in the processing prompt index."
                    )
                }
            },
            "required": ["prompt_id"]
        }
    }
]
```

**`_process_tool_calls()`** — add `get_prompt` handling:

In the `for block in response_content:` loop, after the `get_reference_document` branch, add:

```python
elif block.name == "get_prompt":
    prompt_id = block.input.get("prompt_id", "")
    prompt_content = knowledge_base.get_prompt(prompt_id)

    prompt_meta = next(
        (p for p in knowledge_base.prompt_index if p["id"] == prompt_id),
        None
    )
    tools_used.append({
        "tool": "get_prompt",
        "document_id": prompt_id,
        "document_title": prompt_meta["title"] if prompt_meta else prompt_id,
    })

    tool_results.append({
        "type": "tool_result",
        "tool_use_id": block.id,
        "content": prompt_content,
    })

    logger.info(
        "Tool call: get_prompt(%s) — %s",
        prompt_id,
        prompt_meta["title"] if prompt_meta else "unknown prompt"
    )
```

### Step 6: Edit `server/services/conversation_manager.py`

Two locations where `get_system_prompt()` is called:

**Line ~225 (send_message):**
```python
# Before:
system_prompt = knowledge_base.get_system_prompt()
# After:
system_prompt = knowledge_base.get_system_prompt(mode=conversation.get("mode", "case"))
```

**Line ~341 (send_message_streaming):**
```python
# Before:
system_prompt = knowledge_base.get_system_prompt()
# After:
system_prompt = knowledge_base.get_system_prompt(mode=conversation.get("mode", "case"))
```

The `conversation` dict is already loaded from MongoDB at this point and contains the `mode` field.

## Verification Checklist

After implementation, verify:

- [ ] Server starts without errors
- [ ] `knowledge_base/core/` no longer contains SYSTEM-PROMPT.md
- [ ] `knowledge_base/system-prompt-case.md` exists with unchanged content
- [ ] `knowledge_base/system-prompt-free-chat.md` exists
- [ ] `knowledge_base/prompt-index.yaml` exists with 18 entries
- [ ] Case Investigation chat works identically to before
- [ ] Free Chat creates conversations and streams responses
- [ ] Free Chat system prompt is different from Case Investigation
- [ ] `get_reference_document` works in both modes
- [ ] `get_prompt` works — fetch `tx-analysis` and verify global rules prepended
- [ ] Tool use events appear in the frontend (streaming indicator shows tool fetches)
- [ ] All 18 prompt IDs resolve correctly
- [ ] Prompt index appears in Free Chat system prompt but NOT in Case Investigation

## Notes

- **No frontend changes required** — FreeChatPage.jsx already handles tool_use events in the SSE stream
- **No database changes** — conversation `mode` field already exists
- **Prompt cache:** Both system prompts use `cache_control: {"type": "ephemeral"}` — Anthropic will cache each separately since they're different content
- **Token budget:** Free Chat system prompt is slightly larger (adds prompt index ~800 tokens) but same core KB load
