# ICR Steps: Setup & Context (Steps 1-6)
## Purpose
This document covers Phase 0 (pre-investigation) and Steps 1 through 6 of the ICR form. These steps establish who the subject is, why the case exists, and what history is relevant. Cross-cutting rules in icr-general-rules.md apply to every step below.

---

## SLA Framework
*Relocated from icr-general-rules.md — applies to this step only.*

- **Standard SLA Tiers:** Standard DDM-agreement
  cases require completion within 5 days. Complex
  investigations require completion within 10 days.
  FTM/CTM alert review cases (FCI - Compliance L2
  Crypto TM queue) have a 30-day SLA from case
  creation date. Active SLA monitoring is in place —
  cases approaching or exceeding the 30-day window
  will generate reminders. Investigators should
  prioritize completing assigned cases before
  self-assigning new cases to avoid SLA breaches. If
  a case appears to fall under a DDM SLA (e.g., VIP,
  corporate, high-value), flag this to the
  investigator at Phase 0.
- **ADGM MLRO SLA Tiers:** When escalating to ADGM
  MLRO, the complexity tag affects the MLRO's review
  timeline:
  - Standard: 35 business days from alert date
  - Complex (multiple subpoenas, court-referred,
    employee-related, multi-jurisdiction, extensive
    tracing): 15 business days for first action, 30
    business days for follow-up
  - Priority (TF, CSAM, Proliferation Financing): 10
    days review + 1-5 days reporting
  Tag the case appropriately in HaoDesk when
  submitting the L3 escalation.
- **RFI Response Review SLA:** When a user responds
  to an RFI, the response must be reviewed and
  analysed within 3 business days of receipt.

---

## Scam/Fraud Case Intake Extraction
*Relocated from icr-general-rules.md — applies to this step only.*

**SCAM/FRAUD CASE INTAKE EXTRACTION:**
For scam/fraud cases referred by SSO where the
case package includes extensive customer services
chat logs, victim/suspect evidence screenshots,
and SSO case notes:

The investigator may process these materials in
a standalone chat using the case intake extraction
prompt via `get_prompt("case-intake")`
BEFORE starting Phase 0 in the main chat.

If a case intake extraction is provided, it will contain
nine structured sections: Allegation Summary,
Victim Details, Suspect Details, Victim Evidence,
Suspect Response, Suspect Evidence, CS/SSO Actions,
Translation, and Established Facts vs Allegations.

The main chat should use this structured briefing
alongside the L1 referral to construct the Phase 0
narrative theory. Pay particular attention to
Section 9 (Established Facts vs Allegations) —
this distinguishes what is proven from what is
claimed and directly informs the investigation
approach.

If no case intake extraction is provided, proceed with
Phase 0 using the L1 referral and whatever case
materials the investigator provides directly.

---
## PHASE 0: NARRATIVE FIRST (THE "HARD STOP")
**Trigger:** Case data is loaded into the conversation. The AI receives the pre-processed case data automatically.
**Action:**
1. Ingest ALL provided case data.
2. Reconstruct the story — who did what to whom, when, for how much, and how.
3. Classify the case type. State: "Case Type Identified: [Type]. Primary SOP: [Filename]."
4. Present the Narrative Theory to the user.
5. Generate a Data Inventory confirming what was received and what may still be needed:
   - Received: [list each data type provided]
   - Not received: [list any expected data types not present]
   - May be needed at specific steps: [list anything not yet available]
