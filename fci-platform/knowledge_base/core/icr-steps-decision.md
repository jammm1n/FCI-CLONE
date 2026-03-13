# ICR Steps: Decision & Output (Steps 17-21)
## Purpose
This document covers Steps 17 through 21 of the ICR
form. These steps involve the RFI decision, transaction
summary, investigation summary, and the final
conclusion and recommendation.
Cross-cutting rules in icr-general-rules.md apply to
every step below.
---
## STEP 17: ANY OTHER UNUSUAL ACTIVITY
**ICR Section:** Any other unusual activity
**What you see:** Empty manual entry box (0/10000).
**Action:**
Populate with any additional unusual activity not
covered in previous sections.
**Default (if nothing additional):**
"None identified."
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
---
## STEP 18: RFI ISSUED AS PART OF THIS INVESTIGATION
**ICR Section:** RFI Issued as part of this investigation
**What you see:** Edit button with RFI template fields:
- RFI Case ID
- Date Sent
- Expiry Date
- Type of RFI Sent
- What specific risk is this RFI intended to mitigate?
- What is the suggested outcome should the user provide
  satisfactory justification?
- What is the minimum acceptable response from the user?
- Is escalation to the MLRO required after RFI handling?
- Additional notes or context
**Action:**
IF an RFI was sent for THIS specific case:
Complete all template fields. Paste the RFI questions.
IF no RFI was sent:
State: "No RFI has been issued as part of this
investigation."
Remove the template section entirely from HaoDesk.
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
**RFI TIPPING OFF EXCEPTION:**
Do NOT send an RFI when:
1. The subject is an active law enforcement target
   (e.g., FBI wanted list, subject of ongoing criminal
   investigation, named in an indictment)
2. Contacting the user could alert them to the
   investigation and potentially compromise law
   enforcement operations
3. No user response could mitigate the identified risk
   (identity-based cases)
