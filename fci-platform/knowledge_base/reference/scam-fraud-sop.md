# FCI SOP: Scam/Fraud/Single Deposit Risk Cases Handling

**Version:** 3.2  
**Date of Issue:** 27.10.2025  
**Document Owner:** Michael Whelan, Financial Crime Investigations Team (FCI) Manager  
**Next Review Date:** 28.10.2026 [1]

---

## Document Version Control [1]

| Version No | Change Description | Author | Date |
| :--- | :--- | :--- | :--- |
| **2.0** | Scam/Fraud/Single Deposit Risk cases handling | Charlotte Luo (Internal SAR Team Manager) | 06.02.2023 |
| **3.0** | **Updates:**<br>- Removed escalation to Special Investigations.<br>- Added procedure for victims attempting illicit activities.<br>- Changed threshold for account balance from USD 100 to USD 1,000.<br>- Added procedure for FCI Agents to send reimbursement reminders.<br>- FCI analysts may complete cases/offboard without suspect response. | Michael Whelan (FCI Team Manager) | 28.05.2025 |
| **3.1** | **Updates:**<br>- Added info on checking refunds (Point 3.3).<br>- Added procedure on reminders/Helpdesk tickets (Point 3.5).<br>- Added clarification on 30 days block and reminders (Point 3.5). | Michael Whelan (FCI Team Manager) | 09.07.2025 |
| **3.2** | **Updates:**<br>- Amended 5.1 Procedure (3.5): Added requirement to use "Pending - Refund" status.<br>- Added "Appendix II. Unified Scam Category". | Michael Whelan (Enterprise Comp Ops Manager) | 27.10.2025 |

---

## 1. Purpose [1]

This document serves as a standard operating procedure (SOP) for proper handling of **Unusual Activity Report (UAR)** with subject matter Fraud/Scam and Single deposit risk control referred cases from the **Security Special Operations Team (SSO)** and investigated by the **Financial Crime Investigation (FCI) Team**. It comprises the workflow and guidance for team members on how to complete a HaoDesk Service Case assigned to them.

*   **Scam/fraud:** Refers to the scam, fraudulent, or abnormal activities of an individual/group (victim) reporting to Binance.
*   **Single deposit risk case:** Refers to deposits received from a source address blacklisted wallet which triggered the system risk rule set to control scam or fraudulent funds coming back to a Binance account.

## 2. Scope [1]

Procedures and guidelines included in this document are applicable to all FCI Team members and contribute to an automatic submission of ICRs with contractors and stakeholders handling L2 referrals related to Fraud/Scam and Single deposit risk control reported by the SSO Team.

## 3. Responsibilities [1]

| Role | Responsibilities |
| :--- | :--- |
| **Referral of unusual activities (L1)** | The SSO team creates the ICR case using the latest escalation system, including all unusual transaction patterns and behaviors, along with all collected information and supporting documents. |
| **Financial Crimes Investigation (FCI) Team (L2)** | Conduct investigation of the escalated red flags of a user in accordance with the unusual transaction activities or behaviour related to fraud/scam/single deposit risk control, make a recommendation of the next course of action within the defined SLA to the L3 team. |

## 4. Approval & Annual Review [1]

The procedure will be continuously monitored and updated to ensure its relevance and effectiveness. The updated version will be published on Confluence. Any amendments will be reviewed and approved by relevant stakeholders, including the policy owner.

---

## 5. Procedure and Workflow [1]

### 5.1. Procedure & 5.2. Workflow Logic

The following logic defines the process for FCI and SSO Teams regarding Scam/Fraud/Single Deposit Risk Cases.

1.  **Initial Receipt & Verification (L1 SSO Team)**
    *   SSO receives scam/fraud reports from victims via Haodesk chat.
    *   SSO agent verifies/confirms fraudulent transactions.
    *   SSO advises victim to report to local law enforcement.
    *   **Decision: Wallet vs. Account**
        *   **IF** External Wallet Address involved: Add to blacklist.
        *   **IF** Binance Account involved: SSO blocks user's withdrawals (crypto, fiat, and others).
    *   **Decision: Law Enforcement (LE) Freeze Check**
        *   SSO checks Binance Admin System (Block & Unblock User 360 > User InfoHub > Assets > Frozen).
        *   **IF** LE Freeze exists: Stop standard flow (follow LE protocols).
        *   **IF** NO LE Freeze: Proceed to Step 2.

