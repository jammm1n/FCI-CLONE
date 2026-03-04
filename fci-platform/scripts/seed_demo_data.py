"""
Seed script for FCI Investigation Platform demo data.

Populates MongoDB with:
- 2 mock user accounts
- 5 pre-staged sanitised case records with preprocessed data
  (3 inline cases + 2 LE cases parsed from demo-1.md / demo-2.md)

Usage: python scripts/seed_demo_data.py

Requires: MongoDB running on localhost:27017
"""

import re
from pathlib import Path

from pymongo import MongoClient
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "fci_platform"

# ---------------------------------------------------------------------------
# Markdown case-package parser
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEMO_1_PATH = REPO_ROOT / "demo-1.md"
DEMO_2_PATH = REPO_ROOT / "demo-2.md"

SECTION_KEY_MAP = {
    1: "l1_referral_narrative",
    2: "hexa_dump",
    3: "kyc_id_document",
    4: "c360_transaction_summary",
    5: "web_app_outputs",
    6: "elliptic_screening",
    7: "prior_icr_summary",
    8: "le_kodex_extraction",
    9: "rfi_user_communication",
    10: "case_intake_extraction",
    11: "osint_results",
    12: "investigator_notes",
}

SKIP_CONTENT = {"attached", "none", "n/a", "no trace", "no data"}

# Lines that are template instructions (not real case data)
TEMPLATE_LINES = {
    "Manual review required.",
    "Manual summary required.",
    "Provide summary of previous outcomes.",
    "Click the refresh button in this section if RFIs are issued.",
    "Analysis of User Communication Relating to This Case.",
    "No standalone",
}

# Prefixes of template instruction lines (matched with startswith)
TEMPLATE_PREFIXES = [
    "Ensure transactional analysis provided",
    "Ensure analysis performed manually",
    "Manual review required. If no OSINT",
    "If none is identified in",
    "If large exposure, more analysis needed",
    "Please provide time frame that suspicious",
    "Manual input of 3-4 sentences",
    "RFI Case ID (if available): (Unique",
    "Date Sent: (Date the RFI",
    "Expiry Date: (Deadline for",
    "Type of RFI Sent: (e.g.",
    "What specific risk is this RFI intended",
    "What is the suggested outcome",
    "What is the minimum acceptable response",
    "Is escalation to the MLRO",
    "Additional notes or context: (Optional",
]

# Hexa UI elements (navigation / form chrome, not data)
HEXA_UI_LINES = {
    "Away", "Parent", "L1 Referral", "L2 Handler", "L2 FIAT TM",
    "Investigate", "Summary", "User Investigation", "Documents",
    "Internal Investigation Summary:", "Recommend for external reporting?:",
    "Remark:", "Case Folder Link:", "No", "Yes",
    "1 users need to be investigated",
    "Subject Matter", "Subject Matter Sub-Category",
}

# Chatbot/tool preamble patterns to strip from the start of sections
PREAMBLE_PATTERNS = [
    re.compile(r"^Thank you.*?Let me reprocess.*?\n+---\n*", re.DOTALL),
    re.compile(r"^\*\*Mode 2 —.*?detected\.?\*\*.*?\n*", re.MULTILINE),
    re.compile(r"^\*\*PROMPT #\d+.*?EXECUTION.*?\*\*\n+", re.MULTILINE),
]

# Bare-text headings in the demo case narratives that should become ### headings
KNOWN_HEADINGS = {
    # L1 referral narrative headings
    "Los Halcones del Valle Overview",
    "Los Lobos del Pacífico Overview",
    "Investigation Background",
    "Counterparty Risk Analysis",
    "Conclusion and Recommendation",
    # HEXA analysis sub-headings
    "Prior ICR",
    "LE enquiry review",
    "User transaction overview",
    "CTM Alerts",
    "FIAT transactions",
    "Device and IP analysis.",
    "OSINT",
    "User communication",
    "Any other unusual activity",
    "RFI Issued as part of this investigation",
    "RFI Analysis Summary",
    "Summary of the Unusual transactions",
    "Internal counterparty analysis",
    "Lifetime Top 10 Exposed Address",
    "Lifetime Top Addresses by Value",
    "Privacy coin review",
    "Summary of L1 analysis",
    # UID headings
    "UID 8830467521",
    "UID 8871439206",
}


