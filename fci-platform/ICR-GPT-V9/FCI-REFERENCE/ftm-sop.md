# Standard Operating Procedure: Reviewing On-Chain TM Alerts

## Document Control
*   **Document Name:** FCI: Reviewing On-Chain TM Alerts
*   **Version:** 1.0
*   **Date of Issue:** 25 December 2025
*   **Next Review Date:** 25 December 2026
*   **Owner:** Michael Whelan, Enterprise Compliance Operations Manager, Financial Crimes Investigations
*   **Authors:** Jason Lau (Onchain Lead), Albert Volcek (TM Investigations Ops Lead) [1]

---

## 1. Purpose
This procedure establishes clear guidance for reviewing **Investigation Case Referrals (ICRs)** related to on-chain transaction monitoring that are escalated to the Financial Crime Investigations (FCI) Team. It outlines a three-phase investigation approach to ensure efficient case handling [1].

## 2. Scope
*   **Applicability:** Accounts with triggered on-chain transaction monitoring alerts under the Binance group.
*   **Specific Queue:** ICRs routed to the FCI Team queue on Haodesk labeled "FCI - Compliance L2 Crypto TM."
*   **Phased Approach:** The SOP provides standards for a consistent investigation across three distinct phases (Pre-Check, Initial, and Full Review) [1].

## 3. Approval & Annual Review
*   **Updates:** The SOP is monitored and updated to remain relevant. Updated versions are published on Confluence.
*   **Approval Authority:** Amendments must be approved by stakeholders, including the policy owner.
*   **Frequency:** Reviewed and approved at least annually by the Head of Function [1].

## 4. Responsibilities

| Role | Responsibilities |
| :--- | :--- |
| **Financial Crimes Investigation (FCI) Team (L2)** | • Conduct investigations of escalated red flags based on unusual transaction activities or behavior.<br>• Recommend the next course of action within the defined SLA.<br>• Forward cases to other L2 teams (Sanctions/Special Investigation) or escalate to the MLRO (L3) if applicable. |
| **Money Laundering Reporting Officer (MLRO) (L3)** | • Review escalated cases from L2 teams.<br>• Evaluate trends of unusual activity against AML/Sanction/CTF laws.<br>• Supervise external SAR submission to FIUs.<br>• Decide whether to retain or offboard the user. |

[1]

---

## 5. Procedure Overview

The investigation process is divided into three potential phases. The investigator must assess risks at each stage to determine if the case can be resolved or requires escalation.

### The Three Phases
1.  **Pre-Check Phase:** Identify alert type/category, determine routing, and assess if On-chain Exposure Assessment is needed.
2.  **Initial Review Phase:** An intermediate assessment of historical behaviors, risk patterns, and user explanations.
3.  **Full Review Phase:** A holistic 360-degree review of the account, used when risks cannot be discounted. This phase may involve RFIs, offboarding, or MLRO escalation [1].

### Key Systems
*   **Haodesk:** The primary case management tool where investigators access pre-populated templates for each phase.
*   **Queue:** "FCI - L2 Crypto TM" [1].

### 5.1 Workflow Logic

**Process Flow:**
1.  **Receive Alert:** Case enters "FCI - L2 Crypto TM" queue.
2.  **Phase 1: Pre-Check Review**
    *   *Action:* Check alert category and exposure.
    *   *Decision:*
        *   If **Low Risk/False Positive:** Close Case.
        *   If **Sanctions/Terrorist Financing:** Transfer to Sanctions Team (refer to Guide to Onchain Matrix).
        *   If **Material Red Flags/Risks Identified:** Escalate to Phase 2.
3.  **Phase 2: Initial Review**
    *   *Triggers:* Severe alert categories or risks found in Pre-Check (e.g., Fraud, Gambling, Obfuscation, Platform Risk, ATM).
    *   *Action:* Review historical behavior and patterns.
    *   *Decision:*
        *   If **Mitigated:** Close Case.
        *   If **Risks Persist/Cannot be Discounted:** Escalate to Phase 3.
4.  **Phase 3: Full Review**
    *   *Action:* Holistic 360 review, potential RFI, or Offboarding analysis.
    *   *Decision:* Retain, Offboard, or Escalate to MLRO (L3) [1].

---

## 5.2 Pre-Check Review Phase

