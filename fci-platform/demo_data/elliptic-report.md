```markdown
# Elliptic Wallet Screening Script — Improvement & AI Integration Report

## 1. Overview

This report documents the evaluation of a Python script that uses the Elliptic API to screen cryptocurrency wallets. The script output was compared against the Elliptic UI to ensure data parity for the intended workflow. The goal is to optimise the script output for feeding into the Anthropic API to generate analyst narratives, replacing the current manual process of screenshotting the UI and pasting into a chat window.

---

## 2. Current Workflow Being Replaced

1. Upload CSV of wallet addresses into Elliptic UI
2. Filter by Customer ID
3. Triage from the list view — focus on wallets with risk scores roughly >5
4. Click into high-risk wallets to examine source/destination entities, hop counts, typologies, and dollar values
5. Also screen specific wallets on request (e.g., law enforcement enquiries) regardless of risk score
6. Write a narrative on the higher-risk wallets

---

## 3. Evaluation Result

**The script is capturing all data required for the workflow.** No additional API fields need to be added.

### 3.1 Data Points Confirmed as Captured Correctly

| Data Point | Status |
|---|---|
| Risk scores (overall, source, destination) | ✅ |
| Source entity names and categories | ✅ |
| Destination entity names and categories | ✅ |
| Typology that triggered the risk (e.g., Dark Market, Ponzi Scheme) | ✅ |
| Hop count per entity | ✅ |
| Direct vs indirect dollar amounts per entity | ✅ |
| Total dollar values per entity exposure | ✅ |
| Sanctions flags (e.g., OFAC SDN, NBCTF) | ✅ |
| Wallet inflow/outflow (cluster flows) | ✅ (high risk only — see 4.1) |
| Customer ID | ✅ |

### 3.2 UI Fields Confirmed as NOT Needed

These are visible in the Elliptic UI but are not required for the narrative workflow:

- VASP field
- Status (Open/Closed)
- Last Screened At timestamp
- Screened By username
- Percentage contributions per entity
- Counterparty % vs Indirect % breakdown
- Entity count per category
- Category-level aggregation summaries
- Graph/flow visualisation data
- Notes tab content
- Screening History tab content

---

## 4. Changes Required to the Script Output

### 4.1 Remove: Primary Entity Field

**Why:** The Elliptic UI has a known behaviour where the list view frequently shows "Entity: Unknown" for wallets, even when the detailed exposure data contains fully resolved source and destination entities (e.g., Alphabay, Forsage, Binance). The script already correctly pulls the resolved entities from the exposure data, making the Primary Entity field redundant and potentially confusing to the AI when generating narratives.

**Action:** Remove `Primary Entity` and its associated category from the output for each address.

### 4.2 Remove: Self-Referencing "[THIS WALLET]" Exposure Entries

**Why:** The exposure data includes entries like:
```
Unknown (Unknown) — 0 hops — $39.04 (direct: $0.00 / indirect: $0.00) [THIS WALLET]
```
These are self-referencing entries showing the wallet's own unattributed balance. They add no analytical value for narrative generation and waste tokens.

**Action:** Filter out any exposure entry where hops = 0 and entity = "Unknown" and the entry refers to the screened wallet itself.

### 4.3 Change: Round Risk Scores to 1 Decimal Place

**Why:** The script currently outputs full-precision floats (e.g., `6.357916135605537`). The Elliptic UI displays these rounded to 1 decimal place (e.g., `6.4`). Analysts work with the rounded figure. Full precision wastes tokens and adds no value.

**Action:** Round all risk scores to 1 decimal place in the output.

### 4.4 Change: Remove Repeated "Chain: holistic" Per Address

**Why:** If all addresses in a batch are screened with holistic coverage (which is the standard configuration), repeating `chain: holistic` for every address wastes tokens.

**Action:** State the coverage mode once at the top of the output (e.g., `Coverage: Holistic`) and remove it from individual address entries. If the script ever handles mixed coverage modes, this can be made conditional.

### 4.5 Add: Wallet Inflow/Outflow for ALL Addresses

**Why:** The current script only outputs cluster flows (inflow/outflow) for the two high-risk addresses. The Elliptic UI shows wallet inflow and outflow for every address in the list view. While this may not be critical for every narrative, it provides useful context for the AI — particularly for understanding whether a wallet is a pass-through (similar inflow/outflow) or an accumulator.

**Action:** Ensure wallet inflow and outflow USD values are captured and included for all screened addresses, not just high-risk ones.

---

## 5. AI Narrative Generation — Prompt Design Guidance

### 5.1 Recommended System Prompt

```
You are a cryptocurrency compliance analyst. You are provided with wallet
screening results from the Elliptic platform. Your task is to produce a
concise, professional narrative for each high-risk wallet (risk score > 5)
and any specifically flagged wallets.

For each wallet, your narrative should address:

1. RISK SUMMARY — State the overall risk score and the primary reason it
   is elevated (which typology triggered, e.g., Dark Market, Ponzi Scheme,
   Sanctions exposure).

2. SOURCE OF FUNDS — Describe where funds flowing INTO the wallet
   originated. Highlight:
   - The highest-risk source entities and their categories
   - Whether the exposure is DIRECT (counterparty / 1 hop) or INDIRECT
     (multiple hops) — direct exposure is significantly more concerning
   - The dollar amounts involved — distinguish between material and
     trivial exposures