def _clean_content(content: str, section_key: str) -> str:
    """Clean raw tool-dump content for demo presentation."""

    # --- Section-specific pre-processing --------------------------------

    if section_key == "hexa_dump":
        # HEXA repeats the L1 referral narrative.  Unique content starts at
        # the "II-" roman-numeral heading (account / KYC presentation).
        for marker in ("II- PRESENTATION", "II-1 PEOPLE"):
            idx = content.find(marker)
            if idx > 0:
                content = content[idx:]
                break

    if section_key == "l1_referral_narrative":
        # Convert the form-field dump header into a clean table, then keep
        # the narrative body starting at "Referral Summary:".
        content = _reformat_l1_header(content)
        # Trim HEXA content that sometimes leaks into the L1 section
        for trim_marker in ("II- PRESENTATION", "II-1 PEOPLE"):
            idx = content.find(trim_marker)
            if idx > 200:  # Only trim if we have real content before it
                content = content[:idx].rstrip()
                break

    if section_key == "web_app_outputs":
        # Remove TASK 1 (internal HEXA correction instructions) entirely
        t1_start = content.find("## TASK 1: HEXA CORRECTIONS")
        t2_start = content.find("## TASK 2:")
        if t1_start >= 0 and t2_start > t1_start:
            content = content[:t1_start] + content[t2_start:]
        # Rename TASK headers to readable titles
        content = content.replace("## TASK 2: RISK FLAG TABLE", "## Counterparty Risk Flags")
        content = content.replace("## TASK 3: CLEAN COUNTERPARTY SUMMARY", "## Clean Counterparties")
        content = content.replace("## TASK 4: P2P TOTALS", "## P2P Summary")

    # Strip chatbot / tool preamble from the start of sections
    for pat in PREAMBLE_PATTERNS:
        content = pat.sub("", content, count=1)

    # Strip COMPLETENESS CHECK blocks wherever they appear
    content = re.sub(
        r"^\*\*COMPLETENESS CHECK:?\*\*.*?(?=\n---|\n##|\n\n###|\Z)",
        "", content, flags=re.DOTALL | re.MULTILINE,
    )
    content = re.sub(
        r"^\*\*ADDRESS INTEGRITY CHECK:?\*\*.*?\n*",
        "", content, flags=re.MULTILINE,
    )

    # --- Line-level cleanup ---------------------------------------------

    lines = content.split("\n")
    cleaned: list[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Tool attribution
        if stripped.startswith("--- Answer from SAFUGPT:"):
            i += 1
            continue
        # Empty text-field counters from Hexa UI
        if stripped == "0/10000":
            i += 1
            continue
        # Concatenated UI labels
        if "Pre-checkInitial Investigation" in stripped:
            i += 1
            continue
        # "No data" standalone
        if stripped.lower() == "no data":
            i += 1
            continue
        # Template instruction lines
        if stripped in TEMPLATE_LINES:
            i += 1
            continue
        if any(stripped.startswith(p) for p in TEMPLATE_PREFIXES):
            i += 1
            continue
        # Hexa UI chrome
        if stripped in HEXA_UI_LINES:
            i += 1
            continue
        # Tool / chatbot preamble lines
        if "Standalone Data Processing detected" in stripped:
            i += 1
            continue
        if "Mode 2 detected" in stripped:
            i += 1
            continue
        if stripped.startswith("**PROMPT #") and "EXECUTION" in stripped:
            i += 1
            continue
        # Tool execution labels (e.g. "Processing prior ICR data using Prompt #4...")
        if re.match(r"^Processing .+ using Prompt #\d", stripped):
            i += 1
            continue
        # Bare URLs on their own line
        if re.match(r"^https?://\S+$", stripped):
            i += 1
            continue
        # Empty form fields  (label ending with : and value is empty/next
        # line is also a label or blank)
        if stripped.endswith(":") and len(stripped) < 60:
            next_s = lines[i + 1].strip() if i + 1 < len(lines) else ""
            # If the next line is blank, another label, or very short → skip
            if not next_s or next_s.endswith(":") or next_s in HEXA_UI_LINES:
                i += 1
                continue
            # If the next line is a short value (< 60 chars) and the line
            # after THAT is also a label → this is form metadata, convert
            # to a bold label-value pair
            if len(next_s) < 60:
                after = lines[i + 2].strip() if i + 2 < len(lines) else ""
                if after.endswith(":") or after in HEXA_UI_LINES or not after:
                    label = stripped[:-1]
                    cleaned.append(f"**{label}:** {next_s}  ")
                    i += 2
                    continue

        # Convert === HEADING === to ## HEADING
        m = re.match(r"^={3,}\s*(.+?)\s*={3,}$", stripped)
        if m:
            cleaned.append(f"## {m.group(1)}")
            i += 1
            continue

        # Promote known bare-text headings to ### markdown headings
        if stripped in KNOWN_HEADINGS:
            cleaned.append(f"### {stripped}")
            i += 1
            continue
        # Also promote roman-numeral headings (II-1, III-2, IV-, etc.)
        if re.match(r"^[IVX]+-\d*\s+[A-Z ]", stripped):
            cleaned.append(f"### {stripped}")
            i += 1
            continue

        cleaned.append(line)
        i += 1

    result = "\n".join(cleaned)

    # Convert runs of 3+ consecutive "Key: Value" lines into tables
    result = _convert_kv_runs_to_tables(result)

    # Collapse excessive blank lines
    result = re.sub(r"\n{4,}", "\n\n\n", result)

    return result.strip()


# Pattern for detecting "Label: value" lines (label 3-50 chars, then value)
_KV_LINE = re.compile(r"^(.{3,50}):\s+(.+)$")


def _convert_kv_runs_to_tables(content: str) -> str:
    """Convert runs of 3+ consecutive 'Key: Value' lines into markdown tables."""
    lines = content.split("\n")
    result: list[str] = []
    kv_run: list[tuple[str, str]] = []

    def flush_kv(run: list[tuple[str, str]]) -> None:
        if len(run) >= 3:
            result.append("")
            result.append("| Field | Value |")
            result.append("|-------|-------|")
            for k, v in run:
                result.append(f"| {k} | {v} |")
            result.append("")
        else:
            # Too few for a table — output as bold label: value
            for k, v in run:
                result.append(f"**{k}:** {v}  ")

    for line in lines:
        stripped = line.strip()
        m = _KV_LINE.match(stripped)
        # Only match if it doesn't look like markdown / heading / narrative
        if (
            m
            and not stripped.startswith(("#", "|", "-", "*", ">"))
            and "." not in m.group(1)  # Labels don't contain periods
        ):
            kv_run.append((m.group(1).strip(), m.group(2).strip()))
        else:
            if kv_run:
                flush_kv(kv_run)
                kv_run = []
            result.append(line)

    if kv_run:
        flush_kv(kv_run)

    return "\n".join(result)


def _reformat_l1_header(content: str) -> str:
    """Convert the L1 referral form-field dump into a clean table + narrative."""

    # Find where the narrative body starts
    marker_idx = -1
    for marker in ("Referral Summary:\n", "Referral Summary\n"):
        marker_idx = content.find(marker)
        if marker_idx >= 0:
            break
    if marker_idx < 0:
        return content  # Can't find boundary — return as-is

    header_text = content[:marker_idx]
    narrative_start = content.index("\n", marker_idx) + 1
    narrative = content[narrative_start:]

    # Extract key fields from the header
    fields: list[tuple[str, str]] = []

    # ICR reference
    m = re.search(r"(ICRV\d+-\d+)", header_text)
    if m:
        fields.append(("ICR Reference", m.group(1)))

    # Field:value pairs (label on one line, value on next)
    field_names = [
        ("Subject Matter", "Subject Matter"),
        ("Subject Matter Sub-Category", "Sub-Category"),
        ("Referral", "Referral"),
        ("Referral Date", "Referral Date"),
        ("Referral Team", "Referral Team"),
        ("ADGM Reason", "ADGM Reason"),
        ("Related Parent ICR ID", "Parent ICR"),
    ]
    for raw_label, display_label in field_names:
        pattern = re.compile(
            rf"^{re.escape(raw_label)}:\s*$\n(.+)", re.MULTILINE
        )
        m = pattern.search(header_text)
        if m:
            val = m.group(1).strip()
            if val and val.lower() not in HEXA_UI_LINES and len(val) < 200:
                fields.append((display_label, val))

    # Build clean output
    parts: list[str] = []
    if fields:
        parts.append("| Field | Value |")
        parts.append("|-------|-------|")
        for label, value in fields:
            parts.append(f"| **{label}** | {value} |")
        parts.append("")

    parts.append("### Referral Summary\n")
    parts.append(narrative)

    return "\n".join(parts)


def parse_case_markdown(filepath: Path) -> dict:
    """Parse a case-package markdown file into a preprocessed_data dict.

    Splits on ``## N. SECTION TITLE`` headers and maps each numbered section
    to the corresponding schema key.  Sections with placeholder content
    (e.g. "attached", "none") are omitted.  Content is cleaned for demo
    presentation.
    """
    if not filepath.exists():
        print(f"  Warning: {filepath} not found — skipping")
        return {}

    text = filepath.read_text(encoding="utf-8")

    # Locate every section header: ## 1. … , ## 2. … , etc.
    header_pattern = re.compile(r"^## (\d{1,2})\.\s+", re.MULTILINE)
    headers = list(header_pattern.finditer(text))

    result: dict[str, str] = {}
    for idx, match in enumerate(headers):
        section_num = int(match.group(1))
        key = SECTION_KEY_MAP.get(section_num)
        if key is None:
            continue

        # Content: from end of header line to start of next header (or EOF)
        header_line_end = text.index("\n", match.start()) + 1
        content_end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        content = text[header_line_end:content_end]

        # Strip trailing --- dividers and whitespace
        content = re.sub(r"\n---\s*$", "", content).strip()

        # Skip empty / placeholder content
        if content.lower() in SKIP_CONTENT:
            continue
        if len(content) < 100:
            continue
        # Skip template-only sections (e.g. "[Paste #14E output …]")
        if "[Paste " in content and len(content) < 500:
            continue

        # Clean content for demo presentation
        content = _clean_content(content, key)

        result[key] = content

    return result


# =============================================================================
# Users
# =============================================================================

USERS = [
    {
        "_id": "user_001",
        "username": "ben.investigator",
        "display_name": "Ben",
        "created_at": datetime(2026, 1, 15, tzinfo=timezone.utc),
    },
    {
        "_id": "user_002",
        "username": "demo.investigator",
        "display_name": "Demo User",
        "created_at": datetime(2026, 2, 1, tzinfo=timezone.utc),
    },
]


# =============================================================================
# Case 1: Scam — Romance Scam
# =============================================================================

CASE_1 = {
    "_id": "CASE-2026-0451",
    "case_type": "scam",
    "status": "open",
    "subject_user_id": "BIN-84729103",
    "summary": "Suspected romance scam — multiple outbound transfers to flagged counterparties over 8-week period",
    "assigned_to": "user_001",
    "conversation_id": None,
    "preprocessed_data": {
        "c360_transaction_summary": """## Counterparty Risk Summary

### Overview
Subject BIN-84729103 has interacted with **5 distinct external counterparties** over the period 2026-01-05 to 2026-02-28. Of these, **3 are flagged** as high-risk or scam-associated.

### Flagged Counterparties

| # | Wallet Address | Risk Level | Category | Total Value (USD) | Tx Count | Date Range |
|---|---------------|------------|----------|-------------------|----------|------------|
| 1 | 0x3f2a8b91c4...e8a2c | **High** | Known romance scam cluster | $18,500 | 6 | Jan 12 – Feb 15 |
| 2 | 0x91b7d4f02e...4d8f1 | **Medium** | Scam-associated (indirect) | $7,200 | 3 | Jan 28 – Feb 22 |
| 3 | 0xc4e91a023f...7b3e9 | **High** | Money mule network | $12,800 | 4 | Feb 5 – Feb 28 |

### Unflagged Counterparties

| # | Wallet Address | Category | Total Value (USD) | Tx Count |
|---|---------------|----------|-------------------|----------|
| 4 | 0x2d8f7e610a...9c1b3 | Binance user (internal transfer) | $3,200 | 2 |
| 5 | 0x7a19b4c83d...2e7f0 | Unknown (no risk flags) | $1,500 | 1 |

### Transaction Pattern Summary
- **Total outbound to flagged counterparties:** $38,500 across 13 transactions
- **Average transaction size:** $2,962
- **Pattern:** Gradual escalation — first transaction was $1,200, most recent was $5,500
- **Temporal pattern:** Transactions cluster around weekends, with 2-3 day gaps between clusters
- **Direction:** All outbound (subject sending) — no inbound from flagged counterparties

### Device & IP Analysis
- All transactions initiated from a single mobile device (iPhone, consistent with KYC)
- IP address: residential ISP, consistent with declared country (United Kingdom)
- No VPN or proxy usage detected
- No device sharing with other Binance accounts""",

        "elliptic_screening": """## Wallet Screening Results

### Wallet 1: 0x3f2a8b91c4...e8a2c
- **Elliptic Risk Score:** 9.2 / 10 (Critical)
- **Entity:** Part of identified romance scam cluster (Cluster ID: CL-EU-4891)
- **Exposure:** Direct — wallet is a known collection point for romance scam proceeds
- **First flagged:** 2025-11-20
- **Known victims:** 14 reported victims across 3 jurisdictions
- **Total cluster volume:** $2.4M (estimated)
- **Blockchain:** Ethereum (ERC-20 USDT)

### Wallet 2: 0x91b7d4f02e...4d8f1
- **Elliptic Risk Score:** 6.8 / 10 (Medium-High)
- **Entity:** Indirectly associated with scam operations — 2 hops from Wallet 1 cluster
- **Exposure:** Indirect — wallet received funds from known scam wallets and redistributed
- **First flagged:** 2026-01-05
- **Blockchain:** Ethereum (ERC-20 USDT)
- **Note:** This wallet also interacts with legitimate DeFi protocols, which may indicate a mixing pattern

### Wallet 3: 0xc4e91a023f...7b3e9
- **Elliptic Risk Score:** 8.5 / 10 (High)
- **Entity:** Identified money mule network (Network ID: MN-UK-0234)
- **Exposure:** Direct — wallet is part of a known mule network recruiting via social media
- **First flagged:** 2025-09-15
- **Total network volume:** $890K (estimated)
- **Blockchain:** Ethereum (ERC-20 USDT)
- **Note:** 3 other Binance users have been actioned for interactions with this network""",

        "prior_icr_summary": """## Prior Investigations

### Case CASE-2025-3891 (Closed — October 2025)
- **Type:** FTM alert — unusual fiat deposit pattern
- **Outcome:** No adverse finding
- **Summary:** Subject made 4 deposits of £2,500 each within 3 days from the same bank account. Investigation found this was salary payments from a legitimate employer who paid weekly. Case closed with no action.
- **Investigator notes:** Subject was cooperative and provided payslips to support explanation. No further monitoring recommended.

### No other prior cases found for BIN-84729103.""",

        "l1_referral_narrative": """## L1 Customer Service Interactions

### Interaction 1 — 2026-02-10 (Chat)
**Subject initiated contact** regarding a withdrawal delay.

Key excerpts:
- Subject: "My friend needs the money urgently for a medical emergency. Why is the withdrawal taking so long?"
- Agent: Asked for details about the recipient.
- Subject: "She's my girlfriend. We've been dating for 6 months. She lives in Ghana and needs surgery."
- Agent: Advised subject about common romance scam patterns.
- Subject: "No, this is real. I've video called her. Please just process my withdrawal."
- Agent: Escalated to compliance.

### Interaction 2 — 2026-02-18 (Chat)
**Subject initiated contact** to complain about account monitoring notification.

Key excerpts:
- Subject: "I received a message saying my account is under review. I haven't done anything wrong."
- Agent: Explained that periodic reviews are routine.
- Subject: "I just need to send money to my partner. We're planning to meet in person soon."
- Agent: Asked if the subject has met the partner in person before.
- Subject: "Not yet, but we've been talking every day for months. She sent me her passport to prove who she is."
- Subject mentioned sending small amounts at first "to test the process" before sending larger amounts.

### Red Flags Identified by L1:
- Subject has never met the recipient in person
- Recipient is in a different country (Ghana)
- Gradual escalation of transaction amounts
- "Medical emergency" urgency narrative
- Subject defensive when asked about the nature of the relationship""",

        "kyc_id_document": """## KYC Information

| Field | Value |
|-------|-------|
| **Full Name** | James R. Mitchell |
| **Date of Birth** | 1978-04-15 |
| **Country of Residence** | United Kingdom |
| **Nationality** | British |
| **Verification Level** | Level 2 (Full) |
| **ID Document** | UK Passport (verified) |
| **ID Expiry** | 2029-08-20 |
| **Proof of Address** | Council tax bill (verified, dated 2025-11) |
| **Account Created** | 2024-06-10 |
| **Account Age** | ~20 months |
| **Occupation (declared)** | Warehouse operations manager |
| **Source of Funds (declared)** | Employment salary |

### Verification Notes
- KYC completed 2024-06-10, no re-verification required
- Selfie match: confirmed
- No document anomalies flagged
- Address is a residential property in Manchester, UK""",
    },
    "created_at": datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc),
}