2.  **Request for Information (L1 SSO Team)**
    *   SSO sends RFI (Appendix I) to the suspect via Haodesk.
    *   SSO reviews supporting docs from victim and suspect within **7 days (SLA)**.
    *   **Objective:** Justify if this is true fraud or a dispute between two parties.

3.  **Investigation & Disposition Outcomes**

    *   **Scenario 3.1: Suspect Proves Innocence**
        *   **IF** suspect provides enough supporting documents/info to prove incident is NOT scam/fraud (e.g., dispute):
            *   **THEN** SSO releases the account.

    *   **Scenario 3.2: Voluntary Refund / Victim Illicit Activity**
        *   **IF** suspect voluntarily returns funds AND not confirmed fraud/abnormal activity:
            *   **THEN** SSO releases the account after refund.
            *   **Action:** Guide user on "Authorisation Statement Video" for refund. No ICR needed.
        *   **IF** victim attempted transactions related to illicit activity:
            *   **THEN** Escalate to FCI Team (L2) via 'User Report' in BA system.
            *   **Action:** Transfer CS block to FCI.
            *   **Outcome:** FCI proceeds with offboarding, retain, or escalate to L3 MLRO.

    *   **Scenario 3.3: Suspect Failure to Evidence / Refund Suggestion**
        *   **IF** suspect fails to provide evidence/explanation:
            *   **THEN** SSO suggests suspect refunds the victim (Appendix I - Refund Template).
        *   **IF** Refund is completed (Consent of all parties):
            *   **THEN** Escalate to FCI Team (L2) via 'User Report'.
            *   **Action:** Transfer CS block to FCI.
            *   **Outcome:** FCI proceeds with offboarding, retain, or escalate to L3 MLRO.
        *   *Note on Checking Refunds:* FCI should check "User Asset Log" for "Manual Transfer (425)" or "Binance Security Fund Recovery".

    *   **Scenario 3.4: Valid Proof, Uncooperative Suspect (Balance < $1,000)**
        *   **IF** Victim provides valid proof **AND** Suspect is uncooperative/unresponsive **AND** Balance is **BELOW USD 1,000**:
            *   **THEN** Escalate to FCI Team (L2) via 'User Report'.
            *   **Action:** Transfer CS block to FCI.
            *   **Outcome:** FCI proceeds with offboarding, retain, or escalate to L3 MLRO.

    *   **Scenario 3.5: Valid Proof, Uncooperative Suspect (Balance > $1,000)**
        *   **IF** Victim provides valid proof **AND** Suspect is uncooperative/unresponsive **AND** Balance is **ABOVE USD 1,000**:
            *   **THEN** Request Refund.
            *   **Action:** Keep withdrawal blocked.
            *   **Action:** Transfer Haodesk chat to FCI agents team.
            *   **Action:** Escalate to FCI (L2) via 'User Report' and transfer CS block.
            *   **Action:** FCI Investigators contact FCI agents via WEA group 'FCI-Agent-RFIBot'.
            *   **Action:** Change case status to **"Pending - Refund"**.
        *   **Sub-Process: Refund Reminders (FCI Agents)**
            1.  **Day 1:** Receive request, send Notification/Reminder 1 via Haodesk.
            2.  **Day 4:** Send Reminder 2 (if no response).
            3.  **Day 7:** Send Reminder 3 (if no response).
                *   *Note:* If suspect contacts team and is reminded, it counts as a reminder.
            4.  **Day 10:** If no response, create Helpdesk ticket to notify requestor.
        *   **Decision: 30 Day Threshold**
            *   **IF** no intention to refund within **30 days** (counting from day SSO placed block):
                *   **THEN** FCI proceeds with offboarding, retain, or escalate to L3 MLRO.
            *   **Exception:** A longer block (additional 30 days) may be considered if there is progress by LE or genuine attempts by victim to contact LE.
            *   **Constraint:** A block > 30 days does *not* exempt the reminder procedure if balance > USD 1,000.

