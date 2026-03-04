"""
Knowledge base service — document loading, YAML index parsing, tool handler.

Implements the two-tier knowledge base architecture:
  Tier 1 (Core): Loaded into memory on startup, injected into every system prompt
  Tier 2 (Reference): Available on demand via get_reference_document tool call

See PRD Section 6.2 for the complete specification.
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

    def load_on_startup(self):
        """Load core documents and reference index into memory."""
        # Load all core documents
        core_parts = []
        core_dir = self.base_path / "core"
        if core_dir.exists():
            for filepath in sorted(core_dir.glob("*.md")):
                content = filepath.read_text(encoding="utf-8")
                core_parts.append(f"# {filepath.stem.upper()}\n\n{content}")
        self.core_content = "\n\n---\n\n".join(core_parts)

        # Load reference index
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

    def get_system_prompt(self) -> str:
        """Return the complete system prompt: core docs + reference index."""
        return f"{self.core_content}\n\n---\n\n{self.reference_index_text}"

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


# Singleton instance used across the application
knowledge_base = KnowledgeBase()