# =============================================================================
# Case 2: CTM — On-Chain Alerts (Sanctions Exposure)
# =============================================================================

CASE_2 = {
    "_id": "CASE-2026-0387",
    "case_type": "ctm",
    "status": "open",
    "subject_user_id": "BIN-56201847",
    "summary": "On-chain alerts — interactions with sanctioned wallet cluster and high-risk darknet-associated entities",
    "assigned_to": "user_001",
    "conversation_id": None,
    "preprocessed_data": {
        "c360_transaction_summary": """## On-Chain Alert Details

### Alert Trigger
- **Alert ID:** CTM-A-2026-8847
- **Rule:** OFAC sanctions screening — indirect exposure (2 hops)
- **Triggered:** 2026-02-20
- **Blockchain:** Ethereum

### Transaction Summary
Subject BIN-56201847 account shows the following on-chain activity over the review period (2025-12-01 to 2026-02-28):

| Metric | Value |
|--------|-------|
| Total inbound transactions | 47 |
| Total outbound transactions | 39 |
| Total inbound value | $312,500 |
| Total outbound value | $298,700 |
| Unique counterparties (inbound) | 12 |
| Unique counterparties (outbound) | 8 |
| Flagged counterparties | 3 |

### Flagged Transactions

| Date | Direction | Counterparty | Value (USD) | Risk Flag |
|------|-----------|-------------|-------------|-----------|
| 2026-01-15 | Outbound | 0xd4a7e82f19...3c6b1 | $15,000 | Sanctioned entity (2 hops) |
| 2026-01-22 | Outbound | 0xd4a7e82f19...3c6b1 | $22,000 | Sanctioned entity (2 hops) |
| 2026-02-03 | Inbound | 0xf8b12c940d...e5a72 | $8,500 | Darknet marketplace-associated |
| 2026-02-10 | Outbound | 0xd4a7e82f19...3c6b1 | $18,000 | Sanctioned entity (2 hops) |
| 2026-02-14 | Inbound | 0xf8b12c940d...e5a72 | $11,200 | Darknet marketplace-associated |
| 2026-02-19 | Outbound | 0x5e3c9a71b8...f2d04 | $45,000 | High-risk mixer service |

### Transaction Pattern Analysis
- **Holding period:** Average 3-5 days between inbound and outbound for flagged transactions
- **Conversion activity:** Subject converts between ETH and USDT frequently — 23 swap transactions in the period
- **Withdrawal pattern:** Large outbound transactions ($15K-$45K) to flagged entities; smaller transactions ($1K-$5K) to unflagged wallets
- **Structuring indicators:** No obvious structuring — transaction sizes vary and don't cluster below thresholds
- **Time-of-day pattern:** Most transactions executed between 14:00-18:00 UTC""",

        "elliptic_screening": """## Wallet Screening Results

### Wallet 1: 0xd4a7e82f19...3c6b1
- **Elliptic Risk Score:** 9.8 / 10 (Critical)
- **Entity:** 2 hops from OFAC-sanctioned entity "Garantex" (sanctioned April 2022)
- **Exposure type:** Indirect — wallet received funds from an intermediary that received from Garantex
- **Hop path:** Subject → 0xd4a7... → 0x891f... (intermediary) → Garantex hot wallet
- **Total subject exposure:** $55,000 across 3 transactions
- **Assessment:** The intermediary wallet (0x891f...) is a known facilitator that has processed $4.2M from Garantex addresses. This is not a false positive from exchange hot wallet exposure.
- **Blockchain:** Ethereum

### Wallet 2: 0xf8b12c940d...e5a72
- **Elliptic Risk Score:** 8.1 / 10 (High)
- **Entity:** Associated with Hydra Market successor operations
- **Exposure type:** Direct — wallet is part of a cluster linked to darknet marketplace vendor operations
- **Total subject exposure:** $19,700 across 2 inbound transactions
- **Assessment:** Subject RECEIVED funds from this wallet, suggesting subject may be providing goods/services or acting as a cash-out point
- **Blockchain:** Ethereum

### Wallet 3: 0x5e3c9a71b8...f2d04
- **Elliptic Risk Score:** 7.5 / 10 (High)
- **Entity:** Known mixer/tumbler service ("ChipMixer successor")
- **Exposure type:** Direct — subject sent funds directly to mixer input address
- **Total subject exposure:** $45,000 in a single transaction
- **Assessment:** Use of mixing service immediately after receiving high-risk funds strongly suggests intentional obfuscation
- **Blockchain:** Ethereum""",

        "kyc_id_document": """## KYC Information

| Field | Value |
|-------|-------|
| **Full Name** | Dmitri K. Volkov |
| **Date of Birth** | 1992-11-03 |
| **Country of Residence** | Estonia |
| **Nationality** | Russian (Estonian residence permit) |
| **Verification Level** | Level 2 (Full) |
| **ID Document** | Estonian residence permit card (verified) |
| **ID Expiry** | 2027-05-15 |
| **Proof of Address** | Utility bill, Tallinn address (verified, dated 2025-10) |
| **Account Created** | 2023-08-22 |
| **Account Age** | ~30 months |
| **Occupation (declared)** | IT consultant / freelance developer |
| **Source of Funds (declared)** | Freelance consulting income and crypto trading |

### Verification Notes
- KYC completed 2023-08-22
- Selfie match: confirmed
- No document anomalies flagged
- Estonian residence permit is valid; Russian nationality noted
- Declared income as freelance IT consultant — high transaction volumes may be consistent but require verification""",

        "le_kodex_extraction": """## Law Enforcement Cases

### Active Request: RFI-2026-EU-0178
- **Type:** Request for Information (RFI)
- **Requesting Authority:** Estonian Financial Intelligence Unit (FIU)
- **Date Received:** 2026-02-22
- **Subject:** BIN-56201847 (Dmitri K. Volkov)
- **Scope:** Full transaction history for period 2025-10-01 to present, all associated wallet addresses, KYC documentation
- **Status:** Pending response (deadline: 2026-03-15)
- **Classification:** Confidential — do not disclose to subject

### Notes
- The Estonian FIU RFI was received 2 days after the CTM alert triggered, suggesting parallel investigation
- The RFI references an ongoing investigation into sanctions evasion through crypto exchanges in the Baltic states
- Compliance legal team has reviewed and confirmed the RFI is valid and within scope
- Response is being prepared by the LE coordination team

### Important: This case has an active LE request. Per policy:
1. Do NOT alert the subject about the investigation
2. Do NOT process any withdrawal requests without LE team approval
3. All case actions must be coordinated with the LE team
4. Precautionary account freeze should be considered""",
    },
    "created_at": datetime(2026, 2, 20, 14, 30, 0, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 2, 20, 14, 30, 0, tzinfo=timezone.utc),
}


