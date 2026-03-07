# CTM ALERTS ENHANCED

**When to use:** Cases involving crypto transaction spreadsheets with specific flagged transactions (Period surrounding suspicious activity + Snapshot of suspicious transactions). This is the enhanced version for detailed transaction-level CTM analysis, distinct from Prompt #6 (CTM Standard) which handles aggregate alert summaries.

**Trigger Data:** Crypto transaction spreadsheet

---

**Prompt:**

Use only the information explicitly present in the provided input. Do not infer, estimate, or "fill gaps."

Numbers: Reproduce amounts/counts/dates exactly, but you MUST format all USD amounts with a leading $ and commas for thousands separators (e.g., convert 3889921.42 into $3,889,921.42). Do not change magnitude. All local currency amounts must include USD equivalent in square brackets.

Dates: Use YYYY-MM-DD when a date is present; do not fabricate a date range.

Address Referencing: You MUST include the FULL alphanumeric wallet address for the top 3 high-risk entities. Do not truncate the address.

Absence statements: Only state that something was "not observed" if the dataset explicitly supports absence. If silent, omit.

Tone: Write in a neutral investigative tone suitable for QC/regulators.

Structure: Write one paragraph (60-80 words). No bullets, headings, or line breaks.

Content Requirements:
1. State the total alert count, total exposed USD, and date range.
2. Describe the overall direction and category group pattern.
3. List the top 3 addresses by exposed amount using generic labels (e.g., "Top Wallet") and their exact exposed amounts.
4. Summarize the stated risk score range (min-max).
5. Conclusion: End with one of the following strictly based on the data:
   - If alerts are numerous and illicit/inbound with concentration across addresses: "This pattern may be consistent with layering/structuring indicators."
   - Otherwise: "The provided alert data indicates elevated exposure to illicit risk categories and requires manual verification for typology assessment."
