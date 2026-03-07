# FCI Block / Unblock Account Guidelines

### **BLOCK Procedures**

*   **Unresponsive User (RFI):**
    *   Apply block if a user is unresponsive to an RFI sent by the FCI team after **at least 3 reminders**.
    *   *Note:* This only applies to Investigation Case Referrals (ICRs) filed cases.

*   **Uncooperative User (RFI):**
    *   Apply block if a user responds to RFI attempts but provides intentionally insufficient, evasive, or irrelevant information after **3 RFI attempts** (initial RFI + 2 re-triggers).
    *   **Block Type:** `Withdrawal Only Mode (WOM, no deposit & trade)`.
    *   **Block Reason:** `RFI - Others` (NOT "RFI - SAR Investigation" — that reason is reserved for unresponsive users).
    *   **Status:** Set case status to `Uncooperative user`.
    *   **Timeline:** Offboarding consideration begins **60 days** after WOM placement.
    *   *Note:* This is distinct from the Unresponsive User workflow. Unresponsive = no reply after 14 days + 3 reminders. Uncooperative = replies received but insufficient after 3 RFI attempts. Different block reasons, different tags, different timelines.

*   **P2P Merchant Courtesy Notification:**
    When a P2P merchant is unresponsive to an RFI, before applying blocks, FCI should reach out to the P2P team as a courtesy:
    1.  Notify the P2P team that FCI has an open investigation on the user
    2.  State that FCI has requested documentation and the user has not responded
    3.  Request the P2P team to reach out to the user and encourage a response
    4.  DO NOT share: investigation specifics, alert types, block reasons, potential outcomes, or any confidential investigation details with the P2P team
    This is a courtesy notification, not a requirement.

*   **Confirmed Suspicious Activities:**
    *   **Criteria:** Account with suspicious activities pertaining to high money laundering, sanction, terrorism risk, or other illegal activities confirmed after investigation.
    *   **Scope:** Applies to accounts where the investigator/analyst/agent recommends offboarding under other jurisdictions without MLRO escalations required.
    *   **Block Type:** `Withdrawal Only Mode (WOM, no deposit & trade)`.
    *   **Block Reason:** Must match the offboarding reason.
    *   **Exception:** If no appropriate block reason matches the offboarding reason:
        *   Choose `'Others'`.
        *   Indicate the ICR reference, the matching offboarding reason, and the next course of action in the remarks (e.g., *'SAR20240605-XXXX1, High money laundering risk, pending for offboarding'*).

*   **MLRO Request (Post-Approval):**
    *   Upon MLRO's request after offboarding approval (with withdrawal allowed), the MLRO will instruct to place a `'Withdrawal Only Mode (WOM, no deposit & trade)'` block before offboarding action is taken.

*   **Face Verification Block:**
    *   Investigator may impose a face verification block under Block Reason `"Login Face Verification"` when there is strong suspicion of:
        *   Shared account
        *   Purchased KYC account
        *   KYC fraud

*   **Urgent Ad-Hoc Requests:**
    *   Requests from other Business Units (Legal, MLROs, Business team) receiving external reporting of fraud or hack.
    *   *Requirement:* Only applies with team lead or manager approval.

> **Critical Warnings:**
> *   **Sub-Accounts:** Be aware that blocking a sub-account under an individual/corporate parent account may also apply to the master account and all other sub-accounts. Read the pop-up message: *"This is a normal sub-account, creating a withdrawal/login forbidden case will also block the same function of the Parent account."*
> *   **High Balance Check:** For accounts with a balance **> $100k**, checker's verification and approval under a team is required. The Checker must ensure the block reason matches the block nature and follows the FCI block/unblock account guidelines.
> *   **VIP Account Block Procedures:**
For VIP users, ALL block and unblock actions must be performed manually by the investigator. System-automated triggers (auto-WOM after 14 days, auto-close after 30 days) do NOT apply to VIP accounts. The investigator must maintain a personal tracker for VIP cases.
> *   **VIP RFI Block Notification Tiers:**
When a VIP user is unresponsive to an RFI and WOM is being considered:
- VIP with POC (Point of Contact / Account Manager):
  Contact the POC. Notify them of the required
  withdrawal block and request they contact the user to
  respond to the RFI. POC details are in Binance Admin
  > Info Hub.
