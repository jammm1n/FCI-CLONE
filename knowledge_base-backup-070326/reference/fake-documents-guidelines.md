# Fake Document Investigation Case Referrals (ICRs) Guideline

*   **Created by:** charlotte.l@binance.com
*   **Last Modified by:** marcus.c@binance.com
*   **Date:** Sept 26, 2024

### **Background**

Fake KYC documents (e.g., ID, POA, edited selfie pictures) are detected by the first line of defense (L1 KYC Operations On-boarding team and Operations Risk team) during the on-boarding/KYC review process.

*   **Risk Assessment:** Most cases involve newly opened accounts or sanctioned country users using fake docs. These accounts typically have non-significant or no balance and low money laundering concerns.
*   **Objective:** Allocate limited resources to higher-risk users via a risk-based approach.
*   **Policy Change:** Fake document cases meeting specific conditions are **not required** to go through review by the Financial Crime Investigations (FCI) team before offboarding or releasing action.

---

### **Exemption Conditions**

If **ALL** of the following conditions are met, no FCI investigation and no Investigation Case Referral (ICR) is required before offboarding or releasing:

1.  **Detection Type & Balance:**
    *   Fake documents detected (Fake ID, Fake POA, Edited Selfie Picture).
    *   Account balance is **less than $1000**.
2.  **No Other Red Flags:**
    *   User has **no** other red flags detected aside from fake documents.
    *   *Examples of disqualifying red flags:* LE freeze, fraud/scam on-going investigation, Account Takeover (ATO), chargeback, true WCH, TM alerts, Sanctions, Terrorist Financing, CSAM, Money Laundering, etc.
3.  **Jurisdiction Check:**
    *   User is **excluded** from licensed jurisdictions that require escalation to MLROs (Refer to *MLRO Escalation Requirements Matrix*).

---

### **ICR Referral Narrative Requirements**

If a case *does* require referral (i.e., conditions above are NOT met), the ICR narrative must include:

1.  **Background of the Case:**
    *   Describe all red flags.
    *   Detail what, how, and where the red flags were detected.
2.  **Investigation/Review Conducted:**
    *   Include findings from the referral team.
    *   Detail actions taken.
3.  **Supporting Documents:**
    *   Attach obtained documents (including those from users).
4.  **Conclusion/Recommendation:**
    *   Include recommended action or conclusion (if applicable).

> **Note:** Please provide sufficient background of the red flags in the write-up of the ICR escalation.

---

### **Operational Guidelines**

*   **Multiple Users:**
    *   Multiple users in one ICR is **not recommended** unless:
        *   Users have the same nature of red flags.
        *   Users are connected (e.g., one operator created 20 fake ID accounts with the same device).
*   **Sanctioned Countries:**
    *   For sanctioned country users, refer to the *'Global Sanctions Policy V 3.3'* for handling or escalation to the Sanctions Team.
*   **Offboarding Protocol:**
    *   **Reason Code:** Use the offboarding reason `'KYC fraud'` if offboarding is the decision.
    *   **Reporting:** Monthly reports can be extracted on consolidated fake document cases after offboarding (containing UID, country of residence, and offboarding reason) for documentation kept with the FCI team.