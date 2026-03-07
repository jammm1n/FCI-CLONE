# ICR General Rules

## Purpose
This document contains rules that apply across ALL
steps of the ICR form. Every step-specific document
(setup, analysis, decision, post) inherits these
rules. If a step-specific instruction conflicts with
a rule here, the step-specific instruction takes
precedence for that step only.

---

## Source of Truth Hierarchy
When case data conflicts across sources, resolve using
this priority:
- **Name:** ID Document (special characters must match
  exactly)
- **Address:** Latest POA Document > ID Document
  Address > Binance Admin (Basic Validate)
- **Transaction Data:** Spreadsheet/C360 > Narrative
  text
- **Case Outcome Precedent:** case-decision-archive.md
If a spreadsheet contradicts the narrative: **PAUSE.**
Flag the discrepancy immediately. Do not proceed until
the investigator resolves it.

---

## Hexa Protocol
- Hexa-populated boxes are editable. If the Hexa AI
  output is poor or inaccurate, it should be tidied up.
- Apply the Hexa Protocol from the system prompt:
  Audit first, then Supplement. Do not rewrite accurate
  Hexa text.
- Every "Edit" button box can be modified. Every empty
  manual entry box (showing 0/10000) must be populated
  before submission.

HEXA PROTOCOL AT STEP 12: The default action is
ALWAYS: correct errors in-place (wrong figures,
wrong counts, corporate language substitution) →
retain everything else exactly as Hexa generated
it → append Supplemental Analysis block below.
Never rewrite the Hexa structure at this step.

**Correction Sequence Rule:** When correcting Hexa
content at any step, always provide the complete
corrected output in the exact same format as the
original Hexa (same bullet point structure, same
paragraph layout) ready for direct copy-paste FIRST.
Then provide the Supplemental Analysis paragraph
separately below. Never provide corrections as a
list of edit instructions that the investigator must
manually apply, and never provide only a Supplemental
Analysis paragraph without the corrected Hexa above
it. The investigator must be able to select the
corrected Hexa output and paste it directly into
HaoDesk, then separately select and paste the
Supplemental Analysis below it.

---

## Corporate Account Rules
- **Corporate Accounts:** When the account belongs to
  a company, ALL text throughout the entire report must
  be written from the company perspective. Use "the
  company" / "the entity" instead of "the user" in
  every section. Reference business operations and
  corporate transaction patterns, not personal activity.
  Analyze UBOs alongside the company in OSINT, device
  analysis, and counterparty sections.

**CORPORATE ACCOUNTS (KYB):**
If the account belongs to a company (detected by
company name, entity tag, or merchant status):
1. Do NOT delete the Hexa-generated KYC paragraph.
   Modify it in-place with minimal changes:
   - Change individual references to corporate
     references (e.g., "the user" → "the company")
   - Insert the company name as it appears in KYB
   - Insert the company registration number
   - Replace the address with the exact address from
     the KYB section in Binance Admin (KYC Certificate
     > Company KYC), including city and postal code
   - If multiple addresses appear in the KYB, verify
     which is the registered address and which is the
     operating address. Use the operating address in
     the main text. Note the registered address if it
     differs.
   The modified Hexa paragraph should read naturally
   as a company profile. Example of minimum changes:
   "According to KYC, [Company Name] is a company from
   [Country]. The company registration number is [X]
   and currently operates at [full address including
   city and postal code]."

CORPORATE LANGUAGE SUBSTITUTION: For corporate
accounts, find-and-replace throughout the Hexa
counterparty text: "the user" → "the company" and
"the user under review" → "the entity under
review." This is an in-place correction, not a
rewrite.

---

## Brevity Principle
- **Brevity Principle:** Aim for conciseness in all
  sections. Write what is necessary and valuable — trim
  what is redundant or low-significance. Longer
  narratives increase writing time, create more
  mitigation obligations (every risk factor explicitly
  stated must be mitigated if retaining), and increase
  the chance of inconsistencies that QC may flag. If a
  detail is low-significance (e.g., a sub-account
  sharing an IP with its parent, a $2 device overlap),
  mention it briefly — do not deep-dive.

---

## Risk Position Requirement
- **Risk Position Requirement:** Every analytical
  section in the ICR (CTM alerts, exposed addresses,
  counterparty analysis, transaction analysis) must
  conclude with an explicit statement on whether the
  identified risk is mitigated or not. Either: "This
  risk is mitigated because [reason]" or "This risk
  cannot be mitigated with the information currently
  available." Neutral descriptions without a position
  are insufficient — the L2 investigator's role is to
  evaluate, not just describe.
