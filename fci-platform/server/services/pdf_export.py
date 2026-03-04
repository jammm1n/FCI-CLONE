"""
FCI Platform — PDF Export Service

Generates PDF transcripts of conversations using fpdf2.
Images are read directly from disk (no browser/canvas issues).
Markdown in assistant messages is converted to HTML via the `markdown` library
and rendered with fpdf2's write_html().
"""

import io
import logging
from datetime import datetime, timezone
from pathlib import Path

import markdown
from fpdf import FPDF

logger = logging.getLogger(__name__)

# Brand colours
GOLD_R, GOLD_G, GOLD_B = 240, 185, 11  # #F0B90B
DARK_R, DARK_G, DARK_B = 30, 32, 36


class TranscriptPDF(FPDF):
    """Custom FPDF subclass with header/footer for FCI transcripts."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(DARK_R, DARK_G, DARK_B)
        self.cell(0, 7, "FCI Investigation Platform", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Case Transcript", new_x="LMARGIN", new_y="NEXT")
        # Gold accent line
        self.set_draw_color(GOLD_R, GOLD_G, GOLD_B)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y() + 2, self.w - self.r_margin, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, "CONFIDENTIAL - For authorized use only", align="L")
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="R", new_x="LMARGIN")


def _md_to_html(text: str) -> str:
    """Convert markdown text to simple HTML for fpdf2's write_html()."""
    html = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    # fpdf2 write_html doesn't support <p> well for spacing — replace with <br>
    html = html.replace("<p>", "").replace("</p>", "<br>")
    return html