6. Generate an Attachment Checklist by referencing Appendix E (Standard Attachment Checklist) in icr-steps-post.md. List only 'Always required' and applicable 'Conditionally required' categories. For UOL export, state simply 'UOL export' — required on all cases.
**Account Status Detection (Phase 0):**
In addition to case type classification, Phase 0 must identify and flag:
- **Corporate account:** Company name in KYC/II-1 (Ltda, Ltd, LLC, Inc, S.A., GmbH, Corp), entity tag present, P2P Merchant Status, or KYB data visible. If detected, state: "Corporate account detected. Switching to company perspective." All output text from this point uses "the company" / "the entity" not "the user." Corporate-specific checks apply across steps — see Step 2 (KYB handling), and icr-general-rules.md (corporate rules).
- **HPI status** (User InfoHub): State "HPI account detected. Enhanced offboarding workflow applies." Impact on approval pathway at Step 22 only.
- **KOL status** (User InfoHub / VIP section): State "KOL account detected. Enhanced offboarding approval required (FCMI Manager + CCO + @KOLUserOffboardingBot notification + ELT Notification Form)." Impact on approval pathway at Step 22 only.
- **P2P Merchant status** (affects courtesy notifications)
- **VIP level** (affects approval tier — use highest level if multiple designations)
- **Employee status** (requires enhanced approval pathway)
State any detected special statuses at the end of the Phase 0 output. HPI, KOL, and employee status do not change the investigation methodology — all analytical steps proceed as normal.
**HARD STOP:** Do NOT fill any ICR boxes yet. Ask: "Does this narrative accurately reflect the evidence? Shall we begin the ICR?"
**System Constraint:** "Related Parent ICR" typically refers to the current case reference in HaoDesk/CICM. Do not treat as a missing document unless context explicitly suggests otherwise.
---
## PACING MODE
After Phase 0 confirmation, the investigation proceeds in one of two modes. Express mode is the default.
### EXPRESS MODE (Default)
Triggered by default, or when investigator says "express mode," "block mode," "grouped output," or "let's go fast."
Output is grouped into four blocks. Each block covers multiple ICR steps in a single response. The investigator reviews each block, flags corrections, and says "next block" to proceed.
**EXPRESS MODE BLOCKS:**
BLOCK 1 — SETUP & CONTEXT (Phase 0 + Steps 1-6):
Phase 0 narrative theory and case classification, Step 1 investigation header guidance, Step 2 KYC paragraph, Step 3 account summary and blocks, Step 4 L1 summary, Step 5 prior ICR analysis, Step 6 LE enquiry review.
BLOCK 2 — CORE ANALYSIS (Steps 7-14):
Step 7 transaction overview, Step 8 CTM alerts, Steps 9+10 Elliptic analysis (combined), Step 11 privacy coins, Step 12 counterparty analysis, Step 13 fiat transactions, Step 14 device/IP.
BLOCK 3 — COMMUNICATIONS & SUMMARY (Steps 15-20):
Step 15 OSINT, Step 16 user communication, Step 17 other unusual activity, Step 18 RFI decision, Step 19 RFI analysis summary, Step 20 summary of unusual transactions (Parts A and B).
BLOCK 4 — DECISION (Step 21):
Pre-decision gate (decision matrix scan, MLRO escalation check, auto-fail check), conclusion and recommendation, escalation routing, offboarding guidance if applicable.
Each block output must be clearly labelled with step numbers and ICR section names for copy-paste into HaoDesk fields.
**EXPRESS MODE QC OBLIGATION:**
At the end of each block, append a "BLOCK QC" section. For every step in the block, list QC checks from the step guide documents and confirm each is satisfied or flag what needs attention. Format as a markdown table:
"BLOCK [X] QC:"
| Step | Check | Status |
One row per QC check. Status: PASS or FLAG. If flagged, add short reason (max 10 words). No separate commentary — table is the complete QC output.
**EXPRESS MODE CONSTRAINTS:**
- Phase 0 is ALWAYS presented first and confirmed before Block 1 begins. Hard Stop still applies.
- If case is unusually complex (5+ prior ICRs, 10+ LE cases, multi-jurisdiction, corporate with extensive KYB), recommend Standard Mode.
- All step-specific rules still apply — Express Mode changes grouping, not analytical requirements.
- Investigator may switch to Standard Mode by saying "slow down" or "step by step from here."
### STANDARD MODE
Triggered when investigator says "step by step," "standard mode," or "one at a time."
Rules:
1. One step at a time. Do not generate multiple ICR steps in a single response.
2. The Loop: Execute current step per the relevant step document, applying all rules from icr-general-rules.md. Perform QC check. STOP. Present output and ask: "Ready for the next step?"
3. If user provides bulk data covering multiple steps: acknowledge receipt but still process one step at a time.
Investigator may switch to Express Mode at any point by saying "express mode."
---
## STEP 1: INVESTIGATE HEADER
**ICR Section:** Investigate > Summary tab
**Action:**
1. Select the appropriate investigation tab:
   - For standard cases (Fraud, CTM, LE, Fake KYC):
     Select "Lifetime Suspicious Activity" tab.
   - For FTM phased approach cases: Select "Pre-check"
     or "Initial Investigation" tab as appropriate per
     ftm-sop.md three-phase process.
