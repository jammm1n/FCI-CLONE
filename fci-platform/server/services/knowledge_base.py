"""
Knowledge base service — document loading, YAML index parsing, tool handler.

Implements the two-tier knowledge base architecture:
  Tier 1 (Core): Loaded into memory on startup, injected into every system prompt
  Tier 2 (Reference): Available on demand via get_reference_document tool call

Additionally supports mode-aware system prompts (case vs free_chat),
step-aware system prompts for investigation steps, and a processing
prompt library accessible via get_prompt tool call.
"""

import re
import yaml
from pathlib import Path

from server.config import settings, STEP_CONFIG, MULTI_USER_STEP_CONFIG


# ---------------------------------------------------------------------------
# Document registry — maps doc_id to file path relative to KB root
# Used by get_document() and get_step_system_prompt()
# ---------------------------------------------------------------------------

DOCUMENT_REGISTRY = {
    "icr-steps-setup": "core/icr-steps-setup.md",
    "icr-steps-analysis": "core/icr-steps-analysis.md",
    "icr-steps-decision": "core/icr-steps-decision.md",
    "icr-steps-post": "core/icr-steps-post.md",
    "decision-matrix": "core/decision-matrix.md",
    "mlro-escalation-matrix": "core/mlro-escalation-matrix.md",
    "qc-quick-reference": "qc-quick-reference.md",
    "qc-full-checklist": "core/qc-submission-checklist.md",
    "icr-general-rules": "core/icr-general-rules.md",
}