# =============================================================================
# Case 3: Fraud — Account Activity Anomalies
# =============================================================================

CASE_3 = {
    "_id": "CASE-2026-0512",
    "case_type": "fraud",
    "status": "open",
    "subject_user_id": "BIN-39104826",
    "summary": "Account activity anomalies — sudden high-volume fiat deposits followed by rapid crypto conversion and withdrawal",
    "assigned_to": "user_001",
    "conversation_id": None,
    "preprocessed_data": {
        "c360_transaction_summary": """## Account Activity Analysis

### Overview
Subject BIN-39104826 account has shown a dramatic change in activity pattern starting 2026-01-20. The account was largely dormant for 14 months prior.

### Activity Timeline

| Period | Deposits | Withdrawals | Trading Volume | Status |
|--------|----------|-------------|----------------|--------|
| 2024-08 to 2025-11 | 3 deposits, $4,200 total | 2 withdrawals, $3,800 total | $12,000 | Normal / Low activity |
| 2025-12 | No activity | No activity | None | Dormant |
| 2026-01 (20-31) | 8 deposits, $47,500 total | 5 crypto withdrawals, $41,200 total | $46,000 | **Anomalous spike** |
| 2026-02 | 12 deposits, $78,300 total | 9 crypto withdrawals, $71,800 total | $75,000 | **Continued high volume** |

### Deposit Source Analysis
All fiat deposits via bank transfer from:
- **Bank Account 1:** First National Bank, ending ...4891 — 14 deposits, $89,300 total
- **Bank Account 2:** Metro Credit Union, ending ...7203 — 6 deposits, $36,500 total

**Key observations:**
- Bank Account 2 was added to the Binance account on 2026-01-25 — 5 days after the activity spike began
- Deposit amounts range from $2,500 to $12,000 — no single deposit exceeds $12,000
- Multiple same-day deposits observed (3 occasions with 2+ deposits on the same day)
- Total fiat deposits in 6 weeks: $125,800

### Conversion and Withdrawal Pattern
- Deposits converted to USDT within 24 hours of receipt (100% of deposits)
- USDT withdrawn to external wallets within 48 hours of conversion
- 3 distinct withdrawal wallets used:
  - 0xa1b2c3d4e5...f6789 — 8 withdrawals, $62,000
  - 0x9f8e7d6c5b...a4321 — 4 withdrawals, $38,500
  - 0x1122334455...66778 — 2 withdrawals, $12,500
- **Holding period:** Average 31 hours from deposit to withdrawal

### Device & IP Analysis
- **Primary device changed** on 2026-01-18 (2 days before activity spike)
  - Previous: iPhone 13, iOS (used since account creation)
  - Current: Samsung Galaxy S24, Android
- **IP address changed** on 2026-01-19
  - Previous: Residential ISP, Toronto, Canada
  - Current: Mobile carrier, different city (Montreal, Canada)
- **Session analysis:** Current sessions are shorter and more transaction-focused (average 8 min vs. previous 25 min)""",

        "elliptic_screening": """## Wallet Screening Results

### Wallet 1: 0xa1b2c3d4e5...f6789
- **Elliptic Risk Score:** 4.2 / 10 (Medium)
- **Entity:** Unknown — not associated with any named entity
- **Exposure:** No direct high-risk exposure
- **Note:** Wallet is relatively new (first activity 2026-01-10). Received funds from 6 different sources. Pattern consistent with collection wallet.
- **Blockchain:** Ethereum (ERC-20 USDT)

### Wallet 2: 0x9f8e7d6c5b...a4321
- **Elliptic Risk Score:** 5.8 / 10 (Medium-High)
- **Entity:** Weakly associated with known P2P trading network
- **Exposure:** Indirect — 3 hops from wallets involved in a 2025 investment fraud scheme
- **Note:** The indirect exposure is through a high-volume intermediary, so the connection may be coincidental.
- **Blockchain:** Ethereum (ERC-20 USDT)

### Wallet 3: 0x1122334455...66778
- **Elliptic Risk Score:** 3.1 / 10 (Low-Medium)
- **Entity:** Unknown
- **Exposure:** No significant exposure
- **Blockchain:** Ethereum (ERC-20 USDT)

### Summary Assessment
Wallet screening does not show high-risk direct exposure, but the collection wallet pattern (Wallet 1) and the overall deposit-convert-withdraw behaviour are the primary concerns rather than counterparty risk.""",

        "kyc_id_document": """## KYC Information

| Field | Value |
|-------|-------|
| **Full Name** | Sarah L. Chen |
| **Date of Birth** | 1995-07-22 |
| **Country of Residence** | Canada |
| **Nationality** | Canadian |
| **Verification Level** | Level 2 (Full) |
| **ID Document** | Canadian driver's licence, Ontario (verified) |
| **ID Expiry** | 2028-07-22 |
| **Proof of Address** | Bank statement, Toronto address (verified, dated 2024-07) |
| **Account Created** | 2024-08-05 |
| **Account Age** | ~19 months |
| **Occupation (declared)** | University student (part-time retail) |
| **Source of Funds (declared)** | Part-time employment |

### Verification Notes
- KYC completed 2024-08-05
- Selfie match: confirmed
- No document anomalies at time of verification
- **Concern:** Declared occupation (student/part-time retail) is inconsistent with $125,800 in deposits over 6 weeks
- **Proof of address is 19 months old** — re-verification may be warranted, especially given the city change from Toronto to Montreal

### Account Flags
- Account reactivated after 14-month dormancy
- Device and IP changed shortly before activity spike
- Transaction volume inconsistent with declared source of funds""",
    },
    "created_at": datetime(2026, 2, 25, 11, 15, 0, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 2, 25, 11, 15, 0, tzinfo=timezone.utc),
}


