# MLRO Escalation Rules

> This document contains the escalation logic, universal rules, and quick-reference data needed on every case. For case-type-specific escalation decisions per country, consult **mlro-escalation-decisions.md**.

---

## How Escalation Works

- **ADGM is ALWAYS the default/primary MLRO** for all .com users not covered by a specific local jurisdiction listed below.
- If a user's country of residence is listed below, check whether the case type requires **local MLRO escalation in addition to (or instead of) ADGM**.
- Countries marked **"Dual Escalation: YES"** require both ADGM (primary) and local MLRO (secondary) in HAODesk.
- Countries marked **"Dual Escalation: NO"** require ONLY the local MLRO — ADGM is not needed as secondary.
- If a user's country is **NOT listed below**, escalate to **ADGM only** (if escalation is required for that case type).
- If the case involves **fiat channels**, check BPay Global and Bifinity (legacy) sections separately — fiat channel escalation is **in addition to** country MLRO escalation.

---

## Universal Escalations (ALL Jurisdictions — No Exceptions)

The following case types **ALWAYS** require escalation to the relevant MLRO, regardless of country:

- **6:** Completed Law Enforcement request with official LE freeze order/seizure warrant
- **7:** CSAM
- **8:** Ransomware
- **10:** Terrorist Financing

> These are omitted from individual country tables in mlro-escalation-decisions.md.

---

## Quick Reference — All Countries with Dedicated MLROs

| Country / Entity | MLRO | Dual Escalation |
| :--- | :--- | :--- |
| **Bifinity FIAT Channels** (Fiat) | paulius.baumila@binance.com \| DMLRO: egle.v@binance.com | YES |
| **BPay Global** (Fiat) | somaya.n@binance.com | YES |
| **France** | kevin.r@binance.com | NO |
| **Italy** | rossella.gancitano@binance.com | NO |
| **Spain** | pau.vidal@binance.com | NO |
| **Poland** | beata.wisnicka@binance.com | NO |
| **Sweden** | shawn.parnosi@binance.com | NO |
| **Australia** | andrew.p@binance.com \| DMLRO: veronica.f@binance.com | NO |
| **New Zealand** | arifa.p@binance.com | NO |
| **Japan** | yusuke.kato@binance.com, michinori.murata@binance.com | NO |
| **India** | husain.ahmed@binance.com (interim) | YES |
| **Binance Kazakhstan** | asset.s@binance.com | NO |
| **Thailand (Cloud Exchange)** | thitiwat.w@binance.com | NO |
| **Mexico** | ricardo.roman@binance.com | YES |
| **Colombia** | maria.r@binance.com | YES |
| **Venezuela** | maria.r@binance.com | YES |
| **Argentina** | agustin.iavicoli@binance.com | NO |
| **El Salvador** | rene.guzman@binance.com | NO |
| **Brazil** | victor.mg@binance.com | YES |
| **Turkey (.com)** | derya.i@binance.com | NO |
| **Binance Bahrain** | zainab.jahromi@binance.com | NO |
| **Dubai Exchange** | stephanie.emile@binance.com | NO |
| **ADGM** | Nest Exchange Limited & Nest Clearing and Custody Limited: yp.... | N/A |

> If a country is not listed here, escalate to **ADGM only**.

---

## Fiat Channel Escalation Triggers

### Bifinity FIAT Channels (Legacy)

> ⚠️ **ESCALATIONS EFFECTIVELY ENDED.** Escalations to Bifinity UAB ceased as of **31 December 2025**.
> Legacy cases only: alerts generated before **09 Feb 2026** with successful FIAT transactions on or before 31 Dec 2025.
> After 09 Feb 2026: **do NOT escalate to Bifinity.**

**MLRO:** paulius.baumila@binance.com | DMLRO: egle.v@binance.com
**Dual Escalation:** YES

**Escalate if:** Successful FIAT transactions (DP/WD) via Bifinity UAB channels are linked to suspicious activity.

**Do NOT escalate if:**
- No successful FIAT transactions (only Bifinity tag present)
- FIAT transactions are NOT linked to the suspicious activity
- Time gap between suspicious crypto activity and related FIAT exceeds 3 months
- Exposure is to online gambling addresses only (no other risk)
- Exposure is to OFAC sanctioned addresses only (no other risk)
- True Name Screening Match — OFAC sanctioned

### BPay Global

**MLRO:** somaya.n@binance.com
**Effective Date:** 01 July 2025
**Dual Escalation:** YES

**Escalate if:** Successful/attempted FIAT via BPay channels directly linked to suspicious activity, sanctioned entities, shell companies, or SOF mismatch.

**Do NOT escalate if:** No successful BPay FIAT transactions (unless fake KYC or non-transactional red flags), or BPay FIAT transactions are unrelated to suspicious activity.

**BPay FIAT Channel Tags:** EAZYPAY_BPAY, GP_EAZYPAY_BPAY, SGB_BPAY, PAVEBANK_BPAY_CORP, AP_EAZYPAY_BPAY, SGB_BPAY_CORP, STRAITSX_BPAY_RETAIL, STRAITSX_BPAY_CORP, BPAY_COMBINED, BPAY_COMBINED_CORP, WALLET_BPAY

---

_Generated from MLRO Escalation Requirements Matrix.xlsx on 2026-02-22_