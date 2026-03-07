# ICR Steps: Setup & Context (Steps 1-6)
## Purpose
This document covers Steps 1 through 6 of the ICR form. These steps establish who the subject is, why the case exists, and what history is relevant. Cross-cutting rules in icr-general-rules.md apply to every step below.
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
**METADATA DISPLAY — FORMAT-DEPENDENT:**
The metadata exclusion rule above applies to the
NEWER Hexa box format where these fields are displayed
separately by HaoDesk below the editable section. In
the OLDER full-page ICR format, these metadata lines
appear within the editable text area as part of the
form structure. In the older format, retain them
as-is — they are not duplicated because no separate
system-displayed section exists.
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
2. Do NOT include VIP status, P2P Merchant Status,
   Entity Tag, TNC Tag, or Fiat Channel information in
   the rewritten paragraph. These fields are
   pre-populated by the system below the editable
   paragraph and including them creates duplication.
   The modified paragraph should be a clean corporate
   equivalent of what Hexa would have generated —
   company name, jurisdiction, registration number,
   address, and account metadata (registration date,
   last login, balance) only.
3. APPEND a separate paragraph below the modified Hexa
   text. This supplementary paragraph covers details
   Hexa does not capture. Include:
   - Ultimate Beneficial Owner(s): names (mandatory). Nationality, DOB, country of residence, and other identifying details are required only when adverse media is found on the UBO and additional confirmation is needed that the media subject is the same individual as the UBO.
   - Company's stated business purpose
   - Operational activities and how the company
     generates revenue
   - Any relevant details from the business description
   This paragraph goes BELOW the Hexa text — never
   merged into it or replacing it.
4. Look up the company details in Binance Admin > KYC
   Certificate > Company KYC section. Available fields:
   - Company name
   - Date of incorporation
   - Registry/registration number
   - Registered address
   - Operating address (if different)
   - Ultimate Beneficial Owners (UBOs)
   - Nature of business / business description
5. If Hexa output is an error message or completely
   blank (no text generated at all), THEN and only
   then generate a full replacement using this
   template:
   "Binance Account UID [X] is registered in the name
   of [Company Name], a [nationality] company
   incorporated on [date] with registration number
   [X]. The company is registered at [address] and
   operates from [address if different]. The Ultimate
   Beneficial Owner(s) of the company are [Name(s)]
   ([Nationality/ies]). According to the KYB
   documentation, [Company Name] operates as
   [2-3 sentence summary of business function].
   The account was registered on [date] and as of
   [date], the most recent login was recorded on
   [date] with current balance standing at [amount]."
   This full template is a FALLBACK only — the default
   approach is always to modify Hexa in-place.
   WORKED KYB EXAMPLE (QC Reference):
   "Binance Account UID 37456337 is registered in the name of Airfill Prepaid Ab with email address binance@bitrefill.com. According to the Know-Your-Business (KYB) details submitted with the application, Airfill Prepaid Ab is a company from Sweden with Date Of Incorporation: 2015-01-26. The company holds Register No 559001-6035 and currently located at ATT: Operations Desk, Airfill Mailbox 2333, Stockholm, SE, 111 75. Nature of Business (Company Type) Retail Trade - Others: The company sells phone refills, e-sims, gift cards and other products on the website www.bitrefill.com, mainly to end consumers. The account was registered on Aug 9, 2019, and as of Sep 17, 2025, the most recent login was recorded on Sep 17, 2025 with current balance standing at $314,612.97 USD. The UBO is Sergej Kotliar, of Swedish nationality."
   This example demonstrates QC expectations: company name, email, KYB source reference, country, incorporation date, registration number, full address, nature of business with operational detail, registration date, last login, balance, and UBO name with nationality — all in a single flowing paragraph.
6. The section header stays as "II-1 PEOPLE INVOLVED"
   but the content must reflect corporate identity
   throughout.
7. Note the UBOs — they must be analyzed in the main
   body of the report (counterparty analysis, OSINT,
   device analysis) alongside the company itself.
**QC Check for Corporate (Ref: qc-submission-checklist.md
#1.5):**
- KYC section modified to reflect KYB content (Hexa
  preserved and adjusted in-place, supplementary UBO/
  business paragraph appended below, system-displayed
  metadata fields not duplicated in the paragraph)
- Includes: date of incorporation, registry number,
  registered and operating addresses, UBOs
- Nature of business briefly mentioned
- UBOs and corporate activity analyzed in the main
  body of the report
- Failure to rewrite KYC to KYB = Moderate finding
  (5 points)
- UBO: name is mandatory. Nationality/DOB/residence required only when adverse media necessitates identity confirmation.
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
   b. Execute Prompt #3 (Account Blocks) from
      prompt-library.md using this spreadsheet.
   c. Append the generated block summary paragraph
      UNDERNEATH the existing Hexa content in this
      same box.
**What Prompt #3 produces:**
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
  enhancement: Execute Prompt #5 (Scam Analysis P2P)
  from prompt-library.md.
**Output Format (if using Prompt #5):**
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
2. Execute Prompt #4 (Prior ICR Analysis) from
   prompt-library.md to generate a consolidated
   summary paragraph.
3. Append as Supplemental Analysis or replace if
   Hexa output is insufficient.
**What Prompt #4 produces:**
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
**If LE data was extracted in a parallel chat
using Prompt #15E:**
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
When extraction data from Prompt #15E provides a
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
**If no LE enquiries:** State "No law enforcement
enquiries identified."
**QC Check (Ref: qc-submission-checklist.md #3.11):**
- All LE enquiries in Kodex must match what's in the ICR.
- Mismatch between Kodex and ICR = QC finding.
---