3. DESTINATION OF FUNDS — Describe where funds flowing OUT of the wallet
   went. Apply the same direct/indirect and materiality analysis.

4. SANCTIONS FLAGS — If any source or destination entity is flagged as
   sanctioned (e.g., OFAC SDN, NBCTF), call this out prominently.

5. OVERALL ASSESSMENT — Provide a brief professional opinion on the risk
   profile of the wallet.

Guidelines:
- Be factual and evidence-based. Only reference data provided.
- Direct/counterparty exposure (1 hop) is far more significant than
  indirect exposure at many hops.
- Small dollar exposures at many hops (e.g., $0.44 at 5 hops) are
  generally not material and should not be given undue prominence.
- Use professional compliance language suitable for inclusion in a
  Suspicious Activity Report or law enforcement response.
- Do not speculate beyond what the data shows.
- For medium-risk wallets (score 2-5) that are included, provide a
  shorter summary unless the data warrants detailed analysis.
```

### 5.2 Recommended User Prompt Structure

```
## Screening Context
- Customer ID: {customer_id}
- Date: {screening_date}
- Coverage: Holistic
- Addresses Screened: {count}
- High Risk (>5): {high_count}
- Medium Risk (2-5): {medium_count}
- Low Risk (<2): {low_count}

## Wallets Requiring Narrative

### Wallet: {address}
- Risk Score: {overall_score} (source: {source_score} / destination: {dest_score})
- Wallet Inflow: ${inflow} / Wallet Outflow: ${outflow}
- Risk Triggers:
  {trigger_typology} (score: {score}, direction: {source/destination})
    - {entity} — {hops} hops — ${total} (direct: ${direct} / indirect: ${indirect})
- Source Exposures:
  {entity} ({category}) — {hops} hops — ${total} (direct: ${direct} / indirect: ${indirect})
- Destination Exposures:
  {entity} ({category}) — {hops} hops — ${total} (direct: ${direct} / indirect: ${indirect})

{repeat for each wallet}

Please provide a narrative for each wallet listed above.
```

### 5.3 Token Optimisation Tips

1. **Only send wallets that need narratives** — don't send all 12 addresses if only 2-3 need analysis. Pre-filter in Python based on risk score threshold or specific address list.

2. **For medium-risk wallets in the summary table** — only send the full detail if specifically requested (e.g., law enforcement enquiry). Otherwise just include the summary row.

3. **Truncate long exposure lists** — for wallets like `bc1qj3tv...` which have 30+ source exposures, consider only sending:
   - All exposures flagged as illicit/sanctioned/high-risk categories (regardless of amount)
   - Top 10 exposures by dollar value
   - Any direct (1-hop) exposures
   - This can dramatically reduce token count without losing material information

4. **Batch wallets in a single API call** where possible rather than one call per wallet.

---

## 6. Summary of Implementation Tasks

| # | Task | Priority |
|---|---|---|
| 1 | Remove Primary Entity field from output | High |
| 2 | Remove self-referencing [THIS WALLET] entries | High |
| 3 | Round risk scores to 1 decimal place | Medium |
| 4 | Remove per-address "chain: holistic" (state once at top) | Low |
| 5 | Ensure wallet inflow/outflow is captured for ALL addresses | Medium |
| 6 | Implement Anthropic API integration with system prompt from Section 5.1 | High |
| 7 | Structure the user prompt per Section 5.2 | High |
| 8 | Add pre-filtering logic to only send relevant wallets to AI | Medium |
| 9 | Add exposure list truncation logic per Section 5.3 point 3 | Medium |

---

## 7. Example: Expected Output After Changes

For address `bc1qg3zrlp0mtzwznq6fhf4yllvph0qleay6h6gchw`:

```
### bc1qg3zrlp0mtzwznq6fhf4yllvph0qleay6h6gchw
- **Risk Score:** 10.0 (source: 10.0 / destination: 2.3)
- **Wallet Inflow:** $52,921.71 / **Wallet Outflow:** $73,282.73
- **Risk Triggers:**
  - Illicit Activity (score: 10.0, direction: source, categories: Dark Market - Centralized)
    - Alphabay — 10 hops — $52,921.71 (direct: $0.00 / indirect: $52,921.71)
  - Other Categories (score: 2.3, direction: destination, categories: Exchange)
    - OKX — 17 hops — $18,956.34 (direct: $0.00 / indirect: $18,956.34)
    - Binance — 1 hops — $10,940.15 (direct: $596.79 / indirect: $10,343.35)
    - KuCoin — 2 hops — $8,198.21 (direct: $0.00 / indirect: $8,198.21)
    - BingX — 5 hops — $4,427.80 (direct: $0.00 / indirect: $4,427.80)
- **Source Exposures (funds FROM):**
  - Alphabay (Dark Market - Centralized) — 10 hops — $52,921.71 (direct: $0.00 / indirect: $52,921.71)
- **Destination Exposures (funds TO):**
  - OKX (Exchange) — 17 hops — $18,956.34 (direct: $0.00 / indirect: $18,956.34)
  - Binance (Exchange) — 1 hops — $10,940.15 (direct: $596.79 / indirect: $10,343.35)
  - KuCoin (Exchange) — 2 hops — $8,198.21 (direct: $0.00 / indirect: $8,198.21)
  - BingX (Exchange) — 5 hops — $4,427.80 (direct: $0.00 / indirect: $4,427.80)
```

**Removed:** Primary Entity ("Unknown"), self-referencing entry, chain field, full-precision scores.
```
