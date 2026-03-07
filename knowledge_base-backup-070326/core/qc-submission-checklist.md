# QC Pre-Submission Checklist

## How to Use This Document

**When:** After completing a case, before submitting for QC review.

**Process:**
1. Tell the AI the case type (FTM, CTM, LE, Fraud/Scam, Fake KYC/POA, etc.)
2. Screenshot or describe the completed case sections
3. AI runs through each check below, skipping items marked N/A for the case type
4. AI flags anything missing, incorrect, or at risk of a QC finding
5. Fix flagged items, then submit

**Scoring:** 100 points starting score. Pass mark is 76. One auto-fail (Severe, -25 pts) = borderline fail at 75.

---

## Auto-Fail Checks (Verify These First)

**Any single one of these = case failure. Check these before anything else.**

| # | Check | What Goes Wrong |
|---|-------|-----------------|
| 3.12 | Correct judgment | Decision obviously wrong - e.g., retain user with confirmed fraud, CSAM exposure with warning only |
| 4.2 | Unnecessary RFI sent | RFI with no justification, duplicate RFI, fishing exercise |
| 4.3 | New RFI when previous in progress | Didn't check for existing RFI, didn't contact RFI team |
| 4.5 | Information requested from user is incorrect | Wrong transactions sampled, tipping off the user, internal info disclosed (alert types, WOM codes, possible offboarding), requesting SOW for transactions >2 years old |
| 5.1 | Country MLRO escalation missed | Not escalated or incorrectly escalated per MLRO Matrix |
| 5.2 | Bifinity MLRO escalation missed | No fiat nexus assessment, missed escalation when nexus exists |
| 5.3 | BPay MLRO escalation missed | Not escalated per MLRO Matrix |
| 5.4 | Sanctions escalation missed | Sanctions exposure found but not forwarded to Sanctions team |
| 6.1 | Off-boarding not filed within 30 days | MLRO approved but off-boarding request not submitted in time |
| R.5 | Wrong judgment on RFI response (change of outcome) | User should have been offboarded based on replies / uncooperative history, but was retained instead |

---

## AI Pre-Submission Verification Process

**When the investigator says "run QC checks" or "check before I submit":**

1. **Identify case type** from the case details (FTM/CTM/LE/Fraud/Fake KYC/etc.)
2. **Check auto-fail items first** (Section: Auto-Fail Checks above) - flag any at risk
3. **Run through each section sequentially** (KYC > Suspicious Activity > Main Body > RFI > Escalations > Off-boarding > Attachments > Others)
4. **Skip checks marked N/A** for the case type
5. **For each check:**
   - State what the check requires
   - Confirm whether it's satisfied or flag what's missing
   - If uncertain, ask the investigator to screenshot the relevant section
6. **Summarize findings** with estimated point impact
7. **Recommend fixes** before submission
8. **Run additional quality checks:**
   - All local currency amounts include USD equivalent in square brackets
   - No use of the word "pending" in narrative text
   - No SAR/reporting references in conclusion
   - Every analytical section (CTM, counterparties, exposed addresses, transactions) contains an explicit risk position statement (mitigated because [reason] or cannot be mitigated with available information)
   - Hexa content preserved (modified in-place, not rewritten) with Supplemental Analysis appended below
   - For corporate accounts: "the user" replaced with "the company" / "the entity" throughout
   - Operation log completed
   - "Save All and Generate" used for attachments

---

## Quick Reference: All 48 Investigator Checks

**Severity key:** S = Severe/Auto-fail (-25) | Ma = Material (-10) | Mo = Moderate (-5) | Mi = Minor (-2) | Ob = Observations (-1)

**Applicability key:** Y = Applicable | N = Not applicable | - = Not confirmed

---

### KYC (5 checks, up to 25 pts at risk)

