# Reviewing On-Chain TM Alerts - Standard Operating Procedure (SOP)  
---
## Table of Contents  
1. Purpose  
2. Scope  
3. Approval & Annual Review  
4. Responsibilities  
5. Procedure  
   5.1 Workflow Graph  
   5.2 Pre-Check Review Phase  
   5.3 Initial Review Phase  
   5.4 Full Review Phase  
6. Product Types  
   6.1 Binance DeFi (Defi_Wallet)  
      6.1.1 Types of DeFi wallets  
      6.1.2 DeFi cases handling specifics  
      6.1.3 OSINT Tools  
   6.2 Rescreening  
7. Related Documents and References  
8. Definitions  
9. Training and Awareness  
10. Compliance Monitoring  
11. Feedback Mechanism  
Appendix I - Red Flags and Risk Level  
Appendix II - Decision Matrix  
Appendix III - Supporting Documents  
Appendix IV - On-Chain Exposure Assessment & Tracing Guidance  
---
## 1. Purpose  
This procedure aims to provide clear guidance on reviewing Investigation Case Referrals (ICRs) referred and escalated to the Financial Crime Investigations (FCI) Team related to on-chain transaction monitoring. It outlines necessary investigative steps in a 3-phase approach to ensure consistent and efficient case handling.
## 2. Scope  
The SOP applies to consistent and effective investigation of accounts with triggered on-chain transaction monitoring alerts within the Binance group. It covers the handling of Unusual Activity Reports (UARs) for on-chain transaction monitoring alerts. The SOP is applicable to ICRs routed to the FCI Team queue on Haodesk - "FCI - Compliance L2 Crypto TM."
## 3. Approval & Annual Review  
- The SOP is monitored and updated continuously for relevance and effectiveness.  
- It is made available on Confluence for FCI team members.  
- Any amendments require review and approval by relevant stakeholders and the policy owner.  
- The procedure is reviewed and approved at least annually by the Head of Function.
## 4. Responsibilities  
| Role                                 | Responsibilities                                                                                                                |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Financial Crimes Investigation Team (FCI) (L2) | Conduct investigation of escalated red flags or unusual transaction activities. Recommend next course of action within SLA. Forward to other teams (Sanctions/Special Investigation) or escalate to MLRO (L3) if applicable. |
| Money Laundering Reporting Officer (MLRO) (L3) | Review escalated cases from L2 teams to evaluate trends of unusual activities in accordance with AML/Sanction/CTF laws. Supervise submission of external SAR to authorities. Decide to retain or offboard the user if applicable. |
---
## 5. Procedure  
The investigation process comprises 3 review phases accessible on Haodesk:  
1. Pre-Check Phase  
2. Initial Review Phase  
3. Full Review Phase  
At each phase, investigators review red flags/unusual activity to decide if escalation is warranted or if risk can be mitigated.
### 5.1 Workflow Graph  
**Sequential Process:**  
1. Start with Pre-Check Review.  
2. Identify alert type and category.  
3. Determine appropriate routing.  
4. Assess if On-Chain Exposure Assessment and Tracing is applicable.  
5. If no material red flags found, case can close at Pre-Check. Else escalate to Initial Review.  
6. In Initial Review, examine past behaviors, risk patterns, user explanations, and transaction context.  
7. If no substantial risk or mitigating info found, close case. Otherwise, escalate to Full Review.  
8. In Full Review, conduct holistic 360 review. Consider escalation to Special Investigation, RFI issuance, MLRO escalation, or offboarding.
### 5.2 Pre-Check Review Phase  
- Identify alert type and category.  
- Validate alert exposure type (Direct/Indirect).  
- For indirect exposures, perform Onchain Exposure Assessment (Elliptic Investigator Tracing) to understand risk.  
- Do not send RFIs or offboard at this stage.  
- Escalate case to Initial Review if material red flags detected.  
- Special cases related to Sanction Lists, Sanctioned Countries, or Terrorist Financing after pre-check do not require further investigation; transfer to Sanctions Investigation or close case according to Guide to Onchain Matrix.

**TRACING REQUIREMENT FOR INDIRECT EXPOSURE (Pre-Check):**
At the Pre-Check phase, blockchain tracing using both Elliptic Lens and Elliptic Investigator is required for indirect exposure in the following alert categories: CSAM, Cybercrimes, and Illicit Activity. Tracing must assess:
- Temporal relevance (transaction timing relative to high-risk entity activity)
- Directional relevance (source vs destination of funds relative to the alert trigger)
- Wallet ownership (does the user control intermediary wallets between their address and the high-risk entity?)
- Unattributed cluster identification (behavioral association with known high-risk entities)
Direct exposures do not require tracing at Pre-Check — the exposure is already confirmed.