- VIP Level 1-3 without POC: No notification required.
  Manually apply block when necessary.
- VIP Level 4-9 without POC: Must notify Jonathan
  Bracken (jon.yy@binance.com) BEFORE blocking. Do NOT
  block until approval is received. Screenshot the
  approval correspondence and attach it to the case
  file.
⚠️ NOTE: These VIP blocking tiers apply to RFI-related blocks ONLY. For offboarding-related VIP approval and notification, see icr-steps-post.md Step 22, which uses different tier thresholds (VIP 1-2 / VIP 3-6 / VIP 7-9) and requires different approval levels (including Enterprise Compliance Director and CCO for higher tiers). The two processes are intentionally different — do not apply RFI block tiers to offboarding decisions or vice versa.

---

### **PARTIAL FREEZE Procedures**

*   Partial freeze may be applied to a reported case if:
    1.  The user's account balance is **lower** than the reported dispute amount.
    2.  There is **no direct evidence** of scam/fraud activity.

---

### **UNBLOCK Procedures**

*   **Unresponsive Users (ICR Cases):**
    *   If a user responds to the RFI, remove the relevant block once the user contacts via any communication channel (Haodesk, RFI Tool, or Maildesk).

*   **Purchased KYC / Shared Account:**
    *   The withdrawal block will be uplifted **after** the appeal process is passed.
    *   The account status will be changed to `Withdrawal Only Mode` with a `Trade Block`.

*   **Refund Facilitation:**
    *   Trade block may be temporarily uplifted to allow the suspect to convert assets to facilitate a refund (if the balance is in a different asset and they agreed to refund).

*   **False Positive / Weak Connection (ICR Cases):**
    *   Investigator may proceed to unblock and retain the user if:
        *   The case is a false positive.
        *   The connection to reported red flags is indirect or weak.
        *   Evidence is insufficient to support offboarding.
    *   *Requirement:* MLRO approval is required if the account is under licensed jurisdictions (refer to MLRO Escalation Requirements Matrix).

*   **Request from Original Block Requestor:**
    *   Unblock upon request from Legal, MLROs, or Business team when the matter is confirmed resolved.

> **Cross-Team Block Protocol:**
> Blocks belonging to other compliance teams (Special Investigation, Sanctions, Case team):
> *   **MAKE SURE** to contact the block creator or relevant team members to clarify the nature of the block.
> *   **DO NOT** unblock other teams' blocks.
> *   If the block is related to the ICR escalation, advise the creator to transfer the block to *'Internal SAR Team'* for further action after ICR investigation.
> *   **Note:** If the block nature differs from the escalated red flags, resolve all matters related to the blocks before releasing.

---

### **JUSTIFIED / UNJUSTIFIED BLOCK Matrix**

