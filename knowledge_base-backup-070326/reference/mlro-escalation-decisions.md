# MLRO Escalation Decisions

> This document contains detailed per-country escalation decision tables, special requirements, SAR/STR SLAs, and delegate contacts. Each country block is self-contained for independent retrieval.

> **Universal escalations** (cases 6, 7, 8, 10 — LE freeze/seizure, CSAM, Ransomware, Terrorist Financing) always apply to ALL jurisdictions and are omitted from individual country tables. See **mlro-escalation-rules.md** for universal rules and fiat channel trigger logic.

---

## Fiat Channel Entities

### Bifinity FIAT Channels

> ⚠️ **ESCALATIONS EFFECTIVELY ENDED** — Escalations to Bifinity UAB ceased as of **31 December 2025**.
> Legacy cases only: alerts before **09 Feb 2026** with successful FIAT transactions on or before 31 Dec 2025.
> **EasyEuro** → now Nest Binance AD. **Zenpay** → now Binance Poland.
> After 09 Feb 2026: **do NOT escalate to Bifinity**.

**Effective Date:** 25 November 2021
**MLRO Contact(s):** paulius.baumila@binance.com | DMLRO: egle.v@binance.com
**Delegates/Backup:** Bifinity SAR Analysts: inga.petrauskaite@binance.com (Team Lead); rasa.jasonaite@binance.com; gabija.m@binance.com; aurelija.r@binance.com; migle.v@binance.com; adriana.j@binance.com; povilas.k@binance.com; monika.l@binance.com; mantas.v@binance.com; kristofas.b@binance.com; orestas.k@binance.com; kornelija.j@binance.com; martynas.s@binance.com; michail.f@binance.com; sigita.m@binance.com; ugne.c@binance.com; erika.j@binance.com; saulius.m@binance.com
**Target Group:** All Bifinity UAB users (KYC and KYB). If there were successful* FIAT transactions* (DP/WD) conducted using Bifinity UAB FIAT channels and FIAT transactions (DP/WD) are linked to the suspicious activity (regardless whether decision is to RETAIN or OFFBOARD)
**Dual Escalation:** YES
**SAR/STR SLA:** The SLA starts from the MLRO’s decision to file an external SAR. SARs must be reported to the Financial Crimes Investigation Service within one business day of the MLRO’s approval.

**Special Requirements:**

- ⚠️ Escalations to Bifinity UAB shall continue on new alerts generated before 09 February 2026, if they include successful FIAT transactions (criteria set below) executed until 31 December 2025.
- ❌ If no successful* FIAT transactions (DP/WD) using Bifinity UAB FIAT channels were conducted (only Bifinity tag is present) until 31 December 2025.
- ❌ If successful* FIAT transactions (DP/WD) conducted until 31 December 2025 using Bifinity UAB FIAT channels are NOT linked to te suspicious activity.
- ❌ If the time gap between the escalated suspicious activity on Crypto and the related FIAT transaction exceeds 3 months:
  - last FIAT DP was more than 3 months before Crypto WD - first FIAT WD occurred more than 3 months after Crypto DP
- ❌ Interactions with Online Gambling addresses (if no other suspicious activity factors or high-risk categories/entities present).
- ❌ Interactions with OFAC sanctioned addresses (if no other suspicious activity factors or high-risk categories/entities present).
- ❌ True Name Screening Match - OFAC sanctioned.
- ⚠️Successful FIAT transactions between 25 November 2021 and until 31 December 2025. No attempts, failed or rejected FIAT transactions using Bifinity UAB FIAT channels shall be taken into consideration when escalating.

**Guideline/Reference:** Internal SAR - Binance UAB can be used for escalations where SAR requires approval from local MLRO and Bifinity MLRO

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ ⚠️ Except: True Name Screening Match - OFAC sanctioned |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ❌ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ❌ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ❌ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ ⚠️ Except: Interactions with OFAC sanctioned addresses (if no other suspicious activity factors or high-risk categories/entities present) |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ❌ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | Fake ID document = ❌ Other fake KYC document (POA, etc.) = ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Bifinity TM Alerts |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ✅ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### BPay Global