**PRE-CHECK/INITIAL COMPLETION EXCEPTION:**
A case may be completed at the Pre-Check or Initial Review phase (without escalating to Full Review) if the user under investigation has already been offboarded or submitted for offboarding by the time of the review. In this scenario, document the existing offboarding status (date, reason, submitting team) and close the case at the current phase. Standard phase limitations (no RFIs, no MLRO escalation, no offboarding at Pre-Check/Initial) remain applicable for all other scenarios.

### 5.3 Initial Review Phase  
Triggered if:  
- Pre-check detects additional red flags on severe alert categories.  
- Case falls under Fraudulent Activity, Gambling, Obfuscation, Platform Risk, ATM, or related typologies.  
Investigative actions:  
- Review prior ICR outcomes and previous alerts.  
- Examine user explanations and communication history.  
- Analyze lifetime top 10 exposed address.  
- Consider if risks can be mitigated by documentation or explanations.  
Decision logic:  
- IF material red flags are found with unresolved risk, ESCALATE to Full Review.  
- ELSE IF mitigating information suffices, CLOSE case at Initial Review.
### 5.4 Full Review Phase  
- Perform comprehensive 360-degree review, including all transactional, behavioral, and communication aspects.  
- Use tools such as 360 dashboard for visualization.  
- May request further RFIs from user.  
- May escalate to Special Investigation or MLRO.  
- May decide to offboard user if needed.
---
## 6. Product Types  
### 6.1 Binance DeFi (Defi_Wallet)  
- Dedicated platform to support decentralized finance operations with non-custodial wallets.  
- Supports multiple cryptocurrencies and DeFi protocols.  
- Investigators must access 'Binance - DeFi' environment on Elliptic for such cases.  
- If no access, escalate to Team Lead or notify via designated channels.  
#### 6.1.1 Types of DeFi wallets  
- MPC (Multi-Party Computation)  
- Seed Phrase  
- Private Key  
#### 6.1.2 DeFi cases handling specifics  
- Different data sources used compared to Binance.com cases.  
- Follow specific SOP for DeFi wallet investigations.
#### 6.1.3 OSINT Tools  
Investigators can use these tools for further blockchain analysis:  
- **Blockchain Explorers**: Track transactions, monitor addresses, view blocks. Examples: Etherscan (Ethereum), PolygonScan (Polygon), BscScan (BSC).  
- **Arkham Intelligence**: Deep analytics with entity ID, transaction tracking, risk assessments, behavior analysis.  
- **Blockscan**: Multi-network explorer supporting cross-chain analysis.  
### 6.2 Rescreening  
- Automated rescreening by Elliptic occurs at 30, 60, and 120-day intervals for continuous risk monitoring.  
- Investigators should perform additional rescreens during case reviews and document screenshots.  
- Check alert timestamps:  
  - Created Time: When alert was generated by Elliptic.  
  - Transaction Time: When transaction occurred.  