### Objective
To identify the alert type, determine routing, perform On-chain Exposure Assessment (using Elliptic Investigator Tracing) if applicable, and decide if further investigation is needed [1].

### Limitations of this Phase
During the Pre-Check phase, the investigator **must NOT**:
*   Issue Requests for Information (RFIs).
*   Refer cases to Special Investigations (unless specific criteria met).
*   Escalate to MLRO.
*   Initiate offboarding actions [1].

*Note: If material red flags are found here, the case must move to the Initial Review phase.*

**PRE-CHECK/INITIAL COMPLETION EXCEPTION:**
A case may be completed at the Pre-Check or Initial Review phase (without escalating to Full Review) if the user under investigation has already been offboarded or submitted for offboarding by the time of the review. In this scenario, document the existing offboarding status (date, reason, submitting team) and close the case at the current phase.

### Workflow Logic: Indirect Exposure
*   **Reference:** Consult "CTM-FCI Guidance."
*   **Action:** Evaluate if exposure is unrelated or potentially linked.
*   **Tracing:** Use "Onchain Exposure Assessment (Elliptic Investigator Tracing)" (see Appendix IV) to interpret blockchain risks via temporal, directional, and behavioral tracing concepts [1].

### Workflow Logic: Sanctions & Terrorist Financing
*   **Action:** After pre-checks, these cases generally do **not** require FCI investigation.
*   **Routing:** Transfer to Sanctions Investigations based on thresholds in the "Guide to Onchain Matrix," or close if applicable per guidance [1].

### Pre-Check Review Template Structure

#### I. Presentation of Unusual Activity
*   **Auto-Populated Data:** Alert date, Deposit address, Exposure type, Entity Category, USD Amount, and Elliptic Risk Score.
*   **Investigator Task:** Validate the alert exposure type (Direct vs. Indirect). For indirect exposures, apply tracing assessment [1].

#### II. Presentation of People Involved
*   **User Profile:** UID, Name, Email, Phone, Nationality, DOB, ID type, Address, Account Age, Last Login, Balance.
*   **Key Status Tags:**
    *   *VIP Status:* High volume may require proportional scrutiny.
    *   *P2P Merchant Status:* High volume of counterparties; distinguish between merchant behavior vs. indirect customer exposure.
    *   *Entity/TNC/Bifinity Tags:* May trigger specific escalation workflows (e.g., licensed jurisdiction requirements) [1].

#### III. Conclusion & Analysis
*   **Requirement:** Manual input of 3-4 sentences.
*   **Content:**
    *   Explain why the case is completed in the "Pre-Check" phase.
    *   Attach Tracing Diagram (Lens or Investigator).
    *   **Rationale:** Explain closing or escalating based on:
        *   Tracing analysis (hops, fund direction, amount, temporal relevance).
        *   Transactional patterns (frequency, counterparties, behavioral changes) [1].

---

## 5.3 Initial Review Phase

### Objective
The Initial Review Phase serves as an intermediate assessment of the user's account to decide whether to escalate for a Full Review. It focuses on examining historical behaviors, risk patterns, user explanations, and broader transactional context [1].

### Triggers for Initial Review
An investigation enters this phase when:
1.  **Pre-Check Escalation:** The investigator identifies additional red flags or unusual on-chain risks during the Pre-Check phase (Severe Alert categories).
2.  **Specific Categories:** The case belongs to high-risk categories including:
    *   Fraudulent Activity
    *   Gambling
    *   Obfuscating
    *   Misc
    *   EU Russia
    *   Platform Risk
    *   ATM [1]

### Limitations of Initial Review
Similar to the Pre-Check Phase, the following actions are **NOT** performed during the Initial Review:
*   Sending Requests for Information (RFIs).
*   Escalating to MLROs (L3).
*   Offboarding users [1].

**90-DAY PRIOR ICR COMPARISON:**
Prior ICRs filed within 90 days of the current alert require specific comparison:
1. Check whether new alert rule codes have been triggered that were not present in the prior ICR. If yes → escalate to Full Review regardless.
2. If no new rule codes: check whether the triggered TM rules are the same AND the alerted transaction amounts are materially similar (not greater than 3x difference).
3. If rules and amounts are materially similar: compare Push and Pull factors between the prior ICR and current case to determine if the risk profile has changed.
Note: LVP-I and LVP-O are different rule codes (direction differs). Do not treat as the same rule.