**Effective Date:** 01 July 2025
**MLRO:** somaya.n@binance.com
**Delegates/Backup:** yusuf.a@binance.com
**Target Group:** All BPay Global KYC and KYB users
**Dual Escalation:** YES
**SAR/STR SLA:** SARs must be filed with Bahrain’s Financial Intelligence Unit (FIU) using the CBB Click Portal within 30 days of identifying suspicious activity. Bahrain requires SARs to be filed promptly, usually within 30 days. The criteria doesn't mention timelines.

**Special Requirements:**

- ✅ Escalate if:
  - Successful FIAT transactions (DP/WD) via BPay FIAT channels tags: EAZYPAY_BPAY, GP_EAZYPAY_BPAY, SGB_BPAY, PAVEBANK_BPAY_CORP, AP_EAZYPAY_BPAY, SGB_BPAY_CORP, STRAITSX_BPAY_RETAIL, STRAITSX_BPAY_CORP, BPAY_COMBINED, BPAY_COMBINED_CORP, WALLET_BPAY which are directly linked to suspicious activity, posing a substantial offboarding risk independent of platform retention decisions.
  - Attempted or failed BPay FIAT transactions are linked to ML/TF risks (e.g., structuring, threshold evasion).
  - Virtual asset transactions conducted through BPay are linked to suspicious activity.
  - Transactions involve sanctioned or watchlisted entities.
  - Transactions involve shell companies.
  - There is a mismatch between the source of funds and the customer profile.
- ❌ Do NOT escalate if:
  - No successful BPay FIAT transactions (only BPay tag present), unless fake KYC documents are identified or non-transactional red flags (e.g., high-risk behavior patterns) indicate ML/TF risks.
  - BPay FIAT transactions are unrelated to suspicious activity.
- ⚠️ Additional Notes:
  - Crypto-related suspicious transactions should be escalated to the MLRO responsible for the relevant jurisdiction.
  - FIAT BPay channels involved in suspicious activity must be escalated promptly to the BPay MLRO.
  - File SAR/STRs with Bahrain’s FIU within 30 days and retain records for 5 years.
  - Include virtual asset transactions in SARs if applicable.

**Guideline/Reference:** STR guidance for BPay.docx

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | Only when a suspicious behavior or factor is determined, specifically by IHRE engines that were set up for BPay |
| 12 | Live Crypto TM Alert | ❌ |
| 13 | Post Crypto TM Alert | ❌ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ❌ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ❌ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Only when a suspicious behavior or factor is determined, specifically by IHRE engines that were set up for BPay |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | ❌ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

## Country-Specific MLROs

### France

**Effective Date:** May 2022
**MLRO:** kevin.r@binance.com
**Target Group:** All French residents, i.e., users with country of residence matching either mainland France or any French overseas territory: FR / BL / GF / GP / MF / MQ / NC / PF / PM / RE / TF / WF / YT (Regardless of TnC, entity tag...)
**Dual Escalation:** NO
**SAR/STR SLA:** No fixed SLA as per regulation that states the SAR must be filled without delay. However, after (i) past inspection (ii) past backlog issue and (iii) discussions with the board / acpr / tracfin, Binance France agreed on the 30 business days SLA to be achieved, considering the alerted transaction relevant for the case or situation that triggered investigation

**Special Requirements:**

SLA for suspicious activities counting from transaction date: within 60 days. TF and CSAM cases must be reported within 5 days.
- Escalation Requirement for Non-France Legal Entity Cases: ICR cases involving legal entities registered outside France but linked to Binance France clients (e.g., via a French UBO) should not be routed to the France MLRO because: (i) We lack authorized access to non-FR entities, and (ii) Our access is limited to France-specific data and processes.
- Escalation Protocol: IF > The FCI team’s conclusion is OB and/or SAR for the legal entity, AND > There is a link to a French citizen (e.g., UBO) who is also a Binance France client, THEN > Send a Wea message to kevin.r@binance.com with the following: “SAR sent for the legal entity for the following matter: (<add details>). Please note that the individual (<UID NO.>) is a French resident and client of Binance France." We will then investigate and open an ICR on our client accordingly. Effective Date: 06 Nov 2025

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | Escalate when the user is officially onboarded and transaction(s) have been done. |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | ✅ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ✅ |
| 22b | Market Abuse | — |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Italy