- Identify duplicate alerts and genuine rescreens based on risk rating changes and attribution updates.
---
## 7. Related Documents and References  
| Document Name                          | Description/Source                                                                                     |
|--------------------------------------|------------------------------------------------------------------------------------------------------|
| IHRE Rules Library - On-chain         | On-chain risk rules library.                                                                           |
| ICR Review Templates (Phased Approach)| Templates for investigation case reviews.                                                             |
| CTM-FCI Guidance                      | Detailed guidance for on-chain transaction monitoring.                                                |
| Guide to On-Chain TM Matrix           | Specific guide for Sanction Lists, Countries, and Terrorist Financing alerts.                         |
| UAR Report Format and Writing Guidelines | Standard template and instructions for Unusual Activity Report preparation.                            |
| Escalation to Sanctions and Special Investigations | Procedures for referral to Sanctions and Special Investigation teams.                                 |
| FCI Team Protocol for Request for Information (RFI) | Protocol on RFI issuance and handling.                                                                |
| FCI Offboarding Standards and Guidelines | Standards for offboarding users based on investigation outcomes.                                      |
---
## 8. Definitions  
| Term                             | Description                                                                                   |
|---------------------------------|-----------------------------------------------------------------------------------------------|
| ML Push Factors                 | Risk indicators that increase likelihood of suspicious or high-risk activity.                 |
| ML Pull Factors                 | Indicators that reduce perceived risk or justify transactions, lowering overall risk level.   |
| Money Laundering (ML)           | Concealing illicit origins of funds obtained illegally.                                       |
| Proliferation Financing (PF)    | Funding related to Weapons of Mass Destruction (WMD) proliferation.                           |
| Sanctions                      | Preventative measures by governments to prevent illicit activities e.g. AML and CTF sanctions.|
| Terrorist Financing (TF)        | Providing or collecting funds for terrorist activities.                                      |
| On-Chain Transaction Monitoring | Monitoring blockchain transactions for suspicious activity using third-party tools like Elliptic. |
| Off-Chain Transaction Monitoring| Rules-based monitoring of transaction patterns off the blockchain within Binance risk engines.|
| Unusual Activity                | Any transactional or behavioral activity raising suspicions of illicit involvement.          |
| Suspicious Monetary Transaction | Transactions suspected to involve illicitly obtained funds.                                  |
| Investigation Case Referral (ICR)| Summary of unusual activity review escalated to L2 compliance analysts.                      |
| Unusual Activity Report (UAR)   | Summary from L2 analysts escalated to L3 (MLRO) for review.                                  |
| Suspicious Activity Report (SAR)| Summary from MLRO or delegate (L3) for external filing of suspicious activity reports.       |
| User Report                    | Backend module submitting suspicious activity reports generating ICRs.                       |
| Elliptic                      | Third-party blockchain analytics provider for real-time on-chain risk screening.             |
| Blocktracer                   | Binance in-house blockchain analytics tool with blacklisted address databases.                |
| CSI Center                   | Internal tool for reviewing fund flows and user relationship identification.                  |
| IHRE (In-house Risk Engine)  | Binance's central rules engine for off-chain transaction monitoring.                          |
| Binance Admin                 | Internal system with user personal and transactional data.                                  |
| CTM Task pool                 | In-house case management for on-chain transaction monitoring alerts.                         |
| SAR Task pool                 | Former case management system for SAR escalations until Jan 2024.                           |
| CICM HD                      | New case management system post Jan 2024 for ICR escalations.                               |
---
## 9. Training and Awareness  
- FCI team training materials including videos and SOPs are maintained on Confluence accessible to all FCI members.  
- Comprehensive training is provided by the FCI Quality Control team to ensure investigator proficiency.  
- SOP versions and updates are communicated via internal channels including meetings and WEA.
## 10. Compliance Monitoring  
- Binance QA team and Financial Crime Investigations QC Team enforce SOP compliance.  
- Mandatory annual review of FCI SOPs.
## 11. Feedback Mechanism  
- Feedback can be sent via the Financial Crime Investigations FCI QC Bot on Wea.
---
## Appendix I - Red Flags and Risk Level  
| Red Flag Category                 | Definition                                                                                   | Guidance / Risk Level                                          |
|---------------------------------|---------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| Historical On-chain or Off-chain Alerts | Previously triggered transaction monitoring alerts indicating potentially suspicious patterns. | Persistent alerts may reflect elevated residual risk. Assess impact on current evaluation. |
| Unusual Transaction Frequency/Volume | High volume or repeated transaction patterns incongruent with user profile.                | May indicate laundering or other illicit activity; requires thorough investigation.       |
| Exposure to High-risk Counterparties | Transactions involving wallets flagged as high risk or illicit entities.                   | Higher direct exposure increases concern; assess proximity and frequency.                  |
| Use of Privacy Coins or Mixers    | Use of privacy-enhancing cryptocurrencies or mixer services potentially to obfuscate funds. | Consider as material red flag especially if linked to suspicious activities.              |
| IP Address and Device Anomalies   | Access from high risk jurisdictions, frequent switching of IPs, shared devices with risky users. | Manual analysis needed; abnormal patterns suggest potential evasion or third-party control. |
| Lack of User Cooperation          | Failure or refusal to respond to RFIs or provide supporting documentation.                  | Considered red flag; escalate if combined with other concerns.                            |
| Profile and Transaction Discrepancies | Discrepancy between user's profile (e.g., age, occupation) and account activity volume/type. | Especially relevant in cases like students or retirees handling large or unusual volumes. |
---
## Appendix II - Decision Matrix  
| Scenario Description                                  | Checklist                                                                                      | Action / Guidance                                            |
|-----------------------------------------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| Clear and obvious red flags present, consistent with known ML typology | Multiple high-risk red flags in transaction history. No plausible legitimate justification.    | Escalate case immediately without issuing an RFI.           |
| Some red flags present requiring additional info     | Unresolved concerns, but some context or documentation may mitigate risk.                     | Issue RFI and await user response.                           |
| Risk potentially mitigated by user explanation or documentation | User provides plausible and consistent explanations, documentation aligns with activity.      | Consider closing case with monitoring.                       |
| Concern due to incomplete context rather than confirmed illicit activity | Lack of full info but no evidence of intentional illicit behavior.                             | Close case with rationale; hold open for further monitoring if needed. |
| Crypto gambling exposure legality extreme per country | Crypto gambling transactions prohibited or extremely high risk in user's jurisdiction.        | Escalate per crypto gambling transaction risk matrix.       |
---
## Appendix III - Supporting Documents  
| Document Type                                  | Purpose / Remarks                                                                                  |
|------------------------------------------------|--------------------------------------------------------------------------------------------------|
| User operation log                             | Shows detailed user activities relevant to the escalation.                                       |
| Valid ID document                              | Evidence for user identity; if in UOL, additional copies unnecessary.                             |
| Communication screenshots                      | Support replies to RFIs and verify user engagement and explanations.                              |
| Blockchain tracing graphs (TRM, Chainalysis, Elliptic) | Visualization to substantiate tracing analyses and expose risks.                                  |
| World Check screening report                   | Checks for sanctions, terrorism, money laundering, or embezzlement risks.                         |
| Law Enforcement requests and supporting docs  | For MLRO review only; sharing requires written consent from original LE agency.                   |
| Previous account reviews or transaction analyses | Provide context on historical alerts or compliance checks.                                       |
| ID documents of all parties involved           | Required if relevant parties beyond the user are implicated in the case.                          |
| For non-reporting jurisdictions                | Discretionary documentation helping to support or negate exposure risks.                         |
---
## Appendix IV - On-Chain Exposure Assessment & Tracing Guidance  
### 1. Introduction  
Provides framework for assessing on-chain exposure using Elliptic Lens and Investigator tools by applying:  
- Temporal assessment  
- Directional relevance  
- Behavioral assessment (Wallet ownership)  
- Identifying unattributed clusters  
### 2. Understanding Elliptic Lens  
- Aggregated Flows: total value exchanged between clusters on the chain.  
- Exposure Flows: distribution of exposure values across paths.  
- Closest Proximity: minimum hop distance to a high-risk entity.  
- Triggered Rule: identifies source or destination of funds related to alerts.
### 3. On-Chain Indirect Tracing Framework  
#### 3.1 Temporal Assessment  
- Analyze time sequence of transactions to confirm connected flows.  
- Exclude flows outside relevant timeframes or reversed temporal order.
#### 3.2 Directional Relevance  
- Funds movement must align directionally and temporally to establish exposure.  
- Funds flowing to a risk entity from user wallet indicate exposure; reverse flows do not.
#### 3.3 Behavioral Assessment - Wallet Ownership  
- Determine if user controls intermediary wallets through transaction patterns.  
- Bi-directional repeated transactions between user and wallet indicate likely ownership.
#### 3.4 Determining Unattributed Clusters  
- Some wallets lack explicit vendor labels but behave as known services.  
- Grouping such addresses prevents misclassification and improves exposure assessments.
### 4. Sample Cases Walkthrough  
- Apply concepts of funding patterns, temporal overlaps, and exposure materiality to real examples.  
- Close proximity and temporal consistency with high-risk entities elevate case risk level.
### 5. Step-by-Step Guide on Elliptic Investigator Tool  
1. Open Screening in Lens.  
2. Select Link Type and create duplicate investigation to edit.  
3. Sanitize graph by identifying nearest relevant exposure paths; remove irrelevant branches.  
4. Enable "Show date range on flows" for timeline context.  
5. Connect all nodes to fully understand transactional relationships.  