**TAB SELECTION RULE:** If the case was triggered by
an LE referral, Fraud/Scam referral, Fake KYC, or
any non-CTM/FTM source, always select "Lifetime
Suspicious Activity." The "Pre-check" and "Initial
Investigation" tabs are exclusively for cases
originating from the CTM/FTM alert queue
(FCI - Compliance L2 Crypto TM). The Hexa form
displays all three tabs regardless of case type —
do not be misled by their visibility.
**PHASE SELECTION (QC PARAMETER — Minor):**
The phase selected (Pre-Check, Initial Investigation, or Full Review/Lifetime Suspicious Activity) must be correct for the case type and the depth of review conducted. Points will be deducted if a lower phase was selected to avoid completing the required full review (e.g., selecting Pre-Check when the case clearly requires Initial Review or Full Review). For non-CTM/FTM cases, always select "Lifetime Suspicious Activity." For CTM/FTM cases, select the phase that matches the investigation depth actually performed.
2. Complete the two dropdown selections:
   - **Subject Matter:** Select the category that matches
     the case type identified in Phase 0
     (e.g., "Bank Relationship and Fiat Partners").
   - **Subject Matter Sub-Category:** Select the specific
     sub-type (e.g., "Reported Scam/Fraud").
   - Save the selections.
3. Note the Related Parent ICR ID shown at the top of
   the case. This is the current case reference — do not
   treat it as a missing document.
**QC Check:**
- Subject Matter and Sub-Category must align with the
  actual case evidence, not just the L1 referral label.
- If L1 mislabeled the case type, select the correct
  values here.
---
## STEP 2: II-1 PEOPLE INVOLVED IN THE UNUSUAL ACTIVITY
**ICR Section:** II- Presentation of the People > II-1
**What you see:** Hexa-populated paragraph with user
details (UID, name, email, phone, nationality, KYC
details, address, registration date, balance, VIP
status, merchant status, entity tag, TNC tag, fiat
channels).
**Action:**
1. Compare the Hexa text against:
   - The ID Document (passport, national ID)
   - Binance Admin user profile
   - Any POA documents on file
2. Apply the Source of Truth Hierarchy to resolve
   discrepancies:
   - Name: ID Document (special characters exact)
   - Address: Address Validate (POA section, if approved) > Basic Validate > ID Document Address. Note: KYC Approve Info no longer contains address data as of recent system updates.
   - For corporate accounts: use the exact address from
     the KYB section including city and postal code. If
     multiple addresses appear, use the operating address
     in the main text and note the registered address if
     it differs.
**NAME FIELD — MIDDLE NAME / PATRONYMIC RULE:**
Middle names and patronymics (common for CIS countries)
are included in the KYC paragraph ONLY when they are
visible on the ID document itself — either on the front
face or in the MRZ. If a middle name or patronymic
appears in Basic Validate, KYC Approve Info, or any
other Binance Admin field but is NOT present on the ID
document, it must NOT be added to the Hexa output. The
ID document is the sole authority for the user's name.
This rule applies even when the QC checklist requires
middle names to be included "if visible on ID" — the
operative phrase is "on ID," not "in the system."
**NATIONALITY vs RESIDENCY DISTINCTION:**
The term used in the KYC paragraph ("national" vs "resident") depends on the ID document type:
- If the ID explicitly confirms nationality (passport, national ID card): use "[Country] national."
- If the ID confirms only legal residence or entitlement without proving nationality (driver licence, residence permit, residence card): use "[Country] resident."
Examples:
- Bangladesh National ID → "Bangladeshi national" (document grants nationality)
- Australian Driver Licence → "Australian resident" (document confirms residence and driving entitlement only, not nationality)
- Portuguese Residence Permit → "Portuguese resident" (document confirms legal residence, not nationality)
- Japanese Passport → "Japanese national" (passport confirms nationality)
Examine the ID document type before selecting the term. If uncertain whether the document proves nationality, default to "resident."
3. Forensically update ONLY incorrect fields.
   Do not rewrite correct text.
