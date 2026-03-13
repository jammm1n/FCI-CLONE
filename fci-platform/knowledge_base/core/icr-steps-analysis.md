# ICR Steps: Evidence Analysis (Steps 7-16)
## Purpose
This document covers Steps 7 through 16 of the ICR form. These steps involve analyzing account activity, on-chain exposure, counterparties, devices, OSINT, and user communications.
Cross-cutting rules in icr-general-rules.md apply to every step below.
---
## STEP 7: USER TRANSACTION OVERVIEW
**ICR Section:** User transaction overview
**What you see:** Hexa-populated text with basic
transaction overview and alert rule references.
**OUTPUT LENGTH PRIORITY (OVERRIDES ALL OTHER
GUIDANCE IN THIS STEP):**
The transaction overview output must not exceed 150
words including the risk assessment statement. The
FTM Alert Analysis Structure guidance below describes
WHAT to analyse during the investigation — it does
not mean every element must appear in the final ICR
output. Summarise findings concisely in a single
paragraph. Specific deposit-withdrawal pair examples
with individual timestamps belong in the Phase 0
narrative theory for investigator context — they
should NOT appear in the ICR output unless one or
two examples are needed to illustrate a critical
pattern. When FTM alerts exist, integrate the alert
summary (count, date range, total flagged value, and
the dominant pattern observed) into the single
transaction overview paragraph rather than creating
a separate Supplemental Analysis section. One
paragraph, one risk assessment statement, done.
**Required output:**
A single ~80-100 word paragraph covering:
- Total number of transactions, date range (earliest
  to latest), and total value in original currency
  with USD equivalent in square brackets
- Crypto deposit/withdrawal count and USD volume
- Outbound-to-inbound velocity ratio (flag if >90%)
- Negative confirmation of absent transaction types
  (Fiat, P2P, BPay, BCard — explicitly state which
  were NOT observed)
- Trading analysis (Futures vs Spot) if data available
- For corporate accounts: explicit statement on
  whether the pattern is "consistent with" or
  "inconsistent with" the entity's declared business
  profile
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
**Mandatory Content (Always Editable Field):**
This field must NEVER be empty. Must contain velocity
assessment, ratios, and fund flow summary.
**Risk Assessment Statement (CRITICAL — QC Focus):**
This statement is MANDATORY regardless of whether
the transaction narrative was written in this chat
or received from a parallel chat. If the parallel
chat included a risk assessment, verify it against
the full case context and revise if necessary. If
the parallel chat did not include one, write it
here.
After the transaction narrative, append a brief
statement (1-2 sentences) giving your professional
assessment of the risk. This shows QC that you have
understood and evaluated the L1 referral.
Examples:
- "The transaction pattern is consistent with the
  reported fraud allegation — rapid receipt and
  dissipation of victim funds with no legitimate
  trading activity."
- "Despite the L1 referral, the transaction pattern
  is consistent with normal P2P merchant activity
  and does not present elevated risk indicators."
- "The activity suggests pass-through behavior with
  a 95% outbound-to-inbound ratio and no trading,
  warranting further investigation."
**FTM ALERT ANALYSIS STRUCTURE:**
When analyzing FTM alerts (SAWD, TLI, TLO, LVPI, LVPO,
DSLI, dormant account alerts, etc.), the narrative must
follow this structure:
FOR DEPOSIT/INBOUND ALERTS:
1. State the alert type and the deposit that triggered it
2. Describe what the deposit funded on the account
   (spot trading, futures, earn products, margin, P2P
   trades, or direct withdrawal)
3. State where the funds ultimately went — withdrawn,
   still held on the account, or used for trading
4. Conclude with a risk assessment: was the pattern
   unusual or not? Was the movement rapid or not?
Example flow: "A [SAWD/TLI/LVPI] alert was triggered
by a deposit of [amount] on [date]. The deposit funded
[spot trading activity / was held in earn products /
was not traded]. The funds were subsequently [withdrawn
via crypto to external wallet / remain on the account /
traded via P2P]. The pattern [is consistent with rapid
fund movement and warrants further investigation /
does not indicate unusual activity given the user's
trading profile]."
FOR WITHDRAWAL/OUTBOUND ALERTS:
1. State the alert type and the withdrawal that
   triggered it
2. Describe what preceded the withdrawal — what funded
   it (deposit, trading profits, earn redemption)
3. State whether the deposit-to-withdrawal pattern
   suggests pass-through behavior