**INITIAL PHASE — RE-SCREENING AND RFI ANALYSIS:**
At the Initial Review phase, re-screening of alerts and lifetime top 10 exposed wallets is not obligatory — analysis based on existing data should be sufficient. For prior RFIs, focus on those relevant to the current case and those where the user provided replies; for others, the Hexa summary is sufficient. Fresh re-screening is required only at the Full Review phase.

### Assessment Criteria
The investigator must evaluate the following data points to determine risk:

1.  **Prior ICR (Investigation Case Referrals):**
    *   Does the current case align with previous typologies?
    *   Are there recurring high-risk patterns or unresolved red flags?
2.  **CTM Alerts (On-Chain Transaction Monitoring):**
    *   Review breakdown of historical alerts (category, time period, direction, severity).
    *   Identify recurring patterns.
3.  **Lifetime Top 10 Exposed Addresses:**
    *   Determine if the flagged interaction represents a recurring pattern or an isolated event.
4.  **User Communication:**
    *   Review previous RFI correspondence.
    *   Check for existing Source of Funds (SoF) or Source of Wealth (SoW) declarations that mitigate the risk [1].

### Machine Learning (ML) Guidance
The system uses two Onchain 360 Machine Learning Models to detect suspicious behavior.

*   **Scoring Thresholds for Escalation:**
    *   **Fraudulent Activity:** Score ≥ 0.3155 (31.55%)
    *   **Other FinCrime Typologies:** Score ≥ 0.4572 (45.72%)
    *   *Action:* If scores meet these thresholds, the alert is escalated for manual investigation.
    *   *Action:* If scores are below thresholds, the case is sent to the **Continuous Monitoring Pool (CMP)** for observation (365 days) [1].

*   **ML Factors (Push vs. Pull):**
    *   **Push Factors:** Risk indicators that increase likelihood of suspicious activity (e.g., high-risk counterparties, privacy coin usage).
    *   **Pull Factors:** Indicators that reduce perceived risk or justify the transaction (e.g., consistent history, low value).
    *   *Investigator Action:* Review the summary of 48 explanatory variables ("features") provided by the system [1].

### Initial Review Conclusion Requirements
The investigator must provide a concise summary in the "Conclusion" section:
*   **Reference Key Areas:** Prior ICR outcomes, historical CTM alerts, Lifetime Top 10 exposures, and user communications.
*   **Factor Analysis:** Explain how Push/Pull factors influenced the decision.
*   **Decision Statement:**
    *   *Example (Close):* "Alert closed at Initial Review – low residual risk due to..."
    *   *Example (Escalate):* "Alert escalated to Full Review – further investigation required due to..." [1]

---

## 5.4 Full Review Phase

### Objective
This is the most comprehensive investigation stage, triggered when risks or red flags cannot be discounted in earlier phases. It requires a holistic "360-degree review" of the account [1].

### Permitted Actions in Full Review
Unlike previous phases, the investigator **MAY**:
*   Forward cases to **Special Investigations** teams.
*   Submit a **Request for Information (RFI)** to the user.
*   Escalate the case to **MLROs** (L3).
*   **Offboard** users [1].

### Full Investigation Template Structure
The Full Review template in Haodesk requires manual population and analysis of several key sections:

#### I. Presentation of Unusual Activity
*   **Auto-Populated:** Date, Deposit Address, Exposure Type, Entity Category, Amount, Risk Score.
*   **Action:** Validate the alert details against system records [1].

#### II. Analysis of Transactions
*   **Summary of Account Activities:**
    *   User Trade Volume (Crypto/Fiat/P2P/Card).
    *   Net Asset Holdings.
    *   Law Enforcement Requests (Note: For MLRO review only; do not share documents without consent) [1].
*   **Unusual Transactions (Manual Input):**
    *   Total Successful Unusual Transactions (Count & USD Value).
    *   Total Rejected Unusual Transactions (Count & USD Value) [1].

#### III. Red Flag Analysis (The "What, Where, How")
The investigator must manually screen Top-10 addresses and high-risk transactions. The analysis must describe:
*   **WHAT:** The nature of the red flag.
*   **WHERE:** The source of the red flag.
*   **HOW:** How the red flag was ascertained.