| # | Check | Severity | Inv | Fraud/Scam | Agents |
|---|-------|----------|-----|------------|--------|
| 1.1 | Name matches ID | Mo (5) | Y | Y | Y |
| 1.2 | Nationality/residency correct | Mo (5) | Y | Y | Y |
| 1.3 | Address correct | Mo (5) | Y | Y | Y |
| 1.4 | ID number / issue country correct | Mo (5) | Y | Y | Y |
| 1.5 | Corporate: KYC rewritten to KYB | Mo (5) | Y | Y | Y |

---

#### Section 2: Suspicious Activity
**Total risk:** Up to 2 points (1 check).

#### 2.3 Correct Phase Selected
**Severity:** Minor (2 pts) | **Applies to:** Inv cases only
**Verify:**
- Phase selection matches the investigation depth actually performed
- Pre-Check and Initial Investigation tabs are exclusively for CTM/FTM queue cases
- Non-CTM/FTM cases must use "Lifetime Suspicious Activity"
- Points deducted if a lower phase was selected to avoid completing the required full review

---

### Main Body of the Report (12 checks, up to 76 pts at risk)

| # | Check | Severity | Inv | Fraud/Scam | Agents |
|---|-------|----------|-----|------------|--------|
| 3.1 | Previous blocks mentioned and summarized | Mi (2) | Y | N | N |
| 3.2 | Risk reported by L1 is addressed | Ma (10) | Y | Y | Y |
| 3.3 | Transactional activity described, FTM alerts addressed | Mo (5) | Y | Mo/Mi | Mi (2) |
| 3.4 | High-risk addresses analyzed, CTM alerts mentioned | Mo (5) | Y | **N/A** | **N/A** |
| 3.5 | Counterparties assessed properly | Mo (5) | Y | **N/A** | **N/A** |
| 3.6 | Previous UAR outcomes mentioned and addressed | Ma (10) | Y | Y | Y |
| 3.7 | Privacy coin usage mentioned and mitigated | Mo (5) | Y | Y | Y |
| 3.8 | Device usage (including sharing) analyzed | Mo (5) | Y | Y | Y |
| 3.9 | IP locations analyzed | Mi (2) | Y | N | N |
| 3.10 | Fiat channels mentioned | Mi (2) | Y | Y | Y |
| 3.11 | LE enquiries mentioned and addressed | Mo (5) | Y | Y | Y |
| 3.12 | Correct judgment on the case | **S (25)** | Y | Y | Y |

---

### RFI (6 checks, up to 100 pts at risk - contains 3 auto-fails)

| # | Check | Severity | Inv | Fraud/Scam | Agents |
|---|-------|----------|-----|------------|--------|
| 4.1 | RFI SHOULD have been sent but was NOT | Ma (10) | Y | - | - |
| 4.2 | RFI should NOT have been sent but WAS | **S (25)** | Y | - | - |
| 4.3 | Previous RFI in progress, new RFI sent without contacting RFI team | **S (25)** | Y | - | - |
| 4.4 | HAODesk RFI template properly filled / removed | Mo (5) | Y | - | - |
| 4.5 | Information requested from user is correct | **S (25)** | Y | - | - |
| 4.6 | Previous RFIs properly analyzed | Ma (10) | Y | - | - |

---

### Attachments (6 checks, up to 25 pts at risk)

| # | Check | Severity | Inv | Fraud/Scam | Agents |
|---|-------|----------|-----|------------|--------|
| 7.1 | UOL and valid ID attached for RJs | Ma (10) | Y | - | - |
| 7.2 | Screenshots properly renamed + OSINT/wallet screening rules | Ob (1) | Y | Y | Y |
| 7.3 | All supporting documents saved and attached | Mo (5) | Y | Y | Y |
| 7.4 | Previous RFI files attached | Mi (2) | Y | - | - |
| 7.5 | Case Team communication evidence attached | Mo (5) | Y | - | - |
| 7.6 | Global report exported | Mi (2) | Y | Y | Y |

---

### Others (5 checks, up to 9 pts at risk)