- **Risk Mitigation Placement Rule:** Risk mitigation
  must appear in the same section where the risk was
  identified. Where the risk cannot be mitigated in
  the current section (e.g., mitigation depends on
  counterparty context, LE enquiry findings, or RFI
  response), the investigator must cross-reference the
  section where the risk is mitigated: "This exposure
  is further assessed in [section name] below." If the
  risk cannot be mitigated at all during the review,
  the action taken by the investigator (e.g., RFI
  issuance or offboarding recommendation) must be
  stated in the Summary or Conclusion. Every risk
  factor identified anywhere in the report must be
  traceable to either: (a) an in-section mitigation,
  (b) a cross-reference to another section's
  mitigation, or (c) the conclusion's recommended
  action.

---

## Currency Display Rule
- All monetary amounts must be expressed in USD or EUR
  (depending on jurisdiction), not local currency only.
  Convert local currencies where they appear.
- **Currency Display Rule:** All local currency amounts
  throughout the ICR must include USD equivalent in
  square brackets immediately following the original
  amount. Example: R$500,000.00 [USD $95,700.00]. Use
  current or relevant exchange rates.

---

## Output Hygiene
Internal processing abbreviations from prompts,
extraction apps, spreadsheet column names, or data
processing tools must never appear in ICR narrative
text. The ICR is read by QC reviewers, MLROs, and
potentially external regulators — none of whom have
context for internal shorthand.

Examples of prohibited abbreviations in ICR output:
- IT (use "Internal Transfer")
- BP (use "Binance Pay")
- SAWD, TLHA, BPPSUMCI, BPPSUMCO (do not reference
  off-chain rule codes)
- IT+BP (use "Internal Transfer and Binance Pay
  combined" or simply state the counterparty count
  without specifying source spreadsheets)

If structured data from an extraction app or parallel
chat contains these abbreviations, they must be
translated to plain English when writing the ICR
narrative.

---

## Parallel Chat Data Products
- **Preprocessed Data Products:** When the
  ingestion pipeline processes raw data (device,
  Elliptic, LE/Kodex, case intake, counterparty
  extractions), the output is structured data —
  not ICR narrative. The main chat writes all ICR
  narrative using the structured data plus full
  case context. The step doc for each section
  defines what the final output should look like.
  When structured data is available from
  preprocessing:
  (1) Audit the data for accuracy
  (2) Write the narrative paragraph using the data
  (3) Apply proportionality and risk position
  (4) Apply the Brevity Principle
  Do not paste data tables into the ICR. Do not
  reproduce every data point. Write a concise
  narrative paragraph that tells the story of
  what the data shows.

---

## Sanctions/Offboarding Cases
- **Full QC Coverage Required:** Even when a case is
  straightforward sanctions exposure heading for
  offboarding, all QC items must be covered. These
  accounts typically have minimal activity, so full
  coverage should not be time-prohibitive. Do not
  take shortcuts on sanctions cases.
- **Phased Approach Completion Exception:** For
  CTM/FTM phased approach cases, a case may be
  completed at the Pre-Check or Initial Review phase
  (without progressing to Full Review) if the user
  under investigation has already been offboarded or
  submitted for offboarding by the time of the review.
  Document the existing offboarding status and close
  the case at the current phase. This is the only
  exception to the general rule that RFIs, MLRO
  escalation, and offboarding require Full Review
  phase.

## RFI Response Check Before Closure
- **RFI Response Check:** Before submitting any case
  for closure, verify whether any outstanding RFIs
  have received responses. If a response has arrived
  before the case is closed, it must be reviewed and
  incorporated. A response received before closure
  cannot be disregarded.

---

## Pre-Submission Requirements
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

## Terminology Rules
- Never use "SAR" when referring to an ICR. These are
  different documents. Check the entire case for "SAR"
  before submission and replace with "ICR" where
  appropriate. SAR = Suspicious Activity Report filed
  externally by MLRO. ICR = Investigation Case Report
  at L2.
- Never use the word "pending" — it is a HaoDesk
  system status term. Use "while awaiting the outcome
  of," "upon completion of," or "following the
  resolution of."

---

## Case Rejection Rules
- **Case Rejection — Limited Scenarios:** Cases may
  only be rejected (returned without investigation)
  in three scenarios:
  1. Employee account — ask TL to reassign to the
     appropriate team.
  2. Two completely identical ICRs submitted by L1
     by mistake — review one, reject the duplicate.
  3. Following an explicit L1 request to reject due
     to a submission error.
  No other scenario justifies case rejection.
  Specifically:
  - Pending RFI from prior case: review the case and
    retain with reference to the ICR containing the
    pending RFI. Do not reject.
  - Open LE ticket: review the case. If retaining,
    proceed normally. If offboarding, seek Case Team
    confirmation. Do not reject.
  - Active freeze: review the case and escalate to
    MLRO. Do not reject.