**Effective Date:** 10 March 2023
**MLRO:** rossella.gancitano@binance.com
**Delegates/Backup:** gianfranco.coppola@binance.com, ciro.aurelio@binance.com
**Target Group:** Italian residents with Italian T&C
**Dual Escalation:** NO
**SAR/STR SLA:** SARs must be filed promptly upon detection. Filing beyond 30 business days is considered late.

**Guideline/Reference:** Binance Italy - SAR Escalation .docx

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | ❌ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | — |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Spain

**Effective Date:** July 2022
**MLRO:** pau.vidal@binance.com
**Delegates/Backup:** carlos.jimenez@binance.com
**Target Group:** All Spanish residents and/or user with 'Binance_ES' Entity Tag
**Dual Escalation:** NO
**SAR/STR SLA:** SARs must be filed without delay after the special exam is completed.

**Guideline/Reference:** Spanish MLRO's escalation guidelines.docx

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | Escalate only when determined a suspicious ML behaviour or factor observed |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | Only escalate when the incurred amount ≥ $100K |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | Isolated case NO NEED to escalate *Batch accounts identified related to one user |
| 21 | Specific TM Alerts | ❌ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | Escalate only when determined a suspicious ML or TF behaviour or factor observed |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Poland

**Effective Date:** 01 September 2022
**MLRO:** beata.wisnicka@binance.com
**Delegates/Backup:** dominika.bargiel@binance.com filip.leszczynski@binance.eu
**Target Group:** All Polish/Belgian residents that signed off the PL_TNC or PL_BE_TNC
**Dual Escalation:** NO
**SAR/STR SLA:** Once a suspicion is formed, a report must be submitted within 2 days to the Financial Intelligence Unit (this decision is made by MLRO L3)

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | ❌ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | Escalate only when determined a suspicious ML or TF behaviour or factor observed |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Sweden

**Effective Date:** June 2023
**MLRO:** shawn.parnosi@binance.com
**Delegates/Backup:** arash.masarrat@binance.com
**Target Group:** All Sweden-based residents onboarded under Binance Nordics AB that meet both of the following criteria can be treated as Swedish customers: ✅ COR = SE ✅ TnC = SE
**Dual Escalation:** NO
**SAR/STR SLA:** SARs must be submitted without delay as soon as suspicion arises.

**Special Requirements:**

- If the customer is missing the following, no need to escalate:
  - ❌ COR = SE, and
  - ❌ TnC = SE

**Guideline/Reference:** Guideline:SARS escalations guidelines for Binance Nordics.docx Template:[make a copy] SAR template Sweden 2025 Master.docx

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | ❌ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | Temporary yes, to be assessed in case escalation alerts would need some fine-tuning |
| 22b | Market Abuse | Market abuse should be escalated to the individual responsible for maintaining the company's market rules and policies. This could be a General Manager, a Compliance officer, or another individual with equivalent responsibility. |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Australia

**Effective Date:** 22 October 2023
**MLRO Contact(s):** andrew.p@binance.com | DMLRO: veronica.f@binance.com
**Delegates/Backup:** Delegates: jake.song@binance.com / jemar.santacruz@binance.com / ben.www@binance.com
**Target Group:** All Australia residents
**Dual Escalation:** NO
**SAR/STR SLA:** The SLA starts when the MLRO or delegate reviews a reasonable suspicion. The SAR must be filed within 3 days, and the whole process finished within 30 days.

**Special Requirements:**

AUSTRAC Reporting Requirements: Terrorism Financing (TF) - 24 hours of forming a 'reasonable suspicion'(this is applicable 7 days a week) Suspicious Matter Reporting (SMR) - 3 days of forming a 'reasonable suspicion' (this is applicable to business/working days) *Sanctions cases will be assessed on the following basis: if associated with TF: 24 hours; if associated with money laundering SMR to be filed: 3 days When communicating with Australian users please refer to the Indicators of suspicious activity for the digital currency (cryptocurrency) sector. AUSTRAC

