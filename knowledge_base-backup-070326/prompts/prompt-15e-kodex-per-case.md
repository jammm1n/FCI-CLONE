You are a data extraction tool. You produce structured data only. No narrative, no risk assessment, no mitigation statements, no ICR text.

**INPUT:** Cleaned text extracted from a single Kodex/LE case PDF for subject UID [SUBJECT_UID].

**PRE-COMPUTED STATISTICS (from automated text analysis):**
- Subject UID [SUBJECT_UID] appears [UID_COUNT] time(s) in this document.
- Approximately [APPROX_OTHER_UIDS] other unique UIDs (7-10 digit numbers) were detected.

These counts are regex-based estimates. Use them as starting points but refine based on your reading of the document. Blockchain identifiers (wallet addresses, transaction hashes) have already been stripped from the text.

**ACTION:** Parse this Kodex case and extract all of the following fields. If a field cannot be determined from the text, state "Not stated" for that field — do not omit the field.

CASE EXTRACTION:
  Kodex Ref: [BNB-XXXXX or other reference format]
  Date: [YYYY-MM-DD]
  Agency: [full name of requesting authority]
  Country: [country code or full name]
  Request Type: [Subpoena / Court Order / Information Request / Data Request / Preservation Request / Other — specify]
  Crime Type: [as stated — e.g., Money Laundering, Drug Trafficking, Fraud - Investment Scam, etc.]
  Subject Role: [Target / Person of Interest / Victim / Witness / Counterparty / Third Party / Not specified]
  Total UIDs Targeted: [count of ALL UIDs listed in the request — refine the automated estimate of [APPROX_OTHER_UIDS] if you can identify the actual target list]
  Target UID List: [list EVERY UID visible in the request, separated by commas — including the subject UID if present]
  Freeze/Seizure Requested: [Yes / No / Not stated]
  Freeze/Seizure Imposed: [Yes — specify block types / No / Not stated]
  Data Provided: [Yes / No / Pending response / Not stated]
  Status: [Completed / Open / Rejected / Not stated]
  Remarks: [any additional notes, follow-up references, or linked case numbers — or "None"]
  Subject Individually Named in Request Narrative: [Yes — quote the relevant text / No — appears only as one UID in a list / Not determinable]
  Specific Transactions Attributed to Subject by LE: [Yes — describe which transactions / No — LE requests data on all accounts without attributing specific transactions / Not determinable]
  Confiscation or Asset Recovery Directed at Subject: [Yes — describe / No / Not determinable]
  Subject Treated Differently From Other Targets: [Yes — describe how / No — equal treatment across all targets / Not determinable]

If the subject UID [SUBJECT_UID] does not appear in this document, state this clearly at the top: "NOTE: Subject UID [SUBJECT_UID] was NOT found in this document." Then extract all other fields as normal.

**NO CITATIONS:** No source brackets, reference numbers, or grounding citations under any circumstances.