**KYC RESIDENCE DISCREPANCY WORKFLOW:**
If the system-level country of residence (Basic
Validate > Residence field) conflicts with the
physical address held in Basic Validate and/or the
ID document:
1. Check Address Validate — if the address was
   validated and approved (status: Passed), the
   validated address takes precedence per the Source
   of Truth hierarchy. Note: As of recent system updates, KYC Approve Info no longer contains address data. The address priority is: Address Validate (POA section) > Basic Validate > ID Document.
2. If Address Validate was refused or not attempted,
   fall back to Basic Validate address text — but note
   that the country of residence field and the address
   text field within Basic Validate may contradict each
   other (e.g., address is in Lisbon but residence
   says Ukraine)
3. Escalate to QC for guidance on which residence to
   use for the ICR and MLRO routing
4. Note the discrepancy explicitly in the KYC section
   of the ICR (e.g., "The system residence is recorded
   as Ukraine, however the Basic Validate address and
   ID document indicate Portugal. Per QC guidance,
   Portugal is used as the country of residence for
   this investigation.")
5. Contact KYBKYCBot to request correction of the
   system-level residence field
6. Do NOT change the Entity Tag yourself — this is
   handled by the KYC/KYB team
This is important because the system-level residence
drives the Entity Tag and MLRO escalation routing. An
incorrect residence may cause the case to be escalated
to the wrong MLRO or missed entirely.
**BASIC VALIDATE — LAST RESORT ONLY:**
Basic Validate information should only be used for name, address, or nationality when no other source is available — specifically, when there is no ID document, no approved KYC information in KYC Approve Info, and no validated address in Address Validate. Basic Validate is user-submitted data that may not have been verified. If Basic Validate is the only source, note this limitation: "Address sourced from Basic Validate (user-submitted, unverified)."
**REFUSED KYC HANDLING:**
When a user's KYC status is REFUSED, the system may
display "null" for the ID number and omit the address.
If the submitted ID document is still viewable in
Binance Admin (KYC Certificate section), the
investigator should:
1. Note the ID number from the submitted document
2. State in the KYC paragraph that the ID was submitted
   but KYC verification was refused
3. Include the address from the submitted ID document,
   noting it is from the submitted (not approved)
   documentation
4. Note any system-imposed blocks resulting from the
   KYC failure (e.g., "KYC Not Pass" trade block,
   "No Trading Service Provided" tag)
Example: "The user submitted a China ID_CARD no [X];
however, KYC verification was refused and the account
has no trading service."
**VENDOR-VERIFIED KYC (IN/BR):**
Some jurisdictions (notably India and Brazil) allow account verification through a third-party vendor (e.g., Aadhaar-based verification in India, CPF-based verification in Brazil). In these cases, the ID document image may not be available in Binance Admin. To obtain KYC details:
1. Navigate to Binance Admin > KYC Certificate > Identity Verify > Detail Info
2. Extract name, DOB, nationality, and ID number from this section
3. Use this data as the source of truth when no ID document image is accessible
4. Note in the KYC paragraph: "KYC was verified via vendor verification. ID document image is not available. Details sourced from KYC Certificate > Identity Verify > Detail Info."
**Metadata Exclusion Rule (Individual Accounts):**
For individual accounts, the editable paragraph
must contain ONLY: name, email, phone, nationality,
DOB, ID document details, address, registration
date, last login, and balance. Do not reproduce
system-displayed metadata fields (VIP status, P2P
Merchant Status, Entity Tag, TNC Tag, Bifinity Tag,
Fiat channels) in the editable paragraph — these
are displayed separately by HaoDesk below the
editable section. Including them creates duplication
which is a QC finding. Note these fields for use in
later steps (they affect MLRO escalation, Bifinity
checks, counterparty analysis, and offboarding)
but do not include them in the People Involved
paragraph text.
**Required output (Individual Accounts):**
The corrected Hexa paragraph containing only: full name,
email, phone, nationality/residency (per the Nationality
vs Residency Distinction above), DOB, ID document type
and number, address, registration date, last login, and
account balance. Apply corrections in-place — do not
rewrite accurate Hexa text. If corrections were made,
append a brief note: "Corrections applied: [list fields
changed and reason]."
**METADATA DISPLAY — FORMAT-DEPENDENT:**
The metadata exclusion rule above applies to the
NEWER Hexa box format where these fields are displayed
separately by HaoDesk below the editable section. In
the OLDER full-page ICR format, these metadata lines
appear within the editable text area as part of the
form structure. In the older format, retain them
as-is — they are not duplicated because no separate
system-displayed section exists.
**Corporate accounts (KYB):** See icr-general-rules.md § Corporate Account Rules for the canonical KYB procedure. Apply those rules when writing this section.
**Formatting Rules:**
- Expand all 2-letter country codes to full country
  names (e.g., "BR" → "Brazil") wherever they appear
  in the KYC paragraph — including within address
  strings, phone number country prefixes, nationality
  fields, and country of residence. Do not limit the
  check to standalone country reference fields. Scan
  the entire corrected Hexa paragraph for any remaining
  2-letter codes before finalising.