**Guideline/Reference:** Internal SAR Escalation Country Guidance - Australia.docx

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 21 | Specific TM Alerts | ❌ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### New Zealand

**Effective Date:** 15 September 2022
**MLRO:** arifa.p@binance.com
**Delegates/Backup:** jemar.santacruz@binance.com
**Target Group:** All New Zealand residents
**Dual Escalation:** NO
**SAR/STR SLA:** A SAR must be submitted to the FIU no later than three working days after reasonable grounds for suspicion are formed (this is decided by MLRO in L3)

**Guideline/Reference:** NZ SARs_STRs.docx

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ❌ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ❌ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ❌ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 21 | Specific TM Alerts | ❌ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Japan

**Effective Date:** 01 August 2023
**MLRO:** yusuke.kato@binance.com, michinori.murata@binance.com
**Target Group:** All Japan residents who have account in Binance Japan (the customers who will be given "JP" entity-tag on Dec 1, 2023) (all dot.com Binance users with COR=JP who have not passed the local e-KYC (Liquid) by Dec shall be Withdrawal-Only mode then.)
**Dual Escalation:** NO
**SAR/STR SLA:** SAR filings must be submitted promptly and no later than 30 days from the date of detection, unless a valid justification is provided. The term "detection" may be interpreted as the creation of a case or alert.

