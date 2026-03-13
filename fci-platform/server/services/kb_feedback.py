"""
KB Feedback Service — Automated knowledge base issue detection.

Analyzes completed investigation transcripts using AI to identify
KB gaps, AI mistakes, and investigator corrections. Findings are
written to count-incrementing JSON issue log files, separated by
case type (oneshot, single-user stepped, multi-user stepped).
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from anthropic import AsyncAnthropic

from server.config import settings
from server.database import get_database

logger = logging.getLogger(__name__)

# ── Log File Paths ──────────────────────────────────────────────

FEEDBACK_DIR = Path("data/kb_feedback")
LOG_FILES = {
    "oneshot": FEEDBACK_DIR / "issues_oneshot.json",
    "single_user": FEEDBACK_DIR / "issues_single_user.json",
    "multi_user": FEEDBACK_DIR / "issues_multi_user.json",
}

CASE_TYPE_LABELS = {
    "oneshot": "Oneshot",
    "single_user": "Single-User Stepped",
    "multi_user": "Multi-User Stepped",
}

# ── Prompt Loading ──────────────────────────────────────────────

_prompt_cache: str | None = None


def _load_prompt() -> str:
    global _prompt_cache
    if _prompt_cache is None:
        prompt_path = Path(settings.KNOWLEDGE_BASE_PATH) / "prompts" / "prompt-kb-feedback.md"
        _prompt_cache = prompt_path.read_text(encoding="utf-8")
    return _prompt_cache


# ── API Client ──────────────────────────────────────────────────

_client = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        kwargs = {"api_key": settings.ANTHROPIC_API_KEY}
        if settings.ANTHROPIC_BASE_URL:
            kwargs["base_url"] = settings.ANTHROPIC_BASE_URL
        _client = AsyncAnthropic(**kwargs)
    return _client


# ── Helpers ─────────────────────────────────────────────────────


def _determine_case_type(conversation: dict) -> str:
    mode = conversation.get("mode", "case")
    if mode == "oneshot":
        return "oneshot"
    case_mode = conversation.get("case_mode")
    if case_mode == "multi":
        return "multi_user"
    return "single_user"


def _load_existing_issues(case_type: str) -> dict:
    log_path = LOG_FILES[case_type]
    if log_path.exists():
        return json.loads(log_path.read_text(encoding="utf-8"))
    return {
        "last_updated": None,
        "total_submissions": 0,
        "issues": [],
    }


def _save_issues(case_type: str, data: dict) -> None:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_FILES[case_type]
    log_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _build_transcript(messages: list) -> str:
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        if role in ("system_injected", "tool_exchange"):
            continue
        if not msg.get("visible", True):
            continue
        if role == "step_divider":
            lines.append(f"\n--- {msg.get('content', 'Step divider')} ---\n")
            continue
        label = "INVESTIGATOR" if role == "user" else "AI ASSISTANT"
        content = msg.get("content", "")
        step = msg.get("step")
        step_prefix = f" [Step {step}]" if step else ""
        lines.append(f"[{label}{step_prefix}]: {content}")
    return "\n\n".join(lines)


async def _clear_submitted_flag(db, conversation_id: str) -> None:
    """Clear kb_feedback_submitted so the user can retry after a failure."""
    await db.conversations.update_one(
        {"_id": conversation_id},
        {"$unset": {"kb_feedback_submitted": ""}},
    )
    logger.info("KB feedback: cleared submitted flag for %s (will allow retry)", conversation_id)


# ── Core Analysis ───────────────────────────────────────────────


async def analyze_conversation(conversation_id: str) -> dict:
    """
    Run KB feedback analysis on a conversation.

    Called as a background task — no return value needed by the caller,
    but returns a status dict for logging/testing.
    """
    db = get_database()
    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        logger.error("KB feedback: conversation not found: %s", conversation_id)
        return {"status": "error", "reason": "not_found"}

    case_type = _determine_case_type(conversation)
    messages = conversation.get("messages", [])
    transcript = _build_transcript(messages)

    if not transcript.strip():
        logger.warning("KB feedback: empty transcript for %s", conversation_id)
        return {"status": "skipped", "reason": "empty_transcript"}

    existing = _load_existing_issues(case_type)
    prompt_text = _load_prompt()

    user_content = (
        f"[CASE_TYPE]: {case_type}\n\n"
        f"[EXISTING_ISSUES]:\n{json.dumps(existing, indent=2)}\n\n"
        f"[TRANSCRIPT]:\n{transcript}"
    )

    client = _get_client()
    try:
        response = await client.messages.create(
            model=settings.KB_FEEDBACK_MODEL,
            max_tokens=8192,
            system=prompt_text,
            messages=[{"role": "user", "content": user_content}],
        )

        ai_text = response.content[0].text

        # Strip markdown code fences if present
        json_text = ai_text.strip()
        if json_text.startswith("```"):
            lines = json_text.split("\n")
            json_text = "\n".join(lines[1:-1])

        updated_issues = json.loads(json_text)
        _save_issues(case_type, updated_issues)

        logger.info(
            "KB feedback complete for %s (%s): %d issues, %d input / %d output tokens",
            conversation_id,
            case_type,
            len(updated_issues.get("issues", [])),
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
        return {"status": "complete", "issues_count": len(updated_issues.get("issues", []))}

    except json.JSONDecodeError as e:
        logger.exception("KB feedback: failed to parse JSON response for %s", conversation_id)
        await _clear_submitted_flag(db, conversation_id)
        return {"status": "error", "reason": f"JSON parse error: {e}"}
    except Exception as e:
        logger.exception("KB feedback: analysis failed for %s", conversation_id)
        await _clear_submitted_flag(db, conversation_id)
        return {"status": "error", "reason": str(e)}


# ── Markdown Report ─────────────────────────────────────────────

CATEGORY_LABELS = {
    "kb_gap": "KB Gap",
    "ai_mistake": "AI Mistake",
    "investigator_correction": "Investigator Correction",
    "prompt_issue": "Prompt Issue",
    "tool_misuse": "Tool Misuse",
    "friction": "Friction",
}


def generate_markdown_report() -> str:
    """Generate a combined markdown report from all three issue log files."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        f"# KB Feedback Report",
        f"Generated: {now}\n",
    ]

    for case_type, label in CASE_TYPE_LABELS.items():
        parts.append(f"---\n\n## {label}\n")
        data = _load_existing_issues(case_type)

        if not data.get("issues"):
            parts.append("No submissions yet.\n")
            continue

        parts.append(f"**Total submissions:** {data.get('total_submissions', 0)}\n")

        # Sort by count descending
        issues = sorted(data["issues"], key=lambda i: i.get("count", 0), reverse=True)

        for issue in issues:
            category = CATEGORY_LABELS.get(issue.get("category", ""), issue.get("category", ""))
            steps = issue.get("steps_affected", [])
            steps_str = ", ".join(str(s) for s in steps) if steps else "N/A"
            kb_files = issue.get("kb_files_affected", [])
            kb_str = ", ".join(kb_files) if kb_files else "N/A"
            first = issue.get("first_seen", "")[:10]
            last = issue.get("last_seen", "")[:10]

            parts.append(
                f"### [{category}] {issue.get('summary', 'No summary')}  "
                f"(x{issue.get('count', 1)})\n"
            )
            parts.append(f"{issue.get('detail', '')}\n")
            parts.append(
                f"- **Steps:** {steps_str}  |  **KB files:** {kb_str}\n"
                f"- **First seen:** {first}  |  **Last seen:** {last}\n"
            )
            quote = issue.get("example_quote")
            if quote:
                parts.append(f'- **Example:** "{quote}"\n')
            parts.append("")

    return "\n".join(parts)