**Required Analysis Components:**
1.  **Suspicious Activity List:** Date ranges, amounts, and transaction references.
2.  **Tracing Description:** Include tracing analysis (even if a diagram is attached).
3.  **Counterparty Risk:** Describe interactions with high-risk users.
4.  **IP & Device Analysis:**
    *   Identify substantial risks (e.g., sanctioned jurisdictions, swift location changes).
    *   Analyze devices shared with other high-risk Binance users.
5.  **Privacy Coins/Mixers:** Note any usage related to suspicious activities.
6.  **OSINT:** Include search results (positive hits AND negative results) [1].

#### IV. Request for Information (RFI) Protocol
If an RFI is issued, the following details must be logged:
*   **RFI Case ID & Date Sent.**
*   **Type:** (e.g., Source of Funds, Transaction Justification).
*   **Risk Mitigation:** What specific financial crime risk is being addressed?
*   **Outcome Criteria:** What constitutes a satisfactory vs. unsatisfactory response? [1]

#### V. Conclusion & Decision
*   **Action:** Provide a conclusion based on Red Flags (Appendix I) and the Decision Matrix (Appendix II).
*   **Reporting:** Clearly state whether to **Retain** or **Offboard** the user.
*   **SLA:** Cases from reporting jurisdictions must be reviewed within **30 days** of submission [1].

---

## 6. Product Types
While the main volume of cases falls under the standard `.COM` product type, specific handling is required for specialized products.

**Product Segments:**
*   .COM
*   .COM (MENA)
*   Defi_Wallet
*   COMRESCREENING
*   Defi_Rescreening
*   Binance.TH (Refer to Cloud Exchanges SOP for specific handling) [1]

---

## 6.1 Binance DeFi (Defi_Wallet)

### Definition
The Binance Web3 wallet (formerly "DeFi") is a secured, decentralized mobile platform allowing users to handle and trade cryptocurrencies integrated with DeFi protocols.

**Key Features:**
*   **Non-Custodial:** End-users hold full control over wallet keys and funds.
*   **Multi-Currency:** Supports storage and trade of various cryptos and DeFi applications.
*   **Integration:** Interacts with lending protocols, DEXs, and yield farming platforms [1].

### 6.1.1 Types of DeFi Wallets
The platform supports three wallet types:

1.  **MPC (Multi-Party Computation):** A cryptographic protocol where multiple parties jointly compute a function.
2.  **Seed Phrase:** Traditional mnemonic-based recovery.
3.  **Private Key:** Direct key management [1].

### 6.1.2 DeFi Cases Handling Specifics
Because Binance Web3 Wallets are **non-custodial**, investigators cannot freeze funds or offboard the wallet directly in the same way as a centralized account.

**Investigation Steps:**
1.  **Verify User Linkage:** Determine if the DeFi wallet is linked to a centralized Binance User ID (UID).
2.  **Access:** Use the "Wallet Address" provided in the alert to check the "Defi Wallet Admin" portal.
3.  **Risk Assessment:**
    *   If the wallet is **NOT** linked to a Binance UID: No further action (user is outside custodial control).
    *   If the wallet **IS** linked to a Binance UID: Investigate the centralized account for risks associated with the DeFi activity.
4.  **Escalation:** If illicit activity is confirmed on the linked centralized account, proceed with standard Full Review escalation (RFI/Offboard/MLRO) on the **centralized UID**, not the DeFi wallet itself [1].

### 6.1.3 OSINT Tools
Open Source Intelligence (OSINT) tools are essential for verifying entities and addresses associated with DeFi and standard alerts.

**Recommended Tools:**
*   **Etherscan / BscScan / TronScan:** For verifying on-chain transaction paths and contract interactions.
*   **Google Dorking:** Advanced search queries to identify wallet attributions.
*   **Twitter (X):** Often contains real-time flagging of hacks or scam addresses.
*   **Arkham Intelligence:** Visualizing entity clusters and deanonymizing wallets [1].

---

## 6.2 Rescreening

### Definition
Rescreening alerts occur when the risk status of a previously screened transaction or address changes due to new intelligence (e.g., an address previously thought "safe" is later tagged as "Sanctioned").

### Classification of Rescreening Alerts
Investigators must distinguish between **Duplicate** alerts and **Genuine** rescreening alerts.