| Block Reason | Context | Block Type | SLA (Days) |
| :--- | :--- | :--- | :--- |
| **RFI - Purchased KYC/Shared Account** | Use when the account is identified to be a KYC purchaser or sharing account with a third party while waiting for the user to provide the requested supporting documents for verification. | Trade & All Withdrawal (Crypto, FIAT & Others) | 7 |
| **RFI - SAR Investigation** | Use when there is an RFI sent for an ICR investigation case and the user is not responding to the RFI after 3 reminders. ***DO NOT BLOCK** THE ACCOUNT IMMEDIATELY AFTER THE RFI SENT OR BEFORE THE 3 REMINDERS SENT.* The 14-day grace period is counted in calendar days (not business days), as compliance support operates on a 24/7 basis. | Withdrawal Only Mode, then add the Unresponsive User Tag | 14 |
| **RFI - Others (Uncooperative)** | Use when the user has responded to RFI attempts but provided intentionally insufficient, evasive, or irrelevant information after 3 RFI attempts (initial + 2 re-triggers). ***DO NOT USE** THIS REASON FOR UNRESPONSIVE USERS — use "RFI - SAR Investigation" for unresponsive users.* | Withdrawal Only Mode (WOM, no deposit & trade) | 60 |
| **User reported account compromised** | Use when the user reports account compromised. | Trade & All Withdrawal (Crypto, FIAT & Others) | 30 |
| **Forged Supporting Documents** | Use when the user provided manipulative supporting documents such as edited bank card, bank statement etc. | Trade & All Withdrawal (Crypto, FIAT & Others) | 30 |
| **KYC Fraud** | Use for fake ID, fake POA, face attack cases. | Trade & All Withdrawal (Crypto, FIAT & Others) | 30 |
| **Sanctions - Terrorism** | Use for Terrorism related cases. | Trade & All Withdrawal (Crypto, FIAT & Others) | 30 |
| **Exposure to High Risk Wallet** | Use for the account with transactions to high risk wallet. | Trade & All Withdrawal (Crypto, FIAT & Others) | 30 |
| **Reported money laundering/scam** | Use for the account with high money laundering risk or scam/fraud cases. | Trade & All Withdrawal (Crypto, FIAT & Others) | 30 |
| **Abnormal Fluctuation** | Use when a victim reported unauthorised trading transaction (mostly due to a hack); the most beneficiary of these trades may be the suspect. Restriction on the account usually applies during the investigation. | Trade & All Withdrawal (Crypto, FIAT & Others) | 30 |
| **Others (indicate in remarks)** | Other block reasons outside from the above-mentioned. Clear block reason indicating the nature of the block case required in the remark. | All Withdrawal (Crypto, FIAT & Others), Trade, Trade & All Withdrawal (Crypto, FIAT & Others), Withdrawal Only Mode (WOM, no deposit & trade) | 30 |
| **Login Face Verification** | Use when there is strong suspicion of shared account, purchased KYC account or KYC fraud. Face verification will be imposed. | Login Face | N.A |

---

### **Follow Up Action**

*   **SLA Management:** All block cases should be followed up with the next course of action (send for offboarding / retain and uplift block / move to permanent block) within the given SLA. This excludes cases sent for offboarding.
*   **Permanent Block:** Should be applied when cases are inconclusive without necessary info (SOW/SOF/payment purpose) or necessary action (refund to victim).
    *   *Tagging:* For unresponsive users, apply the `'Unresponsive User'` tag (Only applicable to block reason under 'RFI').
*   **Periodic Review:** Unresponsive users should be followed up every **6 months** (June and December). Reminders must be sent to users blocked for being unresponsive.
*   **Uncooperative User Review:** Uncooperative users (blocked under "RFI - Others" after 3 insufficient RFI responses) should be reviewed for offboarding consideration **60 days** after WOM placement. At the 60-day mark, assess whether: (a) the user has since provided adequate information — if yes, review and potentially uplift the block; (b) the user remains uncooperative — proceed with offboarding recommendation.
*   **Unrelated Blocks:** All unrelated block cases under an account should be resolved before sending the account for offboarding (if applicable).
*   **Exception — Quota Freezes and Chargebacks:** Quota freezes and chargeback blocks placed by the banking team cannot typically be resolved by FCI and constitute an exception to this rule. These accounts can be offboarded with these freezes in place after obtaining Risk Ops team approval via a HaoDesk support ticket. See icr-steps-post.md Step 22 for the full process.
*   **Priority Review:** When a blocked unresponsive user replies to an RFI, these cases must be prioritised and reviewed within **14 days**. Investigators should review responses from blocked users before taking new cases.

---