# =============================================================================
# Case 4: LE — Los Halcones del Valle (OFAC sanctions nexus)
# =============================================================================

CASE_4 = {
    "_id": "CASE-2026-0784",
    "case_type": "le",
    "status": "open",
    "subject_user_id": "274819633",
    "summary": "LE referral — counterparty to OFAC-sanctioned Los Halcones del Valle leader, "
               "$5.9M suspicious volume, Binance Pay pass-through pattern",
    "assigned_to": "user_001",
    "conversation_id": None,
    "preprocessed_data": parse_case_markdown(DEMO_1_PATH),
    "created_at": datetime(2026, 3, 15, 9, 22, 0, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 3, 15, 9, 22, 0, tzinfo=timezone.utc),
}


# =============================================================================
# Case 5: LE — Los Lobos del Pacífico (OFAC sanctions nexus)
# =============================================================================

CASE_5 = {
    "_id": "CASE-2026-0091",
    "case_type": "le",
    "status": "open",
    "subject_user_id": "94712638",
    "summary": "LE referral — counterparty to OFAC-sanctioned Los Lobos del Pacífico leader, "
               "$7.5M total volume, 143 flagged counterparties across 15 jurisdictions",
    "assigned_to": "user_001",
    "conversation_id": None,
    "preprocessed_data": parse_case_markdown(DEMO_2_PATH),
    "created_at": datetime(2026, 3, 12, 3, 17, 0, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 3, 12, 3, 17, 0, tzinfo=timezone.utc),
}