#### 1. Duplicate Alerts (Close Case)
A case is considered a duplicate if:
*   The system shows only one transaction in Binance Admin (BAdmin), but multiple identical entries appear in Haodesk (same timestamp, TxID, amount).
*   There is no prior rescreening of the address.
*   **Risk Rating:** The risk rating and exposure type are unchanged.
*   **Attribution Change:**
    *   *Example:* 10 (Indirect) → 10 (Direct). If the score is the same, treat as duplicate [1].

#### 2. Genuine Rescreening Alerts (Investigate)
A case is genuine if:
*   **Material Change:** Both Risk Rating AND Exposure type have changed.
*   *Action:* Reassess the case based on the new exposure data [1].

---

## 7. Related Documents and References

| Reference Name | Description/Source |
| :--- | :--- |
| **IHRE Rules Library - On-chain** | Onchain rules - Risk rule documentation. |
| **ICR Review Templates** | Guidance on the Phased Approach (Pre-Check/Initial/Full). |
| **Guide to On-Chain TM Matrix** | Thresholds for Sanction Lists, Sanction Countries, and Terrorist Financing categories. |
| **UAR Report Format Guidelines** | v 2.0 (01.04.2025). |
| **Escalation to Sanctions/SI** | Protocol for referring cases to Sanctions and Special Investigations. |
| **RFI Protocol** | FCI Team Protocol for Request for Information v2.0. |
| **Offboarding Standards** | FCI Offboarding Standards and Guidelines. |

[1]

---

## 8. Definitions

| Term | Definition |
| :--- | :--- |
| **ML Push Factors** | Indicators that increase likelihood of high-risk activity (push risk higher). |
| **ML Pull Factors** | Indicators that reduce perceived risk or provide justification (pull risk lower). |
| **Money Laundering (ML)** | Concealing illicit origin of funds. |
| **Proliferation Financing (PF)** | Providing funds for Weapons of Mass Destruction (WMD). |
| **Sanctions** | Preventative measures by governments to change behavior/prevent illicit activity. |
| **Terrorist Financing (TF)** | Providing funds for terrorist activities. |
| **On-Chain TM** | Monitoring via third-party tools (Elliptic) for blockchain risks. |
| **Off-Chain TM** | Monitoring via internal risk engine (IHRE) for behavioral risks. |
| **ICR** | Investigation Case Referral (escalated to L2). |
| **UAR** | Unusual Activity Report (escalated to L3). |
| **SAR** | Suspicious Activity Report (external filing). |

[1]

---

## Appendix I - Red Flags and Risk Level
This section defines specific indicators that determine the risk level of a case. Investigators must reference these factors when justifying decisions.

### Historical Alerts & Records

| Red Flag | Guidance | Risk Level |
| :--- | :--- | :--- |
| **Historical Onchain/Offchain Alerts** | A consistent history of alerts (e.g., high-value ATM usage, SAWD patterns) signals elevated residual risk. Review past resolutions (Closed vs. Escalated). | **Medium** |
| **LE Ticket** | User was subject to Law Enforcement (LE) inquiry. Review type (subpoena vs. info request) and transaction period surrounding the request. | **Medium** |
| **Existing ICR/UAR Record** | Previous Suspicious Activity Reports (SAR/ICR). If current behavior is recurring despite past closures, consider escalation. | **Medium** |

### Transactional Behaviors

| Red Flag | Guidance | Risk Level |
| :--- | :--- | :--- |
| **Privacy Coin Usage** | Frequent or high % of transactions using coins like Monero/Zcash to conceal details. | **Medium** |
| **Inconsistent IP/Device** | User operates from high-risk countries different from KYC residence (non-VPN). High number of shared devices. | **Medium** |
| **Volume Disproportionate to Profile** | Transaction volume exceeds economic profile (World Bank GNI thresholds). *Example:* Student or low-income user moving high-value funds. | **High** |
| **Insufficient RFI Response** | User fails to explain transaction purpose/source of funds, or explanations lack economic sense. | **High** |

### Network & Association Risks

| Red Flag | Guidance | Risk Level |
| :--- | :--- | :--- |
| **Adverse Media** | Credible media hits linking user to financial crime (not general misconduct). | **Medium** |
| **High Risk Associated Parties** | Connections (shared device/transactions) to users with LE tickets, blocks, or fraud history. | **High** |

[1]

---

## Appendix II - Decision Matrix
This matrix provides the "If/Then" logic for case outcomes based on identified Red Flags.

