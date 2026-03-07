"""
Knowledge base service — document loading, YAML index parsing, tool handler.

Implements the two-tier knowledge base architecture:
  Tier 1 (Core): Loaded into memory on startup, injected into every system prompt
  Tier 2 (Reference): Available on demand via get_reference_document tool call

Additionally supports mode-aware system prompts (case vs free_chat),
step-aware system prompts for investigation steps, and a processing
prompt library accessible via get_prompt tool call.
"""

import yaml
from pathlib import Path

from server.config import settings, STEP_CONFIG


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
        self.prompt_index: list[dict] = []
        self.prompt_index_text: str = ""
        self.global_rules: str = ""  # prompts/_global-rules.md (prepended to prompts)
        self.general_rules: str = ""  # core/icr-general-rules.md (step system prompt)
        self.qc_quick_reference: str = ""  # qc-quick-reference.md (steps 1-4)
        self._documents: dict[str, str] = {}  # doc_id → content

    def load_on_startup(self):
        """Load system prompts, core documents, reference index, and prompt index."""
        # 1. Load mode-specific system prompts (from KB root, NOT core/)
        case_sp = self.base_path / "system-prompt-case.md"
        if case_sp.exists():
            self.case_system_prompt = case_sp.read_text(encoding="utf-8")

        free_sp = self.base_path / "system-prompt-free-chat.md"
        if free_sp.exists():
            self.free_chat_system_prompt = free_sp.read_text(encoding="utf-8")

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

        Used by the existing (pre-step) architecture. Kept for backward
        compatibility until Phase C wires in step-based routing.
        """
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

    def get_step_system_prompt(self, step: int) -> str:
        """Assemble the system prompt for a specific investigation step.

        Uses STEP_CONFIG to determine which documents to include.
        Always includes: case system prompt, general rules, reference index.
        Steps 1-4 also get the QC quick reference.
        Step-specific docs are appended per the injection map.
        """
        parts = [
            self.case_system_prompt,
            self.general_rules,
            self.qc_quick_reference if step <= 4 else "",
            self.reference_index_text,
        ]

        step_docs = STEP_CONFIG[step].get("docs", [])
        for doc_id in step_docs:
            parts.append(self.get_document(doc_id))

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