### 5.2 Pre-Check Review Phase (Detailed Steps)  
**Objective:** Identify alert type and category, validate exposure type, perform preliminary on-chain exposure assessment, and determine if escalation is needed.  
**Investigator Actions:**  
1. Review alert details: transaction type, exposure amount, risk score, and counterparties.  
2. Validate exposure type as direct or indirect.  
3. Use Elliptic Lens and Investigator tools for onchain exposure tracing for indirect alerts.  
4. Check user KYC attributes alignment with activity (nationality, residence, VIP status, P2P merchant tag, etc.).  
5. Analyze account overview: total crypto deposits/withdrawals, fiat deposits/withdrawals, Binance Pay activity, P2P purchases/sales, max net asset holding, etc.  
6. Confirm no RFIs, escalations, or offboarding actions are to be performed at this stage.  
7. Escalate case to Initial Review if any material red flags or high-risk exposure detected.  
8. For Sanctions, Terrorist Financing, or sanctioned jurisdictions alerts, route directly to Sanctions Investigation team or close per specific matrix.  
**Special Notes:**  
- Cases with indirect exposure require careful tracing to understand connections with high-risk entities.  
- Use temporal overlap, directional relevance, and wallet ownership concepts during exposure assessment.  

**TRACING REQUIREMENT FOR INDIRECT EXPOSURE (Pre-Check):**
At the Pre-Check phase, blockchain tracing using both Elliptic Lens and Elliptic Investigator is required for indirect exposure in the following alert categories: CSAM, Cybercrimes, and Illicit Activity. Tracing must assess:
- Temporal relevance (transaction timing relative to high-risk entity activity)
- Directional relevance (source vs destination of funds relative to the alert trigger)
- Wallet ownership (does the user control intermediary wallets between their address and the high-risk entity?)
- Unattributed cluster identification (behavioral association with known high-risk entities)
Direct exposures do not require tracing at Pre-Check — the exposure is already confirmed.