| Scenario | Checklist Criteria | Action | Guidance |
| :--- | :--- | :--- | :--- |
| **Clear ML Typology** | • Multiple high-risk red flags present.<br>• Activity matches known ML/TF typology.<br>• No plausible legitimate explanation. | **Escalate without RFI** | If gambling exposure is in a permissible jurisdiction (check "Virtual Asset Gambling Legality Matrix"), do not escalate solely for gambling. |
| **Material Red Flags (Unexplained)** | • Red flags present but context is missing.<br>• Further info could change risk assessment. | **Send RFI** | If response is satisfactory: **Close**. If unsatisfactory: **Escalate**. |
| **Low Risk / Mitigated** | • Red flags are minor or fully explained by past RFIs.<br>• Activity is consistent with known profile. | **Close Case** | Document mitigation clearly in the conclusion. |

[1]

---

## Appendix III - Supporting Documents
Investigators must attach specific evidence based on the jurisdiction and escalation type.

*   **Reporting Jurisdictions (Escalation):** Attach KYC profile, Transaction History (CSV), Tracing Diagrams, and relevant RFI correspondence.
*   **Non-Reporting Jurisdictions:** Attach summary of findings and key risk indicators.
*   **High-Risk Client Team:** Notify `@HRCBot` on WEA for users involving nested VASPs with high volume [1].

---

## Appendix IV - On-Chain Exposure Assessment & Tracing Guidance
This framework guides the use of **Elliptic Lens** and **Elliptic Investigator** to interpret blockchain risks.

### 1. Core Objectives
*   Accurately interpret risk graphs.
*   Differentiate **Intentional** vs. **Incidental** exposure.
*   Apply the four core tracing methods: **Temporal**, **Directional**, **Behavioral**, and **Unattributed Cluster** identification [1].

### 2. Understanding Elliptic Lens Data
*   **Aggregated Flows:** Total value exchanged between two clusters over time.
*   **Exposure Flows:** How exposure is distributed across paths.
*   **Closest Proximity:** The shortest path (hops) to an illicit entity.
*   **Triggered Rule:** Identifies if the risk is Source (Deposit) or Destination (Withdrawal) [1].

### 3. On-Chain Indirect Tracing Framework

#### 3.1 Temporal Assessment (Time)
*   **Principle:** The closer the timestamps between hops, the higher the likelihood of related activity.
*   **Logic:** Long gaps (days/weeks) between hops often indicate unrelated or aggregated fund behavior (e.g., exchange pooling) rather than direct user involvement.
*   *Risk Indicator:* "Peeling chains" or immediate pass-throughs suggest high risk [1].

#### 3.2 Directional Relevance (Flow)
*   **Deposit Alerts:** Assess the **Source** of funds. Where did they come from?
*   **Withdrawal Alerts:** Assess the **Destination**. Is the user sending funds to high-risk entities?
*   **Logic:** If a user *receives* funds from a Mixer, the risk is different than *sending* funds to a Mixer. Validate the "Directional Relevance" to the alert trigger [1].

#### 3.3 Behavioral Assessment (Wallet Ownership)
*   **Objective:** Determine if intermediate wallets are **User-Controlled** or **Third-Party Services**.
*   **Indicators of User Control:**
    *   **Bi-Directional Flows:** Funds move back and forth between User and Wallet X.
    *   **Repeated Funding:** Regular transfers over time (e.g., monthly).
*   **Risk Implication:** If the intermediate wallet is user-controlled, the exposure is considered **Direct**, even if it appears indirect on the graph [1].

#### 3.4 Unattributed Cluster Identification
*   **Concept:** Some wallets act like services (high volume, many counterparties) but lack vendor labels.
*   **Action:** If a wallet shows "Service-like" behavior (e.g., 10k+ transactions), treat it as a Service/Exchange node, which may **break the chain** of direct attribution to illicit funds, potentially lowering the risk [1].

### 4. Risk Indicators for Tracing

| Indicator Type | Metric | Description |
| :--- | :--- | :--- |
| **User Level** | Total Illicit Exposure % | High % suggests deliberate engagement; Low % suggests incidental exposure. |
| **Address Level** | Exposure Proximity (Hops) | **1 Hop:** Direct/High Risk.<br>**3-4 Hops:** Attenuated/Lower Risk. |
| **Pattern Level** | Frequency | Recurring exposure in short intervals suggests deliberate structuring. |

