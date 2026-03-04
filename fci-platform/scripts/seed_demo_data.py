"""
Seed script for FCI Investigation Platform demo data.

Populates MongoDB with:
- 2 mock user accounts
- 3 pre-staged sanitised case records with preprocessed data

Usage: python scripts/seed_demo_data.py

Requires: MongoDB running on localhost:27017
"""

from pymongo import MongoClient
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "fci_platform"


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
        "c360_analysis": """## Counterparty Risk Summary

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

        "elliptic_analysis": """## Wallet Screening Results

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

        "previous_cases": """## Prior Investigations

### Case CASE-2025-3891 (Closed — October 2025)
- **Type:** FTM alert — unusual fiat deposit pattern
- **Outcome:** No adverse finding
- **Summary:** Subject made 4 deposits of £2,500 each within 3 days from the same bank account. Investigation found this was salary payments from a legitimate employer who paid weekly. Case closed with no action.
- **Investigator notes:** Subject was cooperative and provided payslips to support explanation. No further monitoring recommended.

### No other prior cases found for BIN-84729103.""",

        "chat_history_summary": """## L1 Customer Service Interactions

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

        "kyc_summary": """## KYC Information

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
        "c360_analysis": """## On-Chain Alert Details

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

        "elliptic_analysis": """## Wallet Screening Results

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

        "kyc_summary": """## KYC Information

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

        "law_enforcement": """## Law Enforcement Cases

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
        "c360_analysis": """## Account Activity Analysis

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

        "elliptic_analysis": """## Wallet Screening Results

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

        "kyc_summary": """## KYC Information

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
    cases = [CASE_1, CASE_2, CASE_3]
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