**PRE-CHECK/INITIAL COMPLETION EXCEPTION:**
A case may be completed at the Pre-Check or Initial Review phase (without escalating to Full Review) if the user under investigation has already been offboarded or submitted for offboarding by the time of the review. In this scenario, document the existing offboarding status (date, reason, submitting team) and close the case at the current phase. Standard phase limitations (no RFIs, no MLRO escalation, no offboarding at Pre-Check/Initial) remain applicable for all other scenarios.

---
### 5.3 Initial Review Phase (Detailed Steps)  
**Triggered when:**  
- Pre-Check detects severe red flags or complex risks requiring deeper assessment.  
- Cases belong to high-risk categories such as Fraudulent Activity, Gambling, Obfuscation, Platform Risk, ATM risk, and others as defined.  
**Investigator Actions:**  
1. Review historical behaviors, previous ICR outcomes, and off-chain alerts.  
2. Examine broader transactional context and risk patterns.  
3. Validate user communication and responses to prior RFIs.  
4. Analyze Lifetime Top 10 Exposed Addresses for pattern recognition of repeated or related transactions.  
5. Assess Pull and Push Risk Factors using Appendix I definitions.  
6. Decide whether risk can be mitigated with existing information:  
   - IF mitigated → Close case with monitoring.  
   - IF unresolved or emerging high risk → Escalate to Full Review.  
**Prohibited Actions in Initial Phase:**  
- No RFIs sent.  
- No escalation to MLROs.  
- No offboarding initiated.  

**INITIAL PHASE — RE-SCREENING AND RFI ANALYSIS:**
At the Initial Review phase, re-screening of CTM alerts and lifetime top 10 exposed wallets is not obligatory — analysis based on existing data (Hexa-populated content, prior screening results referenced in the case, current alert data) should be sufficient. For prior RFIs at the Initial phase, focus analysis on RFIs relevant to the current case and those where the user provided replies; for other RFIs, the Hexa summary is considered sufficient. Note: Fresh re-screening of all wallets is still required at the Full Review phase.

**90-DAY PRIOR ICR COMPARISON:**
Prior ICRs filed within 90 days of the current alert require specific comparison. The method is:
1. Check whether new alert rule codes have been triggered that were not present in the prior ICR. If yes → escalate to Full Review regardless.
2. If no new rule codes: check whether the triggered TM rules are the same AND the alerted transaction amounts are materially similar (difference not greater than 3x the prior alert amount).
3. If rules and amounts are materially similar: compare Push and Pull factors to determine if the risk profile has changed.
Note: LVP-I (Large Value Payment Inbound) and LVP-O (Large Value Payment Outbound) are different rule codes — the direction of fund flow differs. Do not treat these as the same rule when comparing.