| # | Check | Severity | Inv | Fraud/Scam | Agents |
|---|-------|----------|-----|------------|--------|
| 8.1 | Local currencies converted to USD/EUR | Ob (1) | Y | Y | Y |
| 8.2 | Report is coherent, no contradictory statements | Mi (2) | Y | Y | Y |
| 8.3 | Using SAR instead of ICR | Ob (1) | Y | Y | Y |
| 8.4 | Typos / repetitive statements | Ob (1) | Y | Y | Y |
| 8.5 | Template comments (///) not deleted | Ob (1) | Y | Y | Y |

---

### RFI Response Handling (5 checks, up to 55 pts at risk - contains 1 auto-fail)

*Currently owned by the RFI team. Will transfer to investigators when the RFI team is disbanded.*

| # | Check | Severity | RFI Team |
|---|-------|----------|----------|
| R.1 | RFI response analysis missing/incorrect/incomplete | Ma (10) | Y |
| R.2 | Re-trigger RFI not sent when required | Mo (5) | Y |
| R.3 | Insufficient/incorrect RFI re-trigger content | Ma (10) | Y |
| R.4 | RFI reviewed within SLA | Mo (5) | Y |
| R.5 | Wrong judgment with change of outcome | **S (25)** | Y |

---

## Detailed Checks

### Section 1: KYC

**Total risk:** Up to 25 points (5 checks x 5 pts).

> "Pay particular attention to the KYC section of the report early because that could be the difference between a case being passed and a case being failed." - Alex

#### 1.3 Address Correct
**Severity:** Moderate (5 pts) | **Applies to:** All case types

**Verify:**
- Address in report matches user's submitted documents
- No duplications or errors from system auto-population
- ID number AND ID issue country match the ID provided for KYC verification

**Where to check (priority order):**
1. KYC certificate > Address Validate (POA section)
2. KYC certificate > Basic Validate (fallback — user-submitted, may be unverified)
3. ID Document address (if no other source available)

**Note:** KYC Approve Info no longer contains address data as of recent system updates. Do not reference KYC Approve Info for address verification.

**Rules:**
- Approved information from Address Validate prevails
- If Address Validate has no data or was refused, address from Basic Validate can be taken — note it is user-submitted
- If address is not available in any of these tabs, indicate the country of residency
- No ZIP code = not a mistake
- Special attention should be given to residence permits

**Common error:** System duplicates - "Jakarta, Indonesia, Indonesia, Jakarta and the postcode two or three times." Always visually compare address against source data. This is a frequent QC catch.

---

#### 1.5 Corporate: KYC Rewritten to KYB
**Severity:** Moderate (5 pts) | **Applies to:** Corporate accounts only

**Verify:**
- KYC section header manually changed to "KYB"
- Includes: date of incorporation, registry number, registration and operating addresses, UBOs
- Nature of business briefly mentioned
- UBOs and corporate's activity analyzed in the main body of the report

**Not applicable for:** Personal accounts, merchant accounts (merchants use KYC, not KYB - mention merchant status in template).

**Note from QC:** If no progress on KYB compliance after several months, points deduction increases.

---

### Suspicious Activity (1 check, up to 2 pts at risk)
| # | Check | Severity | Inv | Fraud/Scam | Agents |
|---|-------|----------|-----|------------|--------|
| 2.3 | Correct phase selected (Pre-Check / Initial / Full Review / Lifetime) | Mi (2) | Y | N | N |

---

### Section 3: Main Body of the Report

**Total risk:** Up to 76 points (12 checks). Contains 1 auto-fail.

#### 3.5 Counterparties Assessed Properly
**Severity:** Moderate (5 pts) | **Applies to:** Inv cases

**Verify:**
- Counterparties assessed properly

**Additional counterparty verification:**
- Block/offboard reason stated at the counterparty entry level, not just in a separate narrative paragraph
- P2P counterparties addressed in a separate paragraph with their own count and totals — not mixed into the Hexa header figures
- For corporate accounts: counterparty risk assessed proportionally against total account volume
- Subject UID does not appear in its own counterparty list (known Hexa error)

---

#### 3.6 Previous UAR Outcomes Mentioned and Addressed
**Severity:** Material (10 pts) | **Applies to:** All case types

**Verify:**
- Previous UAR outcomes mentioned and addressed

**Where to check:** Binance Admin > User > User Report > search by UID > FCI tab

**Additional prior ICR verification:**
- Most recent completed or in-progress ICR has been opened and reviewed in full (not just Hexa summary)
- If prior ICRs reviewed and approved significant portion of account activity, this is referenced as mitigation with scope narrowed to new activity
- LE tickets mitigated in prior cases referenced briefly, not re-analyzed in full

---

### Section 4: RFI

**Total risk:** Up to 100 points (6 checks). Contains 3 auto-fails. Second most critical section after Escalations.

**Section introduction (from QC spreadsheet):**
> Ensure that an RFI is sent in the cases where the circumstances of the case require it. Example: a 19-year-old user who engages in pass-through activities moving funds between wallets supporting the same networks, and does not engage in any trading or earn activities. Should the investigator not provide sufficient mitigation, an RFI should be sent. If RFI is not sent, this will be a QC finding. This criterion also embraces incorrect type of RFI.

#### 4.4 HAODesk RFI Template Properly Filled / Removed
**Severity:** Moderate (5 pts) | **Applies to:** All cases

**Verify (if RFI sent) - required fields:**

| Field | Content |
|---|---|
| RFI Case ID | Unique identifier |
| Date Sent | Date RFI issued |
| Expiry Date | Deadline for response |
| Type of RFI | SOF, SOW, Transaction Justification, etc. |
| Specific risk being mitigated | Which financial crime / compliance risk being addressed |
| Suggested outcome if satisfactory | E.g., "If the user can provide plausible justification to wallet address ... then a retain decision is suggested" |
| Minimum acceptable response | Specific detail level required - if multiple questions asked, specify type and level of detail to consider RFI adequately answered |
| MLRO escalation requirements | Per escalation matrix - provide any necessary clarification if escalation is needed |
| Additional notes (optional) | Any relevant background or special instructions |

**If no RFI sent:** Remove the RFI template section entirely.

---

#### 4.5 Information Requested From User Is Correct
**Severity:** SEVERE - AUTO-FAIL (25 pts) | **Applies to:** All RFI cases

**Verify:**
- Template explicitly mentions the reasoning for sending the RFI, and mentions all necessary escalations to MLRO that should follow
- Information requested from the user is relevant and correct
- Sampled transactions are relevant to the case, spelled correctly, without extra symbols
- Not requesting SOW for transactions completed over 2 years ago - request transaction details instead
- Not asking user to go off-platform

**RFI does NOT contain any references to internal information:**
- Types of alerts / rule codes
- Applicable blocks (e.g., WOM)
- Possible outcomes - never mention the user may or will be offboarded; refer to "possible restrictions to the account"

**Not tipping off the user** - when requesting any information, ensure you are not revealing the investigation

**Previous RFIs:**
- If there are previous RFIs sent to this user, the RFIs and user's responses must be mentioned and summarized in the report
- Incomplete or incorrect analysis of previous RFIs = QC finding
- If RFI was sent and user replied separately in Howdesk chat or RFI tool, screenshot(s) of communication should be saved and attached
- Supporting documents must be reviewed and analyzed
- Generic statements such as "the user provided sufficient documents" without mentioning what documents were provided and their contents not properly analyzed = QC finding

---

#### 4.6 Previous RFIs Properly Analyzed
**Severity:** Material (10 pts) | **Applies to:** Cases with prior RFIs

**Verify:**
- Previous RFIs and user responses mentioned and summarized
- Supporting documents reviewed and analyzed
- If no previous RFIs sent by any Compliance team (EDD, Sanctions, FCI, etc.), state "no previous RFIs" - avoid saying "no previous communication" unless you check the chats as well (there can be no RFIs but lots of service chats so no communication would be incorrect)
- Checking for chats is not obligatory, but investigating previous RFIs is

**Bad example:** "User provided sufficient documents." (Vague, doesn't address if documents were efficient responses, failing to clarify the source and purpose of the funds, which raises further concerns)

**Good example:** "RFI-XX was sent on 2024-01-02 to understand the nature of transactions conducted with wallet XX. The user indicated that the transactions were made with/to [entity] for the purpose of XYZ, provided appropriate responses along with supporting documentation, such as bank statements and proof of ownership of the wallet, which helped clarify the source and purpose of the funds."

**Tip:** "If you find five RFIs, take a screenshot. Say 'there are five RFIs linked to this user.' Then detail each one." - Alex Badici (QC)

---

### Section 5: Escalations

**Total risk:** Up to 110 points (5 checks). Contains 4 auto-fails. Most critical section.

> "Make sure the case is escalated properly. If it's not escalated, that's an auto-fail. There is no room for error there." - Alex Badici (QC)

---

### Section 6: Off-boarding / Retention

**Total risk:** Up to 72 points (7 checks). Contains 1 auto-fail.

#### 6.5 Approvals for Off-boarding Received and Attached
**Severity:** Material (10 pts) | **Applies to:** Off-boarding decisions

**Verify:**
- All approvals received per FCI Offboarding Standards and Guidelines matrix
- Screenshots of correspondence with approvers saved and attached to both HAODesk case and off-boarding request

---

### Section 7: Attachments

**Total risk:** Up to 25 points (6 checks).

#### 7.2 Screenshots Properly Renamed + OSINT & Wallet Screening Rules
**Severity:** Observations (1 pt) | **Applies to:** All case types

**Verify:** Screenshots have descriptive filenames (e.g., "top-10-exposed-addresses" not "Screenshot 2026-02-06").

**OSINT screening rules (QC checks all of these):**
- OSINT screenings done with user's name **as it appears on ID, in the same name sequence as on ID**
- If ID shows name in native language > screen the name in native only (prioritize native name on ID)
- Full name screened including middle name / patronymic name (mostly for CIS countries) - if visible on ID, it must be included
- Generic emails (_@mailbox) should NOT be screened
- For Spanish users > screenings performed with a string in Spanish
- For corporate accounts > OSINTs on UBOs should be added, in addition to OSINTs with company's name
- **OSINT screenings must be provided in PDF format (use Cmd+P / Ctrl+P to print the page to PDF)**

**Wallet re-screening rules (QC checks all of these):**
- Re-screenings attached for top wallets as they appear in the report on the date of investigation
- Screenshots must contain the date of re-screening
- **Elliptic customer profile printout is NOT equivalent to batch screening**
- For screenings returning high-risk ratings > save the screenshot
- Each exposed wallet must be re-screened separately, results attached to case file on Howdesk for each one

---

#### 7.3 All Supporting Documents Saved and Attached
**Severity:** Moderate (5 pts) | **Applies to:** All case types

**Required attachments by situation:**

| Situation | Required |
|---|---|
| **All cases with on-chain** | Wallet re-screenings (date visible, fresh data, NOT Elliptic customer profile printout). Must be saved as dated screenshots or PDF exports — CSV files are not accepted as supporting evidence. If any top wallets return high risk, save those re-screenings separately and attach. Verify that the batch screening screenshot/PDF contains the correct wallet addresses matching the C360 top 10 — screening the wrong addresses is a QC finding. |
| **Adverse media found** | PDF of article + analysis with particular indicators suggesting the person referred to is indeed the user (e.g., image, DOB, ID, etc.) |
| **Device sharing via CSI** | Screenshot from CSI tool saved and attached |
| **Fraud/Scam (SSO)** | (a) screenshot of HAODesk chat with victim + (b) print-out of ICR case from Binance Admin containing victim's claim/arguments |
| **RFI team communication** | Evidence of communication saved and attached (when pending RFI exists on same user) |
| **Off-boarding** | All necessary approval screenshots - TL / deputy manager approvals saved and attached to both HAODesk case and off-boarding request |
| **Previous RFI files** | Supporting documents from previous RFIs attached (see 7.4) |

**Recommended:** Download Excel from C360 for top 10 by value and exposed addresses - data can change over time.

---

#### 7.4 Previous RFI Files Attached
**Severity:** Minor (2 pts) | **Applies to:** Cases with prior RFIs

**Verify:** Supporting documents provided with previous RFI attached to case file on Howdesk (especially those the report specifically refers to).

---

#### 7.5 Case Team Communication Evidence Attached
**Severity:** Moderate (5 pts) | **Applies to:** All
cases with cross-team correspondence
**Verify:**
- ALL approval correspondence (MLRO, TL, Risk Ops,
  Case Team, LE Team, Sanctions, Special
  Investigations, VIP team) is screenshot, renamed
  with descriptive filenames, and attached to the ICR
  case file
- This includes correspondence via HaoDesk, support
  tickets, WEA messages, or any other channel
- Even if the correspondence is recorded in HaoDesk
  system logs, it must ALSO be saved as a separate
  attachment for easy reference
- This is mandatory per current QC parameters

---

#### 7.6 Global Report Exported
**Severity:** Minor (2 pts) | **Applies to:** All case types

**Verify:** Global report exported after final version ready.

**Recommended:** Generate anyway - HAODesk has had saving issues. One button press avoids remediation work.

---

### Section 8: Others

#### 8.2 Report Is Coherent, No Contradictory Statements
**Severity:** Moderate (5 pts) | **Applies to:** All case types

**Verify:**
- No contradictions between sections (e.g., privacy coins section says "no privacy coins observed" in another - HEXA may populate privacy coin data while the transaction overview says otherwise)
- Conclusions follow from evidence
- Risk language matches recommendation (high risk > offboard, not "moderate risk" > offboard)

**RJ note:** Where pattern risks not mitigated and user retained on risk-based approach > add remark: "No financial crime risks noted, however, no [specific explanation] provided."

---

#### 8.4 Typos / Repetitive Statements
**Severity:** Observations (1 pt) | **Applies to:** All case types

**Verify:**
- No typos
- No repetitive statements between sections - summary should synthesize, not repeat the body verbatim

**AI warning:** When using AI to generate summaries, check whether the output overlaps with content already in the report. AI-generated content makes duplication obvious because wording stays consistent.

---

### RFI Response Handling Detailed Checks

#### R.1 RFI Response Analysis Missing, Incorrect, or Incomplete
**Severity:** Material (10 pts) | **Applies to:** All cases with returned RFIs

**Verify:**
- Report contains a summary of the user's reply/replies
- Investigator's reasoning for retaining / offboarding / re-triggering RFI is clearly stated
- Red flags identified in the RFI response are addressed
- All notable documents provided by the user in the RFI response are reviewed and analyzed
- List of acceptable documents referenced (same list is provided to each user in the RFI Response)

**QC finding if:** Response analysis is missing, incomplete, or clearly contradicted by the user's replies.

---

#### R.3 Insufficient or Incorrect RFI Re-trigger Content
**Severity:** Material (10 pts) | **Applies to:** Re-triggered RFIs

**Verify:**
- New re-triggered RFI contains more specific questions targeted at collecting vital information for investigators to conclude the case
- **Copy-pasting of the previous RFI = QC finding** - the re-trigger must be tailored based on what the user did or did not provide

---

## PHASE 4: MANDATORY FIELD VALIDATION (THE "EDIT BUTTON" CHECK)

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

---

### 2. CONDITIONALLY EDITABLE FIELDS (Check only if Edit Button is visible)

- **Prior ICRs:** If editable, ensure the summary is accurate. If not editable (no data), skip.
- **Privacy Coin Review:** If editable (Hexa detected usage), ensure **Prompt #7** is applied. If not editable, skip.
- **Analysis of Facts (L1 Summary):** Check that the auto-populated text is **NOT** an error message (e.g., "AI generation failed"). If it is an error, manually paste the L1 summary.
- **Counterparty Header Validation:** If the counterparty section is editable, verify the Hexa header count and dollar total against C360 spreadsheets: Internal Transfer + Binance Pay only. P2P figures must NOT be included in the header totals.
