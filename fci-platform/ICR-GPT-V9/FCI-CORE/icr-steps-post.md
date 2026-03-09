# ICR Steps: Offboarding & Post-Submission (Step 22 + Appendices)
## Purpose
This document covers Step 22 (offboarding submission) and all post-submission procedures.
Cross-cutting rules in icr-general-rules.md apply to every step below.
---
## STEP 22: USER INVESTIGATION TAB & OFFBOARDING
**ICR Section:** User Investigation tab (separate tab
from Summary tab in the Investigate section)
**Action:**
1. Switch to the "User Investigation" tab.
2. Fill in the investigation tab details.
3. If offboarding: select the correct reason code.
**Offboarding Reason Code Mapping:**
| Case Finding | Dropdown Value |
|---|---|
| Fraud/Scam | Scams |
| P2P Fraud | C2C/P2P Scammer |
| High Risk/Dissipation | High Potential to Money Laundering |
| Gambling | FC - Gambling |
| Sanctions | Sanction Nexus |
| Terrorism | Terrorism - Other |
| Fake Docs (ID) | KYC - KYC Fraud |
| Fake Docs (Other) | Other Forged Documentation |
| Hacking/ATO | Account Takeover |
| Shared Account | KYC - Purchased or Shared Account |

**THREE-WAY REASON MATCH REQUIREMENT:**
The offboarding reason must be identical across three locations:
1. The ICR conclusion (Step 21)
2. The User Investigation tab dropdown
3. The Offboarding submission in Binance Admin
A mismatch between any of these three is a QC finding. Before submitting the offboarding request, verify all three match exactly.

"High Potential to Money Laundering" should only be used when the investigation directly and independently establishes money laundering activity through the analysis. For cases based on accumulated suspicious indicators, LE referrals alleging ML, or contaminated counterparty profiles where ML is alleged by LE but not independently proven by the L2 investigation, use "Suspicious Transaction Activities" as the default offboarding reason. The offboarding reason reflects what the investigation found, not what LE alleged. LE referrals for money laundering do not automatically warrant the ML offboarding reason.

**L2 Communication Rule:**
FCI (L2) handles ALL communication with the Offboarding
team. Never redirect questions to MLROs.

**CASE REJECTION — LIMITED SCENARIOS:**
Cases may only be rejected (returned without investigation) in three scenarios:
1. Employee account — ask TL to reassign to the appropriate team.
2. Two completely identical ICRs submitted by L1 by mistake — review one, reject the duplicate.
3. Following an explicit L1 request to reject due to a submission error.
No other scenario justifies case rejection. Specifically:
- If there is a pending RFI from a prior case: review the case and retain with reference to the ICR containing the pending RFI. Do not reject.
- If there is an open LE ticket: review the case. If retaining, proceed normally. If offboarding, seek Case Team confirmation via HaoDesk Helpdesk before submitting.
- If there is an active freeze: review the case and escalate to MLRO. Recommend retention with a note that offboarding is not possible until the freeze is resolved.

**BLOCK REMOVAL — OTHER DEPARTMENTS:**
When blocks were placed by a non-FCI department (bank
relations, customer service, local compliance teams),
do NOT remove them during case closure. Document that
the blocks exist in the case. After the case is
resolved (RFI completed, decision made), blocks can be
lifted by contacting the "Bank Relations FCI" internal
chat channel with the UID and request to unblock.
State the retention decision in the request.
Note: This applies only to blocks placed by other
teams. FCI-placed investigation blocks follow the
standard block/unblock procedure per
block-unblock-guidelines.md.

**P2P MERCHANT COMMUNICATION:**
When offboarding a P2P merchant, FCI should reach out to the P2P team as a courtesy via the WEA channel "FCI-Agent-RFIBot" or via HaoDesk Helpdesk (Category: P2P CS Support, Subcategory: P2P x FCI Escalation). Notify the P2P team that the merchant account is being offboarded. Do NOT share investigation specifics, alert types, block reasons, potential outcomes, or any confidential investigation details. This is a courtesy notification, not a gating approval.