---
### 5.4 Full Review Phase (Detailed Steps)  
**Purpose:** Comprehensive and holistic investigation by conducting a 360-degree review of all user activity.  
**Investigator Actions:**  
1. Access and utilize 360 Dashboard for enhanced visualization of user transactions, relationships, and behaviors.  
2. Perform detailed analysis of transaction flows including on-chain tracing and off-chain activities.  
3. Issue Requests for Information (RFI) to users to clarify source of funds, transaction purposes, and counterparties.  
4. Review user's responses and weigh their sufficiency against observed risk indicators.  
5. Escalate to MLRO if SAR filing, offboarding, or law enforcement reporting is warranted.  
6. Coordinate with Sanctions & Special Investigation teams when appropriate.  
7. Document all findings comprehensively with supporting evidence, tracing diagrams, and communications.  
**Possible Outcomes:**  
- Close case with monitoring.  
- Retain user under enhanced due diligence.  
- Offboard user.  
- File SAR with regulators or law enforcement agencies.  
---
## 6. Product Types (Continued)  
### 6.1 Binance DeFi (Defi_Wallet) (Continued)  
- Access restricted to Elliptic Binance-DeFi environment for trained FCI personnel.  
- DeFi wallet analysis must consider non-custodial nature and privacy challenges inherent to decentralized finance.  
- Investigation toolsets differ from .COM exchange platform approach.  
### 6.2 Rescreening (More Details)  
- Automated rescreening cycles at 30, 60, and 120 days ensure continuous monitoring.  
- Investigators verify rescreen alerts against historical case data.  
- Duplicate alerts identified by:  
  - Same transaction details (timestamp, TxID, amount).  
  - No significant changes in risk rating or exposure type.  
- Genuine rescreen alerts require reassessment when risk rating or exposure changes materially.  
---
## 8. Definitions (Extended)  
| Term                       | Description                                                                                                |
|---------------------------|------------------------------------------------------------------------------------------------------------|
| ML Push Factors           | Indicators or conditions that elevate the user's risk profile (e.g., connection to sanctioned entities).    |
| ML Pull Factors           | Conditions that decrease risk perception, such as adequate source of funds documentation or plausible explanations. |
| Suspicious Monetary Transaction | Transaction suspected of involving proceeds from illicit activities or used in illicit financial flows.   |
| User Operation Log (UOL)  | System-generated record of user account activities assisting in case investigation and anomaly detection.   |
| VIP Status                | Classification indicating high-volume trading, requiring proportionate scrutiny.                            |
| P2P Merchant Status       | Indicates if user engages in peer-to-peer merchant activities with multiple counterparties.                 |
| Unattributed Cluster      | Wallets or addresses lacking explicit labeling but behaviorally associated with known high-risk entities.   |
---
## Appendix I - Red Flags and Risk Level (Expanded)  
| Red Flag                                         | Description                                                                                        | Risk Level              |
|-------------------------------------------------|------------------------------------------------------------------------------------------------|------------------------|
| Historical repeat alerts                         | Multiple past on-chain or off-chain alerts with similar typologies indicating persistent risk.  | Medium to High          |
| Law Enforcement Interaction                      | Presence of LE tickets, subpoenas, or investigations linked to the user.                        | Medium                 |
| Use of Privacy Coins or Mixers                   | Frequent transactions in privacy coins like Monero or Zcash that conceal transactional details. | Medium                 |
| Inconsistent IP address usage                     | User access from countries differing greatly from KYC data without valid VPN explanations.     | High                   |
| Device sharing with high-risk accounts           | Shared devices among users flagged for suspicious behaviors.                                   | Medium to High          |
| Profile and transaction discrepancy               | Demographic data not aligned with account activity, e.g., student with large gambling transfers.| High                   |
| Insufficient response to RFI                       | Failure to provide adequate explanations or documentation upon request.                        | High                   |
---
## Appendix II - Decision Matrix (Expanded)  
- **Scenario: Multiple high-risk red flags detected with no plausible legitimate explanation.**  
  - **Action:** Escalate case without RFI.
- **Scenario: Some red flags present but potential to mitigate with user info.**  
  - **Action:** Issue RFI aiming for clarifications.
- **Scenario: User provides clear and consistent rationales addressing red flags.**  
  - **Action:** Consider case for closure or retention under monitoring.
- **Scenario: Elevated risk due to illegal crypto gambling under local laws.**  
  - **Action:** Escalate case immediately per country gambling legality matrix.
---
## Appendix III - Supporting Documents (Expanded Guidance)  
- Include but not limited to:  
  - User Activity Logs  
  - Valid Identification Documents  
  - Communications with User (RFI replies)  
  - Blockchain Analytics Screenshots (Elliptic, TRM, Chainalysis)  
  - Sanctions and Watchlist Screening Reports  
  - Law Enforcement Request Documentation (with sharing approval)  
  - Historical Case Reviews and Previous SARs
- Provide clear references and links to case folders and supporting evidence for audit trail purposes.