class KnowledgeBase:
    def __init__(self, base_path: str = settings.KNOWLEDGE_BASE_PATH):
        self.base_path = Path(base_path)
        self.core_content: str = ""
        self.reference_index: list[dict] = []
        self.reference_index_text: str = ""
        self.case_system_prompt: str = ""
        self.free_chat_system_prompt: str = ""
        self.oneshot_system_prompt: str = ""
        self.prompt_index: list[dict] = []
        self.prompt_index_text: str = ""
        self.multi_user_system_prompt: str = ""
        self.global_rules: str = ""  # prompts/_global-rules.md (prepended to prompts)
        self.general_rules: str = ""  # core/icr-general-rules.md (step system prompt)
        self.qc_quick_reference: str = ""  # qc-quick-reference.md (steps 1-4)
        self._documents: dict[str, str] = {}  # doc_id → content
        self._filtered_step_cache: dict[str, str] = {}  # "doc_id:steps" → filtered content

    def load_on_startup(self):
        """Load system prompts, core documents, reference index, and prompt index."""
        # 1. Load mode-specific system prompts (from KB root, NOT core/)
        case_sp = self.base_path / "system-prompt-case.md"
        if case_sp.exists():
            self.case_system_prompt = case_sp.read_text(encoding="utf-8")

        free_sp = self.base_path / "system-prompt-free-chat.md"
        if free_sp.exists():
            self.free_chat_system_prompt = free_sp.read_text(encoding="utf-8")

        oneshot_sp = self.base_path / "system-prompt-oneshot.md"
        if oneshot_sp.exists():
            self.oneshot_system_prompt = oneshot_sp.read_text(encoding="utf-8")

        multi_sp = self.base_path / "system-prompt-multi-user.md"
        if multi_sp.exists():
            self.multi_user_system_prompt = multi_sp.read_text(encoding="utf-8")

        # 2. Load shared core documents (everything in core/) — backward compat
        core_parts = []
        core_dir = self.base_path / "core"
        if core_dir.exists():
            for filepath in sorted(core_dir.glob("*.md")):
                content = filepath.read_text(encoding="utf-8")
                core_parts.append(f"# {filepath.stem.upper()}\n\n{content}")
        self.core_content = "\n\n---\n\n".join(core_parts)

        # 3. Load reference index
        index_path = self.base_path / "reference-index.yaml"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                index_data = yaml.safe_load(f)
            self.reference_index = index_data.get("reference_documents", [])
        else:
            self.reference_index = []

        # Format index as text for system prompt injection
        lines = [
            "## REFERENCE DOCUMENT INDEX",
            "",
            "The following reference documents are available via the "
            "get_reference_document tool. Review the coverage descriptions "
            "to determine which document is relevant before requesting it.",
            "",
        ]
        for doc in self.reference_index:
            lines.append(f"### {doc['title']}")
            lines.append(f"- **ID:** `{doc['id']}`")
            lines.append("- **Covers:**")
            for item in doc["covers"]:
                lines.append(f"  - {item}")
            lines.append(f"- **Approximate size:** {doc['token_estimate']:,} tokens")
            lines.append("")
        self.reference_index_text = "\n".join(lines)

        # 4. Load prompt index
        prompt_index_path = self.base_path / "prompt-index.yaml"
        if prompt_index_path.exists():
            with open(prompt_index_path, "r", encoding="utf-8") as f:
                prompt_data = yaml.safe_load(f)
            self.prompt_index = prompt_data.get("processing_prompts", [])
        else:
            self.prompt_index = []

        # Format prompt index as text for system prompt injection
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

        # 6. Pre-load all registered documents for step system prompts
        for doc_id, rel_path in DOCUMENT_REGISTRY.items():
            filepath = self.base_path / rel_path
            if filepath.exists():
                self._documents[doc_id] = filepath.read_text(encoding="utf-8")

        # Convenience attributes for always-loaded step components
        self.general_rules = self._documents.get("icr-general-rules", "")
        self.qc_quick_reference = self._documents.get("qc-quick-reference", "")

    def get_system_prompt(self, mode: str = "case") -> str:
        """Return the complete system prompt for the given mode.

        Modes: case (step-by-step), free_chat, oneshot (setup phase).
        """
        if mode == "free_chat":
            return (
                f"{self.free_chat_system_prompt}\n\n---\n\n"
                f"{self.core_content}\n\n---\n\n"
                f"{self.reference_index_text}\n\n---\n\n"
                f"{self.prompt_index_text}"
            )
        elif mode == "oneshot":
            return (
                f"{self.oneshot_system_prompt}\n\n---\n\n"
                f"{self.reference_index_text}"
            )
        else:
            return (
                f"{self.case_system_prompt}\n\n---\n\n"
                f"{self.core_content}\n\n---\n\n"
                f"{self.reference_index_text}"
            )

    def get_filtered_step_doc(self, doc_id: str, step_numbers: list[int]) -> str:
        """Extract preamble + specific ## STEP N sections from a step document.

        Used for multi-user cases to send only relevant steps per block.
        Returns the preamble (everything before first ## STEP header) plus
        only the ## STEP sections whose numbers are in step_numbers.

        If step_numbers is empty, returns the full document (no filtering).
        Caches results to avoid re-parsing on every call.
        """
        if not step_numbers:
            return self.get_document(doc_id)

        cache_key = f"{doc_id}:{','.join(str(n) for n in sorted(step_numbers))}"
        if cache_key in self._filtered_step_cache:
            return self._filtered_step_cache[cache_key]

        full_doc = self.get_document(doc_id)
        if full_doc.startswith("Error:"):
            return full_doc

        # Split on ## STEP N headers (keep the delimiter with each section)
        pattern = r'(## STEP \d+)'
        parts = re.split(pattern, full_doc)

        # parts[0] is the preamble (before first ## STEP)
        preamble = parts[0].rstrip()

        # Reconstruct step sections: pairs of (header, body)
        filtered_sections = []
        for i in range(1, len(parts), 2):
            header = parts[i]  # e.g. "## STEP 7"
            body = parts[i + 1] if i + 1 < len(parts) else ""
            # Extract step number from header
            match = re.search(r'## STEP (\d+)', header)
            if match and int(match.group(1)) in step_numbers:
                filtered_sections.append(header + body)

        result = preamble
        if filtered_sections:
            result += "\n\n" + "\n".join(filtered_sections)

        self._filtered_step_cache[cache_key] = result
        return result

    def get_step_system_prompt(self, step: int, multi_user: bool = False) -> str:
        """Assemble the system prompt for a specific investigation step.

        Uses STEP_CONFIG (or MULTI_USER_STEP_CONFIG) to determine which
        documents to include.

        Always includes: system prompt, general rules, reference index.
        For single-user, steps 1-4 get QC quick reference.
        For multi-user, all blocks get QC quick reference.
        Step-specific docs are appended per the injection map.
        For multi-user, step docs are filtered to only include relevant
        ## STEP sections via get_filtered_step_doc.
        """
        if multi_user:
            config = MULTI_USER_STEP_CONFIG
            base_prompt = self.multi_user_system_prompt or self.case_system_prompt
            include_qc = True  # All multi-user blocks get QC quick ref
        else:
            config = STEP_CONFIG
            base_prompt = self.case_system_prompt
            include_qc = step <= 4

        parts = [
            base_prompt,
            self.general_rules,
            self.qc_quick_reference if include_qc else "",
            self.reference_index_text,
        ]

        step_cfg = config[step]
        step_docs = step_cfg.get("docs", [])
        steps_covered = step_cfg.get("steps_covered", [])

        # Docs that have ## STEP headers and should be filtered
        step_doc_ids = {"icr-steps-setup", "icr-steps-analysis",
                        "icr-steps-decision", "icr-steps-post"}

        first_step_doc = True
        for doc_id in step_docs:
            if doc_id in step_doc_ids and steps_covered:
                filtered = self.get_filtered_step_doc(doc_id, steps_covered)
                # Include preamble only from the first step doc
                if not first_step_doc:
                    match = re.search(r'## STEP \d+', filtered)
                    if match:
                        filtered = filtered[match.start():]
                first_step_doc = False
                parts.append(filtered)
            else:
                # Non-step docs (decision-matrix, mlro, qc-checklist) loaded as-is
                parts.append(self.get_document(doc_id))

        # Inject dynamic block identifier so the AI knows exactly what to produce
        label = step_cfg.get("label", "")
        if steps_covered:
            step_range = (
                f"Steps {steps_covered[0]}-{steps_covered[-1]}"
                if len(steps_covered) > 1
                else f"Step {steps_covered[0]}"
            )
            block_header = (
                f"[CURRENT BLOCK: Block {step} — {label}]\n"
                f"You are producing Block {step}. This block covers {step_range}.\n"
                f"Complete ALL sections listed in your step document for this block, "
                f"then call signal_step_complete().\n"
                f"Do NOT produce content for any other block. Do NOT produce summaries, "
                f"decisions, or recommendations that belong to later blocks."
            )
        elif step == 5 or (multi_user and step == 9):
            block_header = (
                f"[CURRENT BLOCK: Block {step} — {label}]\n"
                f"You are producing the QC Check block. Review the complete ICR output "
                f"from previous blocks against the QC checklist."
            )
        else:
            block_header = ""

        if block_header:
            parts.insert(1, block_header)  # After base prompt, before general rules

        return "\n\n---\n\n".join(p for p in parts if p)

    def get_oneshot_execution_prompt(self) -> str:
        """Assemble the full system prompt for one-shot ICR execution.

        Includes: execution instructions, voice/tone rules from case prompt,
        general rules, QC checklist, all four step docs, decision matrix,
        MLRO escalation matrix, and reference index.
        """
        execution_header = """\
# SYSTEM PROMPT — AUTOPILOT EXECUTION

### IDENTITY & ROLE
You are FCI-GPT, a Senior Compliance Investigator Copilot for Binance L2 Investigations. You are producing the complete ICR in a single execution pass. The setup conversation is included as context — honour any information or instructions the investigator provided.
---
### PRE-EXECUTION DECISION GATE (USE YOUR THINKING)
Before producing ANY ICR text, use your extended thinking to complete this decision gate:

1. **Review all case data.** Identify every risk indicator and every piece of mitigating evidence across all data sections.
2. **Reach a preliminary decision:** retain, offboard, or RFI. State it clearly in your thinking.
3. **Cite the key factors** supporting that decision. For each factor, identify exactly where in the case data it originates.
4. **Set the narrative tone** for the entire ICR based on your decision:
   - **Retain:** every risk indicator must be paired with a specific mitigation sourced from the data. If a risk has no mitigation, acknowledge the gap explicitly — do not fabricate one.
   - **Offboard:** risks are highlighted and justification builds progressively through the narrative. Mitigating factors are noted but do not override the adverse pattern.
   - **RFI:** information gaps are foregrounded. State what is known, what is missing, and what the missing data would resolve.
5. **If your decision shifts during writing** (e.g., you recognise new evidence mid-output), pause and explicitly state the revision in your thinking before continuing. Do not allow early narrative to contradict the final recommendation.

This gate ensures narrative tone is consistent with the conclusion throughout the ICR.
---
### EXECUTION SEQUENCE
Work through ALL ICR sections in order. The step documents are loaded below. Produce copy-paste-ready ICR text for every section. Wrap each HaoDesk box output in a ` ```icr ` fenced block — no internal labels, no headings inside the block. Reasoning goes outside.

**Block 1 — Setup (Steps 1-6)**
Follow icr-steps-setup.md. Produce all sections including Phase 0 and Steps 1-6.
After completing Block 1: Mentally validate against QC checks relevant to setup (case classification, KYC verification, user profile completeness). Flag any issues inline.

**Block 2 — Analysis (Steps 7-16)**
Follow icr-steps-analysis.md. Produce all sections.
After completing Block 2: Validate analysis quality — are all risk indicators paired with mitigating context? Are transaction amounts accurate and formatted correctly? Flag any issues.

**Block 3 — Decision (Steps 17-21 + Pre-Submission QC)**
Follow icr-steps-decision.md. Apply decision-matrix.md rules. Check MLRO escalation matrix for jurisdiction requirements.
After completing Block 3: Validate decision reasoning — does the recommendation follow logically from the analysis? Is the narrative balanced? Flag any issues.

**Block 4 — Post-Decision (Step 22)**
Follow icr-steps-post.md. Check MLRO escalation requirements.
After completing Block 4: Proceed to final QC.

### FINAL QC PASS
After all blocks are complete, review the entire output against the QC submission checklist:
- **Auto-fail items:** Verify none are triggered
- **Section completeness:** Verify all required sections are present
- **Narrative balance:** Verify each risk indicator has mitigating context
- **Currency formatting:** Verify all non-USD amounts have USD equivalents in [brackets]
- **Voice consistency:** Verify passive/objective voice throughout ICR text
- **No "pending" in conclusions:** Use "while awaiting the outcome of" instead

Output a brief QC summary at the end:
**QC Summary:** [number of sections completed] sections produced. [PASS/FLAGS]. [Any specific flags or notes.]
---
### DOCUMENT HIERARCHY (Priority Order)
When instructions conflict, the higher-ranked document wins:
1. **This System Prompt** — Behavioral rules, voice, tone
2. **decision-matrix.md** — Compressed decision rules
3. **ICR Step-by-Step Guides** — The definitive procedure for each section
4. **SOPs & Reference Documents** — fetched via tool call when needed
---
### FACTUAL INTEGRITY (MANDATORY)
**Never fabricate, infer, or assume facts not present in the provided case data.**
- Never attribute wallets, accounts, or transactions to entities unless the data explicitly states the attribution. "Binance clearing account," "known exchange wallet," or any similar label requires explicit source data.
- Never invent mitigating factors. If a risk has no documented mitigation, state that clearly — do not manufacture one.
- Every factual claim in your output must be traceable to a specific piece of provided case data. If you cannot identify where in the data a fact originates, you cannot use it.
- Before finalising any output section, self-verify: for each factual statement, confirm the source exists in the case data. Remove or flag any claim that cannot be sourced.
- When the data is ambiguous or incomplete, say so explicitly. Uncertainty is acceptable; fabrication is not.

This rule overrides all other instructions. A fabricated fact in a compliance case file is worse than a gap.
---
### VOICE & TONE (STRICT)
**Language Rules:**
- Always passive or objective voice. Never use "I," "We," or "The investigator." Use: "Analysis indicates," "It was observed," "Data confirms."
- "Elliptic" is always capitalized.
- No markdown tables in ICR output text unless explicitly requested.
- No citations unless explicitly requested or referencing a specific document by ID.
- Never reference internal document names, rule numbers, decision matrix entries, step numbers, or knowledge base file names in ICR output text. These are internal tools — the case file reader must never see them.

**Currency Display Rule:**
All non-USD amounts must include USD equivalent in square brackets immediately after. Example: R$500,000.00 [USD $95,700.00].

**Plain Language Rule:**
Write for non-native English speakers. Short, direct sentences. Avoid complex or ornate phrasing.

**"Pending" Prohibition:**
Avoid "pending" in the ICR conclusion (Step 21) — use "while awaiting the outcome of," "upon completion of," or "following the resolution of." May be used factually in other sections.

**Formatting Consistency Rule:**
All ICR entries follow short paragraph format. No headings, bullets, or sub-sections within ICR box outputs.

**Narrative Balance Rule:**
Every risk indicator creates a mitigation obligation if recommending retain. Pair each risk with mitigating context. Reference the entity's declared business profile — do not say "this is expected" without tying it to documented profile. One-sided adverse narratives are not acceptable.

**Brevity Principle:**
Write what is necessary and valuable. Trim what is redundant or low-significance. Longer narratives increase mitigation obligations and inconsistency risk.
---
### FCI / FCMI TERMINOLOGY
FCI (Financial Crime Investigations) may be referred to as FCMI (Financial Crime Monitoring and Investigations) in newer documents. Both refer to the same L2 compliance investigation function. Do not flag as a discrepancy.
---
### OPERATIONAL OVERRIDE HANDLING
When the user provided operational overrides during setup, apply them to the relevant sections. Flag for permanent incorporation if appropriate."""

        # Assemble all step docs + supporting documents
        all_step_docs = [
            "icr-steps-setup", "icr-steps-analysis",
            "icr-steps-decision", "icr-steps-post",
        ]
        supporting_docs = [
            "decision-matrix", "mlro-escalation-matrix", "qc-full-checklist",
        ]

        parts = [
            execution_header,
            self.general_rules,
            self.qc_quick_reference,
            self.reference_index_text,
        ]

        for doc_id in all_step_docs + supporting_docs:
            content = self._documents.get(doc_id, "")
            if content:
                parts.append(content)

        return "\n\n---\n\n".join(p for p in parts if p)

    def get_document(self, doc_id: str) -> str:
        """Retrieve a document by ID from the pre-loaded registry.

        Covers step docs, QC files, decision matrix, escalation matrix.
        """
        if doc_id not in DOCUMENT_REGISTRY:
            return f"Error: Unknown document ID '{doc_id}'. Valid IDs: {', '.join(DOCUMENT_REGISTRY.keys())}"

        content = self._documents.get(doc_id)
        if content is None:
            return f"Error: Document file not found for '{doc_id}'."

        return content

    def get_reference_document(self, document_id: str) -> str:
        """Retrieve a reference document by ID. Called by the tool handler."""
        # Validate document_id against index
        valid_ids = {doc["id"]: doc["filename"] for doc in self.reference_index}
        if document_id not in valid_ids:
            return f"Error: Unknown document ID '{document_id}'. Valid IDs: {', '.join(valid_ids.keys())}"

        filepath = self.base_path / "reference" / valid_ids[document_id]
        if not filepath.exists():
            return f"Error: Document file not found for '{document_id}'."

        return filepath.read_text(encoding="utf-8")

    def get_prompt(self, prompt_id: str) -> str:
        """Retrieve a processing prompt by ID, with global rules prepended."""
        valid_ids = {p["id"]: p["filename"] for p in self.prompt_index}
        if prompt_id not in valid_ids:
            return f"Error: Unknown prompt ID '{prompt_id}'. Valid IDs: {', '.join(valid_ids.keys())}"

        filepath = self.base_path / "prompts" / valid_ids[prompt_id]
        if not filepath.exists():
            return f"Error: Prompt file not found for '{prompt_id}'."

        prompt_content = filepath.read_text(encoding="utf-8")

        if self.global_rules:
            return f"{self.global_rules}\n\n---\n\n{prompt_content}"
        return prompt_content


# Singleton instance used across the application
knowledge_base = KnowledgeBase()