**PRE-OFFBOARDING BLOCK RECONCILIATION:**
While FCI does not remove other teams' blocks during case closure (retain decisions), when the case outcome is offboarding, withdrawal blocks placed by CS or other teams must be reconciled to enable WOM:
- Request the originating team to remove their withdrawal blocks (since WOM will be applied by FCI), OR
- Request the blocks be transferred to FCI so FCI can adjust them to ensure WOM is properly configured.
- Document the correspondence with the originating team and attach to the case file.
During offboarding processing, blocks placed by other teams (e.g., Intelligence Fusion Center, CS, EDD) that were not transferred to FCI must be removed by the block requestor team or transferred to FCI. Contact the originating team to request removal or transfer. The general cross-team protocol ("do not unblock other teams' blocks") applies during investigation — the offboarding reconciliation process is the exception that applies only when processing the offboarding submission itself.

**LE BLOCKS PREVENTING OFFBOARDING:**
When active LE blocks (freezes/seizures) exist on an account recommended for offboarding:
- Non-reporting jurisdiction: The case may be rejected — but only after obtaining documented approval from the Case Team or LE Team confirming the seizure/freeze prevents offboarding on the FCI side. Attach the correspondence to the case file.
- Reporting jurisdiction: Review the case, escalate to MLRO, and recommend closure with a note that the Case Team should resubmit the case after the LE matter is resolved.
- Both scenarios: All correspondence with the Case Team regarding LE blocks must be saved, screenshot, renamed, and attached to the ICR report.
OPEN LE TICKETS — CASE TEAM APPROVAL: For users with open LE tickets on Kodex (even without active freezes), approval from the Case Team should be sought before submitting the offboarding request. Submit a ticket via HaoDesk Helpdesk (Category: Compliance Law Enforcement, Subcategory: Internal teams checking if account is under review by LE). Screenshot the approval and attach to the case file. If the Case Team confirms no conflict, proceed with offboarding. If the Case Team advises against offboarding due to an active investigation, retain the user and close the case with a note to resubmit after the LE matter is resolved.

**QUOTA FREEZES AND CHARGEBACK BLOCKS (Exception):**
When an account recommended for offboarding has quota
freezes or chargeback blocks (placed by the banking
team):
1. These blocks are unlikely to be lifted by the
   banking team and constitute an exception to the
   general rule that all unrelated blocks must be
   resolved before offboarding.
2. Create a HaoDesk support ticket to the Risk Ops
   team informing them the account has quota freezes/
   chargebacks and is recommended for offboarding.
3. Wait for Risk Ops team approval before submitting
   the offboarding request.
4. The account can be offboarded with these freezes
   still in place once Risk Ops approval is received.
5. Attach the Risk Ops approval to the ICR case file.

**FRC FREEZES AND C2C FREEZES (Exception):**
When an account recommended for offboarding has active Fund Recovery Case (FRC) freezes or C2C freezes placed by the P2P team:
1. These accounts can be offboarded with these freezes in place.
2. Obtain approval from the P2P team via HaoDesk Helpdesk (Category: P2P CS Support, Subcategory: P2P x FCI Escalation).
3. Screenshot the P2P team approval and attach to the ICR case file.
4. If the user subsequently submits an offboarding appeal or requests withdrawal enablement, transfer the chat to the P2P team — the user must resolve the FRC/C2C dispute with the P2P team first. Only after the freezes are resolved can FCI review the appeal.

**VIP Notification Rules for Offboarding:**
VIP notification and approval tiers are defined in the Offboarding Approval Matrix above. The following rules supplement the matrix:
- VIP status is determined based on the user's operational VIP level within the last 12 months. When multiple VIP designations exist, use the highest level.
- Screenshot ALL VIP notification and approval conversations and attach to the offboarding request.
- If the VIP contact is unresponsive, note "unresponsive" in the VIP section of the offboarding form.
- This is notification and approval as specified in the matrix — for VIP 1-2 POC notifications, do NOT request permission or recommendations. Simply inform that based on the investigation, the user is being offboarded.
- Exception: if VIP team needs to manually engage the user.