**Guideline/Reference:** Manual for Reporting Suspicious Transactions Regulatory documents: AML Guidelines: https://www.fsa.go.jp/common/law/amlcft/211122_amlcft_guidelines.pdf General AMl Risk Analysis: https://www.npa.go.jp/sosikihanzai/jafic/nenzihokoku/risk/risk071127.pdf Illustration of the Criteria: https://www.fsa.go.jp/str/jirei/#crypto

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Binance Japan is not using Bifinity, but Binance Japan has fiat channels directly with local banks and the fiat channel shall be subject to TM monitoring alerts, based on mappings (https://boffice.toolsfdg.net/Products/Files/DocEditor.aspx?fileid=44630). |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ✅ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### India

**Effective Date:** 19 April 2024
**MLRO:** husain.ahmed@binance.com (interim)
**Delegates/Backup:** patricia.t@binance.com akmal.s@binance.com ankit.k@binance.com abhishek.n@binance.com manju.m@binance.com mansi.s@binance.com
**Target Group:** All India Resident Users only
**Dual Escalation:** YES

**Special Requirements:**

Escalate LE cases effective from 20 June 2024 refer row 17.

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ❌ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ❌ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ❌ |
| 4 | User not willing to provide EDD (SOF/SOW) | ❌ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | Only when determined a suspicious behaviour or factor. |
| 13 | Post Crypto TM Alert | Only when determined a suspicious behaviour or factor. |
| 14A | Fraud/Scam/Hack (Suspect) | Only when determined a suspicious behaviour or factor. |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ❌ |
| 16 | Purchase KYC/KYC Seller/Shared Account | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | Only when determined a suspicious behaviour or factor. |
| 18 | Fake KYC Document (i.e. POA and ID) | ❌ |
| 19 | Edited Card/Bank Statement | ❌ |
| 20 | Batch Accounts Creation | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 21 | Specific TM Alerts | Only when determined a suspicious behaviour or factor. |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | — |
| 22b | Market Abuse | ❌ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Binance Kazakhstan

**Effective Date:** 24 June 2023
**MLRO:** asset.s@binance.com
**Delegates/Backup:** assel.m@binance.com, gaukhar.temirbolat@binance.com
**Target Group:** All Binance Kazakhstan entity users (KZ Entity tag)
**Dual Escalation:** NO
**SAR/STR SLA:** 1. To freeze account and report within 24 hours starting from alert is triggered in case a person appears on the TF/WMD list. 2. To report suspicious transaction/activity within 24 hours from the moment when such transaction/activity is considered suspicious. 3. To report transactions (exposed to gambling) over the defined threshold (1 000 000 KZT (~1 950 USD)) within 24 hours from the moment when such transaction occurs.

**Guideline/Reference:** BN KZ SAR/STR/TTR Procedure_updated_17122025.pdf

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | ✅ IHRE Rules for KZ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ✅ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Thailand (Cloud Exchange)

**Effective Date:** November 2023
**MLRO:** thitiwat.w@binance.com
**Delegates/Backup:** korawan.pattanaworakij@binance.th
**Target Group:** All users of Thailand Cloud Exchange (not include a Thai user of .com exchange)
**Dual Escalation:** NO
**SAR/STR SLA:** The 7-day deadline to submit the SAR to the Anti-Money Laundering Office (AMLO) starts after senior management reviews and approves the report. The local team currently manages this process.

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | N/A. Local team will receive the alert from Thailand Admin Portal. |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ To discuss the data sharing for monitoring |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ To discuss the data sharing for monitoring |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ To discuss the data sharing for monitoring |
| 4 | User not willing to provide EDD (SOF/SOW) | N/A, will be done by local cloud system |
| 5 | EDD on users with high-risk profile such as PEP | N/A, will be done by local cloud system |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | N/A, will be done by local CS |
| 14B | Fraud/Scam/Hack (Victim) | N/A, will be done by local CS |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | N/A, will be done by local cloud system |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | N/A, will be done by local market surveillance |
| 18 | Fake KYC Document (i.e. POA and ID) | N/A, will be done by local cloud system |
| 19 | Edited Card/Bank Statement | N/A, will be done by local cloud system |
| 20 | Batch Accounts Creation | N/A, will be done by local cloud system |
| 21 | Specific TM Alerts | Local report is required for transactions (deposits/withdrawals/trades - both FIAT and Crypto) equals or more than THB 5mm. |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | — |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Mexico

**Effective Date:** 28 August 2023
**MLRO:** ricardo.roman@binance.com
**Delegates/Backup:** andrea.pb@binance.com
**Target Group:** All users with Mexico as country of residence
**Dual Escalation:** YES

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | Only when determined a suspicious behaviour or factor. |
| 13 | Post Crypto TM Alert | Only when determined a suspicious behaviour or factor. |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ❌ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ❌ |
| 21 | Specific TM Alerts | Only when determined a suspicious behaviour or factor. |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Colombia

**Effective Date:** 26 June 2023
**MLRO:** maria.r@binance.com
**Delegates/Backup:** beatriz.q@binance.com
**Target Group:** All users with CO (Colombia) residence Note: When fiat trasantions, tag the case "fiat transactions or fiat channel" for MLRO prioritize the case- criteria to determine an a external SAR
**Dual Escalation:** YES

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | Only when determined a suspicious behaviour or factor. |
| 13 | Post Crypto TM Alert | Bad behaviour factor |
| 14A | Fraud/Scam/Hack (Suspect) | Only when it involves the fiat channel (Inswitch/Movii) |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Application of global standards. In case of alert escalate to local MLRO. |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Venezuela

**Effective Date:** 29 August 2025
**MLRO:** maria.r@binance.com
**Delegates/Backup:** beatriz.q@binance.com, cesar.marin@binance.com, rene.guzman@binance.com
**Target Group:** All users with Venezuela as country of residence
**Dual Escalation:** YES

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ❌ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 4 | User not willing to provide EDD (SOF/SOW) | ❌ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | For cases designated under the Subject Matter Sub-Categories: "Other Unusual Transaction Activity" and "Red Flag Filter Offchain TM," escalation shall be warranted solely when the maximum asset net holding exceeds $40,000, or upon a decision to initiate offboarding. |
| 12 | Live Crypto TM Alert | Only when determined a suspicious behaviour or factor. |
| 13 | Post Crypto TM Alert | Only when determined a suspicious behaviour or factor. |
| 14A | Fraud/Scam/Hack (Suspect) | Escalate only for serious, large-scale organized fraud or criminal activity, or when there is a confirmed case of: Kidnapping, Blackmail or extortion, Ponzi schemes, Fake investment schemes, Token scams, Rug pulls, Fraudulent trading platforms. |
| 14B | Fraud/Scam/Hack (Victim) | Only when determined a suspicious behaviour or factor. |
| 15 | Single Deposit Risk Control | ❌ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ❌ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ❌ |
| 18 | Fake KYC Document (i.e. POA and ID) | ❌ |
| 19 | Edited Card/Bank Statement | ❌ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Only when determined a suspicious behaviour or factor. |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | — |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Argentina

**Effective Date:** September 2023
**MLRO:** agustin.iavicoli@binance.com
**Delegates/Backup:** elio.g@binance.com
**Target Group:** November 2024 update: Entity tag: AR
**Dual Escalation:** NO
**SAR/STR SLA:** The SLA starts when a transaction/situation relevant to the investigation is executed/generated. The suspicious transaction report must be submitted within 90 calendar days from the date the transaction was made or attempted.

**Special Requirements:**

New reg external SAR SLAs (starting july 2024) ML a): 90 days from the moment the transaction was intended/executed ML b): 24 hours from the moment the case is deemed reportable to UIF. TF: 24 hours from the moment the transaction is intended/executed.

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 4 | User not willing to provide EDD (SOF/SOW) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | Only escalate when the incurred amount ≥ $10K. Also, gambling sites that do not have a website ending in ".bet.ar" should be considered unauthorized and unlicensed in Argentina and should be escalated. Licenced entities/sites search link: https://www.alea.org.ar/juegosonlineautorizados |
| 13 | Post Crypto TM Alert | Only escalate when the incurred amount ≥ $10K |
| 14A | Fraud/Scam/Hack (Suspect) | Please escalate cases when there is a proposal to offboard or the case is related to ARG fiat ramps (SG Coinag or other) - July 2024 |
| 14B | Fraud/Scam/Hack (Victim) | Only escalate when an offboarding is requested |
| 15 | Single Deposit Risk Control | Only escalate when the incurred amount ≥ $10K |
| 16 | Purchase KYC/KYC Seller/Shared Account | Only escalate when an offboarding is requested |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | Only escalate when an offboarding is requested |
| 19 | Edited Card/Bank Statement | Only escalate when an offboarding is requested |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Only when determined a suspicious behaviour or factor. |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### El Salvador

