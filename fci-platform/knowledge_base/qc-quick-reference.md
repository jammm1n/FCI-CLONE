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