**QC Check (Ref: qc-submission-checklist.md #6.2):**
- Reason code aligns exactly with Subject Matter.
- All approvals received and attached.
- WOM applied with correct block reason.
- All unrelated blocks resolved before offboarding.
- Offboarding filed within 30 days of MLRO approval.
- Approval pathway matches account profile type per the Offboarding Approval Matrix (not just balance-based).
- For VIP 7-9 and KOL: ELT Notification Form completed and WEA group screenshot attached.
- For dual-escalation cases: Country MLRO approval obtained (Bifinity/BPay MLRO notification is informational only).
- For open LE tickets: Case Team approval obtained via HaoDesk Helpdesk and attached.

---
**Manual Offboarding Submission Process:**
BEFORE starting this process, ensure:
- All required approvals are obtained (MLRO, TL,
  special approvals if needed) with screenshots saved.
- Check Offboarding Management > All Cases > search
  UID to confirm NO existing offboarding case exists.
  If one exists, do not submit a duplicate.
- User is already under Withdrawal Only Mode (WOM).
  If not, apply WOM first.
- **QC Risk:** If the offboarding request is submitted
  without WOM in place, the user can continue normal
  account activity during the processing period (which
  may take weeks or months). This is a QC finding.
  Always verify WOM is active before clicking Submit.
- Confirm withdrawals are not blocked (user must be
  able to withdraw under WOM).
- **OPEN POSITIONS CHECK (Spot/Margin/Futures):**
  Before offboarding, check User InfoHub > Frozen tab
  and the Spot/Margin tabs for open positions or frozen
  assets related to trading. If open spot, margin, or
  futures positions exist, submit the Compliance Exit
  Google Form to request force-cancellation. The form
  is reviewed on Tuesdays and Thursdays only. Plan
  offboarding submissions accordingly and check for
  updates on those days. Do not submit the offboarding
  request until position cancellation is confirmed.
- If the user has open LE tickets on Kodex: obtain Case Team approval via HaoDesk Helpdesk (Category: Compliance Law Enforcement, Subcategory: Internal teams checking if account is under review by LE) before submitting. Screenshot and attach.
- If the user has active FRC or C2C freezes from the P2P team: obtain P2P team approval via HaoDesk Helpdesk (Category: P2P CS Support, Subcategory: P2P x FCI Escalation) before submitting. Screenshot and attach.

**SYSTEM-APPLIED BLOCKS DURING OFFBOARDING:**
When the "Complete - Offboard" button is clicked in HaoDesk, the system automatically applies a WOM block. No manual WOM application is needed when using this button. However, verify after clicking that WOM was actually applied — system automation does not always execute correctly. If WOM was not applied automatically, apply it manually before the offboarding request processes.

SUBMISSION STEPS:
1. Go to Offboarding Management > Submit Offboarding
   Request.
2. Enter the UID.
3. Check: Is user VIP? Check Binance Admin > Info Hub.
   - If VIP/Merchant: obtain additional approvals per
     Offboarding SOP before proceeding.
   - If balance >$100,000: checker verification and
     team approval required.
   - If regular user with no special status: proceed.
   - If HPI: check Binance Admin > User InfoHub for HPI status. If HPI, obtain approvals per HPI Approval Matrix before proceeding.
   - If KOL: obtain FCMI Manager + CCO approval and notify @KOLUserOffboardingBot before proceeding. Complete the ELT Notification Form.
4. Select Offboarding Reason — must match the reason
   in the ICR case and the User Investigation tab.
5. Withdrawals: Select "Always" (standard for WOM).
6. Remarks: Recommended — include the ICR Case ID and
   a brief summary of: (a) why the case was escalated
   to FCI (referral reason), (b) whether an RFI was
   sent and whether the user was responsive, (c) any
   warnings issued.
7. Body of message: Delete the default template text.
   Paste the Summary and Conclusion from your ICR
   (from Step 20 Part B and Step 21). Remove the
   escalation line — the offboarding team does not
   need that.
8. Below the body: Paste the ICR Case ID.
9. Below the Case ID: Paste the approval comment block:
   MLRO Approval: Approved / Not Required
   Team Lead Approval: Approved / Not Required
   FCMI Manager Approval: Approved / Not Required
   Enterprise Compliance Director Approval: Approved / Not Required
   CCO Approval: Approved / Not Required
   Special Approval: Not Required
   ELT Notification: Completed / Not Required
   Adjust each line according to what was needed for
   this specific case per the Offboarding Approval Matrix.
10. VIP Section (below approvals):
    - If VIP: Enter POC name from Binance Admin Info
      Hub and acknowledgement status.
    - If not VIP: Leave blank.
11. Approval Documents: Upload the MLRO approval
    screenshot (and any other approval screenshots).
    - If no approval document exists (cases where no
      MLRO escalation was needed): paste the ICR case
      URL in the URL field instead — the system
      requires at least one attachment or URL.
12. Click Submit.

**MULTI-USER OFFBOARDING (>1 UID):**
The automated HaoDesk offboarding processes one UID at a time. For cases with multiple UIDs requiring offboarding:
- If 2-5 UIDs: Submit each offboarding request individually through the standard manual process. Each UID requires its own offboarding submission with the same reason and approval documentation.
- If >5 UIDs: Use the "Skip Offboard" option in HaoDesk, then submit offboarding requests manually via Binance Admin for each UID.

**BATCH OFFBOARDING (6+ UIDs from same investigation):**
For investigations resulting in offboarding of 6 or more UIDs (e.g., batch fake KYC, coordinated fraud rings):
- Since December 2025, batch offboarding approvals are routed automatically through Binance Admin via WEA notifications.
- Approvers receive approve/reject buttons in their WEA notifications — no manual messaging or screenshot sharing is required for the approval step itself.
- The investigator still must screenshot and attach the final approval confirmation to the ICR case file.
- Batch offboarding follows the same approval matrix as individual offboarding — each account profile type within the batch must meet its respective approval requirements.

**Automated Offboarding:**
When the MLRO clicks "Complete - Offboard" on the case, the system may automatically submit the offboarding request. Check Offboarding Management > All Cases before manually submitting to avoid duplicates. This automation does not always work — always verify.
AUTOMATIC OFFBOARDING UID LIMIT: Cases with more than 5 UIDs cannot use the automated HaoDesk offboarding. For multi-UID cases exceeding this limit, use "Complete - Offboard" → scroll down → select "Skip Offboard to proceed case update," then submit manually via Binance Admin for each UID.
ALREADY OFFBOARDED: If the user is already offboarded (existing OB request found in Offboarding Management > All Cases), select "Complete - Offboard" → scroll down in the pop-up → select "Skip Offboard to proceed case update." This applies the correct case status without creating a duplicate offboarding request.

**OFFBOARDING APPROVAL MATRIX (Profile-Based — Effective UAR Framework v3.1, February 2026):**
Approval requirements are determined by account profile, not balance or trade volume.
Standard Accounts (No special status):
→ No additional approvals required beyond standard L2 recommendation and L3/MLRO review (where applicable per jurisdiction).
Regulated Jurisdiction (User resides in licensed jurisdiction per mlro-escalation-matrix.md):
→ Country MLRO approval required.
Corporate Account:
→ TL + FCMI Manager (or Designate) approval required.
VIP 1-2:
→ TL + FCMI Manager approval required.
→ If POC (VIP Manager) exists in Binance Admin > Info Hub: notify the POC via WEA. Screenshot and attach.
→ If no POC exists: no VIP Manager notification required.
VIP 3-6:
→ TL + FCMI Manager + Enterprise Compliance Director approval required.
→ Notify jonathan.yy@binance.com or xia.yu@binance.com.
→ Complete the Compliance VIP or KOL User Block / Offboard ELT Notification Form (see ELT NOTIFICATION below).
VIP 7-9:
→ TL + FCMI Manager + Enterprise Compliance Director + CCO (Noah Perlman) approval required.
→ Complete the Compliance VIP or KOL User Block / Offboard ELT Notification Form (see ELT NOTIFICATION below).
KOL (Key Opinion Leader):
→ FCMI Manager + CCO approval required.
→ Notify @KOLUserOffboardingBot.
→ Complete the Compliance VIP or KOL User Block / Offboard ELT Notification Form (see ELT NOTIFICATION below).
HPI (High Profile Individual — check Binance Admin > User InfoHub):
→ Follow the HPI Approval Matrix. HPI requirements apply IN ADDITION to any VIP-tier requirements.
P2P Merchant:
→ As a courtesy, notify the P2P team before offboarding (see P2P Merchant Courtesy Notification in block-unblock-guidelines.md). This is a notification, not a gating approval.
Internal Employee:
→ TL + FCMI Manager + Enterprise Compliance Director approval required. Treat as complex case for ADGM SLA purposes.
CUMULATIVE RULE: If an account has multiple statuses (e.g., Corporate + VIP 3), ALL applicable approval paths must be satisfied. The paths are cumulative, not alternative.
VIP LEVEL RULE: When a user has multiple VIP designations (e.g., Ops VIP 1 / VIP 3), treat the user as the HIGHEST VIP level for approval and notification purposes.
DUAL ESCALATION OFFBOARDING RULE: For cases escalated to both a Country MLRO and Bifinity/BPay MLRO, only the Country MLRO approval is required to proceed with offboarding. The Bifinity/BPay MLRO notification is for information and reporting purposes — it is not a gating approval.
Enterprise Compliance Director Delegation: In the absence of an Enterprise Compliance Director, the FCMI Manager may act as delegate for approval purposes. Confirm current delegation status with TL if uncertain.

**ELT NOTIFICATION PROCESS (VIP 7-9, KOL):**
When an account has VIP status 7-9 or KOL status, the Executive Leadership Team must be notified:
1. Make a copy of the "Compliance VIP or KOL User Block / Offboard ELT Notification Form"
2. Complete all fields
3. Create a WEA group with the following ELT Committee members: Richard Teng (CEO), Sunny (Operations Director), Roger (COO), He Yi (Co-Founder), Aaron Chua (Head of CS), Noah Perlman (Global CCO), Catherine C (Head of VIP)
4. Share the completed form in the WEA group
5. Screenshot the WEA group conversation and attach to the ICR case file and offboarding request
This is notification only — ELT does not approve or reject the offboarding decision. The required approvals per the matrix above must be obtained separately.

**WARNING TEMPLATES FOR OFFBOARDING-ADJACENT SCENARIOS:**
When the investigation outcome is a warning rather than offboarding, and the warning relates to activity that could lead to future offboarding if repeated:
- Gambling warning: "Interaction with high-risk gambling-related addresses has been identified on your account. Please refrain from future interactions with such addresses. Continued interaction may result in restrictions on your account."
- Shared account warning: "Activity patterns suggest your account may be accessed by or shared with third parties. Binance accounts are for individual use only. Please ensure your account is used solely by you."
- High-risk address warning: "Interaction with addresses associated with high-risk activity has been identified. Please exercise caution and refrain from future interactions with such addresses."
These are templates — adjust the specific language to the case facts. Warnings are sent via HaoDesk, not Binance Admin back end.

---

## Pre-Submission Requirements
*Relocated from icr-general-rules.md — applies to this step only.*

- **Pre-Submission Requirements:** Before final
  submission, ensure: (1) the operation log is
  completed, and (2) "Save All and Generate" has been
  used in the case status section to automatically
  attach all necessary documents and details. All
  supporting documentation must be uploaded directly
  to HaoDesk. The previously-used B-Office upload system
  is deprecated and applies only to legacy cases
  predating the migration.

**TEMPLATE CLEANUP:** Before submission, scan the
entire ICR for bracketed or parenthesised
instructional text (e.g., "[delete this]",
"_(delete: provide summary...)_",
"_(delete: manual review required...)_"). These are
template guidance comments and must be removed. They
commonly appear as suffixes to section headings in
the older full-page ICR format. Leaving them in the
final report is a QC finding (8.5, -1 point). The
AI should flag any remaining instances during QC
pre-submission checks by scanning for patterns:
"(delete:", "[delete", "_(delete", "please delete",
and any italic text containing instructions.
Additionally, scan for HaoDesk default instructional
text that appears in editable sections but is not
part of the case narrative. Known instances include:
"Click the refresh button in this section if RFIs
are issued" (RFI Analysis Summary section),
"Manual summary required" (multiple sections), and
"Manual review required" (multiple sections). When
no RFI was issued, retain only the substantive
default text ("No RFIs were issued during this
investigation, and no RFI analysis is available")
and delete any instructional text that follows it.
When a section has been populated with analysis,
delete all "Manual summary required" or "Manual
review required" placeholder text. Any system-
generated instructional text remaining in the final
report is a QC finding.

**OLDER FORMAT ICR — SAVE WARNING:** The older
full-page ICR format (used for multi-user cases and
some legacy case types) does NOT auto-save. The
investigator must manually click "Save" at the
bottom of the page after every significant edit.
Drafting in a Word document and pasting in is an
acceptable alternative workflow to avoid data loss.

---

## Mandatory Field Validation (The "Edit Button" Check)
*Relocated from icr-general-rules.md — applies to this step only.*

**Objective:** Ensure all mandatory fields in the Hexa report system are populated.

**Logic:**
- **Always Editable:** These sections *always* have an edit button and *must* contain analysis (even if it is just "0/10000" or "No data").
- **Conditionally Editable:** These sections only show an edit button if Hexa pulls data. If no edit button exists, they are skipped.

**Action:** Scan the final report. If any of the "Always Editable" fields below are **blank** or contain **error messages**, the report is **FAIL**.

### 1. ALWAYS EDITABLE FIELDS (Must never be empty)

| **ICR Section** | **Minimum Required Content** |
| :--- | :--- |
| **User Transaction Overview** | Must contain **Prompt #1 output** (Velocity, Ratios, Fund Flow summary). |
| **Lifetime Top Addresses by Value** | **CRITICAL:** Requires Elliptic screening. Must contain analysis or "0/10000". |
| **Internal Counterparty Analysis** | Must contain analysis of links or "No data". |
| **Device and IP Analysis** | Must contain **Prompt #9 output** (Locations, Consistency, Shared Devices). |
| **OSINT** | Must contain specific findings or "Open source research has been performed but no specific / negative news has been identified". |
| **User Communication** | Must summarize chat history/responsiveness or state "No response received." |
| **Any Other Unusual Activity** | Must contain "0/10000" or "None identified." |
| **RFI Issued** | Must state "No RFI issued..." or provide RFI Summary. |
| **RFI Analysis Summary** | **NEW:** Must contain analysis of the user's response to the *current* RFI. If no RFI was sent, must state: *"No RFIs were issued during this investigation, and no RFI analysis is available."* |
| **Summary of Unusual Transactions** | Must calculate Total Value and Date Range (e.g., "TOTAL UNUSUAL TRANSACTIONS: X"). |
| **Conclusion (IV)** | Must contain full narrative summary + Final Recommendation (Retain/Offboard/Refund). Must NOT contain: the word "pending," references to reporting/SAR/STR, or one-sided adverse narrative without mitigating context. All local currency amounts must include USD equivalent in square brackets. For offboarding recommendations: must explicitly state "offboarding with withdrawals enabled" or equivalent — omission is a rejection trigger. The only exceptions are active LE seizure/freeze or explicit Sanctions/SI team instruction to restrict withdrawals, which must be stated with the authority reference. For "close to avoid duplication" cases: must contain (1) what was reviewed, (2) key risks, (3) open RFI reference, (4) reason for closure. |

### 2. CONDITIONALLY EDITABLE FIELDS (Check only if Edit Button is visible)

- **Prior ICRs:** If editable, ensure the summary is accurate. If not editable (no data), skip.
- **Privacy Coin Review:** If editable (Hexa detected usage), ensure **Prompt #7** is applied. If not editable, skip.
- **Analysis of Facts (L1 Summary):** Check that the auto-populated text is **NOT** an error message (e.g., "AI generation failed"). If it is an error, manually paste the L1 summary.
- **Counterparty Header Validation:** If the counterparty section is editable, verify the Hexa header count and dollar total against C360 spreadsheets: Internal Transfer + Binance Pay only. P2P figures must NOT be included in the header totals.

---

## Fraud/Scam Case Template Cleanup
*Relocated from icr-general-rules.md — applies to this step only.*

For fraud/scam cases (SSO-referred scam, P2P fraud,
single deposit risk), certain ICR sections are not
applicable per the QC checklist (ref:
qc-submission-checklist.md). These sections should be
REMOVED from the template entirely rather than left
blank or populated with placeholder text.
Sections to remove for fraud/scam cases:
- Previous blocks (QC #3.1: N/A for Fraud/Scam)
- High-risk addresses / Top 10 exposed addresses
  (QC #3.4: N/A for Fraud/Scam)
- Counterparties (QC #3.5: N/A for Fraud/Scam)
CRITICAL: If a non-required section is left in the
template and populated with incorrect or incomplete
analysis, QC will assess it as if it were required
and deduct points for errors. The safest approach is
to delete the section entirely. If retained, the
content must be accurate — "not applicable" or
removal is preferred over incorrect analysis.

**FRC/C2C FREEZE HANDLING IN FRAUD CASES:**
For fraud/scam cases where the suspect account has
active Fund Recovery Case (FRC) freezes or C2C
freezes from the P2P team:
- The account can be offboarded with these freezes
  in place after obtaining P2P team approval
- Submit approval request via HaoDesk Helpdesk
  (Category: P2P CS Support, Subcategory: P2P x FCI
  Escalation)
- If the user subsequently appeals or requests
  withdrawal enablement, transfer the chat to the
  P2P team — the user must resolve the FRC/C2C
  dispute first

---
## APPENDIX B: BIFINITY UAB CHANNEL LIST
For use at Step 13 — Fiat Transactions.
Paysafe, Eternal, Mobilum, checkout, HzBankCard,
WorldPay, SafeCharge, Modulr, TrueLayer, SafetyPay,
Zenpay, applepay, googlepay, GIROPAY, zenpaycorp, emp,
paynetics, nuveiocbs, nuveisepa, paysafewithdraw,
bebawaocbs, bebawacorp, unlimit, easyeuro, paytend,
gpsafechargecom, apsafechargecom, revolut,
bankingcircle, apworldpaycom, gpworldpaycom,
easyeurocorp, blik, apempcom, gpempcom, paypal, blikocb.
Sunset Clause: Do NOT escalate alerts generated AFTER
09 February 2026. Technical capability ends 09 March
2026.
---
## APPENDIX C: POST-SUBMISSION CHECKS
After a case is submitted and completed:
1. The case does NOT return to your queue.
2. To check the MLRO response: Go to HaoDesk >
   Service Cases > All Cases > search by case ID
   or UID.
3. Check the L3/MLRO tab on the left side to read
   their comments and recommendation.
4. Check the User Investigation tab to see if the
   MLRO changed the offboarding reason or decision.
5. If the MLRO approved offboarding:
   - Check Offboarding Management > All Cases to see
     if the automated offboarding was triggered.
   - If it was: no further action needed.
   - If it was not: submit manually per Step 22.
6. Screenshot the MLRO approval (Summary page showing
   their decision and comments) — label as
   "MLRO_Approval_[CaseID].png"
7. Record the outcome if the MLRO disagreed with your
   recommendation or if you learned something from
   their comments: add one row to decision-matrix.md
   and one full narrative entry to
   case-decision-archive.md using the next available
   sequential number.
---
## APPENDIX D: OFFBOARDING APPEALS PROCESS
**Trigger:** A CS agent assigns an offboarding appeal
to the original investigator via HaoDesk (Support >
Related to Me).
**SLA:** 7 days from escalation date.

**APPEAL ASSIGNMENT:** Appeals are assigned to the original investigator who submitted the offboarding case. If the original investigator is unavailable (left the team, on extended leave), the TL reassigns the appeal to another team member. The reassigned investigator must review the original case file in full before conducting the re-evaluation.

**Scope of Review:** This is NOT a full case review.
The investigator must:
1. Re-examine the original red flags and the
   offboarding rationale
2. Check whether the user has now responded to any
   previously unanswered RFIs
3. Check whether new information or justification
   has been provided via the appeal

**ONE-TIME APPEAL:** Users are permitted one appeal only. If a user has previously submitted an appeal and the offboarding decision was upheld, inform them that the account remains permanently offboarded and will be closed. No further re-evaluation is conducted.

**RE-EVALUATION STANDARD:** The re-evaluation must be based on the current compliance standard to determine if offboarding reversal can be considered. If compliance standards or risk appetite have changed since the original offboarding decision, the current standard applies — not the standard at the time of the original decision.

**Three Possible Outcomes:**
1. **Remain Offboarded:** The original decision stands.
   Provide a brief explanation in the resolution field
   stating the red flags remain unmitigated.
2. **Reverse Offboarding:** The user provided sufficient justification or new information that mitigates the original concerns.
   APPROVAL REQUIREMENTS FOR REVERSAL:
   - Licensed jurisdiction (user resides in jurisdiction with local MLRO): Country MLRO approval required, following the standard MLRO Escalation Requirements Matrix (mlro-escalation-matrix.md / mlro-escalation-decisions.md).
   - Non-licensed jurisdiction where the original offboarding required no additional approvals: The reversal may proceed without additional approvals, provided the re-evaluation confirms the risk profile is within current FCMI risk appetite.
   - High-value accounts (VIP, corporate) regardless of jurisdiction: TL/Manager approval required.
   - The principle is: the reversal follows the same approval pathway as the original offboarding decision. If the original required MLRO, the reversal requires MLRO. If the original required no additional approvals, the reversal requires no additional approvals (subject to the high-value exception above).
   REVERSAL SUBMISSION: Navigate to Binance Admin > Compliance > Offboarding > Offboarding List > search UID > select > click "Trigger Reversal Offboarding Request." Complete: Department, Reason for reversal, Remarks. Upload approval screenshots. Submit. A WEA notification from Binance Admin Assistant will confirm when the reversal is executed.
   Screenshot the MLRO/TL approval (where required) and upload to the HaoDesk case.
   Consult the standard MLRO Escalation Requirements Matrix (mlro-escalation-matrix.md / mlro-escalation-decisions.md) for the relevant jurisdiction MLRO. The same escalation matrix used for case-level MLRO routing applies to appeal reversals.
3. **RFI:** The risk could be mitigated if the user
   provides specific information. Since the user is
   already offboarded, either:
   (a) Contact the offboarding team to temporarily
       reopen the account for RFI response, OR
   (b) Relay the RFI questions to the CS agent via WEA
       and ask them to send a chat to the user with a
       response deadline (e.g., 7 days).
   WITHDRAWAL-ONLY APPEAL PATH: If the appeal is solely about enabling withdrawals (user wants to withdraw remaining funds from an offboarded account), and no other grounds for reversal are presented, this can be handled by enabling withdrawal-only access without reversing the offboarding. Coordinate with the offboarding team to enable withdrawals if appropriate. This does not require MLRO approval unless the original offboarding included a specific instruction to restrict withdrawals.

**Resolution Fields:** Fill in the compliance tag, the
user's UID, and provide a brief explanation of the
decision in the resolution/solution field.
Note: This process is subject to SOP updates. Check
Confluence for the latest offboarding appeals matrix.

**FINDING THE ORIGINAL INVESTIGATOR:**
When a CS agent assigns an offboarding appeal and the original investigator needs to be identified:
1. HaoDesk > Service Cases > All Cases > search by UID
2. Filter for ICR cases associated with the UID
3. The investigator who submitted the original case is the assigned reviewer for the appeal
4. If the original investigator is no longer available (left the team, on leave), the TL assigns the appeal to another investigator on the team
---
## APPENDIX E: STANDARD ATTACHMENT CHECKLIST

The following attachments must be uploaded to HaoDesk
before submission. Items in the "NOT uploaded" category
are already present from L1 or system-generated and do
NOT need to be re-uploaded by the investigator.

**Always required (investigator uploads):**
- UOL export (required on ALL cases regardless of
  jurisdiction or case type)
- Elliptic batch screening PDF or dated screenshot
- Elliptic individual wallet detail PDF for every
  wallet scoring 5 or above
- OSINT results saved as PDF (including no-trace
  results)
- Global report export (generated after final save
  via "Save All and Generate")

**Conditionally required (investigator uploads):**
- RFI correspondence screenshots (if RFI sent)
- MLRO approval screenshot (if escalation made)
- VIP/KOL/HPI notification screenshots (if applicable)
- Case Team approval screenshot (if open LE tickets
  exist and offboarding)
- Risk Ops / P2P team approval screenshots (if quota
  freezes, FRC/C2C freezes exist)
- Refund request screenshot (if fraud case with refund)
- Sanctions team referral screenshot (if escalated)
- Non-English OSINT translations (if adverse media
  found in non-English language)

**NOT uploaded by investigator (already in HaoDesk or
not required):**
- L1 referral attachments (already attached by L1 —
  do not duplicate)
- Kodex case screenshots (not required as attachments
  — LE data is documented in the ICR narrative from
  Binance Admin review)
- C360 transaction summary screenshots (not required
  as attachments — data is narrated in the ICR body)
- C360 spreadsheet downloads (working documents used
  for analysis — not attached unless specifically
  required for a data point that cannot be narrated)
---