- Special characters in names must match the ID exactly.
- For vendor-verified KYC accounts (India, Brazil) where the ID document image is not available, source details from KYC Certificate > Identity Verify > Detail Info. Note the verification method in the KYC paragraph.
- If Fake KYC suspected, consult
  fake-documents-guidelines.md for exemption conditions.
**Important Fields to Note for Later Steps:**
- VIP status (affects Step 22 offboarding process)
- P2P Merchant Status (affects counterparty analysis)
- User Entity Tag (affects MLRO escalation jurisdiction)
- User TNC Tag (affects MLRO escalation jurisdiction)
- User Fiat Channels (affects Step 13 Bifinity check)
**QC Check (Ref: qc-submission-checklist.md #1.1, #1.3):**
- Final text matches ID/Address proofs exactly.
- Country of residence is the full name, not a code.
---
## STEP 3: III-1-1 SUMMARY OF ACCOUNT ACTIVITIES
**ICR Section:** III-1 Transaction Analysis > III-1-1
Summary of account activities during the examined period
**What you see:** Hexa-generated box containing:
- On-chain transaction monitoring alerts summary
- Off-chain transaction monitoring alerts summary
- Account activity summary (trade volume, crypto
  deposits/withdrawals, fiat deposits/withdrawals,
  P2P, BPay, max holdings, etc.)
- Block cases (if any exist)
**Action:**
1. Audit the Hexa content for accuracy. Tidy if needed.
2. If block cases are listed:
   a. Download the Lifetime Block/Unblock spreadsheet
      from Compliance 360 > User Status Info.
   b. Write the block summary using the account
      block data.
   c. Append the generated block summary paragraph
      UNDERNEATH the existing Hexa content in this
      same box.
**Required output:**
A single paragraph listing all block/unblock actions in
chronological order with block type, action taken,
timestamp, unlock reasons, and current status of each
block type.
**If no blocks exist:** No action needed beyond auditing
the Hexa content.
**2FA RESET AND ONE-CLICK DISABLE BLOCKS:**
Blocks classified as 2FA reset or one-click disable in the block/unblock history are routine security operations initiated by the user. These can be left as Hexa-populated — no investigator analysis is required. Do not flag these block types as concerning unless they appear in unusual volume or timing that suggests account compromise.
**OTHER TEAM'S BLOCKS IN MULTI-STEP CASES:**
When blocks exist from a prior review by another team
(Sanctions/CTF, Special Investigations, Case Team) and
the case has been transferred to FCI for further
review:
1. Document the blocks fully: date, block type, reason,
   placing team, remark text, current status
2. Explicitly state these are not FCI blocks: "These
   blocks were placed by the [team name] and are not
   FCI blocks."
3. Do NOT remove them — cross-team protocol applies
4. If the blocks are directly related to the same
   subject matter as the current investigation (e.g.,
   Sanctions/CTF blocked the account for the same FBI
   indictment that FCI is now reviewing for
   offboarding), note that they align with the
   offboarding reason rather than treating them as
   "unrelated blocks" that need resolution before
   offboarding
**QC Check:**
- If blocks exist in C360 but are not reflected, flag.
- If blocks from other teams exist (SI, Sanctions, Case
  Team, CS SSO), note them but DO NOT unblock them.
  Ref: block-unblock-guidelines.md cross-team protocol.
---
## STEP 4: III-2 ANALYSIS OF FACTS (L1 SUMMARY)
**ICR Section:** III-2 Analysis of Facts > Summary of
L1 analysis
**What you see:** Hexa-populated text summarizing the
L1 referral reason.
**Action:**
- Audit the Hexa L1 summary for accuracy.
- If the Hexa text is an error message (e.g., "AI
  generation failed"), manually replace with the actual
  L1 referral summary.
- If L1 referral narrative is available and needs
  enhancement: Write the L1 summary enhancement
  using the referral data.
**Output Format (L1 enhancement):**
"It was referred to the FCI Team that [summarize the
allegation]. The activity was performed between
YYYY-MM-DD to YYYY-MM-DD and was attempted in [ADID or
OID] for a total attempted amount of XXX USD."
**Multiple Suspects / Unidentified UIDs:**
If the L1 referral mentions multiple suspects or UIDs
that cannot be immediately connected to the case:
1. Download the suspect's UOL (User Operation Log).
2. Search the UOL for the victim's UID or specific
   transaction IDs to establish connections.
3. If a UID cannot be connected to the suspect through
   evidence (UOL, chat screenshots, transaction data):
   State explicitly: "UID [X] was mentioned in the L1
   referral but no evidence was identified connecting
   this UID to the suspect in this investigation."
4. Only include transactions in the refund request
   that can be evidentially connected to the suspect.
**MULTI-USER ICR RULE (Step 4):**
In multi-user cases, the L1 referral narrative
typically explains why both users are in the same case
and how they are connected. Audit this narrative for
accuracy but do not rewrite or add to it unless the
Hexa text is an error message. The L1 summary already
covers both users.
**If no L1 narrative exists:** State "No L1 Narrative
provided."
---
## STEP 5: PRIOR ICR
**ICR Section:** Prior ICR
**What you see:** Hexa-populated bullet list of previous
ICRs with reference numbers and outcomes.
**Action:**
1. Audit the Hexa content for accuracy.
2. Write a consolidated prior ICR
   summary paragraph.
3. Append as Supplemental Analysis or replace if
   Hexa output is insufficient.
**Required output:**
A single paragraph (~60-75 words) summarizing each ICR
with reference number, creation date, and outcome.
Concludes with one neutral sentence on overall patterns.
**QC Check (Ref: qc-submission-checklist.md #3.6):**
- All previous ICRs mentioned with outcomes.
- Hexa content alone is NOT sufficient — analysis must
  be provided on top.
- If 5+ ICRs: mention all outcomes, provide analysis
  of sampled 5.
**ADDITIONAL RULES — PRIOR ICR ANALYSIS:**
MOST RECENT ICR DEEP DIVE: Regardless of how many
prior ICRs exist, the most recent completed or
in-progress ICR must always be opened in HaoDesk and
reviewed in full — not just summarised from the Hexa
bullet points. Check for:
(a) what specific findings were made
(b) whether any RFIs remain unanswered
(c) whether the case is still in progress at L3
(d) whether the investigator identified risks that
    were deferred rather than resolved
(e) any specific counterparty or on-chain findings
    that carry forward to the current case
For VIP and corporate accounts with extensive history,
this deep dive is especially critical as prior
investigators may have built a body of evidence that
informs the current decision.
FOCUS ON NEW ACTIVITY: Identify which alerts and
transactions have already been reviewed and resolved
in prior ICRs. Focus the current analysis on new and
unresolved alerts only. Acknowledge prior alerts
briefly but do not re-analyze in depth. If prior ICRs
reviewed and MLRO-approved a significant portion of
account activity, reference this explicitly as a
mitigation factor and narrow the current scope to
activity since the last approved case.
PRIOR LE TICKET MITIGATION: If law enforcement
tickets were addressed and mitigated in prior ICRs
approved by MLRO, reference that prior mitigation
briefly rather than re-analyzing in full. A brief
statement is sufficient: "Law enforcement tickets
were reviewed and mitigated in prior ICR [reference],
approved by MLRO on [date]." For corporate accounts
(especially OTC brokers/merchants), LE tickets often
relate to the company's clients, not the entity
itself — note this distinction.
**PRIOR ICR SCOPE QUANTIFICATION:**
When a prior ICR reviewed a significant portion of
the account activity, the Supplemental Analysis should
explicitly quantify the overlap:
- State how many transactions and what dollar volume
  was already reviewed (e.g., "48 of 49 total
  transactions, $701,085.32 of $731,085.31 total
  volume")
- Note the scope of the current investigation relative
  to the prior review (e.g., "focuses on activity
  after [date]")
- If the balance changed between reviews, note this
  and provide possible explanations (new transactions,
  asset appreciation, trading activity)
- If the current case represents a different team's
  perspective (e.g., Sanctions/CTF retained, now FCI
  is reassessing), state this explicitly
**FTM PHASED APPROACH — 90-DAY PRIOR ICR COMPARISON:**
For FTM cases under the phased approach, any prior ICR filed within 90 days of the current alert requires specific comparison. Check:
1. Are there new alert rule codes triggered that were not present in the prior ICR? If yes → escalate to Initial Review regardless.
2. If no new rule codes: are the triggered TM rules the same AND are the alerted transaction amounts materially similar (not greater than 3x difference)?
3. If rules and amounts are similar: compare Push and Pull factors between the prior ICR and the current case.
This comparison informs whether the current case represents a genuinely new risk or a repetition of previously reviewed activity. Note: LVP-I and LVP-O are different rule codes (direction matters).
---
## STEP 6: LE ENQUIRY REVIEW
**ICR Section:** LE enquiry review
**What you see:** Hexa-populated text summarizing law
enforcement cases.
**Action:**
1. Audit the Hexa content for accuracy.
2. Cross-reference against Binance Admin > Users >
   Kodex Case Details.
3. If Kodex shows cases not in the Hexa text, add them.
4. Provide appropriate level of detail per request type.
**If LE data was extracted by the ingestion
pipeline:**
The investigator will paste structured LE data
containing an LE Case Table and Summary. Using
this data:
1. Cross-check against Binance Admin > Users >
   Kodex Case Details to verify completeness
2. If Hexa has populated LE content, compare the
   extraction data against it — correct any Hexa
   errors in-place
3. Write the LE section following the Detail
   Required by Request Type rules below:
   - Data/information requests: authority, date,
     subject matter, outcome — one line each
   - Subpoenas, seizures, court orders: content
     summary, follow-ups, blocks imposed — fuller
     treatment
4. Use the Subject Role field from the extraction
   to distinguish direct requests against the
   subject from third-party/counterparty
   appearances
5. Append a risk position statement
6. Apply the CONSTRAINT — PROPORTIONATE OUTPUT
   rule and the CORPORATE CONTEXT rule as
   documented below
Do not paste the extraction table into the ICR.
Write a narrative paragraph using the data.
**Detail Required by Request Type:**
Data/information requests (Kodex):
→ Authority, date, subject matter (if no blocks resulted)
Subpoenas, seizures, court orders:
→ Content summary, follow-ups, blocks requested/imposed.
Verify the criminal acts and check for further links.
**BLOCKCHAIN IDENTIFIER LOOKUP:**
When LE referrals include blockchain identifiers
(transaction hashes or wallet addresses), the
investigator may need to look up transaction details
independently using block explorers. To determine the
identifier type:
- **40 hex characters** (after 0x prefix) =
  **wallet address** — shows transaction history for
  that address but cannot identify a specific
  transaction without additional context (date,
  amount, counterparty)
- **64 hex characters** (after 0x prefix) =
  **transaction hash (TxID)** — can be looked up
  directly to obtain the exact amount, date, from/to
  addresses, token type, and transaction status
Recommended block explorers (per
CTM-on-chain-alerts-sop.md):
- **Etherscan** (etherscan.io) — Ethereum and ERC-20
  tokens
- **BscScan** (bscscan.com) — Binance Smart Chain
- **PolygonScan** — Polygon network
- **Arkham Intelligence** — entity identification and
  cross-chain analysis
If LE provides only a wallet address without a TxID,
amount, or date, and the specific transaction cannot
be identified in the account records, state this
limitation in the ICR: "The LE request referenced
wallet address [address] as a deposit without a
corresponding TxID or amount. The specific transaction
could not be identified or valued from the available
account records."
**LE TARGET COUNT RULE (MANDATORY):**
When writing the LE narrative — whether from Hexa
content, extraction data, or manual Kodex review —
every Kodex case must explicitly state the total
number of targeted UIDs at the point where that case
is first described. Use the format: "This request
targeted [X] UIDs including the subject" or "[Agency]
submitted a request targeting [X] UIDs including the
subject." Do not bury the target count in a later
sentence, generalise it across multiple cases, or
omit it entirely.
The scale of an LE request is a material factor in
the risk assessment. Being one of two targets in a
money laundering investigation carries different
weight than being one of 50+ targets in a mass drug
trafficking sweep. The narrative must make this
distinction immediately clear to the reader.
When the preprocessed LE extraction data provides a
target UID count per case, that count must appear
verbatim in the ICR narrative for each case. If
extraction data is not available and the Kodex case
lists multiple target UIDs, count them manually and
state the total.
**CORPORATE CONTEXT:** For corporate accounts
(especially OTC brokers, merchants, payment
processors), note whether LE tickets appear to relate
to the entity itself or to its clients/counterparties.
This distinction is critical for the risk assessment
and must be stated explicitly.
**LE RISK WEIGHT ASSESSMENT:**
Before assigning risk weight to any LE case in the
ICR narrative, assess the specificity of targeting
using the following three-tier classification:

**HIGH SPECIFICITY — carries independent risk weight:**
The subject meets ONE OR MORE of:
- Sole target of the request
- Freeze, seizure, or confiscation requested or
  imposed against the subject
- Specific transactions attributed to the subject
  by the requesting authority
- Subject individually named in the request narrative
  in connection with specific criminal activity
- Subject treated differently from other targets
  (e.g., higher data scope, additional restrictions)

High-specificity cases require substantive analysis
in the ICR and carry independent weight toward
offboard, RFI, or escalation decisions.

**MEDIUM SPECIFICITY — warrants attention but limited
independent weight:**
The subject meets ONE OR MORE of:
- One of a small number of targets (2-5 UIDs)
- Freeze requested but not imposed
- Crime type specifically attributed to the subject's
  transaction category (e.g., money laundering) even
  though multiple UIDs are listed
- Follow-up requests from the same agency narrowing
  scope toward the subject

Medium-specificity cases should be documented and
noted but do not independently support offboarding.
They gain weight when combined with other unmitigated
indicators per Decision Matrix Rule #58.

**LOW SPECIFICITY — mitigated:**
The subject meets ALL of:
- One of many targets (6+ UIDs)
- No freeze, seizure, or confiscation requested or
  imposed
- No specific transactions attributed to the subject
- Broad-scope data collection request across multiple
  accounts and jurisdictions
- Subject appears only as one UID/address in a list

Low-specificity cases are mitigated by stating the
lack of individual targeting. Standard mitigation
text: "The subject is one of [X] targeted UIDs in a
broad data request with no freeze, seizure, or
specific transaction attribution. The LE profile does
not carry independent risk weight."

The LE Target Count (stated per the mandatory LE
TARGET COUNT RULE above) directly informs this
assessment — the number of targets is the first
data point in determining specificity.

This classification should be applied to every LE
case and the tier stated in the risk position
statement for the LE section. See also Decision
Matrix Rule #56.
**Required output:** One or more narrative paragraphs
covering all LE cases. For each case: the requesting
authority, date, subject matter, LE target count
(mandatory), subject role (direct target vs
third-party), and the specificity tier (High / Medium /
Low per the LE RISK WEIGHT ASSESSMENT above). Group
related cases from the same agency where appropriate.
Conclude with a risk position statement summarising the
overall LE risk profile. Length is proportional to
complexity — a single low-specificity data request may
be 2-3 sentences; multiple high-specificity cases with
freezes may require a full paragraph.
**If no LE enquiries:** State "No law enforcement
enquiries identified."
**QC Check (Ref: qc-submission-checklist.md #3.11):**
- All LE enquiries in Kodex must match what's in the ICR.
- Mismatch between Kodex and ICR = QC finding.
---