### 5.3. Legal advice on handling fraud scam cases [1]
*   [Link to Legal Advice Document](https://docs.google.com/document/d/1DmvUaLiDgG8QOldDomWZwf6NnTPpTQLcb9_sikl-fY8)

---

## 6. Related Documents and References [1]

| Reference | Description | Link |
| :--- | :--- | :--- |
| **Investigation Case Referral (ICR) Guidelines** | Guidelines/Procedure on creating internal ICR cases to escalate to FCI by referral teams (L1). | [Link](https://docs.google.com/document/d/1whdL4I3Sm_qNMNuwfUGTtbRz92lJ5v8Xc5bzAMZoMwk/edit) |
| **Financial Crimes Investigation (FCI) Guidelines** | Guidelines for FCI Team on investigating escalated red flags, unusual transaction activities, and SAR/STR filing obligations. | [Link](https://docs.google.com/document/d/1hNikqouKE4bgUr_R-BXgbfOG2yD8DWo-/edit) |
| **UAR Report Format and Writing Guidelines** | Guidelines on drafting UAR reports and supporting docs for MLROs. | [Link](https://docs.google.com/document/d/1qZwABMjtPESDyNfAybtBwc9TZOFCXhcbffpxI5ryMdc/edit?tab=t.0) |
| **FCI Block / Unblock Account Guidelines** | Guidelines on placing/uplifting blocks under FCI Investigation. | [Link](https://confluence.toolsfdg.net/pages/viewpage.action?pageId=271712026) |
| **FCI Offboarding Standards and Guidelines** | Guidelines on offboarding decisions and required approvals. | [Link](https://docs.google.com/document/d/1ERzC0YQP7dFIsKJbhzxnE2qTDQtR3tef0Z4lDemWrbk/edit?tab=t.0) |

---

## 7. Definition [1]

| Term | Description |
| :--- | :--- |
| **Binance Admin System (BA)** | In-house platform to allow searches and download of Binance users' personal and transaction information. |
| **CICM HD** | In-house case management system to collect and process ICR/UAR escalation from L1/L2 teams. |
| **Confluence** | Collaboration software by Atlassian for documentation and content management. |
| **Financial Crimes Investigator (L2)** | Person conducting holistic review of accounts with escalated suspicious activities to recommend next actions (retain, close, escalate). |
| **Haodesk System (HD)** | In-house platform supporting case management systems (CICM, Off-Chain TM, Chats, Mail). |
| **Investigation Case Referral (ICR)** | Summary of an unusual activity review conducted by a compliance/AML analyst being escalated to L2. |
| **SAR / STR** | Summary of a suspicious activity review conducted by an MLRO or delegates (L3). |
| **Unusual Activity** | Any activity raising suspicion of potential money laundering, terrorist financing, sanctions evasion, or illicit activity. |
| **Unusual Activity Report (UAR)** | Summary of an unusual activity review conducted by an FCI analyst being escalated to L3. |

---

## 8. Training and Awareness [1]

The allocated investigators of the FCI Team will undergo comprehensive training conducted by the FCI Quality Control (QC) team. The most recent version of the document will be published on Confluence.

---

## Appendix I. RFI and Refund Template [1]

### I. RFI for scam/fraud/single deposit scenario:
*As part of our routine monitoring procedures, we are required to conduct due diligence on your account including obtaining information on certain transactions. Please kindly provide us with the following information with documents on the following transaction:*
*   TxID: [Insert TxID]
*   Type: Deposit
*   Transaction amount: [Amount]
*   Date: [Date]
1.  What was the purpose of this transaction?
2.  What is your relationship to the counterparty?
3.  Please provide the information about the source wallet including owner of the source wallet, type of the source wallet (Trust Wallet/Exchange Wallet).
4.  Please provide supporting documents for proof of source of funds (e.g. conversation history, invoices/bank statement, deposit video).

### II. Refund Template (To be sent if suspect is unable to provide evidence):
*Binance has received a report of the aforementioned transaction being linked to fraudulent activities and the victim has provided sufficient evidence... We strongly suggest that you resolve the issue with the counterparty by returning the funds.*
*If you agree to return the funds, please provide us with the following:*
*   **Video Requirement:** "Today is day/month/year I request the transfer of [Insert coin name+amount] from my binance account xxxx@xxx.com to the original sender."

### III. FCI Template summary (Example):
*   **Case Context:** In CID xxxx, victim UID xxx reported... Victim sent total xxx USDT to suspect UID xxx.
*   **Evidence:** Victim provided conversation history and concrete supporting documents.
*   **Suspect Defense:** Suspect UID xxx claimed funds sent by friends but provided no corroborating documents. Unwilling to refund.
*   **Conclusion:** Recommend to offboard the suspect.

---

## Appendix II. Unified Scam Category from Security (SSO) Team [1]

**Disclaimer:** This table serves as a guideline. Users are NOT REQUIRED to provide ALL listed evidence. Meeting ANY ONE criteria may be sufficient.

| Type of Scam | Description | Valid Scam vs Not Valid | Evidence from VICTIM (Any ONE validates) | Evidence from SUSPECT |
| :--- | :--- | :--- | :--- | :--- |
| **Fake investment** | Scammers promise high returns through investments by recommending websites/apps or claiming to be experts. | **Valid:** Investment made but no returns.<br>**Not Valid:** High-risk investment with potential losses. | - Chat logs showing promises of returns.<br>- Screenshots of fake investment site.<br>- Ads sent by scammer. | - Context showing they were selling goods/services, not investment.<br>- Proof messages were altered.<br>- Proof funds were loan/debt repayment.<br>- Signed receipts/contracts. |
| **Payment without delivery** | Seller fails to deliver promised goods/services (physical/digital) after payment. | **Valid:** Paid but DID NOT receive service/item.<br>**Not Valid:** Dispute case (Unsatisfied with item). | - Payment confirmation.<br>- Comms indicating non-delivery.<br>- Screenshots of listing. | - Proof of delivery/shipment.<br>- Proof services provided.<br>- Evidence victim refused delivery. |
| **Job or Income scam** | Scammers offer jobs but require deposit before starting work. | **Valid:** Deposit paid but no job provided.<br>**Not Valid:** Misunderstanding of terms. | - Chat logs/offer emails with upfront fee requests.<br>- Screenshots of platform.<br>- Ads/Social profiles. | - Documentation of Job Offered.<br>- Documentation victim was informed of non-selection. |
| **Impersonation scam** | Scammers impersonate support, police, tax bureaus to request transfers. | **Valid:** Funds transferred due to impersonation.<br>**Not Valid:** Genuine communication misinterpreted. | - Payment receipts.<br>- Comms logs.<br>- Screenshots of fake profiles. | - Proof of genuine communication intent.<br>- Proof of real identity.<br>- Evidence they never used fake profiles. |
| **Off-platform crypto exchange** | Conducting exchanges outside authorized platforms and failing to complete transfer. | **Valid:** Funds transferred but no crypto received.<br>**Not Valid:** Legitimate transaction delay. | - Transaction records.<br>- Chat evidence of off-platform deal.<br>- Screenshots of platform used. | - Documentation proving transaction completion.<br>- Documentation proving legitimate delays. |
| **Fake token Fraud** | Scammers create fake tokens and trick victims into buying them. | **Valid:** Tokens bought are worthless/scam.<br>**Not Valid:** Legitimate projects. | - Purchase records.<br>- Screenshots of promos.<br>- No real project info.<br>- Wallets dumping tokens. | - Verified contracts.<br>- Project validity proof. |
| **Item Not as Described** | More towards a dispute, not a scam attempt. | - | - Chat logs showing goods received but not as described. | - |
| **Remote Access Scam** | Victim authorizes scammers to control device, leading to fund loss. | **Valid:** Unauthorized access granted & funds transferred.<br>**Not Valid:** Technical issue mistaken for access. | - Transaction history.<br>- Logs showing unauthorized access.<br>- Software installation records. | - Technical reports proving no unauthorized access. |
| **Blackmail or Extortion** | Threats of disclosure of sensitive info unless payment is met. | **Valid:** Victim feels threatened and pays.<br>**Not Valid:** Empty threat, no ransom paid. | - Communication logs for demand.<br>- Threatening texts/voice. | - Evidence disproving actual threat existence. |
| **Attempted scam** | Attempt made but no loss occurs (victim stopped in time). | **Valid:** No financial loss incurred.<br>**Not Valid:** - | - Copies of scam attempts (messages).<br>- Proof of preventive measures. | - Proven service is legit and not scam. |
| **Face2Face Fraud** | Scammer meets victim in person, makes promises, steals crypto. | **Valid:** Victim meets scammer, loses money.<br>**Not Valid:** Meeting honest, no loss. | - Payment Receipt.<br>- Witness statements.<br>- Photos/videos of meetings. | - Recorded conversations to prove innocence. |
| **Known Acquaintance Fraud** | Scammer impersonates someone you know. | **Valid:** Person impersonates acquaintance.<br>**Not Valid:** No impersonation. | - Chat logs showing trust-building.<br>- Sudden requests for crypto.<br>- Messages mimicking known contacts. | - Context showing different context.<br>- Proof messages altered. |
| **Others** | Info suggests scam but doesn't match sub-categories. | **Valid:** Suspicious activity identified.<br>**Not Valid:** Legitimate transaction. | - Proof of payment.<br>- Any supporting doc showing scam. | - Documentation showing proof of service.<br>- Chat logs showing different context. |