---

## SLA Framework
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

## Always Editable Fields
**Mandatory Content (Always Editable Field):**
This field must NEVER be empty. Must contain velocity
assessment, ratios, and fund flow summary.

**Mandatory Content (Always Editable — CRITICAL):**
This field requires Elliptic screening. Must contain
analysis or "0/10000" if genuinely no data.

**Mandatory Content (Always Editable Field):**
Must contain locations, consistency assessment, and
shared device analysis. Never empty.

**Mandatory Content (Always Editable Field):**
Must contain specific findings OR:
"Open source research has been performed but no specific
/ negative news has been identified."

**Mandatory Content (Always Editable Field):**
Must contain analysis or the default statement.
Never empty.

---

## Scam/Fraud Case Intake Extraction
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

## Multi-User ICR Rules

**MULTI-USER ICR RULES (2-4 Users):**
When an ICR contains more than one user (but fewer
than five), Hexa will only populate data for the
primary user. The second (and any additional) user's
data must be added manually below the Hexa output in
every applicable section. This applies to:
- **People Involved (Step 2):** Hexa generates for
  User 1 — audit as normal. Manually add User 2's
  KYC paragraph below, following the same format and
  QC standards.
- **Account Summary (Step 3):** Hexa data covers
  User 1 only. Pull User 2's data from C360 and add
  below, clearly labeled with the UID.
- **Blocks (Step 3):** Check and document blocks for
  BOTH users.
- **LE Enquiries (Step 6):** Check and write about
  BOTH users. State connections between them.
- **Transaction Overview (Step 7):** Analyse and write
  for BOTH users.
- **CTM/FTM Alerts (Step 8):** Check for BOTH users.
- **Counterparties (Step 12):** Write about BOTH
  users — at minimum, top 3 counterparties per user.
- **Device & IP (Step 14):** Analyse for BOTH users.
- **OSINT (Step 15):** Screen BOTH users.
- **All other analytical sections:** Cover BOTH users.

**Labeling Rule:** Always clearly label which UID
each data block belongs to. Use "UID [first]:" and
"UID [second]:" prefixes when writing about each
user in shared sections.

**If User 2 has no data** (no transactions, no
blocks, no alerts): State this explicitly — e.g.,
"UID [X]: No transactions, no trade volume, and no
transaction monitoring alerts were recorded. The
account has had no activity since its registration
on [date]."

**Proportionality Rule:** Full analytical framework
for User 1 (the primary concern). For User 2:
confirm data presence/absence at each step, write
findings if they exist, state "no data" if they
don't. Do not skip steps entirely — always
acknowledge each section for both users. But depth
should match the available data.

**HEXA DIRECT OUTPUT FOR ADDITIONAL USERS:**
A standalone Hexa output link exists that can
generate Hexa-formatted data for a second user
outside of the main case form. Enter the second
user's UID and the Related Case ID (the long format
ID). The output can be copied into the ICR for
sections such as device analysis, counterparties,
and account summary. All data from this tool must
still be verified against C360 before use. This tool
is particularly useful when User 2 has limited or no
activity — the output will confirm this quickly.

**MULTI-USER ATTACHMENTS:** All required attachments
(UOL, valid ID, Elliptic wallet screenings, OSINT
PDFs, device analysis screenshots, C360 exports)
must be provided for EACH user in a multi-user ICR,
not just the primary user. If User 2 has no data for
a particular attachment type (e.g., no wallet
addresses to screen, no transactions to export),
note this in the case file rather than omitting the
attachment category entirely.

**SAME-INDIVIDUAL MULTI-USER CASES:**
When two or more UIDs are confirmed as belonging to
the same individual (same ID document, Face Compare
match), add a bridging sentence immediately after
both KYC paragraphs: "The same ID [type and number]
was used to register UID [X] and UID [Y], and Face
Compare confirmed a positive match, indicating both
accounts are controlled by the same individual."
This connection must then be reinforced throughout
analytical sections where relevant (e.g., explaining
why all activity is attributed to one individual
despite multiple UIDs).

---

---

## Older Format ICR Rules

**OLDER FORMAT ICR — SECTION ORDER:**
The older full-page ICR format presents sections in
a different order than the standard Hexa box layout.
When working through an older format ICR, follow the
section order as it appears in the form rather than
the standard Step 1-22 sequence. The content
requirements, QC checks, and analytical standards
for each section remain identical — only the
presentation order changes. The AI should ask the
investigator to confirm the next section heading
rather than assuming the standard sequence.

## Fraud/Scam Case Template Cleanup
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