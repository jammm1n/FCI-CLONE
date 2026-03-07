"""
Knowledge base service — document loading, YAML index parsing, tool handler.

Implements the two-tier knowledge base architecture:
  Tier 1 (Core): Loaded into memory on startup, injected into every system prompt
  Tier 2 (Reference): Available on demand via get_reference_document tool call

Additionally supports mode-aware system prompts (case vs free_chat) and
a processing prompt library accessible via get_prompt tool call.
"""

import yaml
from pathlib import Path

from server.config import settings


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
        self.global_rules: str = ""

    def load_on_startup(self):
        """Load system prompts, core documents, reference index, and prompt index."""
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