**Effective Date:** 02 October 2023
**MLRO:** rene.guzman@binance.com
**Delegates/Backup:** maria.r@binance.com
**Target Group:** All users with El Salvador residence. Entity Tag: SV
**Dual Escalation:** NO
**SAR/STR SLA:** SARs need to be reported within 15 business days once the alert is notified to the MLRO - This means that the SLA starts when an ICR is escalated to the MLRO

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | ❌ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | — |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Brazil

**Effective Date:** 01 October 2023
**MLRO:** victor.mg@binance.com
**Delegates/Backup:** aline.f@binance.com beatriz.q@binance.com
**Target Group:** All users with Brazil as country of residence
**Dual Escalation:** YES
**SAR/STR SLA:** External SARs are included in the regulation but they are not yet fully enforceable as we await the license by the Central Bank of Brazil (Q3). Once regulated by the Central Bank of Brazil (3Q), Resolution 3,978/20 requires suspicious transactions to be selected within 45 days from occurence (FCI SLAs - Art. 39, sole paragraph), and the analysis to be completed within an additional 45 days (Art. 43, 1).

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ❌ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | Escalate when transaction occurred, no escalation required when the user is not onboarded |
| 4 | User not willing to provide EDD (SOF/SOW) | ❌ |
| 5 | EDD on users with high-risk profile such as PEP | ❌ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | Direct/indirect links to known suspicious sources such as darknet marketplaces, mixing services, gambling sites, service providers, wallets known to be involved in illegal activities, and/or theft or ransomware reports |
| 13 | Post Crypto TM Alert | Only when determined a suspicious behaviour or factor. |
| 14A | Fraud/Scam/Hack (Suspect) | Only when determined a suspicious behaviour or factor. |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ❌ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ❌ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ❌ |
| 18 | Fake KYC Document (i.e. POA and ID) | ❌ |
| 19 | Edited Card/Bank Statement | ❌ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Only when determined a suspicious behaviour or factor. |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | — |
| 22b | Market Abuse | ❌ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Turkey (.com)

**Effective Date:** 01 January 2025
**MLRO:** derya.i@binance.com
**Target Group:** All .COM Turkey resident user and all sub account UIDs under BinanceTR master account UID: 42520824
**Dual Escalation:** NO
**SAR/STR SLA:** 10 business days: For BinanceTR sub account UIDs when the alert is triggered and also when a 'reasonable suspicion' is occured/formed