def _sanitize_text(text: str) -> str:
    """Replace characters that fpdf2 can't encode in latin-1."""
    # Common Unicode substitutions before lossy encoding
    replacements = {
        "\u2014": "--",   # em dash
        "\u2013": "-",    # en dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
        "\u2022": "*",    # bullet
        "\u00a0": " ",    # non-breaking space
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_conversation_pdf(
    conversation: dict,
    case_doc: dict | None = None,
    images_dir: str = "./data/images",
) -> bytes:
    """
    Generate a PDF transcript from a conversation document.

    Args:
        conversation: MongoDB conversation document with messages array.
        case_doc: Optional case document for metadata (case mode only).
        images_dir: Base directory where images are stored.

    Returns:
        PDF file content as bytes.
    """
    pdf = TranscriptPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    mode = conversation.get("mode", "case")
    conv_id = conversation["_id"]

    # ---- Metadata table ----
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)

    meta_rows = []
    if case_doc:
        meta_rows.append(("Case ID", case_doc.get("case_id", "N/A")))
        meta_rows.append(("Type", case_doc.get("case_type", "N/A")))
        meta_rows.append(("Subject", case_doc.get("subject_user_id", "N/A")))
        meta_rows.append(("Status", case_doc.get("status", "N/A")))
    elif mode == "free_chat":
        title = conversation.get("title", "")
        if title:
            meta_rows.append(("Topic", title))

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    meta_rows.append(("Generated", now_str))

    if meta_rows:
        col_w = 35
        val_w = pdf.w - pdf.l_margin - pdf.r_margin - col_w
        for label, value in meta_rows:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(col_w, 5.5, _sanitize_text(label + ":"), new_x="RIGHT")
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(val_w, 5.5, _sanitize_text(str(value)), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # Gold separator after metadata
    pdf.set_draw_color(GOLD_R, GOLD_G, GOLD_B)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(4)

    # ---- Messages ----
    messages = conversation.get("messages", [])
    visible = [m for m in messages if m.get("visible", True)]

    if not visible:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 10, "No messages in this conversation.", new_x="LMARGIN", new_y="NEXT")
        buf = io.BytesIO()
        pdf.output(buf)
        return buf.getvalue()

    usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    for msg in visible:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        images = msg.get("images", [])
        tools_used = msg.get("tools_used", [])
        timestamp = msg.get("timestamp", "")

        # Format timestamp
        ts_str = ""
        if timestamp:
            if isinstance(timestamp, datetime):
                ts_str = timestamp.strftime("%H:%M")
            elif isinstance(timestamp, str):
                try:
                    ts_str = datetime.fromisoformat(timestamp).strftime("%H:%M")
                except (ValueError, TypeError):
                    ts_str = ""

        # Check if we need a page break (at least 20mm needed)
        if pdf.get_y() > pdf.h - 30:
            pdf.add_page()

        # Role label + timestamp
        if role == "user":
            label = "Investigator"
            bg_r, bg_g, bg_b = 255, 252, 235  # light yellow
            label_r, label_g, label_b = 120, 90, 0
        else:
            label = "AI Assistant"
            bg_r, bg_g, bg_b = 243, 244, 246  # light gray
            label_r, label_g, label_b = 60, 60, 80

        # Role header line
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(label_r, label_g, label_b)
        role_text = f"{label}  {ts_str}" if ts_str else label
        pdf.cell(0, 5, _sanitize_text(role_text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        # Message content background block
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        # -- Images (user messages) --
        if images and role == "user":
            for img_ref in images:
                stored_path = img_ref.get("stored_path", "")
                if not stored_path:
                    # Try to reconstruct path from image_id
                    image_id = img_ref.get("image_id", "")
                    if image_id:
                        img_dir = Path(images_dir) / conv_id
                        matches = list(img_dir.glob(f"{image_id}.*")) if img_dir.is_dir() else []
                        if matches:
                            stored_path = str(matches[0])

                if stored_path and Path(stored_path).is_file():
                    try:
                        img_w = min(60, usable_w - 10)  # max 60mm wide
                        pdf.image(stored_path, x=pdf.l_margin + 2, w=img_w)
                        pdf.ln(2)
                    except Exception as e:
                        logger.warning("Failed to embed image %s: %s", stored_path, e)
                        pdf.set_font("Helvetica", "I", 8)
                        pdf.set_text_color(180, 80, 80)
                        pdf.cell(0, 5, _sanitize_text(f"[Image could not be loaded: {Path(stored_path).name}]"),
                                 new_x="LMARGIN", new_y="NEXT")
                else:
                    pdf.set_font("Helvetica", "I", 8)
                    pdf.set_text_color(180, 80, 80)
                    img_name = img_ref.get("image_id", "unknown")
                    pdf.cell(0, 5, _sanitize_text(f"[Image not found on disk: {img_name}]"),
                             new_x="LMARGIN", new_y="NEXT")

        # -- Text content --
        if content and content.strip():
            if role == "assistant":
                # Render markdown as HTML
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(30, 30, 30)
                html_content = _md_to_html(content)
                html_content = _sanitize_text(html_content)
                try:
                    pdf.write_html(html_content)
                except Exception as e:
                    # Fallback to plain text if HTML rendering fails
                    logger.warning("write_html failed, falling back to plain text: %s", e)
                    pdf.multi_cell(0, 4.5, _sanitize_text(content))
                pdf.ln(2)
            else:
                # Plain text for user messages
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(0, 4.5, _sanitize_text(content))
                pdf.ln(1)

        # -- Tools used footer --
        if tools_used:
            tool_names = ", ".join(
                t.get("document_title") or t.get("tool", "unknown")
                for t in tools_used
            )
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(140, 140, 140)
            pdf.cell(0, 4, _sanitize_text(f"Referenced: {tool_names}"),
                     new_x="LMARGIN", new_y="NEXT")

        # Thin separator between messages
        pdf.ln(2)
        pdf.set_draw_color(220, 220, 220)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(3)

    # Output to bytes
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def build_pdf_filename(conversation: dict, case_doc: dict | None = None) -> str:
    """Build a descriptive filename for the PDF export."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if case_doc and case_doc.get("case_id"):
        return f"FCI-{case_doc['case_id']}-transcript-{date_str}.pdf"
    conv_id = conversation.get("_id", "unknown")
    short_id = conv_id[:8] if len(conv_id) >= 8 else conv_id
    return f"FCI-chat-{short_id}-{date_str}.pdf"