In such cases, remove the RFI template entirely and
state: "No RFI has been issued as part of this
investigation. Given the nature of the referral —
[specific reason, e.g., an active FBI indictment
confirmed by face and name matching] — contacting the
user would risk tipping off an active law enforcement
target and no user response could mitigate the
identified risk."
This is supported by both SOP decision matrices:
CTM-on-chain-alerts-sop.md Appendix II ("Multiple
high-risk red flags present, no plausible legitimate
explanation → Escalate without RFI") and ftm-sop.md
Appendix II ("Clear ML Typology → Escalate without
RFI").
**RFI RE-TRIGGER LIMIT — MAXIMUM 3 ATTEMPTS:**
The RFI cycle is limited to a maximum of 3 attempts: initial RFI → re-trigger 1 → re-trigger 2. After three attempts where the user intentionally provides insufficient, evasive, or irrelevant responses:
1. Classify the user as "uncooperative" (distinct from "unresponsive" — see below)
2. Apply WOM block under block reason "RFI - Others"
3. Set the case status to "Uncooperative user"
4. Offboarding consideration begins 60 days after WOM placement
This is distinct from the unresponsive workflow:
- Unresponsive = user does not reply at all after 14 days + 3 reminders → WOM under "RFI - SAR Investigation" + "Unresponsive User" tag
- Uncooperative = user replies but responses are intentionally insufficient after 3 RFI attempts → WOM under "RFI - Others" + "Uncooperative user" status
Each re-trigger must contain more specific questions targeted at collecting the vital information needed to conclude the case. Copy-pasting the previous RFI as a re-trigger is a QC finding (ref: qc-submission-checklist.md R.3).
**MULTI-USER ICR RULE (Step 18):**
For multi-user ICRs, a single RFI entry in the
template is acceptable covering both users. If RFIs
are sent to both users, note both in the same section.
Separate RFI case IDs should be referenced if they
differ.
**QC Check (Ref: qc-submission-checklist.md #4.4):**
- All template fields completed if RFI sent.
- Template removed if no RFI sent.
- RFI questions are relevant to the case (not generic).
- No internal information disclosed (alert types, WOM
  codes, possible offboarding).
- Not tipping off the user about the investigation.
- Not requesting SOW for transactions >2 years old.
**RFI does NOT contain any references to internal
information:**
- Types of alerts / rule codes / FTM alert category
  names (e.g., "low value payments," "transaction
  limit," "historic average inbound/outbound")
- Applicable blocks (e.g., WOM)
- Possible outcomes — never mention the user may or
  will be offboarded; refer to "possible restrictions
  to the account"
- Elliptic screening results, risk scores, or entity
  attributions (e.g., do not state "exposure to Mega
  Darknet Market" or "rescreening from Elliptic")
- Counterparty UIDs — do not reveal which Binance
  users were transacted with by UID
- Internal system transaction identifiers (see RFI
  TRANSACTION IDENTIFIER RULES below)
**What CAN be included in the RFI:** External wallet
addresses, transaction amounts, transaction dates, and
user-facing TXIDs (from UOL or Binance Admin). The user
can see these on their own transaction history.
**EXISTING PENDING RFI — RE-TRIGGER PROCEDURE:**
When an existing RFI is pending with the RFI team
and the current investigation identifies additional
risks not covered by that RFI:
1. Do NOT send a duplicate RFI (QC auto-fail per #4.3)
2. Contact the RFI team via the designated Google form
   (or WEA channel) requesting a re-trigger of the
   existing RFI to include the additional risk items
   (e.g., new counterparties, additional transaction
   queries)
3. Specify what additional information should be
   requested from the user
4. Screenshot the form submission or RFI team
   communication
5. Upload the screenshot to HaoDesk as supporting
   documentation
6. Close the case — do not leave it in pending status.
   The case is closed because the investigator has
   completed their review and communicated the
   additional risks to the RFI team.
**PRIOR RFIs FROM OTHER DEPARTMENTS:**
RFIs can be issued by departments other than FCI (e.g., local compliance teams, bank relations, customer service) without a corresponding FCI ICR. When reviewing RFI history, use Binance Admin > User profile > RFI section for the most complete view. Check the issuing department. If prior RFI responses contain relevant information, summarize and include them in the current ICR regardless of which department issued them.
**RFI RESPONSE REVIEW SLA:**
When a user responds to an RFI, the response must be reviewed and analysed within 3 business days of receipt. This SLA applies to the analysis itself — separate from the broader case review prioritisation timeline (blocked user responses reviewed within 14 days per block-unblock-guidelines.md). If the response arrives while the case is in the investigator's queue, begin the analysis within 3 business days. If the response arrives after the case has been closed or transferred, coordinate with the assigned team member or TL to ensure timely review.
**DUAL-LANGUAGE TEMPLATE RULE:** When the RFI is sent
in both English and the user's native language, amending
one language version does NOT automatically update the
other. The investigator must manually update BOTH
templates (English and native language) when modifying
grace periods, transaction details, sampled TXIDs, or
any other template fields. Mismatched templates between
languages are a QC finding.
**RFI Block Rule (Ref: block-unblock-guidelines.md):**
- If the user does not respond to the RFI, at least
  3 reminders must be sent before any block is applied
  for non-response.
- Do NOT block the account immediately after sending
  the RFI or before the 3 reminders are sent.
- After 3 reminders with no response: apply Withdrawal
  Only Mode block + Unresponsive User tag.
**HISTORICAL TRANSACTION RULE:**
For transactions that occurred more than 2 years ago,
prioritize mitigation over RFI. Users are unlikely to
remember or provide meaningful documentation for old
transactions, and requesting SOW for transactions over
2 years old is a QC auto-fail (ref:
qc-submission-checklist.md #4.5). Mitigation factors
for historical activity include: (1) no similar
transactions after the flagged period, (2) low
exposure amount relative to total activity, (3) no
ongoing high-risk patterns, (4) user profile otherwise
clean. RFI for transactions over 2 years old should
only be sent if the exposure is both significant and
cannot be mitigated through available data.
**SOW/SOF RFI RESTRICTION (Policy Update):**
Source of Wealth (SOW) and Source of Funds (SOF) RFIs
are generally no longer sent by FCI investigators.
These requests have been transferred to a dedicated
team to reduce user friction and repetitive RFIs. If
an SOW/SOF RFI is genuinely necessary for the
investigation, team lead approval is required before
triggering the RFI. This restriction applies to all
case types including gambling, high-value transactions,
and profile-mismatch scenarios. Alternative RFI types
(transaction justification, source of funds for
specific transactions) remain available.
Note: This is a current operational restriction and
may be revised. Check with team lead for the latest
status if uncertain.
**SOW/SOF Decision Tree (When All Risks Mitigated Except
FTM Pattern Alerts):**
1. All risks (CTM, device/IP, counterparties, on-chain
   exposure) are mitigated — only unresolved FTM pattern
   alerts remain.
2. If low severity and low number of FTM alerts: Close
   the case or escalate to MLRO per jurisdiction
   requirements. No SOW RFI needed.
3. If high severity or high number of FTM alerts:
   Request team lead approval to send SOW/SOF RFI with
   strong justification.
   - If approved: Trigger SOW/SOF RFI.
   - If denied: Escalate to MLRO (reporting
     jurisdiction) or close the case (non-reporting
     jurisdiction).
4. For all RJ escalations without SOW/SOF on file:
   Include the remark: "No financial crime risks
   identified; however, no SOW/SOF on file" in the
   escalation to enable the MLRO to request enhanced
   due diligence if deemed necessary.
**RFI DECISION THRESHOLD (PRE-CHECK):**
Before issuing any RFI, confirm all four conditions
in Decision Matrix Rule #60 are met. If any condition
is not satisfied, the RFI is not justified and must
not be sent. The default position is mitigate with
available data and retain.
**WARNING (NOT RFI) WORKFLOW:**
When the investigation outcome is to send a warning
(not an RFI) to the user about high-risk address
interaction, gambling activity, shared account, or
commingling personal/business funds:
1. Send the warning via HaoDesk — do NOT send warnings
   from the Binance Admin back end. All investigator
   communications must be routed through HaoDesk for
   record-keeping.
2. After sending the warning, HaoDesk may route the
   case toward the RFI queue. Warnings do NOT need to
   go to the RFI team.
3. Use the "Resume Case" option in HaoDesk to pull the
   case back.
4. Close the case on your side after sending the
   warning. There is no need to wait for a user
   response.
5. A warning is not an RFI — the user has no obligation
   to respond. Non-response to a warning cannot be
   treated as unresponsiveness for block purposes.
6. Do NOT cancel the warning/RFI in the system — use
   "Resume Case" instead.
7. Warning RFIs do not follow the standard 14-day grace
   period or WOM block process.
**GTR PRE-CHECK BEFORE RFI:**
Before issuing an RFI requesting wallet ownership or
transaction purpose, check the Global Travel Rule
(GTR) tabs in Binance Admin (GTR Withdraw / GTR
Deposit) for the user's UID. If the user has already
declared the wallet ownership or transaction purpose
via the Travel Rule questionnaire, and that
declaration adequately addresses the investigative
question, an RFI on the same point may be unnecessary.
If the GTR declaration is insufficient or raises
further questions, the RFI should reference the
existing GTR response and request clarification on
the discrepancy or additional detail.
**TRANSACTION SAMPLING FOR RFI:**
RFI transactions are sourced from C360 spreadsheets:
Lifetime SAR Internal Transfer Direct Link, Lifetime
SAR Top 10 Binance Pay Direct Link, and Lifetime SAR
Top 10 P2P Direct Link. Filter by the flagged
counterparty UIDs identified in the counterparty
analysis (Step 12). Sample 3-5 transactions
representing the highest-risk counterparties. For
each sampled transaction, extract: TxID, date, amount,
and asset. These are the transactions to include in
the RFI questions.
**RFI TRANSACTION IDENTIFIER RULES:**
When extracting transaction details for RFI questions,
the identifier used must be visible and searchable on
the user's end. Three common sources of incorrect
identifiers:
1. UAL INTERNAL TRANSACTION IDs: The User Asset Log
   displays internal system transaction IDs (short
   format, displayed in blue). These are Binance
   internal tracking numbers not visible to the user.
   Do NOT include them in RFIs. Always use the
   blockchain transaction hash (TxID) from C360 or the
   UAL hash field.
2. BINANCE PAY TRANSACTIONS: Use the Binance Pay Order
   ID (visible to the user), NOT the Binance Pay
   Transaction ID shown in Binance Admin. The
   Transaction ID is an internal system identifier the
   user cannot search in their transaction history.
3. FTM ALERT TXIDs: Do NOT copy-paste TXIDs from FTM
   alert dashboards or the internal data window. These
   system-generated identifiers often include asset
   suffixes (e.g., "USDT") and do not correspond to
   blockchain transaction hashes. Always retrieve the
   correct TXID from the User Operation Log (UOL) or
   Binance Admin.
Including any internal-only identifier in an RFI
constitutes internal information disclosure (ref:
qc-submission-checklist.md #4.5 — auto-fail).
---
## STEP 19: RFI ANALYSIS SUMMARY
**ICR Section:** RFI Analysis Summary
**What you see:** Edit button with default text:
"No RFIs were issued during this investigation, and no
RFI analysis is available. Click the refresh button in
this section if RFIs are issued."
**Action:**
IF RFI was sent and response received:
Analyze the adequacy of the user's answers and
supporting documents. Address whether the response
mitigates the identified risk.
IF no RFI was sent:
Retain the default text: "No RFIs were issued during
this investigation, and no RFI analysis is available."
**IF RFI was sent and user was uncooperative (replied but insufficient after 3 attempts):**
Summarize each RFI attempt and the user's response. State what specific information was requested, what the user provided, and why each response was deemed insufficient. Conclude with: "After [X] RFI attempts, the user's responses were assessed as intentionally insufficient. The user has been classified as uncooperative." This analysis must demonstrate that the investigator gave the user reasonable opportunity to address the concerns before classifying them as uncooperative.
**IF RFI was sent and user was unresponsive (no reply after reminders):**
State the RFI date, the number of reminders sent, the dates of reminders, and confirm no response was received. State: "After [X] reminders with no response, the user has been classified as unresponsive."
**Mandatory Content (Always Editable Field):**
Must contain analysis or the default statement.
Never empty.
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
---
## STEP 20: SUMMARY OF UNUSUAL TRANSACTIONS
**ICR Section:** Summary of the Unusual transactions
**What you see:** Edit button with preset format:
"Unusual activity performed between YYYY-MM-DD to
YYYY-MM-DD:
TOTAL SUCCESSFUL UNUSUAL TRANSACTIONS: X (XXXX USD)
TOTAL REJECTED UNUSUAL TRANSACTIONS: X (XXXX USD)"
**This step has two parts:**
**PART A: Transaction Totals**
**CRITICAL RULE:** These totals must reflect ONLY the
current L1 referral transactions — the specific
suspicious activity that triggered this case. Do NOT
use historical alert totals, lifetime transaction
sums, or aggregated volumes from prior cases. If
prior ICRs have already reviewed earlier activity,
those transactions are excluded from these totals.
**MITIGATED ALERT EXCLUSION:**
If the investigation successfully mitigates the risk associated with a specific alert — explaining with documented reasoning why the underlying transaction is not suspicious — that alert should be excluded from the suspicious activity count. The mitigated alert's transaction amount and date are removed from the totals.
Example: 3 alerts triggered on 2025-01-01 (1 transaction, $5,000), 2025-01-15 (2 transactions, $12,000), and 2025-02-01 (2 transactions, $8,000). If the 2025-01-01 alert is mitigated during the analysis (e.g., the transaction is confirmed as a legitimate cross-exchange rebalancing), the suspicious period becomes 2025-01-15 to 2025-02-01 with 4 suspicious transactions totaling $20,000.
When excluding mitigated alerts, briefly state which alerts were excluded and the mitigation basis in the plain text description below the totals: "1 alert triggered on [date] for [amount] was excluded from the suspicious activity totals as the underlying transaction was mitigated — [brief reason]."
**SUSPICIOUS ACTIVITY PERIOD BY CASE TYPE:**
The date range and transaction count for the Summary
of Unusual Transactions depends on the case type:
- **FTM cases:** First alert trigger date to last
  alert trigger date. Transaction count = number of
  FTM alerts triggered. Amount = total of alert
  amounts.
- **CTM cases:** Same as FTM — first CTM alert
  trigger date to last CTM alert trigger date.
- **Fraud/Scam cases (SSO/P2P referrals):** The
  specific date(s) of the fraudulent transaction(s)
  reported.
- **Case Team referrals (full account review):** Full
  account lifetime (registration date to date of
  review), including all transactions for the full
  period.
These calculations determine what populates the
"Unusual activity performed between YYYY-MM-DD to
YYYY-MM-DD" line and the total counts/amounts.
**LE-REFERRED CASES:** When the LE referral does not
identify specific suspicious transactions (e.g.,
broad data requests covering the entire account
history without flagging particular transactions),
the unusual transaction totals default to the
CTM-triggered alert transactions as the identifiable
suspicious activity. State this context in the plain
text description below the totals: "The LE referral
covered general account activity without identifying
specific suspicious transactions. The CTM alert
transactions are used as the basis for unusual
activity totals."
**CTM OFFBOARDING EXCEPTION — LIFETIME ALERT COUNT:**
For CTM cases where the recommendation is to offboard, the suspicious activity totals should reflect the lifetime count of relevant CTM alerts — including those reviewed and closed in prior ICRs — to demonstrate the cumulative pattern justifying offboarding.
Example: The current case was triggered by 1 gambling-related CTM alert. However, the user's lifetime gambling-related CTM alerts total 51 (1 current + 50 from prior ICRs that were individually closed or retained). The cumulative pattern of 51 gambling alerts over the account lifetime demonstrates persistent high-risk behavior that justifies offboarding even though each individual alert was previously assessed as insufficient for offboarding on its own.
In this scenario, the suspicious activity totals should state the lifetime count (51 alerts) with a note: "The suspicious activity totals reflect the lifetime CTM alert count to demonstrate the cumulative pattern of [alert category] activity that supports the offboarding recommendation. [X] of these alerts were reviewed in prior ICRs [references]."
This exception applies to CTM offboarding decisions only. Retain decisions continue to use current L1 referral totals only per the CRITICAL RULE above.
**IDENTITY-BASED UNUSUAL ACTIVITY:**
When the case referral reason is the account holder's
identity (e.g., FBI-indicted individual, confirmed
criminal, designated person) rather than specific
suspicious transactions, all account activity may be
classified as unusual. In such cases:
- The unusual transaction totals should reflect the
  ENTIRE account activity (full date range, all
  successful transactions, all volume)
- Add a justification sentence: "All account activity
  conducted by UID [X] is considered unusual as the
  account holder has been identified as [specific
  reason]."
- This approach is supported by the template
  instruction: "Should the investigation suggest that
  all activity is deemed suspicious, then the time
  frame and value should reflect that."
**DEVIATION EXPLANATION REQUIREMENT:**
Where the standard guidance does not explicitly address the case type, or the investigator determines it necessary to deviate from the standard calculation method (due to unusual case circumstances, technical issues, AI-generated data errors, L1 escalation errors, or other discretionary situations), the investigator must:
1. Populate the template as closely as possible to the standard format
2. Provide a brief explanation of how the transaction count, amounts, and dates were determined
Example: "The L1 referral did not identify specific suspicious transactions. The suspicious activity totals were calculated using the CTM alert transactions as the identifiable unusual activity. [X] alerts totaling [amount] between [dates] form the basis of these totals."
Failure to explain the methodology when deviating from standard guidance is a QC finding.
**MULTI-USER ICR RULE (Step 20):**
For multi-user ICRs, the Summary of Unusual
Transactions uses a SINGLE combined entry — not one
per user. Use the earliest start date and latest end
date across both users' suspicious activity. Combine
the total successful and rejected unusual transaction
amounts. Do not duplicate this section per user.
**HIGH ALERT COUNT — GENERALISATION:**
For cases involving a very high number of alerts (50+, 100+, 1000+), it is acceptable to generalise the suspicious activity totals rather than enumerate every individual transaction. State the total count, total value, and date range. Individual transaction-level detail is not required in the totals section — it is covered in the analytical sections (Steps 7-8).
Calculate from the L1 referral data:
- Total Successful Unusual Transactions (count + USD)
- Total Rejected Unusual Transactions (count + USD)
All local currency amounts must include USD equivalent
in square brackets.
Strict Format (Plain Text Only — No Tables):
Unusual activity performed between YYYY-MM-DD to
YYYY-MM-DD:
TOTAL SUCCESSFUL UNUSUAL TRANSACTIONS: X (XXXX USD)
TOTAL REJECTED UNUSUAL TRANSACTIONS: X (XXXX USD)
[Plain text description listing specific amounts and
TXIDs as applicable]
**Output format:** Wrap the complete Step 20 output (transaction totals + executive summary) in ONE ` ```icr ` block — no "Part A:" or "Part B:" labels inside the block (see ICR Output Formatting in icr-general-rules.md).

**PART B: Executive Summary**
Using the L1 Narrative and ALL outputs generated in
Steps 2-19 as context, write an executive case summary.
**CRITICAL — This is a NARRATIVE SUMMARY:**
It must tell the story of what actually happened — not
list sections. Summarize the events, the evidence, and
the specific findings from the investigation.
Format: Two paragraphs, 150-200 words total, neutral
investigative tone:
- Paragraph 1 (2-3 sentences): Why the user/case was
  flagged and the initial concerns. Use only phrases
  and facts present in the case data.
- Paragraph 2: One sentence per available section, in
  this order when available:
  1. User transactions overview
  2. CTM/FTM alerts or exposed addresses
  3. Top addresses by value
  4. Fiat transactions
  5. Internal CP analysis (use CP/CPs)
  6. Device/IP analysis
  7. OSINT
  8. LE inquiries/cases
  9. User communications
  Only sections that exist. Do not mention missing
  sections.
Constraint: Do not introduce numbers not present in the
case data. Do not add recommendations unless already
present.
**MANDATORY RISK POSITION:** The executive summary must
conclude with a risk position statement (1-2 sentences)
assessing whether the overall findings present mitigated,
partially mitigated, or unmitigated risk. Do not use the
words "retain," "offboard," or "RFI" in this statement.
This is distinct from the case recommendation (which
belongs in Step 21) — it is a factual summary of the
risk posture based on the evidence reviewed. Omitting
this statement is a QC-relevant gap as it leaves the
reader without an analytical assessment before reaching
the conclusion.
**QC Check (Ref: qc-submission-checklist.md #2.2):**
- Activity period explicitly stated.
- Totals explicitly stated.
- Summary synthesizes — does not copy body text.
---
## STEP 21: IV-CONCLUSION & RECOMMENDATION
**ICR Section:** IV-CONCLUSION
**What you see:** Empty manual entry box (0/10000) with
guidance text: "Manual input of 3-4 sentences is
required, provide a brief summary affecting the case
outcome and clearly state whether you want to retain or
offboard the user. What MLROs are required."
**Pre-Decision Gate (MANDATORY):**
Before writing ANYTHING:
1. Scan decision-matrix.md for rows where the Scenario Pattern matches the current case.
2. Check mlro-escalation-matrix.md for jurisdiction, MLRO contact, and dual escalation status. For case-type-specific decisions, retrieve the relevant country block from mlro-escalation-decisions.md.
3. Check for Dual Escalation (ADGM + Country MLRO).
**ADGM ESCALATION FOR NON-REPORTING JURISDICTIONS
(QUICK REFERENCE):**
When the user is from a non-reporting jurisdiction (no
local MLRO exists), ADGM escalation is most commonly
required for four case types: (1) Sanctions, (2) CSAM,
(3) Terrorism Financing, and (4) Proliferation
Financing. Other case types (money laundering, fraud,
unresponsive RFI, EDD) from non-reporting jurisdictions
generally do NOT require ADGM escalation. However, this
is a heuristic — always verify against the ADGM block 
in mlro-escalation-decisions.md for the specific case type,
as conditional escalation requirements exist for several
additional categories.
**SEYCHELLES QUEUE — NO-WAIT RULE:**
When escalating to the Seychelles project queue (for
non-reporting jurisdiction cases involving CSAM,
Sanctions, Terrorist Financing/World Check matches, or
Proliferation Financing), the investigator does NOT
wait for a response before proceeding with the
offboarding or retain decision. No MLRO is currently
assigned to the Seychelles queue — cases are queued for
future review. Escalate, then proceed immediately with
the case decision.
**ADGM COMPLEX CASE TAG:**
When escalating to ADGM MLRO, the investigator must tag the case with the appropriate complexity level. This affects the MLRO's SLA for review:
- Standard cases: default tag (no special action) — MLRO SLA is 35 business days from alert date
- Complex cases: tag as "Complex" in HaoDesk — MLRO SLA is 15 business days for first SAR, 30 business days for follow-up
- TF/CSAM/Proliferation Financing cases: tag as "Priority" — MLRO SLA is 10 days review + 1-5 days reporting
Cases qualifying as "Complex" include: multiple subpoena requests, legal/court-referred cases, employee-related investigations, cases involving multiple jurisdictions, and cases requiring extensive on-chain tracing.
Cases qualifying as "Priority" include: Terrorist Financing (as advised by LE or sanctions hit on local lists), CSAM, and Proliferation Financing.
The tag is applied in HaoDesk when submitting the L3 escalation. If uncertain about classification, default to "Complex" rather than standard — under-classifying a complex case may cause SLA issues for the MLRO.
   Key jurisdiction-specific triggers:
   - Argentina: Escalate if offboarding proposed OR
     case involves Argentinian fiat ramps
     (CoinEgg or other local channels).
   - India: Escalate only when determined suspicious.
   - Colombia: Escalate if involves fiat channel
     (Inswitch/Movii).
   - Venezuela: Escalate for serious fraud/criminal.
   - Brazil: Escalate only when determined suspicious.
     Always verify against the relevant country block 
     in mlro-escalation-decisions.md for the specific 
     case type and jurisdiction combination.
4. Verify no Auto-Fail triggers
   (qc-submission-checklist.md #3.12).
**LANGUAGE RULES FOR CONCLUSIONS:**
- Never use the word "pending" — it is a HaoDesk
  system status term. Use "while awaiting the outcome
  of," "upon completion of," or "following the
  resolution of."
- Never mention potential reporting obligations
  (SARs, STRs, or any external filing). Escalation
  to L3/MLRO is appropriate and should be stated.
  Reporting decisions belong to the MLRO — the L2
  investigator does not pre-judge or reference them.
- Write in plain, simple language. Many reviewers
  (L3, MLRO) may not be native English speakers. Use
  short, direct sentences. Avoid complex or ornate
  AI-generated phrasing.
- All local currency amounts must include USD
  equivalent in square brackets.
- Every risk factor stated must be paired with
  mitigating context if the recommendation is to
  retain. One-sided adverse narratives are not
  acceptable.
**CLOSE TO AVOID DUPLICATION VARIANT:**
When the case is being closed because a relevant RFI
has already been issued by any team covering the same
transactions or subject matter, the conclusion should
contain four elements only:
1. Summary of what was reviewed in this investigation
2. Key risks identified (briefly)
3. Reference to the existing open RFI (by case number)
   and the related ongoing investigation
4. Statement that the case is being closed to avoid
   duplication while awaiting the RFI outcome and L3
   review
Do not include offboarding recommendations or
excessive risk elaboration in this variant.
**CASE CLOSURE — ALREADY OFFBOARDED:**
When the investigation determines that the user has already been offboarded or submitted for offboarding (by another team, prior investigation, or automated process) at the time of the current review:
1. The case may be completed without performing a Full Review — Pre-Check or Initial Review phase completion is acceptable
2. Document the existing offboarding status (date, reason, submitting team)
3. State in the conclusion: "The user was already offboarded on [date] under reason [reason] by [team]. This case is closed as the offboarding action has already been taken."
4. No additional offboarding submission, RFI, or MLRO escalation is required unless the current investigation reveals risks not covered by the original offboarding (e.g., sanctions exposure requiring Sanctions team referral)
**AI MITIGATION TOOL:**
AI can be used to generate mitigation language.
Provide the AI with: (1) the entity's business
profile from KYB, (2) specific mitigating factors
(proportionality of flagged vs total volume,
sub-account structure, business model expectations),
and (3) clear instruction to frame the narrative as
mitigating. This is an accepted practice for drafting
mitigation sections.
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
**Structure (Strict):**
TARGET: 2-3 sentences for standard offboard/retain
cases. The conclusion assumes the reader has already
absorbed the executive summary (Step 20 Part B).
Do not restate facts, figures, entity names, Elliptic
scores, LE case details, counterparty percentages,
or transaction ratios that appear in the summary.
The conclusion is a DECISION STATEMENT — not a
second summary.
For standard offboard or retain cases, use this
compressed structure:
- Sentence 1: One clause stating the basis for the
  decision (e.g., "Based on the LE profile, the
  pass-through transaction pattern, and the
  contaminated counterparty network"). This is a
  reference to the themes — not a restatement of
  the details.
- Sentence 2: The recommendation with withdrawal
  position (e.g., "it is recommended to offboard
  UID [X] with withdrawals enabled").
- Sentence 3: MLRO escalation routing if applicable.
For fraud/scam cases with refund process, the
structure expands to accommodate refund instructions:
PARAGRAPH: A single plain-text paragraph containing:
1. Core finding (e.g., "Confirmed P2P Fraud")
2. Asset status (e.g., "Current balance is $X")
3. Refund instruction if applicable:
   - For fraud cases where suspect balance >$1,000:
     Refund process should be engaged per
     scam-fraud-sop.md (3 reminders).
   - For fraud cases where suspect balance <$1,000:
     Refund process is optional but can be considered.
   - 30-Day Block Threshold: The 30-day limit runs
     from the date SSO placed the original block. If
     no refund intention is shown within 30 days,
     proceed with the offboard/retain/escalate decision.
   - Exception: An additional 30 days may be granted
     if there is active LE progress or genuine victim
     attempts to contact LE.
   - A block exceeding 30 days does NOT exempt the
     reminder procedure if balance >$1,000.
4. Final recommendation: Offboard / Retain / Escalate
5. For offboarding: explicitly state "offboarding with withdrawals enabled" (ref: OFFBOARDING WITHDRAWAL RULE below). Additionally state the offboarding reason that will be selected in the User Investigation tab and Binance Admin — this must match the ICR conclusion exactly (three-way match requirement).
**Pending Refund Workflow:**
When requesting a refund before offboarding:
1. Send refund request via FCI-Agent-RFIBot on WEA
   with: refund amount, victim UID, suspect UID.
2. Change case status to "Pending - Refund."
3. The case remains in your queue.
4. Screenshot the refund request and attach to case.
5. Monitor the case: check the WEA chat for agent
   responses (look for "Done" + Chat ID).
6. Check weekly — go into the Chat ID to see if the
   suspect has responded to refund reminders.
7. If suspect refuses or does not respond after the
   3 reminders are sent: screenshot the refusal/
   non-response, attach to case, proceed to offboard.
   You do NOT need to wait the full 30 days if refusal
   is clear.
8. Track all pending refund cases on a personal
   tracking list — review weekly.
REFUND CASE STATUS RULE: Cases in "Pending - Refund" status remain in the investigator's queue. The investigator is responsible for monitoring these cases. When the refund process completes (either successful refund, suspect refusal, or 30-day expiry), the investigator must update the case status and proceed with the final decision (offboard/retain/escalate). Do not leave cases indefinitely in "Pending - Refund" status — the 30-day block threshold (counted from the date SSO placed the original block) applies regardless of the refund status.
ESCALATION LINE (if applicable):
"Escalation to ADGM and [Country] MLRO is required."
ADGM is ALWAYS listed first as the primary MLRO for
all .com users. For dual-escalation jurisdictions,
the format is always: ADGM first, then local MLRO
second. Never reverse this order. For single-
escalation jurisdictions (Dual Escalation: NO), list
only the local MLRO: "Escalation to [Country] MLRO
is required." Do not mention ADGM for jurisdictions
where Dual Escalation is NO.
**SANCTIONS TEAM ESCALATION MECHANICS:**
When escalating to the Sanctions team:
1. In the HaoDesk case, click Forward
2. Select "Sanctions" from the dropdown
3. Submit — the case automatically goes to your pending
   queue
4. The Sanctions team creates a separate case in their
   queue
5. You receive a HaoDesk notification when their
   investigation is complete
6. The Sanctions team provides recommendations only —
   they do NOT close your case, file offboarding, or
   apply blocks
7. Based on their recommendations, proceed with:
   offboarding, retain, or send RFI/SOW as recommended
Note: If the Sanctions team does not respond within a reasonable timeframe and the case requires closure for SLA reasons, the investigator may proceed with the case decision based on available evidence. Document the Sanctions team referral and note that a response is outstanding. The Sanctions team's recommendations, when received, can be addressed in a subsequent review if they change the risk assessment.
Note: You can escalate to the Sanctions team AND take
parallel actions (e.g., exhaust RFI reminders, contact
the P2P team for merchant users) while the case is
pending with Sanctions.
**SPECIAL INVESTIGATIONS (SI) TEAM ESCALATION:**
Two escalation paths exist:
PATH 1 — EXTERNAL REPORTING INTENTION (HaoDesk
Forward):
If the case meets the SI-FCI referral matrix
requirements for external LE reporting:
1. In the HaoDesk case, use the comment box to type
   "Transfer to SI team"
2. Click Forward, select the SI team from the dropdown
3. Submit — the case goes to your pending queue
4. SI will investigate and return the case with
   recommendations
5. Upon return: proceed with offboarding, retain, or
   await external reply based on SI recommendations
PATH 2 — INTERNAL REFERRAL ONLY (Binance Admin
Report):
If the case meets SI internal referral criteria (e.g.,
potential ML network with 10+ devices, 5+ accounts with
same selfies) but does NOT meet external reporting
requirements:
1. Complete the case review as normal on HaoDesk
2. Go to Binance Admin > User Reports > Submit New
   Report
3. Enter the UID, select "Special Investigations Team"
4. Choose the appropriate category
5. Indicate whether LE requests exist on the user
6. Provide a brief summary of why the case is being
   referred
7. Submit — no HaoDesk forward needed
**IF Offboarding:**
- WOM (Withdrawal Only Mode, no deposit & trade)
  must be applied. Block reason must match offboarding
  reason.
- The conclusion text must already state "offboarding
  with withdrawals enabled" or equivalent per the
  OFFBOARDING WITHDRAWAL RULE above. If this language
  is missing from the conclusion, add it before
  proceeding to submission. This is a rejection
  trigger if omitted.
- "Complete - Offboard" button automatically submits
  the request and applies WOM. Do NOT submit a
  separate Admin request.
- If user ALREADY offboarded: Select "Complete -
  Offboard" → scroll down in pop-up → select
  "Skip Offboard to proceed case update."
- If full freeze required (withdrawals NOT allowed):
  Manually remove the auto-WOM and apply correct
  Freeze block after clicking.
**IF Retaining:**
- Verify no Fraud/CSAM exposure exists.
- Remove all investigation-related blocks.
**Formatting:**
- Plain text only. No bullets, no bold, no markdown.
- Strict maximum: 2-3 sentences for standard cases,
  4-6 sentences for fraud/scam refund cases.
- No bracket explanations (e.g., do not write
  "[Entity Tag: BR]").
- No tag references or system metadata in the
  conclusion text.
- Do not state the offboarding dropdown reason
  (e.g., "Suspicious Transaction Activities,"
  "Scams," "KYC Fraud," "High Potential to Money
  Laundering") in the conclusion text. The
  offboarding reason is selected in the User
  Investigation tab dropdown and does not need
  to appear in the narrative paragraph.
**NO NARRATIVE DUPLICATION RULE:**
The executive summary (Step 20 Part B) carries the
full narrative of the investigation — the events,
evidence, and specific findings. The conclusion must
NOT re-tell the story. Do not restate specific
figures, entity names, Elliptic scores, counterparty
contamination percentages, LE case details, or prior
ICR context that are already present in the executive
summary. The reader has already absorbed the summary
before reaching the conclusion.
The conclusion adds the DECISION only. It must assume
full context from the summary and limit itself to:
(1) One sentence stating what triggered the case
(2) One sentence stating the key unmitigated risks
    — in general terms, not restating specifics
(3) One sentence stating key mitigations if
    recommending retain — in general terms
(4) The recommendation (offboard / retain / RFI)
    with withdrawals enabled if offboarding (see
    OFFBOARDING WITHDRAWAL RULE below)
(5) MLRO escalation routing if applicable
If the conclusion exceeds 3 sentences for standard
cases (or 6 sentences for fraud/scam refund cases),
or restates detail from the executive summary, it
must be cut back. When in doubt, shorter is better
— 2 sentences is preferred over 3.
**OFFBOARDING WITHDRAWAL RULE (CRITICAL):**
When the recommendation is to offboard, the
conclusion must explicitly state that withdrawals
are to remain enabled. Use the phrase "recommend
offboarding with withdrawals enabled" or equivalent
(e.g., "recommend the account be offboarded under
Withdrawal Only Mode"). Never state "recommend
offboarding" without specifying the withdrawal
position.
This is a mandatory requirement. Offboarding
submissions that do not confirm withdrawals enabled
will be rejected by the offboarding team. The only
exceptions are:
(a) An active LE seizure/freeze order explicitly
    prevents withdrawals, OR
(b) The Sanctions team or Special Investigations
    team has explicitly requested no withdrawals.
In either exception case, state the exception and
the authority for it: e.g., "recommend offboarding
with withdrawals restricted per LE freeze order
[reference]."
---
## PRE-SUBMISSION VERIFICATION
**Trigger:** User says "ready to submit," "check the case," or "run QC checks."
**Action:**
1. Identify the case type.
2. Check all Auto-Fail items from qc-submission-checklist.md first — flag any at risk.
3. Run through each QC section sequentially (KYC > Suspicious Activity > Main Body > RFI > Escalations > Offboarding > Attachments > Others). For escalation checks (#5.1-5.4): re-derive the escalation routing independently from source documents (mlro-escalation-matrix.md Quick Reference) rather than verifying against the escalation stated in the conclusion. Quote the source table row or confirm absence. This prevents propagation of an earlier escalation error through QC.
4. Skip checks marked N/A for the case type.
5. For each check: state what it requires, confirm satisfied or flag what is missing.
6. Summarize findings with estimated point impact.
7. Recommend fixes before submission.
**Additional checks:**
- Verify operation log is completed.
- Verify "Save All and Generate" has been used for attachments.
- Verify all local currency amounts include USD equivalents.
- Verify no use of "pending" in narrative text.
- Verify no SAR/reporting references in conclusion.