**Special Requirements:**

- For cases of sub account UIDs under BinanceTR master account UID: 42520824 please escalate to BinanceTRCompBot.
- For .com - no specific SLA.
- For specific issues mentioned in the Binance Turkey internal SAR escalation Guide they should be escalated immediately. For BinanceTR - 10 working business days after the alert generated.

**Guideline/Reference:** https://docs.google.com/document/d/1JfPazorhy_hhWtK9qZ4g6muQ8yGXYHu4/edit?usp=drive_link&ouid=118350414630992159725&rtpof=true&sd=true

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | Only if determined the user in question is also a BinanceTR user |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | Only if determined the user in question is also a BinanceTR user |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | Only if determined the user in question is also a BinanceTR user |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | Direct/indirect links to known suspicious sources such as darknet marketplaces, mixing services, gambling sites, service providers, wallets known to be involved in illegal activities, and/or theft or ransomware reports |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | Only if determined the user in question is also a BinanceTR user |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | Only if determined the user in question is also a BinanceTR user |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | Only if determined the user in question is also a BinanceTR user |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Only when determined a suspicious behaviour or factor. |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ❌ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Binance Bahrain

**Effective Date:** 19 January 2025
**MLRO:** zainab.jahromi@binance.com
**Delegates/Backup:** hamad.a@binance.com husain.t@binance.com
**Target Group:** All Binance Bahrain entity users
**Dual Escalation:** NO
**SAR/STR SLA:** File the STR immediately after finding a suspicious transaction. Complete investigation and report within 60 days of the alert.

**Guideline/Reference:** Offboarding cases need to be escalated to MLRO/DMLRO for approval. Users can have one account with Binance.com (Global) and another with Binance Bahrain entity. (No escalation or offboarding is required for such scenarios).

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | Direct/indirect links to known suspicious sources such as darknet marketplaces, mixing services, gambling sites, service providers, wallets known to be involved in illegal activities, and/or theft or ransomware reports. |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | ❌ |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ✅ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### Dubai Exchange

**Effective Date:** 12 February 2024
**MLRO:** stephanie.emile@binance.com
**Delegates/Backup:** mehmet.yy@binance.com
**Target Group:** All AE tagged to be escalated to the DUBAI EXCHANGE MLRO. Please make clear if AE Tagged User at TOP and BOTTOM of SAR.
**Dual Escalation:** NO
**SAR/STR SLA:** Starts from the alert date. - File STR/SAR within 35 business days. For complex cases: - File first STR/SAR within 15 business days, marked “Complex investigation.” - File follow-up STR/SAR within 30 business days after the first. If suspicious activity continues, keep monitoring and file more STR/SARs quickly

**Special Requirements:**

- SLA for suspicious activities counting from transaction date: within 30 days TF and CSAM cases must be reported within 5 days AE .com cases are not to be escalated to the L3 HAODesk Queue except
- for cases in the following categories: - CSAM - Terrorist Financing - Proliferation Financing - TFS Sanctions (Local list and UNSC list only)

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | ✅ |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ |
| 12 | Live Crypto TM Alert | ✅ |
| 13 | Post Crypto TM Alert | ✅ |
| 14A | Fraud/Scam/Hack (Suspect) | ✅ |
| 14B | Fraud/Scam/Hack (Victim) | ✅ |
| 15 | Single Deposit Risk Control | ✅ |
| 16 | Purchase KYC/KYC Seller/Shared Account | ✅ |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ✅ |
| 18 | Fake KYC Document (i.e. POA and ID) | ✅ |
| 19 | Edited Card/Bank Statement | ✅ |
| 20 | Batch Accounts Creation | ✅ |
| 21 | Specific TM Alerts | Obligation to investigate any related alerts that will impact local transactions |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | ✅ |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

### ADGM