# =============================================================================
# Seed function
# =============================================================================

def seed():
    """Connect to MongoDB and seed all demo data."""
    print(f"Connecting to MongoDB: {MONGO_URI}")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Clear existing data
    print("Dropping existing collections...")
    db.users.drop()
    db.cases.drop()
    db.conversations.drop()

    # Seed users
    db.users.insert_many(USERS)
    print(f"Seeded {len(USERS)} users")

    # Seed cases
    cases = [CASE_1, CASE_2, CASE_3, CASE_4, CASE_5]
    db.cases.insert_many(cases)
    print(f"Seeded {len(cases)} cases:")
    for case in cases:
        pp_fields = [k for k, v in case["preprocessed_data"].items() if v]
        print(f"  {case['_id']} ({case['case_type']}) — {len(pp_fields)} data sections")

    # Verify
    print("\nVerification:")
    print(f"  Users: {db.users.count_documents({})}")
    print(f"  Cases: {db.cases.count_documents({})}")
    print(f"  Conversations: {db.conversations.count_documents({})}")

    # Show case summaries
    print("\nCase summaries:")
    for case in db.cases.find():
        print(f"  [{case['_id']}] {case['case_type'].upper()} — {case['summary'][:60]}...")

    client.close()
    print("\nDone. Demo data seeded successfully.")


if __name__ == "__main__":
    seed()