4. Conclude with a risk assessment
**FLOW OF FUNDS NARRATIVE (QC EXPECTATION):**
QC expects the transaction overview to describe the
causal chain of fund movements — not just list figures
by category. A QC finding will result from merely
stating "deposits totalled $X, P2P totalled $Y,
withdrawals totalled $Z" without connecting them. The
narrative must explain: where funds entered the account
(deposits, P2P inbound, fiat), what happened to them on
the account (spot trades, futures, earn products), and
how they exited (withdrawals, P2P outbound, Binance
Pay). The User Asset Log (UAL) and C360 activity
summary support this causal chain analysis.
Failure to provide analysis on FTM alerts — including
identifying what funded the activity and where it led
— is a QC finding (ref: qc-submission-checklist.md
#3.3).
**FTM ALERT CATEGORY DISTINCTION:**
FTM alerts divide into two categories requiring
different analytical approaches:
MOVEMENT-BASED ALERTS (SAWD, DSLI, TLI, TLO, LVPI,
LVPO, dormant account): Analyze the fund flow pattern
(deposit → activity → withdrawal). No mandatory
counterparty investigation at the alert analysis level
— counterparties are covered in Step 12.
COUNTERPARTY-BASED ALERTS (Binance Pay, P2P): The
alert is triggered by the counterparty's risk profile
or jurisdiction. The alert analysis MUST include:
(a) The counterparty UID
(b) A brief risk assessment of the counterparty
    (ICR history, LE requests, offboarded/blocked
    status, jurisdiction)
(c) Whether the counterparty risk can be mitigated
Failure to include counterparty analysis for Binance
Pay or P2P alerts is a QC finding.
**HIGH ALERT COUNT — PER-RULE ANALYSIS:**
When an account has a high number of FTM alerts
(50+), individual alert-by-alert analysis is not
required. Instead, group analysis by rule type
(e.g., SAWD alerts, THLI alerts, LVP alerts).
For each rule type, explain what activity on the
account triggered that alert category and whether
the pattern is consistent with legitimate use or
constitutes unusual activity. Do not cite internal
rule codes in the ICR narrative (ref: Output
Hygiene rule in icr-general-rules.md) — instead
describe the observable behavior (rapid
deposit-to-withdrawal, threshold exceedance,
high-value P2P patterns, etc.).
**COMMON FTM ALERT MITIGATIONS:**
The following patterns trigger SAWD and similar
rapid-movement alerts but may represent legitimate
activity. When identified, state the mitigation
explicitly:
- **Arbitrage trading:** User deposits and withdraws
  the same stablecoin (e.g., USDT) repeatedly across
  exchanges to capture small price differences. The
  system flags the deposit-withdrawal cycle as rapid
  movement, but the pattern is consistent with
  legitimate arbitrage if the amounts are similar and
  the timing aligns with known exchange price
  differentials.
- **Cross-chain bridging:** User deposits via one
  blockchain network (e.g., Ethereum/ERC-20) and
  withdraws via another (e.g., TRON/TRC-20). This
  triggers movement alerts but represents a network
  transfer, not fund dissipation.
- **Cross-exchange rebalancing:** Similar to arbitrage
  — funds move between Binance and external exchanges
  for portfolio management purposes.
These mitigations do NOT automatically clear the risk.
State the mitigation, then assess whether the pattern
is fully explained by the legitimate activity or
whether additional indicators (counterparty risk,
jurisdiction risk, volume disproportionate to profile)
remain unresolved.
**PASS-THROUGH RATIO — RISK CALIBRATION:**
A high outbound-to-inbound ratio (90%+) does not
independently support offboarding or RFI. It is a
descriptive metric that gains or loses significance
depending on what accompanies it.

Before treating pass-through as a risk factor:
1. Verify the pattern against the UOL — confirm what
   actually occurred (arbitrage cycles, cross-exchange
   rebalancing, and cross-chain bridging all produce
   high pass-through ratios legitimately)
2. Check whether any other unmitigated red flags exist
   alongside the pass-through pattern
3. If pass-through is the only remaining indicator
   after all other risks are verified and mitigated,
   retain the account

Pass-through becomes significant only when it forms
part of a convergent pattern with additional
unmitigated indicators (e.g., contaminated
counterparties, high-specificity LE cases, confirmed
direct exposure to high-risk Elliptic entities). The
pattern of convergence — not the ratio alone — drives
the decision.

The pass-through ratio must still be described in the
transaction overview per QC #3.3 — this calibration
applies to the decision weight, not to the
documentation obligation. State the ratio, describe
the fund flow, then state the risk position.

See Decision Matrix Rule #57.
**PHASED APPROACH — PRE-CHECK/INITIAL COMPLETION EXCEPTION:**
For CTM/FTM phased approach cases, RFIs, MLRO escalation, and offboarding may only be performed at the Full Review phase. However, a case may be completed at the Pre-Check or Initial Review phase if the user under investigation has already been offboarded or submitted for offboarding by the time of the review. In this scenario, document the existing offboarding status and close the case at the current phase.
**CORPORATE TRANSACTION MITIGATION:**
For corporate accounts where the declared business
profile explains the observed transaction pattern
(e.g., OTC broker = high fiat volumes from
third-party clients, merchant = high counterparty
count, payment processor = high throughput), reference
the business profile explicitly as mitigation: "The
transaction pattern is consistent with the entity's
declared business profile as [type], which involves
[activity]." Do not flag expected business activity as
inherently suspicious.
**C360 DATA GAP — STAKING AND LENDING:**
Staking and lending activities are not reflected in
C360. If transaction volumes or fund holding patterns
appear unexplained by the C360 data, check the User
Asset Log (UAL) for staking and lending products.
These activities may explain why funds are held for
extended periods or why balances do not match
expected transaction flows.
**UAL DOWNLOAD LIMITATION:** The User Asset Log export
is limited to a maximum of 365 days per download. For
accounts with activity spanning multiple years, multiple
exports segmented by date range are required to obtain
complete fund flow data. Plan UAL downloads around the
specific period of suspicious activity identified in the
L1 referral rather than attempting lifetime exports.
**UAL FUND FLOW ANALYSIS METHOD:** When analysing the
User Asset Log to trace fund flows, read the data from
bottom to top (oldest to newest) as the UAL presents
entries in reverse chronological order. Match
transactions across rows using three fields: (1)
timestamp — operations occurring at the same second or
within seconds are typically part of the same operation,
(2) amount — a deposit amount appearing as a negative
in one asset and positive in another at the same
timestamp indicates a trade/conversion, and (3)
operation type code — the numerical code can be looked
up on the Confluence operation type reference page if
the short description is unclear.
**BOT TRADING vs SINGLE ORDER DISTINCTION:** When UAL
shows many rows of trading activity, distinguish between
two patterns: (1) Rows with seconds between timestamps
(e.g., 21s, 22s, 27s, 29s) indicate likely bot/API
trading — multiple distinct automated operations
executed in rapid succession. This can be confirmed via
the UAL first page which shows API IP information. Bot
trading is a valid mitigating factor for SAWD alerts
(ref: decision-matrix.md Rule #26). (2) Rows at the
exact same timestamp indicate a single large order
filled incrementally by the exchange order book — this
is one operation generating multiple fill entries, not
multiple trades. Do not count these as separate
transactions in transaction volume assessments, as it
would significantly overstate the user's actual trading
activity.
**UNUSUAL TRANSACTION TOTALS — CRITICAL RULE:**
The transaction totals for the current case must
reflect ONLY the current L1 referral transactions —
the specific suspicious activity that triggered this
case. Do not use historical alert totals, lifetime
transaction sums, or aggregated volumes from prior
cases. If prior ICRs have reviewed and approved
earlier activity, state this and narrow the focus.
**FTM PHASED APPROACH — PRIOR ICR 90-DAY WINDOW:**
When reviewing FTM cases under the phased approach, prior ICRs filed within 90 days of the current alert must be identified and assessed for behavioral similarity. The comparison method is:
1. Check whether new alert rule codes have been triggered that were not present in the prior ICR. If yes → escalate to Initial Review regardless of other factors.
2. If no new rule codes: check whether the triggered TM rules are the same AND the alerted transaction amounts are materially similar (difference not greater than 3x the prior alert amount).
3. If rules and amounts are materially similar: compare Push and Pull factors to determine if the risk profile has changed.
Note: LVP-I (Large Value Payment Inbound) and LVP-O (Large Value Payment Outbound) are different rule codes as the direction of fund flow differs. Do not treat these as the same rule when comparing.
**QC Check (Ref: qc-submission-checklist.md #1):**
- Velocity assessment present.
- Negative confirmations present.
- Clean narrative paragraph — no file references or
  citation brackets.
---
## STEP 8: CTM ALERTS
**ICR Section:** CTM Alerts
**What you see:** Hexa-populated alert summary with
direction, category, address, exposure amount, risk
scores, and transaction count.
**Action — Determine which prompt to use:**
IF data includes a "Snapshot of Suspicious Transactions"
(specific flagged transactions):
→ For cases with specific flagged transaction spreadsheets, fetch the CTM Enhanced Analysis prompt from the reference tier via `get_prompt("ctm-enhanced")`
IF data is general lifetime alert summary:
→ Write the CTM alert summary using the following spec:
**Required output:** Single paragraph, 60-80 words.
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
1. Report the date range covered by the CTM alerts
   (only if start and end dates are explicitly present).
2. Identify the top 1-3 entities by exposure amount (or
   by risk score if exposure is not provided). For each:
   entity attribution (or "unattributed"), exposure
   amount, and associated wallet address(es).
3. State the number of distinct entities if countable
   from the data (do not approximate).
4. Describe any explicit patterns (repeated exposure to
   same entity, consistently high scores, concentration
   in few entities).
5. End with: "This is a summary of the provided alert
   data and requires manual verification against the
   underlying CTM records."
IF no CTM data exists:
→ State "No off-chain alerts triggered."
**BINANCE ADMIN CTM ALERT LOOKUP:**
To review the full CTM alert history in Binance Admin:
- Navigate to: Asset tab → Deposit Control Management
  → Abnormal Chain Transactions
- Search by UID (not case ID) to retrieve all alerts
  for the user's lifetime
- Do NOT rely on "Abnormal Deposit and Withdrawals" —
  this view is incomplete and may not display all
  triggered alerts
- Click on individual cases to view the CTM team's
  investigation report, disposition (closed/escalated),
  and the specific addresses involved
- Compare this data against the Hexa-populated CTM
  section and C360 data for completeness
**CTM PRE-CHECK — TRACING REQUIREMENT FOR INDIRECT EXPOSURE:**
At the Pre-Check phase for CTM alerts, blockchain tracing using both Elliptic Lens and Elliptic Investigator is required for indirect exposure in the following alert categories: CSAM, Cybercrimes, and Illicit Activity. Tracing must include:
- Temporal assessment (transaction timing relative to high-risk entity activity)
- Directional relevance (source vs destination of funds)
- Wallet ownership assessment (does the user control intermediary wallets?)
- Unattributed cluster identification (behavioral association with known entities)
Direct exposures do not require tracing at Pre-Check — the exposure is already confirmed.
**Key Rules for Both Prompts:**
- All USD amounts: $ with comma separators
  (e.g., $3,889,921.42)
- Dates: YYYY-MM-DD format
- Full wallet addresses for top 3 high-risk entities
  — NEVER truncate
- End with the mandatory verification sentence as
  specified in the prompt
**Ref:** CTM-on-chain-alerts-sop.md for alert category
definitions and phase routing logic.
---
## STEP 9: LIFETIME TOP 10 EXPOSED ADDRESS
**ICR Section:** Lifetime Top 10 Exposed Address
**What you see:** Hexa-populated text with exposed
address data (direction, address, entity, exposure
amount, date range).
**Action:**
1. Audit the Hexa content.
2. Open with the standardized Elliptic template.
3. Identify all high-risk entities with full wallet
   addresses.
**If Elliptic data was extracted by the ingestion
pipeline:**
The investigator will paste structured Elliptic
data containing a Wallet Screening Table and
Summary Statistics. Using this data:
1. Verify all wallet addresses are complete (not
   truncated)
2. Apply the standardised Elliptic opening
   template: "Elliptic screening was conducted on
   [count] wallet addresses. Risk scores ranged
   from [min] to [max] out of 10."
3. For high-risk wallets (score >= 5): include
   the full wallet address, entity attribution,
   alert category, and exposure amount
4. For low-risk wallets: state "No additional
   significant risks were identified among the
   remaining addresses"
5. If any wallets are attributed to gambling
   entities: check gambling-legality-matrix.md
   for the user's jurisdiction and state whether
   gambling is legal, illegal, conditionally
   legal, or unregulated in that jurisdiction
6. Cross-reference against CTM alert data from
   Step 8 for overlap
7. Append a risk position statement
Do not paste the extraction table into the ICR.
Write a narrative paragraph using the data.
Target: 80-120 words.
Supplemental Analysis for exposed addresses must not
exceed 120 words excluding any standard mitigation
text provided by senior investigators. If all exposed
addresses are low risk, the entire section can be
covered in 2-3 sentences.
**COMBINED SCREENING WORKFLOW (Steps 9 + 10):**
In practice, investigators do not screen exposed
addresses and top addresses by value as two separate
exercises. The standard workflow is:
1. Obtain the exposed addresses list (from C360 /
   Hexa) and the top 10 addresses by value list
   (from C360).
2. Combine both lists into a single batch.
3. De-duplicate — addresses appearing in both lists
   are screened once only.
4. Screen the combined de-duplicated batch through
   Elliptic as a single operation.
5. Use the screening results to populate both Step 9
   and Step 10 narratives.
When a case has NO exposed addresses (common), the
batch consists only of the top 10 by value addresses.
In this scenario, Step 9 should either retain the
Hexa default text or state: "No exposed addresses
were identified for this account." All substantive
Elliptic analysis then appears in Step 10.
When a case HAS exposed addresses, the screening
results are split across both steps as follows:
- Step 9: Brief acknowledgement of the exposed
  addresses, directing the reader to Step 10 for
  the full Elliptic analysis.
- Step 10: Contains the Elliptic opening template,
  full risk score range, all detailed high-risk
  wallet analysis, and the risk position statement.
See Step 10 below for the full analysis placement
rules.
**Standardized Opening (Robert's Rule):**
The Elliptic opening template and all substantive
wallet analysis are presented in Step 10 (Top
Addresses by Value), not in this section. See the
COMBINED SCREENING WORKFLOW above.
**STEP 9 NARRATIVE CONTENT:**
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
When exposed addresses exist, Step 9 should contain
a short paragraph (2-4 sentences maximum) that:
1. States how many exposed addresses were identified
2. Notes the direction (deposit/withdrawal) and
   general category of exposure (e.g., fraudulent
   activity, gambling, obfuscation)
3. Directs the reader to Step 10: "Full Elliptic
   screening analysis covering both exposed addresses
   and top addresses by value is presented in the
   following section."
When no exposed addresses exist, state: "No exposed
addresses were identified for this account. Elliptic
screening analysis is presented in the following
section."
Do not include the Elliptic opening template, risk
score ranges, individual wallet analysis, or risk
position statements in Step 9. These belong in
Step 10.
**RESCREENING RULE:**
Always rescreen wallets through Elliptic at the time
of investigation. Do not rely solely on risk scores
from the L1 referral or CTM alert — scores can change
between referral and investigation dates due to
attribution updates or rescreening cycles. If the
rescreened score is materially different from the
original referral, note this change as it may
constitute a mitigation factor (e.g., "At the time of
referral the wallet scored 7/10; upon rescreening on
[date], the score decreased to 3/10, indicating
reduced risk attribution by Elliptic").
**SCREENING OBLIGATION:**
Batch screening of all top 10 exposed addresses and
top 10 addresses by value through Elliptic is
mandatory for every investigation. Transaction-level
batch screening (screening individual TxIDs) is
recommended but not mandatory.
**ELLIPTIC vs UOL CROSS-REFERENCE (ADVISORY):**
Elliptic top 10 by value and exposed addresses are
derived from aggregated blockchain tracing and do not
confirm the user directly transacted with the
attributed entity. An entity appearing in these lists
may reflect indirect exposure through intermediary
wallets rather than a direct counterparty
relationship.

When UOL cross-reference data is available (provided
by the web app or through manual UOL review), use it
to distinguish direct from indirect exposure:

IF an address appears in the UOL deposit/withdrawal
history: The exposure is direct. Apply standard
high-risk wallet documentation per the HIGH-RISK
WALLET DOCUMENTATION rules below.

IF an address does NOT appear in the UOL
deposit/withdrawal history: The exposure is indirect.
State in the ICR: "The entity [name] does not appear
as a direct transaction counterparty in the User
Operation Log, indicating the exposure is indirect
(via intermediary wallets)." Indirect exposure carries
significantly less risk weight than direct exposure.
Indirect exposure alone, without additional
corroborating indicators, is generally mitigable.

EXCEPTION: Indirect exposure through one hop with a
high-volume intermediary may still warrant attention.
If the intermediary wallet handled significant volume
and the temporal proximity is close, note this and
assess proportionally rather than dismissing outright.

When UOL data is not available, standard Elliptic
analysis applies without this additional layer. This
is an advisory analytical step — not a mandatory gate
or a replacement for batch screening.

**WEB APP UOL INTEGRATION:** When the investigator
processes Elliptic data in a parallel chat using
the ingestion pipeline and the web app provides UOL
cross-reference data, the extraction output will
include a Section 3 (UOL Cross-Reference) and UOL
Status fields per wallet in Section 1. This
structured UOL data replaces the need for manual
UOL lookup of screened addresses. The main chat
should treat the UOL Status field as equivalent to
a manual UOL check for the purposes of applying
Rule #59. If the extraction does NOT include
Section 3 (because the web app did not provide UOL
data, or the investigator did not use the web app),
the manual UOL cross-reference procedure described
above remains available as an advisory step.

See Decision Matrix Rule #59.
**Elliptic Customer Profile Caveat:**
The Elliptic Customer Profile view (searchable by UID)
aggregates all prior wallet screenings for that user
from all investigators. These results may be outdated
and do not substitute for fresh batch screening. Use
the Customer Profile for contextual reference only —
always perform a new batch screening with current data.
**RISK SCORE THRESHOLD RULE:** Only wallets scoring
5 or above out of 10 require individual analysis.
Wallets below 5 are dismissed in one sentence: "No
additional significant risks were identified among
the remaining addresses." Do not name triggered rules
(Gambling, Sanctions, Fraudulent, Obfuscating, etc.)
for wallets scoring below 5 — the low score means
Elliptic assessed the exposure as negligible and
naming the rule creates an unnecessary mitigation
obligation.
Note: If the risk cannot be fully mitigated within this section (e.g., a high-risk wallet requires counterparty context from Step 12 or LE context from Step 6 to assess), provide a cross-reference: "This exposure is further assessed in the context of [section name] below." Every risk identified must be mitigated somewhere in the report — if not in this section, explicitly direct the reader to where the mitigation appears.
**HIGH-RISK WALLET DOCUMENTATION (5 or above):**
For every wallet scoring 5 or above, document ALL
of the following in the narrative:
- Full wallet address (never truncate)
- Entity name from Elliptic (e.g., "HUIONE Pay",
  "Hydra Market", "Tornado Cash"). Do not describe
  wallets generically as "illicit" or "fraudulent"
  without naming the attributed entity. If the
  wallet is unattributed in Elliptic, state
  "unattributed entity" explicitly.
- Direction: whether funds moved TO the entity or
  FROM the entity (or both)
- Number of hops between the user's wallet and the
  high-risk entity
- Brief comment on the nature of the exposure
Write one paragraph covering all high-risk findings.
Do not write a separate paragraph per wallet.
**DOMINANT ENTITY RULE FOR HIGH-RISK WALLETS:**
When a high-risk wallet's score is overwhelmingly
driven by one entity (e.g., a Ponzi Scheme
contributing 60%+ of the source or destination
exposure), report only the primary entity driving
the score and its contribution percentage. Secondary
triggered rules (e.g., Obfuscating, FATF Increased
Monitoring, Sanction List, Fraudulent) with minor
percentage contributions should NOT be listed in the
ICR narrative.
Secondary triggered rules should only be mentioned
if they meet EITHER of these thresholds:
(a) The rule individually represents more than 5%
    of the source or destination exposure, OR
(b) The rule relates to a sanctioned entity that
    requires escalation assessment per the SANCTIONS
    ENTITY ESCALATION DECISION framework.
All other minor triggers must be omitted from the
narrative entirely. Naming them creates mitigation
obligations disproportionate to their significance
and clutters the paragraph with detail that distracts
from the dominant finding.
Example (correct): "The wallet scored 8/10, with 72%
of destination exposure attributed to a Ponzi Scheme
entity (FinanceRevolution)."
Example (incorrect): "The wallet scored 8/10, with
exposure to Ponzi Scheme (72%), Obfuscating (1.2%),
FATF Increased Monitoring (0.8%), and Sanction List
(0.3%)."
**GAMBLING EXPOSURE CHECK:**
If "Gambling" appears in the exposure on a wallet
scoring 5 or above:
1. Identify the user's jurisdiction (country of
   residence).
2. Consult gambling-legality-matrix.md for that
   country.
3. If prohibited/banned: State "Gambling is prohibited
   in [Country]. High regulatory risk."
4. If conditionally legal: Note the licensing
   requirement.
If "Gambling" appears only on wallets scoring below
5, do not perform the gambling check — the low score
indicates negligible exposure and raising it creates
an unnecessary mitigation obligation.
**GAMBLING PATTERN INDICATOR:** Rapid deposit-withdraw
cycles in the same asset with no trading or conversion
in between (particularly XRP/Ripple) is a known
indicator of gambling activity. When this pattern is
observed, prioritise Elliptic screening of the
associated deposit and withdrawal addresses for gambling
entity attribution. This pattern alone is not
conclusive — always verify through blockchain screening
tools — but it has a high correlation with gambling
platform usage and should prompt the gambling legality
matrix check for the user's jurisdiction.
**SANCTIONS ENTITY ESCALATION DECISION:**
When Elliptic screening identifies exposure to a
sanctioned entity (e.g., Garantex, Nobitex, Lazarus
Group, ISIS-affiliated wallets), apply the following
risk-rating-based escalation logic:
1. Risk score 6 or above AND sanctions exposure is the
   ONLY red flag on the account (no other red flags such
   as rapid movements, high-risk counterparties, device
   sharing, suspicious transaction patterns):
   → Escalate to the Sanctions team for further
   investigation. The Sanctions team provides
   recommendations only — FCI retains case ownership.
2. Risk score 6 or above BUT other independent red flags
   exist sufficient to justify offboarding without
   relying on the sanctions exposure (e.g., rapid fund
   movements, high-risk counterparties, device sharing,
   suspicious transaction patterns):
   → Proceed with offboarding directly. No Sanctions
   team escalation required. Apply the "remove the
   sanctions address" test: if the case would still
   warrant offboarding without the sanctions exposure,
   offboard directly.
3. Risk score below 6, no other red flags:
   → Close the case with normal review. No escalation to
   Sanctions team required. A risk score below 6
   indicates indirect exposure with significant distance
   from the sanctioned entity.
4. Risk score below 6, BUT disproportionate exposure
   volume:
   → Discretionary escalation. If the indirect exposure
   represents a disproportionate share of total account
   activity (e.g., 50% of deposits), the investigator
   may motivate escalation as "reasonable, necessary,
   and proportionate." Document the motivation in the
   ICR conclusion.
**SANCTIONS TEMPORAL ASSESSMENT (CRITICAL):**
Before escalating or offboarding based on sanctions
exposure, verify THREE temporal data points:
(1) When was the entity sanctioned (designation date)?
(2) When did the user's transaction occur?
(3) Has the entity been delisted (delisting date)?
Apply the following logic:
- Transaction occurred BEFORE the entity was sanctioned:
  The transaction is not a sanctions violation. Proceed
  with normal review only. Example: Garantex was
  sanctioned in April 2022 — transactions with Garantex
  before April 2022 do not warrant sanctions escalation.
  Elliptic scores reflect current attribution, not
  historical status at the time of the transaction.
- Transaction occurred DURING the active sanctions
  period (between designation and delisting, or after
  designation if not yet delisted): Treat as sanctions
  exposure. Apply the risk-rating escalation logic
  above. Escalate to Sanctions team regardless of
  current delisting status if the transaction occurred
  while sanctions were active.
- Transaction occurred AFTER the entity was delisted:
  Treat as standard high-risk exposure (e.g., mixer,
  obfuscation) rather than sanctions exposure. The
  entity may remain high-risk (e.g., Tornado Cash as a
  mixer) but is no longer sanctions-triggering for
  post-delisting transactions.
The OFAC SDN list (ofac.treasury.gov) provides current
designation status and dates. Elliptic typically shows
the sanctions designation date in brackets next to the
entity name.
**Formatting Rules:**
- "Elliptic" always capitalized.
- FULL wallet addresses for high-risk entities — never
  truncate.
- Batch screening results must be uploaded as dated screenshots or PDF exports from Elliptic. CSV files are not accepted as supporting evidence per QC parameters. For high-risk wallets (score ≥ 5), additionally export the individual wallet detail as a PDF file for more detailed supporting documentation. Save files as Elliptic_Screening_[WalletAddress].pdf (for PDFs) or Elliptic_BatchScreening_[UID]_[Date].pdf (for batch screenshots).
**CTM RISK MITIGATION BEFORE RFI:**
RFI is a last resort for CTM exposure risk. Before
considering an RFI for high-risk wallet exposure,
verify all of the following: (1) was the transaction
successful or rejected, (2) was the exposure direct
or indirect, (3) what is the total exposed amount
relative to overall account activity, (4) how many
transactions and over what time period, (5) has the
wallet been rescreened with a changed risk score
(see RESCREENING RULE above), (6) has a warning
already been issued and acknowledged. If these
factors sufficiently mitigate the risk, no RFI is
needed. This aligns with the universal RFI mitigation
test (decision-matrix.md Rule #14).
**CTM INITIAL PHASE — RE-SCREENING NOT OBLIGATORY:**
Per the current version of the CTM phased approach SOP, for CTM alerts at the Initial Review phase, re-screening of CTM alerts and lifetime top 10 exposed wallets is not obligatory — analysis based on existing data (Hexa-populated content, prior screening results referenced in the case) should be sufficient. For RFIs at the Initial phase, focus on RFIs relevant to the case and those where the user provided replies; for other RFIs, the Hexa summary is considered sufficient. Note: This applies only to the Initial Review phase — Full Review still requires fresh re-screening of all wallets.
**QC Check (Ref: qc-submission-checklist.md #7.3):**
- Wallet re-screenings must be fresh (date of
  investigation).
- Elliptic customer profile printout is NOT equivalent
  to batch screening.
- High-risk wallet re-screenings saved separately
  and attached.
---
## STEP 10: LIFETIME TOP ADDRESSES BY VALUE
**ICR Section:** Lifetime Top Addresses by Value
**What you see:** Empty manual entry box (0/10000).
**Action:**
1. Per the COMBINED SCREENING WORKFLOW (Step 9 above),
   the de-duplicated batch has already been screened.
   Use the screening results to write the Step 10
   narrative.
**STEP 10 NARRATIVE CONTENT:**
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
Step 10 is where all substantive Elliptic analysis
is presented. This section must contain:
1. THE ELLIPTIC OPENING TEMPLATE:
IF highest risk score < 5:
"On a scale from 0 to 10, Elliptic screening returned
an average wallet risk score of [X]. No abnormal
triggers to high-risk addresses or prohibited sites
during Elliptic screening."
IF highest risk score >= 5:
"On a scale from 0 to 10, Elliptic screening returned
a wallet risk score between [X] and highest risk score
of [Y]. The higher risk of [Y] was due to [Count]
wallet(s), [Full Address] related directly with
[Entity Name]."
2. RISK SCORE THRESHOLD RULE: Only wallets scoring
   5 or above out of 10 require individual analysis.
   Wallets below 5 are dismissed in one sentence:
   "No additional significant risks were identified
   among the remaining addresses." Do not name
   triggered rules (Gambling, Sanctions, Fraudulent,
   Obfuscating, etc.) for wallets scoring below 5 —
   the low score means Elliptic assessed the exposure
   as negligible and naming the rule creates an
   unnecessary mitigation obligation.
3. HIGH-RISK WALLET DOCUMENTATION (5 or above):
   For every wallet scoring 5 or above, document ALL
   of the following in the narrative:
   - Full wallet address (never truncate)
   - Entity name from Elliptic (e.g., "HUIONE Pay",
     "Hydra Market", "Tornado Cash"). Do not describe
     wallets generically as "illicit" or "fraudulent"
     without naming the attributed entity. If the
     wallet is unattributed in Elliptic, state
     "unattributed entity" explicitly.
   - Direction: whether funds moved TO the entity or
     FROM the entity (or both)
   - Number of hops between the user's wallet and the
     high-risk entity
   - Brief comment on the nature of the exposure
   Write one paragraph covering all high-risk findings.
   Do not write a separate paragraph per wallet.
4. If any exposed addresses from Step 9 scored 5 or
   above, their detailed analysis appears HERE — not
   in Step 9. Reference them naturally within the
   same paragraph as other high-risk wallets.
5. CROSS-REFERENCE RULE: When a high-risk address
   appears in both the exposed addresses and top
   addresses by value, include the full wallet
   address/hash identifier to create a clear
   cross-reference. The reader should be able to
   connect the two sections without searching.
6. RISK POSITION STATEMENT: Conclude with an explicit
   risk position (mandatory).
RISK MITIGATION CROSS-REFERENCE: If any high-risk wallet finding in this section cannot be fully mitigated here (e.g., mitigation depends on the user's RFI response, counterparty analysis, or LE context), state: "This risk is further assessed in [section reference] below" or "This risk cannot be mitigated with the information currently available and is addressed in the conclusion." Do not leave high-risk findings without either a mitigation statement or a cross-reference to where mitigation is addressed.
7. GAMBLING EXPOSURE CHECK: If "Gambling" appears on
   a wallet scoring 5 or above, perform the
   jurisdiction check per gambling-legality-matrix.md
   as documented in Step 9.
**If Elliptic data was extracted by the ingestion
pipeline:**
The same extraction may cover both Step 9
(exposed addresses) and Step 10 (top addresses
by value) if the investigator screened all
wallets in one batch. Using the extraction data:
1. Apply the standardised Elliptic opening
   template as in Step 9
2. Only comment in detail on wallets that return
   HIGH risk scores (>= 5)
3. If a high-risk wallet is already analysed in
   Step 9, reference it briefly: "the
   aforementioned [entity]" with the full wallet
   address as cross-reference — do NOT duplicate
   the full analysis
4. If all remaining wallets are low risk, state:
   "No additional significant risks were
   identified among the remaining top addresses
   by value."
5. Do NOT reference the total number of wallets
   in the full batch screening — only the top 10
   by value are relevant here
6. Append a risk position statement
Do not paste the extraction table into the ICR.
Write a narrative paragraph using the data.
7. If the extraction includes Section 3 (UOL
   Cross-Reference) — indicating the web app
   provided UOL data alongside the Elliptic
   screening — use the UOL Status field for each
   wallet to apply Decision Matrix Rule #59
   directly:
   - Wallets confirmed as DIRECT in UOL: state
     the direction, volume, and date in the
     narrative. Rule #59 mitigation does not apply.
   - Wallets confirmed as INDIRECT (not found in
     UOL): state this in the narrative and apply
     Rule #59 mitigation language: "The entity
     [name] does not appear as a direct transaction
     counterparty in the User Operation Log,
     indicating the exposure is indirect (via
     intermediary wallets)."
   - When Section 3 is present, the investigator
     does NOT need to perform a separate manual UOL
     lookup for the screened wallets — the web app
     has already completed this cross-reference.
   Additionally, note any pattern observations from
   Section 3 (cross-chain patterns, shared TxIDs,
   test transaction patterns) in the Phase 0
   narrative theory or Step 7 transaction analysis
   as appropriate — these inform the fund flow
   assessment but do not belong in the Elliptic
   narrative section.
**EFFICIENT SCREENING PROCEDURE:**
Since Step 10 now carries the full Elliptic analysis,
the "already analysed in Step 9" cross-reference
scenario no longer applies. All high-risk wallet
analysis appears in this section. If no wallets score
5 or above, the entire section is the Elliptic
opening template plus one sentence confirming no
significant risks were identified.
For all high-scoring wallets, apply the ELLIPTIC vs
UOL CROSS-REFERENCE procedure documented in Step 9
when UOL data is available, before assigning risk
weight.
DEFAULT OUTPUT: 60-100 words for low-risk cases.
Up to 150 words when high-risk wallets require
individual documentation.
**Cross-Reference Rule:** When a blacklisted or
high-risk address appears in both Step 9 and Step 10,
include the full wallet address/hash identifier in
both sections to create a clear cross-reference. The
reader should be able to connect the two sections
without searching.
**Mandatory Content (Always Editable — CRITICAL):**
This field requires Elliptic screening. Must contain
analysis or "0/10000" if genuinely no data.
**Recommendation:** Download the Excel from C360 —
values can change over time.
---
## STEP 11: PRIVACY COIN REVIEW
**ICR Section:** Privacy coin review
**What you see:** Either Hexa data or "No data" with
greyed-out section.
**Action:**
- IF data exists and edit button is visible:
  Write the privacy coin analysis using the data
  provided.
- IF "No data" shown and section is greyed out:
  Skip entirely. Do not populate.
**Required output:**
50-70 words reporting total transaction count, USD
value, date range, and relevant privacy coin features
(XMR, ZEC, DASH) with AML/CFT risk statement.
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
---
## STEP 12: INTERNAL COUNTERPARTY ANALYSIS
**ICR Section:** Internal counterparty analysis
**What you see:** Hexa-populated text with counterparty
summary (count, total value, countries, LE requests,
offboarded status, device sharing) followed by bullet
points for top counterparties by value and highest-risk
counterparties.
**Action:**
1. Audit the Hexa content against C360 Spreadsheets.
   The Hexa counterparty header (total count and total
   USD value) is the sum of TWO specific spreadsheets:
   a. Lifetime SAR Internal Transfer Direct Link
      (counterparty count +
      total_internal_crypto_trans_amt_usd column)
   b. Lifetime SAR Top 10 Binance Pay Direct Link
      (counterparty count +
      total_bpay_trans_amt_usd column)
   P2P counterparties (Lifetime SAR Top 10 P2P Direct
   Link) are EXCLUDED from both the Hexa header count
   and the dollar total. P2P counterparties must be
   addressed in a separate paragraph within the
   Supplemental Analysis, with their own count and
   total transaction values. Do not mix P2P figures
   into the Hexa header totals — QC will cross-check
   these numbers against C360.
   HEXA PROTOCOL AT STEP 12: The default action is
   ALWAYS: correct errors in-place (wrong figures,
   wrong counts, corporate language substitution) →
   retain everything else exactly as Hexa generated
   it → append Supplemental Analysis block below.
   Never rewrite the Hexa structure at this step.
   **Output format:** Wrap the entire box replacement (corrected Hexa + corrected bullet points + supplemental paragraph) in ONE ` ```icr ` block — no internal labels like "Supplemental Analysis:" inside the block (see ICR Output Formatting in icr-general-rules.md). Separate each UID entry with TWO blank lines so HaoDesk's bullet formatter treats them as individual items.
   CORPORATE LANGUAGE SUBSTITUTION: For corporate
   accounts, find-and-replace throughout the Hexa
   counterparty text: "the user" → "the company" and
   "the user under review" → "the entity under
   review." This is an in-place correction, not a
   rewrite.
   SELF-REFERENCE CHECK: Verify that the subject UID
   does not appear in its own counterparty list. This
   is a known Hexa error — remove the entry if found.
   **BINANCE INTERNAL CLEARING ACCOUNT MITIGATION:**
   When an internal counterparty is identified as a Binance internal account (e.g., clearing account for crypto_box payouts via Binance Pay, P2P clearing accounts, or other system-level operational accounts), the LE tickets and ICR history on that account relate to aggregate platform activity across thousands of users — not to the individual counterparty relationship. State this as mitigation in the Hexa bullet point: "This counterparty is a Binance internal clearing account used for [function]. The associated LE/ICR history reflects aggregate platform operations rather than individual user risk." Do not deep-dive into the clearing account's individual LE tickets — they are not relevant to the subject's risk profile.
   FORMATTING CHECK: Review Hexa counterparty output
   for spacing errors, garbled text, or missing spaces
   (common in counterparty transaction counts such as
   "received seven of 22 from and made one"). Correct
   silently.
**If counterparty data was extracted by the
ingestion pipeline:**
The investigator will paste structured data
containing four tasks: Hexa Corrections, Risk
Flag Table, Clean Counterparty Summary, and P2P
Totals. Using this data:
1. Apply Hexa corrections from Task 1 in-place
   (adjust header counts, remove self-references,
   fix formatting)
2. If the extraction app output includes block reasons
   parsed from the block_case_details field (format:
   "→ BLOCKED: trade, withdraw | Reason: Law
   enforcement (BNB-82259)"), use these directly when
   correcting the Hexa bullet points. Verify the
   reason is present for every blocked counterparty.
   If the app outputs "empty block reason" for any
   blocked counterparty, perform a manual lookup in
   Binance Admin > Block & Unblock User 360 before
   finalising the Hexa corrections.
3. Write ONE supplemental paragraph (80-120 words)
   covering:
   - Proportionality: counterparty transaction
     volume as percentage of total account volume
   - The 2-3 most significant risk flags from the
     Task 2 table (one line each — do not list
     every flagged counterparty)
   - P2P totals from Task 4 in one sentence
   - Risk position statement contextualised
     against the primary case concerns from
     Phase 0
   - Do not repeat information already corrected in the
     Hexa entries above — the supplemental paragraph
     covers only analytical findings not visible in the
     Hexa text itself.
4. Clean counterparties from Task 3 do not need
   individual mention — the sentence from Task 3
   is sufficient context
5. For corporate accounts: state whether
   counterparty patterns are consistent with the
   entity's declared business profile
6. RISK MITIGATION CROSS-REFERENCE: If a counterparty risk finding cannot be fully mitigated within this section (e.g., mitigation depends on the user's RFI response or the LE enquiry review), state: "This counterparty risk is further assessed in [section reference]." Every risk identified must be either mitigated in this section or explicitly cross-referenced to where mitigation appears.
Do not paste the risk flag table into the ICR.
Write a narrative supplemental paragraph using
the data.
2. Perform checks on EVERY mentioned counterparty:
**KYC Status Check (CRITICAL):**
Check the is_kyc column in the spreadsheet.
- If False or Null: State explicitly:
  "Counterparty [UID] has Failed/No KYC status,
  limiting their transactional capabilities."
When correcting Hexa counterparty entries, if a
counterparty has no KYC (is_kyc = False or Null in
the spreadsheet), insert "No KYC on file."
immediately after the UID and residence line, before
the transaction details. This is a critical
compliance fact — a counterparty with no KYC has
limited transactional capabilities and its presence
as a high-volume counterparty is itself a risk
indicator. Hexa does not flag No KYC status — the
investigator or extraction app must check and add it.
**Offboarded/Blocked Counterparty Check (CRITICAL):**
When Hexa states a counterparty is offboarded or
blocked:
- Look up the counterparty in Offboarding Management
  > All Cases to find the offboarding reason.
- Look up block reasons in Block & Unblock User 360.
  If the block reason is not visible in the summary
  view, check the block_case_details field — the
  reason is embedded as the 4th element in a
  delimited string separated by "->" (format:
  case_id->block_type->status->block_reason->
  block_remark->owner_department)
- State BOTH the block type AND the reason
  IMMEDIATELY after the block or offboard status at
  the counterparty entry level: e.g., "Currently
  blocked: trade and withdrawal — Law enforcement
  (BNB-82259)" or "Offboarded: Suspicious Transaction
  Activities"
- Simply stating "Currently blocked: trade and
  withdrawal" without the reason is insufficient. QC
  assumes the investigator did not check if the reason
  is not stated, and this will result in a scoring
  deduction.
- If the extraction app provides block reasons from
  the block_case_details field, verify and include
  them. If the app outputs "empty block reason,"
  perform a manual lookup in Binance Admin.
- The reason must appear at the counterparty entry
  level — not just in a separate narrative paragraph
  elsewhere in the section. QC should be able to see
  the status and reason together without searching
  through the text.
- Include transaction values with each mentioned
  counterparty.
**SHARED LE TICKET / COURT ORDER CHECK (CRITICAL):**
Cross-reference the LE tickets listed for each
counterparty against the subject's own LE tickets
(from Step 6). If any counterparty appears in the
SAME Kodex ticket as the subject, this is a critical
finding — it means both the subject and the
counterparty are targets or persons of interest in
the same criminal investigation. Flag this
prominently in the Hexa bullet point entry: e.g.,
"The counterparty appears in the same Polícia
Judiciária requests (BNB-216759, BNB-216831) as the
subject of this investigation."
Similarly, if any counterparty has a court order from
the same LE agency that referred the current case,
this connection must be stated explicitly.
If a counterparty with a shared LE ticket or court
order is not already listed in the Hexa bullet points
(e.g., because it is a low-value counterparty), ADD
it as an additional bullet point. The LE connection
outweighs the low transaction value.
**CO-SUSPECT COUNTERPARTY CHECK (Fraud/Scam Cases — CRITICAL):**
For fraud/scam cases referred by SSO/L1, cross-
reference all internal counterparties against every
UID named in the L1 referral as a suspect,
accomplice, or co-conspirator. If any internal
counterparty is a named suspect in the same referral:
1. State the co-suspect role at the counterparty
   entry level: "UID [X] is identified as Suspect
   [N] in the L1 referral and is implicated in the
   same fraud scheme."
2. The transaction volume between subject and co-
   suspect is immaterial to the risk assessment —
   the relationship to the fraud scheme is the
   finding. Note the volume for completeness but do
   not use it to characterise the counterparty as
   "minimal" or "insignificant."
3. Device sharing between the subject and a co-
   suspect is an aggravating factor corroborating
   the fraud network — not a routine device overlap
   to be briefly mentioned per the Brevity Principle.
4. If a co-suspect counterparty is not already listed
   in the Hexa bullet points (because of low
   transaction volume), ADD it as an additional bullet
   point. The co-suspect relationship outweighs the
   low transaction value — same principle as the
   Shared LE Ticket check above.
See Decision Matrix Rule #62.
**BLOCKS ARE NOT COUNTERPARTY MITIGATIONS:**
Active blocks on the subject's account (trade and
withdrawal restrictions) are operational controls
that prevent future activity. They do not mitigate
the risk finding of an existing counterparty
relationship. Do not state "active blocks mitigate
further counterparty risk" or equivalent in the
counterparty analysis section. Blocks are documented
in Step 3 as account status facts. The counterparty
section assesses the nature and risk of relationships
— and a high-risk counterparty relationship (co-
suspect, offboarded for fraud, shared LE ticket)
remains high-risk regardless of whether the subject's
account is currently blocked.
**COUNTERPARTY CAUSATION CHECK:**
When writing the counterparty risk position statement,
do not draw causal connections between counterparty
risk flags and the subject's own profile unless
evidence directly supports the link. For example, do
not state "the concentration of counterparties with
cybercrime LE requests is consistent with the
subject's cyber threat actor profile" unless the
counterparties' LE cases are demonstrably connected
to the same operation. Instead, state: "X of Y
counterparties were flagged with LE requests or ICR
history. The LE requests relate to [broad/unrelated
crime types] and do not appear directly connected to
the subject's [specific case]. The counterparty risk
profile is noted but cannot be fully assessed without
further information regarding the nature of the
relationships." 
Similarly, do not use the transaction channel or
location of the primary fraud to dismiss internal
counterparty risk. The fact that fraudulent
transactions occurred off-platform (e.g., via on-
chain transfers on Solana, Ethereum, or other
networks) does not reduce the risk significance of
internal counterparty relationships on Binance. The
off-site nature of the scam explains where the
fraudulent transactions took place — it does not
explain or mitigate why the subject has an internal
counterparty relationship with a co-suspect, shared
device identifiers, or financial links to other
flagged accounts. These are separate analytical
dimensions.
**COUNTERPARTY NETWORK PATTERN CHECK:**
When multiple high-risk counterparties are present,
check for patterns suggesting a coordinated network
rather than unrelated P2P activity: (a) counterparties
appearing in the same LE tickets, (b) geographic
clustering (same country or region), (c) same FTM
alert types or crime categories, (d) similar account
behaviors (registration dates, transaction patterns).
If a pattern is identified, state this in the
supplemental analysis — it significantly elevates the
risk assessment from "unrelated high-risk
counterparties" to "potential organized network."
OSINT screening in the counterparties' native language
may reveal criminal records or media coverage not
visible in English-language searches.
**COUNTERPARTY SUMMARY PARAGRAPH:**
Following the individual counterparty assessments in the Hexa bullet points and the Supplemental Analysis paragraph, QC expects a concise summary that: (1) highlights the key risks identified across all counterparties and corresponding mitigation measures, and (2) provides a brief summary of the overall interaction pattern with other users — describing counterparty profile patterns such as merchant-like activity, concentration of internal transfers, geographic clustering, or B2B consistency with the entity's declared business profile. This summary is part of the Supplemental Analysis paragraph (within the existing 120-word limit) — it is not a separate section.
**P2P COUNTERPARTY ANALYSIS — CONDITIONAL
REQUIREMENT:**
P2P aggregate totals (count and volume) must always
be stated in the Supplemental Analysis per the
existing P2P Totals requirement. However, individual
P2P counterparty-level risk analysis (examining
specific P2P UIDs for LE requests, ICRs, blocks) is
mandatory ONLY when: (a) the case was escalated due
to P2P-related risk, (b) the L1 referral specifically
flags P2P counterparties, or (c) P2P activity is a
significant component of the suspicious pattern. For
standard CTM/FTM cases where P2P activity is
incidental, individual P2P counterparty analysis is
not required and omitting it will not result in a QC
finding. However, if P2P counterparties are
voluntarily included in the analysis and that analysis
is incorrect or incomplete, a QC finding will result.
**Dusting/Spam Handling:**
Do NOT remove low-value counterparties (<$1) from
the analysis. They may be relevant for device linking
or network mapping. Note them as "dusting/spam
transactions" and state the value — do not ignore them.
**QC Check (Ref: qc-submission-checklist.md #3.8):**
- Block/offboard reason stated at the counterparty
  entry level, not just in narrative.
- P2P counterparties addressed in separate paragraph
  with own count and totals, not mixed into Hexa
  header figures.
- If counterparty offboarded: explain why (reason +
  transaction values).
- If 30-35+ counterparties: sort Compliance 360 in
  descending order by transaction volume. Select the
  top 3-5 by volume PLUS any counterparties that are
  offboarded, blocked, or subject to LE requests
  (regardless of volume). Provide brief analysis with
  mitigation factors for each sampled counterparty.
  Add statement: "The investigator has analyzed a
  sample of counterparties."
**SUPPLEMENTAL ANALYSIS LENGTH RULE:**
The Supplemental Analysis paragraph must not exceed
120 words. Focus on the 2-3 most significant flagged
counterparties only. Proportionality, top risk flags,
P2P totals, and risk position — nothing more.
**LOW-VOLUME OFFBOARDED COUNTERPARTY — PROPORTIONAL REVIEW:**
In scenarios with multiple counterparties, it is acceptable not to individually mention a counterparty that was offboarded if the transacted amount was bare minimum (e.g., <$5), provided there is thorough review of the high-risk and top counterparties by volume. The obligation is proportional — prioritize analysis of the most significant counterparties first. However, if the investigator reviews only low-risk counterparties while omitting offboarded or heavily flagged counterparties with significant volume, this is a QC finding. Always review the highest-risk counterparties first regardless of their offboarding status.
---
## STEP 13: FIAT TRANSACTIONS
**ICR Section:** FIAT transactions
**What you see:** Hexa-populated text with fiat deposit
and withdrawal totals, channels used, and rejected
transaction summary.
**Action:**
**C360 DOWNLOAD — MANDATORY PRE-STEP:**
Before downloading the Lifetime Failed Fiat Deposit
Transaction Details spreadsheet from C360, the
investigator MUST click the **"All"** button in the
`card_txn_ind` filter at the top of the table
(options: All / card / non-card). The default view
may not include all transaction types, resulting in
missing rows. After downloading, verify the row count
in the spreadsheet matches the rejected transaction
count stated in the Hexa output. If there is a
mismatch, re-download with the "All" filter selected.
Failure to do this can result in missing
fraud-flagged transactions — this was identified as a
critical data integrity issue during case
ICRV20260213-01298 where a fraud-flagged unlimit
transaction was excluded from the initial download.
**SCOPE CEILING:** The fiat section requires three
components only:
(1) The Hexa fiat overview narrative (audit and
    retain as-is unless errors found)
(2) One paragraph of failed fiat analysis if failed
    fiat data exists (3 sentences maximum)
(3) The Bifinity escalation flag check
The failed fiat analysis output constitutes the complete
failed fiat analysis. Do not add card-level
breakdowns, discrepancy investigations, temporal
analysis, channel-by-channel breakdowns, or
additional commentary beyond the prompt output.
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
If the Hexa rejected count does not match the
spreadsheet row count, note the discrepancy in
one sentence — do not investigate the cause.
**FIAT SUCCESSFUL/FAILED RATIO:**
The fiat section must include the ratio of successful to failed fiat transactions. This can be a single sentence (e.g., "Of 47 total fiat transactions, 42 were successful and 5 were rejected, representing an 89% success rate"). Additionally, provide a brief indication of the top rejection reasons and whether the most common rejection reason raises compliance concerns. If the top rejection reason is "suspected fraud," this must be stated prominently. This ratio may be incorporated into the failed fiat analysis output or stated as a supplementary sentence after the failed fiat analysis paragraph.
1. Audit the Hexa content.
2. If Failed Fiat data exists: Write the failed fiat
   analysis using the data provided.
3. Identify the specific fiat channel used for
   suspicious activity (from UAL or C360 Fiat Details).
**Error Reason Check:**
Scan the error_reason column in Failed Fiat data.
- If text contains "Fraud", "Scam", or "Security":
  MUST quote the exact error message in the analysis.
**Bifinity Escalation Check:**
Note the escalation flag based on the channel
list check below. The full nexus assessment and
escalation decision is confirmed at Step 21
(Conclusion). Do not perform extended analysis
of fiat channel usage at this step.
Step A: Identify the fiat channel used for the
suspicious/fraudulent activity.
Step B: Check if that channel is on the Bifinity UAB
Channel List:
Paysafe, Eternal, Mobilum, checkout, HzBankCard,
WorldPay, SafeCharge, Modulr, TrueLayer, SafetyPay,
Zenpay, applepay, googlepay, GIROPAY, zenpaycorp, emp,
paynetics, nuveiocbs, nuveisepa, paysafewithdraw,
bebawaocbs, bebawacorp, unlimit, easyeuro, paytend,
gpsafechargecom, apsafechargecom, revolut,
bankingcircle, apworldpaycom, gpworldpaycom,
easyeurocorp, blik, apempcom, gpempcom, paypal, blikocb.
Step C: Apply the logic:
- Channel IS on the list AND linked to fraud
  → Escalate to Bifinity MLRO
- Channel is NOT on the list (even if user has
  Bifinity tag) → DO NOT escalate to Bifinity MLRO
**OVERRIDE — Bifinity Sunset Clause:**
Do NOT escalate alerts generated AFTER 09 February 2026
to Bifinity MLRO. Technical capability ends 09 March
2026.
**Additional Bifinity Non-Escalation Scenarios:**
- User has >3 months gap from crypto activity
- Exposure is to online gambling addresses only
  (if no other risk)
- Exposure is to OFAC sanctioned addresses only
  (if no other risk)
---
## STEP 14: DEVICE AND IP ANALYSIS
**ICR Section:** Device and IP analysis
**What you see:** Hexa-populated text with device count,
IP locations, language settings, VPN usage, and device
sharing summary.
**Action:**
1. Audit the Hexa content.
2. Write the device and IP analysis using:
**Data Required for This Step:**
1. User's nationality and country of residence
   (from C360 or KYC section)
2. Compliance 360 Lifetime SAR Alerted User Device
   Analysis table (spreadsheet download)
3. Screenshot of the C360 Device Analysis summary
   page showing: total distinct devices used, total
   distinct IP locations, and total distinct system
   languages. These headline figures anchor the
   device paragraph and must not be approximated
   from raw data.
**If device data was extracted by the ingestion
pipeline:**
The investigator will paste structured data
containing six sections: Headline Figures,
Location Frequency, Language Summary, VPN Usage,
Shared Device Analysis, and Sanctioned/Restricted
Jurisdiction Check. Using this data:
1. Verify the Headline Figures against the Hexa
   device statement — correct Hexa if they differ
2. Write one paragraph (60-100 words) covering:
   - Total devices, IP locations, and languages
     (from Headline Figures)
   - Primary access locations and whether
     consistent with the user's nationality and
     country of residence
   - VPN usage percentage
   - Sanctioned or restricted jurisdiction access
     — if present, state the country, login count,
     and proportion of total activity. If absent,
     confirm no access from sanctioned or
     restricted jurisdictions
   - Multi-person access assessment based on
     location and language diversity
   - Shared device findings — if shared UIDs
     exist, list ALL of them. If no sharing
     detected, state this.
3. Cross-reference shared UIDs (if any) against
   Associated Users / Device Link data and against
   Victims, Suspects, and Counterparties from
   Phase 0
4. Append a risk position statement
Do not paste the extraction tables into the ICR.
Write a narrative paragraph using the data.
**Required output:**
Assessment of whether access locations and device
languages are normal for user's nationality/residence,
VPN usage percentage, sanctioned/restricted jurisdiction
access, and likelihood of multi-person account access.
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
**LOW-RISK DEVICE PROFILES:**
When all access locations are consistent with the
user's nationality and residence, a brief
confirmation statement is sufficient (e.g., "All
access locations are consistent with the user's UK
residence. No sanctioned or restricted jurisdiction
access identified."). Detailed city-by-city analysis
is not required for straightforward, low-risk device
profiles. Omitting low-risk device information
entirely is not penalized by QC, but a brief
confirmation is recommended.
**OUTPUT LENGTH AND QC-MINIMUM RULE:**
QC checks only #3.8 (device sharing analysed) and
#3.9 (IP locations analysed). Do not list every city
individually. State the dominant access country,
whether it is normal for the user's nationality and
residence, restricted or sanctioned jurisdiction
access (if any), VPN usage percentage, shared device
findings, and multi-person access assessment. Target:
80-100 words maximum. Listing individual cities with
login counts is unnecessary and inflates the section
beyond QC requirements.
**DEVICE SHARING — 12-MONTH TEMPORAL DISTINCTION:**
When reporting device sharing findings, always specify the timeframe:
- "Within the last 12 months: [UIDs] shared device identifiers with the subject."
- "Lifetime only (no sharing within the last 12 months): [UIDs] shared device identifiers with the subject historically."
If the C360 data or Hexa output provides a 12-month filter, use it. If only lifetime data is available, state: "Device sharing data reflects the lifetime period. A 12-month-specific breakdown was not available." QC checks for this temporal distinction.
**CRITICAL — LIST ALL UIDs:**
When device analysis identifies shared device
identifiers across UIDs, list EVERY SINGLE UID
identified. If the data shows 12 shared UIDs, all 12
must be listed. Copy them directly from the data and
include them in the section. Do not summarise as
"shared with 12 UIDs" without listing them.
**Two Components Required in This Section:**
1. DEVICE PROFILE (from the device analysis): Total device count,
   total IP location count, total language count, VPN
   usage percentage, and whether this is normal for the
   user's nationality/residence.
2. DEVICE SHARING (from Hexa + manual analysis): Which
   UIDs share devices, their risk status
   (offboarded/blocked/LE), and the connection strength.
   The device sharing analysis must explicitly state
   whether shared device identifiers were observed within
   the last 12 months or only in the lifetime period.
   Recent sharing (within 12 months) carries higher risk
   weight than historical-only sharing.
Both components must be present. The device analysis output alone
without device sharing analysis = QC finding. Device
sharing analysis alone without the location/language
profile = QC finding.
**Placement in the form:** Append the device analysis output
after the Hexa-generated device sharing paragraph
(after the "12 months" device sharing text).
**QC Check — Shared Devices (CRITICAL):**
If output says "Shared with X users":
- MUST list the UIDs of those users.
- Cross-reference with Associated Users / Device Link
  spreadsheet.
- State explicitly if Subject is linked via device to
  any Bad Actors, Victims, or Counterparties from
  Phase 0.
- If CSI tool used, save screenshot and attach.
**CORPORATE DEVICE ANALYSIS:**
SUB-ACCOUNT CHECK (CRITICAL): When multiple UIDs
share device identifiers with a corporate account,
check whether those UIDs are sub-accounts of the main
account. Navigate to Binance Admin > user profile >
click to view sub-account list. Compare shared-device
UIDs against this list. If they are sub-accounts,
state this explicitly: "UIDs [list] are confirmed as
sub-accounts of the main corporate account, and
shared device identifiers are expected." This
significantly reduces the risk assessment.
EXPECTED CORPORATE BEHAVIOR: For corporate accounts,
a high number of associated devices and shared device
identifiers/IPs among sub-accounts is expected
behavior, not a red flag. Mitigate by referencing the
company's employee base and sub-account structure:
"The entity operates with [X] sub-accounts and
multiple employees accessing the platform, which is
consistent with the corporate account structure."
LOW-SIGNIFICANCE OVERLAPS: Do not over-elaborate on
low-significance device overlaps. For sub-accounts
sharing IPs with their parent, UIDs with negligible
transaction amounts, or UIDs with no KYC and no
activity, a brief mention is sufficient. Deep-dives
should be reserved for shared-device UIDs that have
been blocked, offboarded, or are subject to LE
requests.
**2FA RESET AND ONE-CLICK DISABLE BLOCKS:**
Blocks classified as 2FA reset or one-click disable in the block/unblock history can be ignored for device analysis purposes. These are routine security operations initiated by the user and do not indicate suspicious access patterns. No investigator analysis is required for these block types — leave the Hexa-populated content as-is.
**Sanctioned Jurisdictions:**
North Korea, Cuba, Iran, Crimea, Donetsk People's
Republic, Luhansk People's Republic.
**Restricted Jurisdictions:**
Canada, Netherlands, United States, Belarus, Russia.
**SANCTIONED COUNTRY IP — RESIDENCE CONFIRMATION
WORKFLOW:**
When device/IP analysis identifies access from a
sanctioned jurisdiction (Cuba, Iran, North Korea,
Crimea, DNR, LNR) but the user's KYC shows a
non-sanctioned country of residence:
1. Send RFI requesting Proof of Address to confirm
   current residence
2. If user confirms non-sanctioned residence with valid
   POA: mitigate — note the sanctioned country IP access
   may be due to travel or temporary presence
3. If user is unresponsive to RFI (after standard
   reminders): escalate to Sanctions team for further
   investigation — do NOT offboard directly based solely
   on the IP without confirmed residence, as the user
   may have been traveling
4. If other independent red flags exist alongside the
   sanctioned IP access: apply the standard "remove the
   address" test from the Sanctions escalation decision
   framework (Step 9)
Note: If the user is from a regulated jurisdiction,
MLRO escalation may also be required in parallel.
**US Exposure:** Must be mentioned and mitigated if
present — failure to do so is a QC finding. Assess US
IP connections by frequency and proportion:
- Rare or single occurrence for a corporate account
  with multiple employees: mitigable by referencing
  the corporate structure and employee base.
- Significant proportion (40-50%+ of total access):
  this becomes an offboarding-level issue regardless
  of other factors. The MLRO will likely direct
  offboarding as the entity is not permitted to
  operate from the US.
- Always quantify: state the number and percentage of
  US-based connections relative to total access.
**Mandatory Content (Always Editable Field):**
Must contain locations, consistency assessment, and
shared device analysis. Never empty.
---
## STEP 15: OSINT
**ICR Section:** OSINT
**What you see:** Empty manual entry box (0/10000).
**Action:**
1. Perform open source research on the subject.
2. If user has a native name (non-Latin script),
   screen the native name as well.
3. Screen the name as it appears on the ID document
   in the same sequence.
4. Include middle name / patronymic if visible on ID.
5. Do NOT screen generic email addresses
   (e.g., user@mailbox).
6. For Spanish users: perform screenings in Spanish.
7. If OSINT results are returned in a non-English
   language, a translated version must also be saved
   and uploaded alongside the original-language PDF.
   QC and MLROs require English-language results for
   review.
7a. For Australian users: perform OSINT screenings using the following search string in addition to the standard name search:
   "NAME" AND (scandal OR lawsuit OR fraud OR charges OR "money laundering" OR "financial crime" OR ASIC OR AUSTRAC OR "crypto scam" OR investigation OR "criminal" OR "court" OR "penalty" OR "enforcement" OR "regulatory action" OR "banned" OR "disqualified" OR "ponzi" OR "terrorist financing")
   This is a jurisdiction-specific requirement similar to the existing Spanish-language requirement for Spanish users.
8. For corporate accounts: OSINT must be performed on
   ALL of the following:
   a. The company name
   b. Every individual named in the KYB (UBOs,
      directors, shareholders)
   c. Email addresses associated with the account
   Each search must be documented separately.
9. Check for a company website during OSINT:
   - If a website exists, note it and summarise
     relevant content (AI can assist with
     summarisation).
   - If no website exists, state "no company website
     identified."
   - If nothing negative is found across all searches,
     state "open source research has been performed
     but no specific / negative news has been
     identified."
**Required output:**
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
IF no adverse findings:
"Open source research has been performed but no specific
/ negative news has been identified."
IF adverse media is found: A narrative paragraph (60-100
words) stating:
1. What was found (article headline/topic, publication,
   date)
2. Identity confirmation — how the investigator
   confirmed the subject in the article is the account
   holder (matching name + at least one of: photo, DOB,
   ID number, address, or unique identifier)
3. Relevance to the investigation (e.g., fraud charges,
   sanctions, criminal proceedings)
4. A risk position statement on the finding
For corporate accounts: one paragraph per entity
screened (company + each UBO/director), clearly labeled.
**QC Check (Ref: qc-submission-checklist.md #7.2):**
- All screenshots saved as PDFs (Cmd+P / Ctrl+P).
- If adverse media found: PDF of article + analysis
  confirming the person is the user (image, DOB, ID).
---
## STEP 16: USER COMMUNICATION
**ICR Section:** User communication
**What you see:** Hexa-populated bullet list of previous
RFI cases with dates, types, and response summaries.
**Action:**
1. Audit the Hexa content.
2. Write a consolidated RFI summary using the data
   provided.
3. Add a comment on general responsiveness:
   e.g., "User is responsive to compliance requests"
   or "User has not provided responses to multiple
   RFI requests."
**Required output:**
50-60 word summary of RFI types sent and responses
received, with date range.
**Output format:** Wrap in ` ```icr ` block (see ICR Output Formatting in icr-general-rules.md).
**RFI LOOKUP — ALTERNATIVE METHOD:**
For a more complete view of the user's RFI history,
use Binance Admin > User profile > RFI section
(request info). This shows all RFIs for the user
including which department issued them, their status,
and associated case references. This provides more
data and context than the ICR queue view alone.
**RFI RESPONSE REVIEW SLA:**
When a user responds to an RFI, the response must be reviewed and analysed within 3 business days of receipt. This is the SLA for the response analysis itself — separate from the broader case review prioritisation timeline. If the response arrives while the case is in the investigator's queue, begin the analysis within 3 business days. If the response arrives after the case has been closed or transferred, coordinate with the assigned team member or TL to ensure timely review.
**RFIs FROM OTHER DEPARTMENTS:**
RFIs can be issued by departments other than FCI
(e.g., local compliance teams, bank relations,
customer service, EDD) without a corresponding FCI
ICR. When an unexpected RFI appears, check Binance
Admin to identify the issuing department. If prior
RFI responses from any department contain relevant
information (e.g., client identification, transaction
explanations, source of funds documentation),
summarise and include them in the current ICR
regardless of which department issued them.
**COMMON QC FINDING — PRIOR RFI/SOW ANALYSIS:**
Simply stating "the user has previously provided
source of wealth documents" or "the user responded
to a prior RFI" is insufficient. The analysis must:
(a) state what specific documents were provided,
(b) summarize their content, (c) assess whether they
are consistent with the observed transaction activity.
Generic statements without content analysis are a QC
finding (ref: qc-submission-checklist.md #4.6).
**RFI RE-TRIGGER LIMIT:**
No more than 3 re-triggers may be sent to a user. The cycle is: initial RFI → re-trigger 1 → re-trigger 2. After three attempts where the user intentionally provides insufficient or evasive responses, classify the user as uncooperative. Apply WOM block under "RFI - Others" with "Uncooperative user" status. Offboarding consideration begins 60 days after WOM placement for uncooperative users. This is distinct from the unresponsive workflow (user does not reply at all after 14 days + 3 reminders → WOM under "RFI - SAR Investigation" + "Unresponsive User" tag).
**SOW VOLUME REASSESSMENT:**
Prior Source of Wealth (SOW) documentation accepted
in an earlier ICR does not automatically mitigate
the current case if transaction volumes have
increased significantly. For example, if a prior
SOW covered $100K in deposits and the current case
involves $1M+ in deposits, the investigator must
explicitly state whether the prior SOW is
sufficient to cover the current volume. If not,
this should be flagged as a gap requiring either a
new SOW request via RFI (subject to current SOW
restriction — see Step 18) or explicit statement
that the prior documentation is insufficient for
the current activity level.
**CHECK MULTIPLE SOURCES FOR PRIOR COMMUNICATIONS:**
Prior user communications and documents may exist
across multiple systems: (1) HaoDesk chat history
including service chats from customer service teams,
(2) RFI tool responses, (3) Binance Admin > User >
Certificate > KYC Detail > EDD Document and Answer
Info sections. The Answer Info section may contain
compliance questionnaire responses from users in
certain jurisdictions (particularly EU countries)
that include source of funds declarations, account
purpose statements, and other onboarding compliance
data. This information is prompted by the system
during KYC/onboarding — not in response to an FCI
RFI — and may pre-date the investigation. Check this
section before concluding that no prior SOW/SOF
documentation exists. Prior SOW declarations may have
been submitted through customer service channels
rather than formal RFI responses. Check all sources
before concluding "no previous RFIs."
**TRAVEL RULE (GTR) DATA CHECK:**
For users in jurisdictions where the Travel Rule is
implemented, Binance Admin contains Global Travel Rule
(GTR) responses under the deposit/withdrawal role
management section. Two tabs are available: "GTR
Withdraw" and "GTR Deposit." Search by UID to view
the user's prior responses to Travel Rule
questionnaires, which include: transaction purpose,
wallet ownership declarations, beneficiary identity,
and whether the transfer is a same-user transfer or
third-party transfer.
This data serves two investigative purposes:
(1) PRE-RFI CHECK: If GTR data already contains the
user's explanation for a flagged transaction (wallet
ownership, purpose), an RFI requesting the same
information may be unnecessary — the answer already
exists on file.
(2) CROSS-REFERENCE: If an RFI has been sent and the
user's response contradicts their prior GTR
declaration (e.g., GTR states the wallet belongs to
their father, RFI response states it belongs to their
mother), this inconsistency is a material red flag
that must be documented.
Note: GTR data is only available for users in
jurisdictions that have implemented the Travel Rule.
Not all jurisdictions are covered. If the GTR tabs
show no data for a user, this does not indicate
non-compliance — it may mean the user's jurisdiction
does not require Travel Rule responses. Access: If
the GTR tabs are not visible in Binance Admin,
request access through your team lead.
**QC Check (Ref: qc-submission-checklist.md #4.6):**
- All previous RFIs mentioned and summarized.
- If no previous RFIs: state "No previous RFIs" —
  do NOT say "no previous communication" unless chats
  also checked.
- No "Manual summary required" placeholders remaining.
- Prior RFI responses from ALL departments (not just
  FCI) reviewed and relevant content incorporated.
- RFI summary follows short plain-text paragraph
  format — no headings, no bullets, no sub-sections.
---