**Effective Date:** 05 January 2026
**MLRO:** Nest Exchange Limited & Nest Clearing and Custody Limited: yp.cheung@binance.com Nest Trading Limited: david.harrington@binance.com
**Delegates/Backup:** tatyana.t@binance.com
**Target Group:** All.com users with ADGM tag (except local entity users)
**Dual Escalation:** N/A
**SAR/STR SLA:** The general rule is to submit SARs within 35 business days upon alert generation if deemed suspicious SARs / STRs must be filled via the go AML portal promptly (i.e. within 24hrs). TF cases (as advised by LE or sanctions hit on local lists), Employee-related investigations, Multiple subpoena requests, Legal / court referred or Complex investigations - review within 10 days and report (applicable to L3 MLRO) within 1-5 days Possible name match report (PNMR) and Confirmed Name Match Report (CNMR) must be reported within 5 business days Measures taken post sanctions screening (Account freezing / suspension of products & services) must be reported within 5 business days https://services.uaefiu.gov.ae/goaml/

**Special Requirements:**

- Alert investigation
- SLA for suspicious activities, counting from transaction date: within 30 days TF cases (as advised by LE or sanctions hit on local lists), Employee-related investigations, Multiple subpoena requests, Legal / court referred or Complex investigations - review within 10 days and report (applicable to L3 MLRO) within 1-5 days Account freezing / suspension of products & services as a result of confirmed / partial name matches must be applied within 24 hrs

**Guideline/Reference:** Binance ADGM - MLRO External Reporting Procedure

**Escalation Decisions:**

| # | Case Type | Escalate? |
|---|-----------|-----------|
| 1A | True Name Screening Match - Sanction/Terrorism (KYC on-going monitoring) | ✅ |
| 1B | True Name Screening Match - Sanction/Terrorism (Reject at onboarding or no transactions) | ✅ |
| 2A | True Name Screening Match - Fraud/Scam/Tax Evasion (KYC on-going monitoring) | ✅ |
| 2B | True Name Screening Match - Fraud/Scam/Tax Evasion (Reject at onboarding or no transactions) | ✅ |
| 3A | True Name Screening Match - Money Laundering/Embezzlement (KYC on-going monitoring) | ✅ |
| 3B | True Name Screening Match - Money Laundering/Embezzlement (Reject at onboarding or no transactions) | ✅ |
| 4 | User not willing to provide EDD (SOF/SOW) | ✅ |
| 5 | EDD on users with high-risk profile such as PEP | EDD high risk profile --> refer to HRC PEP —> HRC team to review Final PEP approval to onboard —> ADGM MLRO / Deputy MLRO |
| 9 | Sanctions | ✅ |
| 11 | Money Laundering | ✅ For Fiat TM Alerts - Only if suspicious money laundering, terrorist financing or other criminal activity. |
| 12 | Live Crypto TM Alert | Only when determined a suspicious money laundering and terrorist financing |
| 13 | Post Crypto TM Alert | Only when determined a suspicious money laundering and terrorist financing |
| 14A | Fraud/Scam/Hack (Suspect) | Only when determined a suspicious transaction/fund related to proceeds of crime. For P2P related fraud/scam/hack cases: If there is no financial loss, or the scam attempt is unsuccessful → escalation to ADGM L3 is not required, and these cases can be handled/completed at the L2 level. |
| 14B | Fraud/Scam/Hack (Victim) | ❌ |
| 15 | Single Deposit Risk Control | ❌ |
| 16 | Purchase KYC/KYC Seller/Shared Account | Only when determined a suspicious money laundering and terrorist financing |
| 17 | Abnormal Fluctuation Trading Transaction (API hack) | ❌ |
| 18 | Fake KYC Document (i.e. POA and ID) | Escalate when the user refuses to provide requested information. |
| 19 | Edited Card/Bank Statement | Only when determined a suspicious money laundering, terrorist financing or financial crimes |
| 20 | Batch Accounts Creation | Only when determined a suspicious money laundering and terrorist financing |
| 21 | Specific TM Alerts | Only when determined a suspicious money laundering and terrorist financing |
| 22a | Use of Money Mixers (Further Clarification needed from MLROs requested) | — |
| 22b | Market Abuse | ✅ |

> Universal escalations (cases 6, 7, 8, 10) always apply and are omitted from this table.

---

---

_End of MLRO Escalation Decisions — Generated from MLRO Escalation Requirements Matrix.xlsx on 2026-02-22_