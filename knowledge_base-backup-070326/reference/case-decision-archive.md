# Case Decision Archive
## Purpose
Full narrative entries recording case outcomes, QC feedback, and MLRO decisions. Each entry is numbered to match the corresponding row in decision-matrix.md. This document is reference material — the AI does not scan it at Step 21 unless a matrix match requires disambiguation or the investigator requests context.
---
## Entries
### #1 — 2026-02-19 — Offboarding — Offboarding Reason Selection
- **Case Ref:** ICRV20260213-01298
- **Scenario:** LE-referred case with Polícia Judiciária money laundering investigation, heavily contaminated counterparty profile, and multiple risk indicators. Knowledge base mapping suggested "High Potential to Money Laundering" as the offboarding reason.
- **My Decision:** Selected "High Potential to Money Laundering" based on the mapping.
- **Outcome:** Robert corrected — use "Suspicious Transaction Activities" instead.
- **What I Learned:** "High Potential to Money Laundering" requires a higher burden of proof where the activity is more directly and clearly money laundering. For cases based on accumulated indicators (LE referrals, counterparty risk, transaction patterns) rather than independently proven ML activity, "Suspicious Transaction Activities" is the safer and more appropriate choice. The offboarding reason reflects what the investigation found, not what LE alleged.
- **Lesson:** Default to "Suspicious Transaction Activities" unless the investigation independently proves money laundering activity. LE referrals alleging ML do not automatically warrant the ML offboarding reason.
---
### #2 — 2026-02-19 — RFI — Offboard vs RFI for LE Targets
- **Case Ref:** ICRV20260213-01298
- **Scenario:** LE-referred money laundering case with three Kodex cases from two agencies, 38.7% risk-flagged counterparties, co-target in same criminal case, fraud-flagged fiat, multi-country device access, $0 balance. Investigator considered RFI to give user opportunity to explain.
- **My Decision:** Initially leaned toward RFI.
- **Outcome:** Robert confirmed offboard. His test: "What answer would you expect that would be credible enough to retain this user?" If the honest answer is "nothing they say would change the outcome," then RFI adds delay without value. Additionally, contacting a named LE target via RFI risks tipping off the subject and compromising the law enforcement investigation.
- **What I Learned:** The RFI decision should be tested against the question: "If the user responds with the best possible answer, would it actually change the outcome?" When the evidence is overwhelming AND the user is a named LE target, sending an RFI is both unnecessary and potentially harmful.
- **Lesson:** Apply Robert's test before defaulting to RFI. For LE targets specifically, the tipping-off risk adds a second reason not to send RFI. This is a specific application of the universal principle in Rule #14.
- **See also:** #14 (universal RFI mitigation test)
---
### #3 — 2026-02-19 — Escalation — Bifinity Temporal Nexus for LE Cases
- **Case Ref:** ICRV20260213-01298
- **Scenario:** LE-referred case where user had successful fiat deposits via Bifinity channels (2022-2023) but the suspicious transactions identified by LE were from 2025. User had Bifinity Tag: Yes and both successful and rejected fiat via Bifinity channels.
- **My Decision:** Initially flagged for Bifinity escalation based on Bifinity tag and channel match.
- **Outcome:** Robert confirmed no Bifinity escalation. His reasoning: Bifinity escalation requires successful fiat transactions to be LINKED to the suspicious activity. The fiat deposits from 2022-2023 were deposited and used long before the 2025 suspicious transactions. There is no temporal nexus. Robert checked the UOL to confirm the fiat deposits occurred in a completely different time period to the LE-identified transactions.
- **What I Learned:** Bifinity escalation is not triggered simply by having a Bifinity tag or having used Bifinity channels. The specific test is: did the fiat funds flow into or support the specific suspicious activity identified in this case? If the fiat deposits occurred years before the suspicious activity, they cannot be linked.
- **Lesson:** For Bifinity escalation: (1) identify the successful fiat transactions and their dates, (2) identify the suspicious transactions and their dates, (3) check whether the fiat funds can be temporally linked to the suspicious activity using the UOL. If the fiat is years apart from the suspicious activity, no escalation. The Bifinity tag alone is never sufficient.
---
### #4 — 2026-02-19 — Elliptic — Ambiguous High Risk Scores (FATF Monitoring)
- **Case Ref:** ICRV20260213-01298
- **Scenario:** Elliptic screening returned a 10/10 risk score for a WhiteBIT wallet. The trigger was FATF increased monitoring due to Croatia's grey list status, not illicit or fraudulent activity. WhiteBIT is a registered VASP and operational exchange.
- **My Decision:** Mitigated in the ICR as regulatory risk rather than criminal risk.
- **Outcome:** Robert agreed — "Standalone it's not high risk anything." He treated it as a neutral factor that becomes negative only when coupled with other ML indicators.
- **What I Learned:** A 10/10 Elliptic score does not automatically mean high criminal risk. The triggered rule matters more than the numerical score. FATF increased monitoring relates to jurisdictional risk, not entity-level illicit activity. When the entity is an attributed, operational VASP, the score is driven by the jurisdiction rather than the entity's behaviour. An unattributed wallet with the same score and trigger would warrant more caution.
- **Lesson:** For Elliptic scores triggered by FATF monitoring or jurisdictional rules on attributed VASPs: state the score, explain the specific trigger rule, note the entity is a registered VASP, and assess as regulatory rather than criminal risk. Only treat as criminal risk if coupled with other ML indicators in the case.
---
### #5 — 2026-02-19 — Device — Shared FaceVideo ID Interpretation
- **Case Ref:** ICRV20260213-01298
- **Scenario:** Device analysis identified a shared FaceVideo ID between the subject (UID 354217838) and UID 397173891. The linked UID had no KYC, no nationality recorded, residence listed as Portugal, zero balance, no transaction history, no LE cases, and no blocks.
- **My Decision:** Interpreted as possible duplicate account controlled by the same person.
- **Outcome:** Robert agreed — "It might be a duplicate account. He tries to recreate the account."
- **What I Learned:** Shared FaceVideo IDs suggest the same individual completed face verification for both accounts. When the linked account has no KYC, no activity, and zero balance, the most likely explanation is a duplicate or test account. This is an additional risk factor that contributes to the overall profile assessment but is not independently decisive when the linked account is inactive.
- **Lesson:** Shared FaceVideo IDs = same person likely completed face verification for both. Severity depends on the linked account's profile: no KYC and no activity = lower concern, active account with suspicious activity = higher concern. Always list the linked UID and its full status regardless of severity.
---
### #6 — 2025-07-XX — General — Multi-User ICR: Pragmatic Scope
- **Case Ref:** N/A (mentoring guidance)
- **Scenario:** Discussion about how thoroughly to analyse the second user in a multi-user ICR, specifically regarding CTM/FTM alerts and full transaction monitoring data.
- **My Decision:** N/A
- **Outcome:** Robert confirmed that technically, every step should be completed for both users. However, he personally focuses on the biggest concern and does not replicate full CTM/FTM analysis for the second user if their activity is minimal or absent. He has never received a QC question about this approach.
- **Lesson:** In multi-user ICRs, apply proportionality to the second user. Full framework for User 1 (the primary concern). For User 2: confirm data presence/absence at each step, write findings if they exist, state "no data" if they don't. Do not skip steps entirely — always acknowledge each section for both users. Depth should match the available data.
- **See also:** #7 (understanding the connection between users)
---
### #7 — 2025-07-XX — General — Multi-User ICR: Understand the Connection
- **Case Ref:** N/A (mentoring guidance)
- **Scenario:** Robert emphasized understanding and articulating WHY the second user is included in a multi-user ICR.
- **My Decision:** N/A
- **Outcome:** Robert stressed: "Read the context of the case. Understand why this one is here."
- **Lesson:** In every multi-user ICR, the report must explicitly state HOW the users are connected (shared device, counterparty relationship, same LE ticket, same fraud scheme, same ID document, etc.). This connection should appear in the L1 summary context and be reinforced throughout analytical sections where relevant. If the connection is unclear from the L1 referral, investigate it before proceeding.
- **See also:** #6 (proportional depth for second user)
---
### #8 — 2025-07-XX — LE — Confirmed Criminal Proceedings: Offboarding Threshold Met
- **Case Ref:** ICRV20260218-00040
- **Scenario:** Wu Haibo (吴海波), Chinese national controlling two Binance accounts, confirmed via Face Compare as FBI-indicted member of the Aquatic Panda Cyber Threat Actors group. Prior Sanctions/CTF review retained under restriction to facilitate FBI coordination. FBI obtained data but took no further action. FCI asked to reassess offboarding.
- **My Decision:** Offboard both UIDs. No RFI (tipping off risk). Escalate to ADGM MLRO.
- **Outcome:** Awaiting MLRO decision.
- **What I Learned:** An active criminal indictment, warrant, or proceedings from any jurisdiction — with confirmed identity match (face + name + DOB + ID number) — constitutes "hard, undeniable evidence that cannot be questioned or denied." The fact that LE did not request a freeze does not mean the account should be retained. A prior team's decision to retain for tactical reasons (facilitating LE coordination) does not bind FCI when the coordination is complete and LE has taken no further action. This principle applies regardless of VIP or corporate status — it overrides Rule #13.
- **Lesson:** Confirmed identity + active criminal proceedings = offboard. No RFI (tipping off risk). Prior retain decisions by other teams made for tactical reasons do not prevent FCI from recommending offboarding. The absence of an LE enforcement request does not negate compliance risk.
- **See also:** #13 (VIP/corporate threshold — overridden by this rule)
---
### #9 — 2025-07-XX — General — Balance Change Between Reviews
- **Case Ref:** ICRV20260218-00040
- **Scenario:** Balance increased from $366K to $478K between prior ICR and current review, despite full account blocks being placed.
- **My Decision:** Noted as likely due to trading activity before blocks or asset price appreciation on held positions.
- **Outcome:** N/A — observational.
- **Lesson:** When balance changes between ICR reviews, always note and explain. Possible causes: (1) new transactions between the prior case close and block date, (2) asset price appreciation/depreciation on held positions, (3) trading activity if trade blocks were not yet in place, (4) staking/earn rewards. State the likely cause based on the timeline of blocks vs activity.
---
### #10 — 2026-02-XX — Offboarding — Cumulative Risk Overrides Individual Mitigation
- **Case Ref:** ICRV20260211-01805
- **Scenario:** Myanmar national (UID 579611040) referred following a Bulgarian organized crime unit fraud data request (BNB-216016). Investigation revealed: 9 CTM alerts across 6 illicit-categorized wallets (5 attributed to HUIONE Pay), 7 of 14 internal counterparties connected to the same Bulgarian fraud investigation with LE tickets, dominant Cambodia access (59% of logins) abnormal for a Myanmar-registered user, 98% outbound-to-inbound fund dissipation ratio, and a $0.53 balance. HUIONE Pay exposure was individually mitigated as a widely adopted regional payment platform. The investigator recommended RFI based on the reasoning that no single piece of hard proof existed.
- **My Decision:** Recommended RFI (Transaction Verification) to address counterparty transactions.
- **Outcome:** Robert overruled — recommended offboard. His reasoning: while HUIONE Pay exposure can be mitigated in isolation, when it sits alongside multiple other unmitigated red flags (LE fraud referral, heavily flagged counterparty network sharing the same LE investigation, Cambodia access pattern for a Myanmar user, near-complete fund dissipation, dormant account), the HUIONE mitigation does not resolve the broader risk picture. The cumulative weight of all indicators together tips the case to offboard. An RFI would not resolve the Cambodia access concern or the counterparty network connections — the core risks would remain regardless of the user's response.
- **What I Learned:** Individual mitigations can resolve a specific finding in isolation, but they do not cancel out unrelated risk factors. When multiple independent risk indicators all point in the same direction, the totality must be assessed as a whole. The critical test is: would a satisfactory RFI response actually resolve the primary concerns? If the concerns are behavioral patterns and network connections rather than explainable transactions, the answer is no — and offboard is the correct decision.
- **Lesson:** When assessing whether to send an RFI or offboard, ask: "Would a satisfactory RFI response resolve the primary concerns?" If concerns are behavioral/network-based rather than transaction-based, RFI adds delay without changing the outcome. Offboard directly.
- **See also:** #12 (HUIONE mitigation — overridden by this rule when cumulative risk is high), #14 (universal RFI mitigation test)
---
### #11 — 2026-02-XX — Elliptic — Do Not Report Low-Risk Wallet Triggered Rules
- **Case Ref:** ICRV20260211-01805
- **Scenario:** Elliptic screening returned 13 wallets. Wallets scoring 2.3 and 4 had triggered rules including Gambling and Sanction List. These were included in the Step 10 narrative, creating unnecessary mitigation obligations.
- **My Decision:** Initially included gambling and sanctions references in the narrative for low-scoring wallets.
- **Outcome:** Robert confirmed that triggered rules on wallets scoring below 5 out of 10 should not be mentioned. Only wallets scoring 5 or above require individual analysis with entity names, direction, hop count, and commentary. Mentioning low-score triggers creates QC risk by introducing findings that then require mitigation.
- **What I Learned:** The risk score is the gatekeeper. Below 5, Elliptic has assessed the exposure as negligible. Naming the triggered rule (Gambling, Sanctions, Fraudulent) elevates it in the reader's mind and creates a formal obligation to mitigate it in the ICR — an obligation that would not exist if the rule had not been mentioned.
- **Lesson:** Only report triggered rules and entity details for wallets scoring 5 or above. Below 5, dismiss with one sentence. Do not perform gambling matrix checks for low-scoring wallets. The principle is: do not create mitigation obligations for findings that the screening tool itself assessed as negligible.
---
### #12 — 2026-02-XX — Elliptic — HUIONE Pay Exposure for Southeast Asian Users
- **Case Ref:** ICRV20260211-01805
- **Scenario:** Myanmar user with direct exposure to multiple HUIONE Pay-attributed wallets. HUIONE Pay has been designated under FinCEN Section 311 as a primary money laundering concern. Initial analysis flagged the exposure as high risk.
- **My Decision:** Initially flagged as high risk requiring detailed analysis of each HUIONE wallet.
- **Outcome:** Robert provided standard mitigation text. HUIONE Pay is a widely adopted regional payment platform across Southeast Asia. Exposure alone does not raise concerns for users in the region without additional red flags linking the specific transactions to confirmed illicit activity.
- **What I Learned:** HUIONE Pay exposure for Southeast Asian users is analogous to PayPal exposure for Western users — it is a common payment platform in the region. The FinCEN designation should be stated factually but does not automatically make every HUIONE transaction suspicious. The mitigation is overridden when multiple independent risk factors exist alongside the HUIONE exposure (see Rule #10).
- **Lesson:** For Southeast Asian users with HUIONE Pay wallet exposure, apply the standard mitigation text below verbatim unless additional indicators link the HUIONE transactions to confirmed illicit activity. Do not over-elaborate on the FinCEN designation.
- **Standard Mitigation Text (Robert — verbatim):** "Exposure to Huione Pay among Asian users is regarded as normal given its broad adoption and acceptance in the region. As a popular payment service, Huione Pay is frequently used for a variety of transactions such as online shopping, bill payments, and money transfers. Its common presence in everyday financial activities makes it a trusted and familiar platform for users in these areas. Without any additional red flags or unusual behavior, the use of Huione Pay by itself does not raise concerns. Evaluations of user activity should take into account the regional context and customary practices, as regular use of a widely accepted service like Huione Pay reflects typical financial behavior in Asia."
- **See also:** #10 (this mitigation is overridden when cumulative risk is high)
---
### #13 — 2026-02-17 — Corporate — VIP/Corporate Offboarding Threshold
- **Case Ref:** Anonymized — Brazilian OTC broker, ~$15M+ trading volume
- **Scenario:** A VIP corporate OTC broker showed multiple suspicious indicators: blacklisted counterparties, banking fraud alerts, law enforcement tickets, high-risk device overlaps, and counterparties that had been offboarded. Initial instinct was to recommend offboarding based on accumulated risk indicators.
- **My Decision:** Considered recommending offboarding.
- **Outcome:** Robert confirmed offboarding a VIP corporate client of this size is extremely rare. Hard proof is required — evidence that "cannot be questioned and cannot be denied." Multiple RFIs and source of funds requests would be needed first. If the company responds with explanations consistent with their business profile, offboarding will not be supported.
- **What I Learned:** Suspicion alone, even strong suspicion with multiple red flags, is insufficient to offboard a high-volume VIP corporate client. The entity must be given opportunities to explain via RFI. Explanations consistent with the declared business profile (e.g., OTC broker processing client transactions) are accepted as mitigating. Offboarding requires unresponsiveness or definitively proven illicit activity.
- **Lesson:** For VIP/corporate accounts, do not recommend offboarding based on accumulated indicators. Send RFI first. Only recommend offboarding if the entity is unresponsive or evidence is undeniable. Exception: Rules #2 and #8 override this when evidence is identity-based (confirmed criminal proceedings) or undeniable regardless of VIP status.
- **See also:** #8 (overrides this rule for confirmed criminal proceedings), #15 (balanced narrative approach)
---
### #14 — 2025-07-XX — General — The Universal RFI Mitigation Test
- **Case Ref:** N/A (mentoring guidance, refined through cases ICRV20260213-01298 and ICRV20260211-01805)
- **Scenario:** General decision-making framework for when to send an RFI versus when to offboard directly, applicable to all case types.
- **My Decision:** N/A — this is the foundational principle.
- **Outcome:** Robert's consistent position across multiple cases: an RFI is only justified when a credible response from the user could realistically change the outcome of the investigation. If the identified risks are such that no response — no matter how well-crafted — would mitigate them below the offboarding threshold, then the RFI serves no purpose and adds unnecessary delay.
- **What I Learned:** RFI is not a default action for uncertainty or indecision. It is a specific investigative tool deployed when there is a genuine information gap that, if filled, could change the risk assessment. The test is always forward-looking: "If I receive the best possible response, does the case outcome change?" If yes, send the RFI. If no, the decision is already clear and the RFI is procedural box-ticking.
- **Lesson:** Before sending any RFI, apply the mitigation test: "Could any credible response to this RFI realistically mitigate the risk below offboarding threshold?" If yes, send it. If no, offboard directly. This applies universally — individual accounts, corporate accounts, LE cases, fraud cases, CTM cases. The test adapts to context but the principle is constant.
- **See also:** #2 (LE-specific application with tipping-off dimension), #10 (cumulative risk application), #20 (three-tier decision framework)
---
### #15 — 2026-02-17 — General — Compliance Investigation vs Law Enforcement Mindset
- **Case Ref:** Anonymized — Brazilian OTC broker
- **Scenario:** Investigator with a police background found it difficult to observe highly suspicious activity and not recommend immediate enforcement action. Robert addressed this tension directly.
- **My Decision:** Instinct was to act decisively on the red flags.
- **Outcome:** Robert explained that compliance requires a balance between the company's business interests and investigation findings. The investigator's role is to document findings and present them in a balanced way, not to make unilateral enforcement decisions. L3 reviewers and MLROs provide additional oversight and will escalate if needed.
- **What I Learned:** The FCI investigator documents and presents a balanced case. L3/MLRO makes the ultimate retain/offboard/report decision. This is not law enforcement — proportionality and mitigation attempts are expected before escalation. Strong personal conviction about offboarding must still be supported by evidence meeting the appropriate threshold.
- **Lesson:** Present balanced narratives, not advocacy for a particular outcome. If the evidence does not meet the hard proof threshold, the investigator's role is to document the risk factors, attempt to mitigate them, and present the case for L3/MLRO review — not to force a particular outcome.
- **See also:** #13 (VIP/corporate threshold), #17 (L3/MLRO safety net)
---
### #16 — 2026-02-17 — Corporate — US IP Address Proportionality Assessment
- **Case Ref:** Anonymized — Brazilian OTC broker
- **Scenario:** A United States IP address was identified in the device/connection analysis for a Brazilian corporate entity. Investigator was unsure how to assess the significance.
- **My Decision:** Initially unsure whether to flag as high risk.
- **Outcome:** Robert clarified: US IP connections must be assessed by frequency and proportion. A single or rare connection from a corporate account with many employees is not automatically a dealbreaker and can be mitigated by referencing the company's employee base. However, if US connections constitute a significant proportion (40-50%+) of total activity, the MLRO will likely say offboard because the entity is not permitted to operate from the US.
- **What I Learned:** The significance of US IP access is entirely dependent on proportion. The same single US login is negligible for a corporate account with hundreds of sessions but concerning for a personal account with ten total logins. Always quantify before assessing.
- **Lesson:** For US IP connections: quantify first as a percentage of total access, then assess. Rare or single occurrence for a corporate account with multiple employees is mitigable by referencing the corporate structure and employee base. Significant proportion (40-50%+) is an offboarding-level trigger regardless of other factors.
- **See also:** #13 (VIP/corporate approach)
---
### #17 — 2025-07-XX — General — L3/MLRO Safety Net for Genuine Uncertainty
- **Case Ref:** Anonymized — Brazilian OTC broker
- **Scenario:** Investigator was concerned about personal accountability if a risky account was retained based on their recommendation.
- **My Decision:** Uncertain about recommending retain given the volume of red flags.
- **Outcome:** Robert confirmed that L3 reviews every case after the investigator submits. The MLRO then makes the final retain/offboard/report decision. Robert stated: "There's two people watching this."
- **What I Learned:** The investigation chain has built-in oversight. L3 and MLRO will catch cases that need escalation even if the investigator recommends retain. This does not mean investigators should be careless — it means that genuine uncertainty about a borderline case should not cause paralysis. The safety net exists for cases where reasonable, competent investigators could disagree on the outcome.
- **Lesson:** When genuinely uncertain on a borderline case, focus on thorough documentation and balanced presentation rather than agonizing over the final recommendation. This is NOT a reason to under-analyse or submit lazy work — it is reassurance specifically for cases where reasonable investigators could disagree on the outcome. The L3/MLRO oversight exists for exactly these situations.
- **See also:** #15 (balanced narrative approach)
---
### #18 — 2025-07-XX — Fraud — Refund Process and the $1,000 Threshold
- **Case Ref:** N/A (mentoring guidance)
- **Scenario:** Discussion about whether to engage the 3-reminder refund process when suspect balance is below $1,000.
- **My Decision:** N/A
- **Outcome:** Robert confirmed: SOP flowchart says below $1,000 you can offboard directly without the refund process. Above $1,000, the refund process with 3 reminders is expected.
- **What I Learned:** Below $1,000 — refund process is optional but can be done if you want to (more ethical/customer-centric approach). Above $1,000 — refund process is expected by the SOP. Engaging the refund process below $1,000 adds complexity (pending status, tracking, follow-ups) that may not be justified for small amounts.
- **Lesson:** Below $1,000: offboard directly unless there is a specific reason to try for a refund. Above $1,000: always engage the refund process with 3 reminders first per SOP before proceeding to offboard.
---
### #19 — 2025-07-XX — LE — MLRO Overrode Retain on Unresponsive RFI
- **Case Ref:** [8546 case]
- **Scenario:** LE case with prior RFI sent by another investigator. Closed as unresponsive RFI pending user reply. MLRO reviewed and approved offboarding instead, citing multiple alerts and medium-to-high risk profile despite user non-response.
- **My Decision:** Close pending user reply to RFI.
- **Outcome:** MLRO approved offboarding. Changed the User Investigation tab to "Suspicious Transaction Activities" and recommended offboard.
- **What I Learned:** An unresponsive user with multiple red flags can be offboarded even without an RFI response — the non-response itself, combined with existing evidence, can be sufficient. The MLRO reached the same conclusion the investigator should have reached. Closing as unresponsive and waiting was the less decisive option.
- **Lesson:** When a user has multiple historical red flags (LE cases, prior ICRs, high alert count) and fails to respond to RFI, lean toward recommending offboard rather than closing as unresponsive and waiting indefinitely. The MLRO will likely reach the same conclusion independently. Be decisive — non-response combined with accumulated evidence is often sufficient.
---
### #20 — 2025-07-XX — General — Three-Tier Decision Framework
- **Case Ref:** N/A (mentoring guidance, refined through multiple cases)
- **Scenario:** General decision-making framework discussed with Robert, applicable to every case at Step 21.
- **My Decision:** N/A — this is the foundational framework.
- **Outcome:** Robert confirmed three possible outcomes and when each applies.
- **What I Learned:** The decision framework is:
  1. **RETAIN:** Risk can be mitigated with available evidence. Clear to retain.
  2. **OFFBOARD:** Clear red flags that cannot be mitigated. No credible explanation would change the assessment.
  3. **RFI:** Only when a credible response from the user could realistically mitigate the identified risk below the offboarding threshold. There is a genuine information gap that, if filled, would change the outcome.
- **Lesson:** RFI is never a default for indecision. It is a specific tool for genuine information gaps. If the investigator cannot articulate what response would change the outcome, the decision is already clear — either the risk is mitigated (retain) or it is not (offboard). Approximately 20% of cases should result in RFI — if the rate is significantly higher, the investigator may be avoiding decisions rather than making them.
- **See also:** #14 (universal RFI mitigation test)
---
### #21 — 2025-07-XX — Fraud — Multiple Suspects and Evidential Connection
- **Case Ref:** [To be added]
- **Scenario:** L1 referral listed multiple suspects and four transactions. Only three could be evidentially connected to the suspect under investigation. Fourth transaction went to a different UID with no established connection.
- **My Decision:** Initially confused about total refund amount.
- **Outcome:** Robert clarified: only request refund for transactions that can be evidentially connected to the suspect.
- **What I Learned:** When calculating refund amounts, the evidential connection between each transaction and the specific suspect matters. Not every transaction in an L1 referral necessarily belongs to the suspect under investigation — other UIDs may be involved.
- **Lesson:** Include ONLY transactions where the connection to the suspect is established through evidence (UOL, chat screenshots, transaction data). Mention unconnected UIDs in the report for completeness but exclude their transactions from the refund request. State explicitly: "UID [X] could not be connected to this suspect through available evidence."
---
### #22 — 2025-07-XX — Elliptic — Trivial Gambling Exposure
- **Case Ref:** [To be added]
- **Scenario:** Elliptic screening showed $5 exposure to a gambling wallet. User jurisdiction required gambling matrix check.
- **My Decision:** Initially unsure whether to flag as high risk per gambling matrix.
- **Outcome:** Robert advised that trivial amounts can be mitigated by stating the amount is insignificant relative to overall transaction volume. However, the gambling matrix check for the user's jurisdiction is mandatory regardless of the exposure amount.
- **What I Learned:** The gambling matrix check is non-negotiable — always perform it. But the risk assessment is proportional. A $5 gambling exposure on a $500,000 account is a different risk proposition than a $5,000 gambling exposure on a $10,000 account.
- **Lesson:** Always check the gambling matrix for the user's jurisdiction — this is mandatory regardless of amount. For trivial amounts ($5-10), mitigate by stating: "Exposure to gambling-related address was identified at [amount], which is insignificant relative to the user's overall transaction volume of [amount]." This is sufficient for QC.
---
### #23 — 2025-07-XX — Fraud — Grey Market Purchase Dispute
- **Case Ref:** [To be added]
- **Scenario:** Victim purchased grey market service (Netflix-type account sharing) from suspect's platform via Binance P2P. Service not delivered. Suspect refused refund and doxed victim.
- **My Decision:** Offboard suspect with refund request.
- **Outcome:** Robert confirmed approach was correct — offboard was for the fraud/refusal to refund/threatening behavior, NOT for selling grey market services.
- **What I Learned:** The nature of the underlying goods or services is separate from the fraudulent conduct. Grey market services (account sharing, subscription reselling) are not grounds for offboarding on their own — they may be against terms of service for the service provider, but that is not Binance's concern. The fraud, threatening behavior, and refusal to refund are what constitute the offboarding trigger.
- **Lesson:** Grey market services are not grounds for offboarding. The fraud/threatening/refusal-to-refund behavior is the trigger. Do not conflate the nature of the goods with the fraudulent conduct when writing the ICR or selecting the offboarding reason.
---
### #24 — 2026-02-16 — General — Risk Must Be Explicitly Mitigated or Not
- **Case Ref:** ICRV20260213-00572
- **Scenario:** CTM alerts showed $2.7M direct exposure to a 10/10 fraud-attributed wallet. Initial AI output described the data accurately but did not take a position on whether the risk was mitigated.
- **My Decision:** Revised to explicitly state risk cannot be mitigated with available information.
- **Outcome:** Awaiting QC review.
- **What I Learned:** Neutral descriptions without a position are insufficient. The L2 investigator's job is to evaluate, not just describe. QC checks for whether the investigator took a position on each risk factor. An analytical section that describes a risk without stating whether it is mitigated or not leaves the reader — and the MLRO — without the investigator's professional assessment.
- **Lesson:** Every analytical section in the ICR must conclude with a clear statement: either "this risk is mitigated because [reason]" or "this risk cannot be mitigated with the information currently available." This applies to CTM alerts, exposed addresses, counterparty analysis, and transactional analysis. No exceptions.
---
### #25 — 2025-01-16 — General — Report Language Must Be Consistent With Conclusion
- **Case Ref:** N/A (QC Training — Risk Mitigation Session, 16 January 2025)
- **Scenario:** QC identified cases where investigators used definitive language ("the user is involved in money laundering," "terrorist financing activity identified") in the body of the report, then concluded with a retain recommendation. This is internally contradictory and would fail external review.
- **My Decision:** N/A
- **Outcome:** QC confirmed this is a material finding. The language in the report body must be consistent with the conclusion. If retaining, the body should use hedging language ("indicators consistent with," "patterns that may suggest") not definitive statements of guilt.
- **What I Learned:** If the conclusion is to retain, the body of the report must not contain definitive statements of criminal involvement. Definitive accusatory language is only consistent with an offboard conclusion. This is the Narrative Balance Rule in practice — risk factors must be paired with mitigation, and the language must reflect the assessed level of certainty, not stated as proven fact.
- **Lesson:** If retaining: use "indicators consistent with," "patterns that may suggest," "elevated risk related to." If the language in the body states the user IS involved in illicit activity, the only consistent conclusion is offboarding. Imagine the report being reviewed externally — the body and conclusion must tell the same story.
- **See also:** #24 (explicit risk position required — this rule governs the tone of that position)
---
### #26 — 2025-01-16 — General — API Trading as Mitigation Factor
- **Case Ref:** N/A (QC Training — Risk Mitigation Session, 16 January 2025)
- **Scenario:** Q&A discussion about how API trading affects FTM alerts and device analysis. API traders connect platforms programmatically, which generates: (1) SAWD alerts from rapid automated deposits/withdrawals between exchanges, (2) diverse IP locations from different server/cloud access points within short time periods.
- **My Decision:** N/A
- **Outcome:** QC/senior staff confirmed API trading status is a valid mitigating factor for SAWD alerts and for diverse IP locations in device analysis. However, API trading does NOT mitigate high-risk counterparty exposure or CTM alerts.
- **What I Learned:** API trading explains specific patterns that would otherwise appear suspicious: rapid fund movements between exchanges and IP diversity from cloud server access. The mitigation has a clear boundary — it covers transactional velocity and device/IP anomalies only, not the quality of counterparties or on-chain exposure.
- **Lesson:** When a user is identified as an API trader (visible in account profile or UOL): (1) SAWD/rapid movement FTM alerts can be mitigated — state the user is an API trader and the rapid movements are consistent with automated inter-exchange activity, (2) diverse IP locations in short time periods can be mitigated — API connections may originate from different server locations, (3) API status does NOT mitigate CTM exposure, high-risk counterparties, or other non-transactional red flags.
---
### #27 — 2025-01-16 — General — Family Member Counterparty Identification
- **Case Ref:** N/A (QC Training — Risk Mitigation Session, 16 January 2025)
- **Scenario:** Sample case showed a counterparty sharing the same address and last name as the subject. Training confirmed this is a valid mitigation factor (likely family member). However, also warned about the risk of offboarded users operating through family members' accounts.
- **My Decision:** N/A
- **Outcome:** Dual lesson: (1) Shared address + shared surname = likely family member, which is a valid mitigation for the counterparty relationship. (2) Be alert for the reverse scenario where a previously offboarded user is operating through a family member's account.
- **What I Learned:** Family member identification works in two directions. As a mitigation: it explains the counterparty relationship and reduces the risk of an unknown third-party connection. As a risk indicator: if the subject has been offboarded or has a high-risk history, transactions with family members may indicate the subject is circumventing the offboard by operating through a relative.
- **Lesson:** Check counterparties for shared addresses and surnames with the subject. If found, state: "The counterparty shares the same residential address and surname as the subject, indicating a likely family relationship. This mitigates the counterparty risk." Simultaneously, if the subject was previously offboarded or has high-risk history, check whether family member counterparties might be allowing the subject to continue operating on the platform.
---
### #28 — 2025-01-16 — LE — Multiple Tickets May Represent Single Investigation
- **Case Ref:** N/A (QC Training — Risk Mitigation Session, 16 January 2025)
- **Scenario:** Training highlighted that multiple LE tickets may represent a single investigation with back-and-forth communication between the case team and law enforcement. Five tickets from the same agency about the same subject is one investigation, not five separate investigations.
- **My Decision:** N/A
- **Outcome:** QC confirmed this is a valid mitigation factor. The raw count of LE tickets is less significant than the count of distinct investigations.
- **What I Learned:** LE ticket count can be misleading. A single investigation may generate multiple Kodex tickets as the case team and law enforcement exchange follow-up requests, clarifications, and additional data. The analytical value is in counting distinct investigations (unique agencies + unique subject matter), not individual tickets.
- **Lesson:** When reviewing LE enquiries, check whether multiple tickets are from the same agency regarding the same subject matter. If so, state: "The user was subject to [X] LE requests; however, [Y] of these relate to the same investigation from [Agency], representing back-and-forth communication rather than separate investigations." Count distinct investigations, not individual tickets. This is particularly relevant when the LE ticket count is used as a risk factor in the conclusion — the count must reflect reality.
---
### #29 — 2025-01-16 — General — Victim vs Suspect in CTM Fraud Exposure
- **Case Ref:** N/A (QC Training — Risk Mitigation Session, 16 January 2025)
- **Scenario:** Training emphasized the importance of determining the user's role (victim vs suspect) when assessing CTM exposure to fraud schemes (Ponzi, pig butchering, ransomware).
- **My Decision:** N/A
- **Outcome:** The direction of funds relative to the high-risk entity determines the user's likely role: deposits TO the entity indicate the user may be a victim (sending funds to a scam). Withdrawals FROM the entity indicate the user may be receiving illicit proceeds (suspect). The transaction pattern and context must be stated in the report.
- **What I Learned:** The same CTM alert — exposure to a fraud-attributed wallet — has a completely different risk implication depending on whether the user sent funds to or received funds from the entity. A victim sending funds to a Ponzi scheme needs protection, not offboarding. A suspect receiving proceeds from a Ponzi scheme needs investigation and likely offboarding. The direction of funds is the critical first assessment.
- **Lesson:** For CTM exposure to fraud-related entities, always state: (1) the direction of the flagged transaction (to or from the high-risk address), (2) whether the user appears to be a victim (sending funds) or a suspect (receiving proceeds), (3) how this determination affects the risk assessment. This distinction significantly changes the recommendation — victims are generally retained with monitoring, suspects are investigated for offboarding.
---
### #30 — 2025-01-16 — General — Source of Wealth Threshold and Profile Mismatch
- **Case Ref:** N/A (QC Training — Risk Mitigation Session, 16 January 2025)
- **Scenario:** Training provided guidance on when to request Source of Wealth: (1) single transactions over $100K as a general threshold, (2) any transaction volume that is disproportionate to the user's KYC profile (age, occupation, declared income). Example given: a 22-year-old Albanian residing in Greece, junior employee in construction industry, with $350K in a single transaction.
- **My Decision:** N/A
- **Outcome:** Both volume-based and profile-based triggers for SOW requests were confirmed. The profile mismatch test is the more important of the two.
- **What I Learned:** The absolute dollar amount is less important than the relationship between the transaction volume and the user's profile. A $50K transaction from a 20-year-old student is more suspicious than a $200K transaction from a 45-year-old confirmed business owner. The profile mismatch test forces the investigator to consider whether the funds are plausible given what is known about the user.
- **Lesson:** Consider SOW request when: (1) a single transaction exceeds $100K, or (2) transaction volumes are clearly disproportionate to the user's profile regardless of the absolute amount. The profile mismatch test is the stronger trigger. When flagging disproportionate volumes, state the specific mismatch: "The user's KYC profile indicates [age, occupation] which is inconsistent with the transaction volume of [amount]."
- **See also:** #14 (apply the RFI mitigation test — if SOW is requested via RFI, the response must be capable of changing the outcome)
---
### #31 — 2025-XX-XX — General — Prior Warning as Aggravating Factor for Continued High-Risk Interaction
- **Case Ref:** N/A (Onboarding training — CTM Alerts Session + Gambling Session)
- **Scenario:** Two training sessions independently discussed how prior warnings factor into case assessment. For CTM cases: if a user was warned about interacting with a high-risk address and continues to interact with the same or similar high-risk addresses, this is an aggravating factor. For gambling cases: the default workflow for licensed entities in prohibited jurisdictions is warning first, offboard on repeat — the prior warning is what enables the offboard decision on the second occurrence.
- **My Decision:** N/A
- **Outcome:** Trainers confirmed: prior warning + continued interaction supports offboarding. The warning demonstrates the user was notified and chose to continue. A simple warning is no longer appropriate on the second occurrence — escalate to RFI or offboard depending on severity.
- **What I Learned:** Warnings create an evidence trail. When reviewing the RFI/warning history (Step 16) and CTM alerts (Step 8), check whether the user was previously warned about the SAME address or same type of exposure. If yes, the mitigation threshold is higher — the user cannot claim ignorance.
- **Lesson:** Check the CTM team's warning history (Binance Admin > Abnormal Chain Transactions) and the FCI warning history (HaoDesk RFI section) for prior warnings. If the user was previously warned and continues the same behavior: (1) this is an aggravating factor, (2) a simple warning is no longer appropriate — escalate to RFI or offboard depending on severity, (3) state in the ICR: "The user was previously warned on [date] regarding interaction with [address/entity type] and continued to interact despite the warning."
- **See also:** #14 (RFI mitigation test), #19 (unresponsive user with multiple red flags), #32 (gambling — licensed entity warning workflow)
---
### #32 — 2025-XX-XX — Gambling — Warning Before Offboard for Licensed Entities in Prohibited Jurisdictions
- **Case Ref:** N/A (Onboarding training session)
- **Scenario:** Trainer explained the standard gambling handling workflow for cases where a user in a gambling-prohibited jurisdiction (e.g., Dubai/UAE) interacts with a licensed gambling entity such as Stake.com, with Elliptic risk score 5 or above.
- **My Decision:** N/A
- **Outcome:** The standard workflow is: (1) issue a warning to the user advising them to refrain from future interaction with the gambling address, (2) if the user continues after the warning, offboard. Some MLROs in regulated jurisdictions take zero tolerance and may instruct immediate offboarding without warning — follow MLRO instructions when given (see #34). Otherwise, warning first is the default for licensed entities.
- **What I Learned:** Licensed gambling entities are treated differently from unlicensed ones. A licensed entity operating legally in some jurisdictions but not the user's jurisdiction triggers a warning-first approach. The user is given an opportunity to cease the activity before offboarding is pursued. For trivial gambling exposure on wallets scoring below 5, Rule #22 (proportionality) applies instead of this workflow.
- **Lesson:** Two-step gambling assessment: First check entity licensing status. Licensed + prohibited jurisdiction = warning first, offboard on repeat. Unlicensed = offboard directly (see #33). The warning should state that high-risk address interaction was identified and the user should refrain from future interactions.
- **See also:** #22 (trivial gambling exposure proportionality), #33 (unlicensed = offboard), #34 (MLRO approach varies), #31 (prior warning as aggravating factor)
---
### #33 — 2025-XX-XX — Gambling — Unlicensed Gambling Entity = Direct Offboard
- **Case Ref:** N/A (Onboarding training session)
- **Scenario:** Trainer distinguished between licensed and unlicensed gambling entities. For unlicensed entities, the approach is zero tolerance — offboard directly.
- **My Decision:** N/A
- **Outcome:** If the gambling entity is unlicensed (not a registered/licensed gambling operator in any jurisdiction), there is no warning step. The user is offboarded directly. The warning-first workflow (Rule #32) only applies to licensed entities.
- **What I Learned:** The critical first assessment for gambling cases is: (1) Is the gambling entity licensed? (2) Is gambling legal in the user's jurisdiction? If the entity is unlicensed, the answer to question 2 is irrelevant — offboard regardless. If the entity is licensed, proceed to the jurisdiction check and warning workflow.
- **Lesson:** Decision tree for gambling: Entity unlicensed → offboard directly, no warning. Entity licensed + user jurisdiction prohibits gambling → warning first, offboard on repeat (#32). Entity licensed + user jurisdiction allows gambling → retain (check proportionality per #22). Entity licensed + MLRO-regulated jurisdiction → follow MLRO instruction (#34).
- **See also:** #32 (licensed entity warning workflow), #22 (trivial exposure proportionality), #34 (MLRO varies)
---
### #34 — 2025-XX-XX — Gambling — MLRO Approach Varies by Jurisdiction for Gambling Cases
- **Case Ref:** N/A (Onboarding training session)
- **Scenario:** Trainer noted that MLROs in regulated jurisdictions have different approaches to gambling exposure — some take zero tolerance and instruct immediate offboarding, while others prefer a warning/RFI approach first.
- **My Decision:** N/A
- **Outcome:** No universal rule exists for MLRO-regulated jurisdictions — the investigator must follow the specific MLRO's instruction for the jurisdiction. When uncertain, escalate to the MLRO for direction.
- **What I Learned:** Gambling handling in regulated jurisdictions is MLRO-dependent. The investigator should not assume either zero tolerance or warning-first without checking or escalating. If the MLRO has previously communicated a standing instruction for gambling cases (e.g., "always offboard for gambling in my jurisdiction"), follow that standing instruction without re-asking.
- **Lesson:** For gambling cases in MLRO-regulated jurisdictions: escalate to the jurisdiction MLRO and follow their instruction. Do not assume a default approach — MLROs differ.
- **See also:** #32 (warning workflow default), #33 (unlicensed = always offboard)
---
### #35 — 2025-XX-XX — Elliptic — Gambling Fund Direction Assessment
- **Case Ref:** N/A (UAL Training Session — Nat, QC Team Lead)
- **Scenario:** Training discussed gambling exposure and the significance of fund direction. Two gambling case examples were presented: one user offboarded (heavy gambling, unresponsive), one retained with warning (some gambling exposure alongside normal trading activity).
- **My Decision:** N/A
- **Outcome:** Nat explained that the direction of funds relative to gambling platforms is a critical risk differentiator. Sending funds to gambling = spending money (expected behavior for a gambler, lower ML concern). Receiving funds from gambling = potential laundering indicator, because gambling platforms are normally net receivers of funds, not net payers.
- **What I Learned:** This is the gambling-specific version of Rule #29 (victim vs suspect direction assessment). A user depositing crypto to a gambling platform and losing it is engaging in gambling activity — compliance concern depends on jurisdiction. A user receiving significant funds from a gambling platform raises money laundering red flags because it suggests the gambling platform is being used to clean funds rather than for genuine gambling.
- **Lesson:** When gambling exposure is identified: (1) always check gambling-legality-matrix.md for the user's jurisdiction (mandatory per Rule #22), (2) assess the direction — funds TO gambling = lower ML risk, funds FROM gambling = higher ML risk, (3) receiving significant amounts from gambling platforms warrants deeper investigation as a potential laundering indicator regardless of jurisdiction legality.
- **See also:** #22 (trivial gambling proportionality), #29 (direction determines role — general principle)
---
### #36 — 2025-XX-XX — General — Retail Account Used for Corporate Funds
- **Case Ref:** N/A (UAL Training Session — Nat, QC Team Lead)
- **Scenario:** Training example showed a user with transaction patterns similar to a P2P merchant (deposits, trades, internal transfers, withdrawals). When asked via RFI about the activity, the user stated the account was used for business purposes but was registered as a retail individual account.
- **My Decision:** N/A
- **Outcome:** Nat confirmed: retail accounts cannot be used for corporate fund flows. Binance requires corporate accounts to go through separate KYB verification (shareholder identification, business background, etc.). The user should be directed to register a corporate account. Similar patterns on a verified merchant account with proper documentation resulted in a warning only — the pattern itself is not suspicious, but the account type matters.
- **What I Learned:** Transaction patterns that look identical can have completely different outcomes depending on the account type and the user's explanation. A P2P merchant with proper verification doing high-volume deposit-trade-transfer-withdraw cycles = normal business activity, warning at most. A retail user doing the same thing and admitting it's for business = compliance violation requiring corporate registration or offboarding.
- **Lesson:** When RFI response indicates business/corporate use of a retail account: (1) direct user to register corporate account with KYB, (2) if user cooperates and registers, close with warning, (3) if user refuses or cannot provide business documentation, offboard. Do not treat the transaction pattern as inherently suspicious — assess the account type against the stated purpose.
---
### #37 — 2025-XX-XX — RFI — Transaction Sampling Criteria
- **Case Ref:** N/A (RFI onboarding training session — Alan)
- **Scenario:** Trainee asked how to select which TXIDs to include in an RFI when there are many transactions with many counterparties.
- **My Decision:** N/A
- **Outcome:** Trainer confirmed: select the highest-value transactions relating to the specific flagged counterparty or high-risk address identified in the case. The connection between the RFI questions and the red flags in the report must be clear and direct. 3-5 transactions is the standard number; special scenarios may require more or fewer.
- **What I Learned:** Transaction sampling for RFIs is not random — it is driven by the identified risk. The highest-value transaction related to the flagged entity is prioritized because it represents the most significant exposure and is the most likely to elicit a meaningful response.
- **Lesson:** When sampling transactions for an RFI: (1) identify the specific counterparty or address that triggered the red flag, (2) select the highest-value transactions with that specific entity, (3) limit to 3-5 transactions unless the case requires more, (4) ensure every sampled transaction connects directly to a red flag stated in the report.
- **See also:** #14 (universal RFI mitigation test)
---
### #38 — 2025-XX-XX — Escalation — Sanctions Team: The "Remove the Address" Test
- **Case Ref:** N/A (Sanctions & SI Escalation Training Session)
- **Scenario:** Training scenario: French resident made withdrawals to an address linked to ISIS (financial terrorism, risk rating 10), with 64% of funds going to that address. User also had other red flags. Trainees chose to escalate to Sanctions team. Trainer corrected: offboard directly.
- **My Decision:** N/A
- **Outcome:** Trainer confirmed: when sanctions exposure exists alongside multiple independent red flags, apply the "remove the sanctions address" test. Ask: "If the sanctioned address were removed from the case, would there still be enough to offboard?" If yes, offboard directly without Sanctions team escalation. The Sanctions team is needed only when sanctions exposure is the sole or primary red flag and risk score is 6 or above.
- **What I Learned:** Sanctions team escalation is not automatic when a sanctioned entity is identified. The purpose of the Sanctions team is to provide a second opinion when the investigator does not have sufficient independent grounds to offboard. When the case already has enough independent red flags, the Sanctions team investigation would add delay without changing the outcome.
- **Lesson:** Before escalating to Sanctions team, apply the "remove the address" test: mentally remove the sanctions exposure from the case. If the remaining red flags are sufficient for offboarding, proceed directly. If sanctions is the only concern and risk ≥ 6, escalate. If risk < 6, close with normal review unless disproportionate volume justifies discretionary escalation.
- **See also:** #10 (cumulative risk), #14 (RFI mitigation test — similar "would it change the outcome?" logic)
---
### #39 — 2025-XX-XX — Elliptic — Sanctions Temporal Assessment (Pre-Sanctions, Active Sanctions, Post-Delisting)
- **Case Ref:** N/A (Sanctions & SI Escalation Training Session + Onboarding Training — Sanctions Escalation Examples)
- **Scenario:** Multiple training scenarios addressed timing of sanctions exposure: (1) KZ resident sent funds to Garantex in March 2022 (before April 2022 sanctions designation) — not a violation. (2) User received funds from Garantex in May 2022 (during active sanctions) — escalate. (3) User made withdrawals to Tornado Cash in October 2022 (during active OFAC sanctions) — escalate to Sanctions team even though sanctions were later uplifted. Tornado Cash post-delisting is a mixer, not sanctions-triggering.
- **My Decision:** N/A
- **Outcome:** Trainers confirmed: the relevant date is the transaction date relative to the sanctions period, not the current sanctions status. Elliptic may retroactively attribute risk scores to addresses that were not sanctioned at the time of the transaction.
- **What I Learned:** Three temporal data points must be checked: (1) transaction date, (2) sanctions designation date, (3) delisting date (if applicable). Pre-designation transactions are not violations. During-sanctions transactions are violations regardless of subsequent delisting. Post-delisting transactions may still be high-risk (mixer, obfuscation) but are not sanctions-triggering.
- **Lesson:** For every sanctions-flagged transaction: verify the designation and delisting dates. Pre-sanctions = normal review. During-sanctions = escalate regardless of current status. Post-delisting = standard high-risk exposure (not sanctions). The Elliptic risk score reflects current status, not historical status at the time of the transaction.
- **See also:** #4 (ambiguous high risk scores — look beyond the numerical score), #38 (remove the address test)
---
### #40 — 2025-XX-XX — General — Proportionality: Low-Value Counterparty With Post-Transaction LE Freeze
- **Case Ref:** N/A (Sanctions & SI Escalation Training Session)
- **Scenario:** Training scenario: Panama resident with normal account activity. In 2022, the user made two withdrawals totaling $245 to a counterparty. In March 2024, that counterparty received a frozen LE order related to financial terrorism. No other red flags on the account.
- **My Decision:** N/A
- **Outcome:** Trainer confirmed: proceed with normal review. Two mitigating factors: (1) $245 is an insignificant amount relative to overall account activity, (2) the LE freeze on the counterparty occurred approximately two years after the user's transactions.
- **What I Learned:** The same counterparty red flag (terrorism-related LE freeze) can be mitigated or not depending on the proportionality of the transaction amount and the temporal relationship between the user's transactions and the counterparty's LE event.
- **Lesson:** When a counterparty is flagged for sanctions/terrorism LE activity, assess: (1) what was the user's transaction volume with this counterparty vs total account volume? (2) when did the user's transactions occur relative to the LE event? Insignificant amounts + significant temporal distance = mitigable.
- **See also:** #22 (trivial gambling proportionality), #28 (multiple LE tickets — look beyond the surface flag)
---
### #41 — 2025-XX-XX — Escalation — BPay vs Bifinity Linkage Threshold
- **Case Ref:** N/A (MLRO Escalation Training Session)
- **Scenario:** Training clarified the different linkage standards for Bifinity vs BPay MLRO escalation.
- **My Decision:** N/A
- **Outcome:** Trainer confirmed: BPay escalation requires a DIRECT link between BPay fiat transactions and the suspicious activity. Bifinity requires only a potential or indirect link. The existing matrix for BPay says "Successful/Attempted" which may include rejected transactions — this is stricter on the type of fiat but looser on the linkage standard than initially assumed.
- **What I Learned:** The two fiat-channel MLRO escalation pathways have different evidentiary thresholds. Bifinity's threshold is lower (potential/indirect link sufficient), while BPay's threshold is higher (direct link required).
- **Lesson:** When assessing BPay escalation, the fiat must directly fund or directly result from the suspicious activity. Indirect chains (fiat → trading → crypto withdrawal to high-risk) are sufficient for Bifinity but NOT for BPay.
- **See also:** #3 (Bifinity temporal nexus), #42 (Bifinity entity tag insufficient)
---
### #42 — 2025-XX-XX — Escalation — Bifinity Entity Tag Alone Is Insufficient
- **Case Ref:** N/A (MLRO Escalation Training Session)
- **Scenario:** Trainee asked whether a Bifinity entity tag on an account without any successful UAB channel transactions still requires Bifinity MLRO escalation.
- **My Decision:** N/A
- **Outcome:** Trainer stated: "The matrix changed... We only look at whether or not there was successful UAB channels used after November 2021. That's the only determining factor." Additionally, the "supported country" column in the Bifinity UAB channel spreadsheet is irrelevant for escalation decisions.
- **What I Learned:** The old Bifinity escalation rule triggered on entity tag presence. The current rule is exclusively channel-based: only successful fiat transactions via UAB channels after November 2021 matter. The entity tag is informational but not determinative. The supported country column is operational/technical, not escalation-related.
- **Lesson:** When checking Bifinity escalation: (1) Check for successful UAB channel fiat transactions after November 2021. (2) If none exist, no Bifinity escalation regardless of entity tag. (3) Ignore the "supported country" column.
- **See also:** #3 (Bifinity temporal nexus), #41 (BPay vs Bifinity threshold)
---
### #43 — 2025-XX-XX — Escalation — MLRO Escalation Requires Matrix Category Match, Not Residence Alone
- **Case Ref:** N/A (Onboarding training — escalation example)
- **Scenario:** Training example: A French national residing in Poland was previously convicted of a violent crime (non-financial, non-ML related — an assault over a neighbour dispute). Transaction pattern showed fiat deposit via Bifinity, trading, and P2P withdrawal. User had a Bifinity tag. A trainee answered that the case should be escalated to the Poland MLRO because the user resides in Poland. The trainer and team manager corrected this.
- **My Decision:** N/A
- **Outcome:** No MLRO escalation was required. The crime was a violent offence unrelated to money laundering, sanctions, terrorism financing, or any other category on the MLRO escalation matrix for Poland. The trainer added that if the scenario had included unusual transaction activity, THEN escalation to the Poland MLRO would be required — because the case would then involve an escalation-triggering category.
- **What I Learned:** Two independent checks for MLRO escalation: (1) Is the user resident in a regulated jurisdiction? (2) Does the case TYPE/FINDING match a category in the MLRO escalation matrix for that jurisdiction? Both conditions must be met. Residence alone is necessary but not sufficient.
- **Lesson:** Before escalating to any MLRO, check the escalation matrix for the specific jurisdiction AND the specific case type. If the case finding does not match any row in the matrix, no escalation is required. This is particularly important for cases where non-financial criminal history is discovered during OSINT but no financial crime indicators are present on the account.
- **See also:** #3 (Bifinity temporal nexus)
---
### #44 — 2025-XX-XX — General — Dormant Account Alert Mitigated by Staking/Earn Activity
- **Case Ref:** N/A (FTM Onboarding Training Session)
- **Scenario:** Training scenario where a user deposited USDT, used funds for spot trading and then placed them in earn/staking products, logged off, and returned over a year later to withdraw. The dormant account alert was triggered upon reactivation.
- **My Decision:** N/A
- **Outcome:** Trainer confirmed this is mitigable by referencing the investment activity during the dormant period. The User Asset Log (UAL) should be checked for staking/earn entries, which are not visible in C360 transaction data.
- **What I Learned:** Dormant account alerts trigger based on inactivity (no deposits, withdrawals, or spot trades for approximately one year or more). However, funds held in staking or earn products do not generate trading activity, so the account appears dormant while the user is actively invested. The mitigation requires checking the UAL to confirm earn/staking activity during the dormant period.
- **Lesson:** For dormant account alerts: (1) check the User Asset Log for staking/earn/lending activity during the dormant period, (2) if funds were held in investment products, state this as mitigation: "The dormancy is consistent with the user holding funds in earn/staking products during the inactive period," (3) the alert alone, without additional risk indicators, does not warrant escalation. This complements the existing C360 DATA GAP note in Step 7.
- **See also:** #26 (API trading as mitigation for SAWD — similar principle of legitimate activity triggering alerts)
---
### #45 — 2025-XX-XX — General — Block Classification QC Impact
- **Case Ref:** N/A (Block & Unblock Training Session — Alan)
- **Scenario:** Training clarified the QC scoring impact of incorrectly classifying blocks when applying them in Block & Unblock 360.
- **My Decision:** N/A
- **Outcome:** QC confirmed: selecting Unjustified when the block should be Justified (or vice versa) is a valid QC finding with material deduction. Selecting Preventive when it should be Justified (or vice versa) is an Observation — still a deduction but minor.
- **What I Learned:** The block classification has real QC impact. The safest approach is to select Justified when there is clear evidence supporting the restriction. Preventive is appropriate for temporary, risk-based restrictions pending investigation.
- **Lesson:** When applying a block: (1) verified violations or significant risk with clear evidence → Justified. (2) Temporary restriction based on potential risk pending investigation → Preventive. (3) Incorrect choice between Justified and Unjustified = material QC finding. Incorrect choice between Justified and Preventive = minor observation.
---
### #46 — 2025-XX-XX — Offboarding — WOM Exception for LE Seizures
- **Case Ref:** N/A (Block & Unblock Training Session — Alan, Omer)
- **Scenario:** Trainee noted some historical offboarding cases did not have withdrawals allowed.
- **My Decision:** N/A
- **Outcome:** Standard FCI process requires WOM for all offboarding submissions. Exceptions exist only for: (1) LE seizure/freeze cases where the account is under active seizure, (2) explicit requests from Special Investigations or Sanctions teams to block withdrawals. When WOM cannot be applied, the investigator must determine the reason, document it, and attach correspondence from the relevant team.
- **What I Learned:** WOM is not optional for offboarding — it is a QC-checked requirement. The exception is narrow and must be documented.
- **Lesson:** For every offboarding submission: (1) Apply WOM as standard. (2) If WOM cannot be applied, investigate why. (3) Obtain and screenshot correspondence from the blocking team. (4) Attach to case file. (5) Absence of WOM without documented justification = QC finding.
- **See also:** #1 (offboarding reason selection)
---
### #47 — 2025-XX-XX — RFI — Unjustified RFIs as Decision Avoidance (Management Priority)
- **Case Ref:** N/A (QC Onboarding Training Session)
- **Scenario:** QC team lead explained that management has specifically flagged excessive RFI sending as a departmental problem. The pattern identified is investigators sending RFIs not because of a genuine information gap, but because they are unwilling to make the retain or offboard decision independently, effectively passing the decision to the RFI team.
- **My Decision:** N/A
- **Outcome:** QC confirmed this is a severe auto-fail (consistent with qc-submission-checklist.md #4.2). The specific behavioral pattern flagged is: investigator identifies risks, cannot fully mitigate them, but instead of recommending offboard or providing a clear retain rationale, sends an RFI as a "safe" middle ground. This is identifiable when the RFI justification section lacks specific explanation of what information gap the RFI addresses and how the response would change the outcome.
- **What I Learned:** The RFI justification within the ICR (Step 18 template) is not a formality — QC specifically reads it to determine whether the RFI was genuinely necessary. An RFI without clear justification is worse than no RFI at all, because it creates a severe auto-fail (-25) rather than the material finding (-10) that would result from not sending an RFI when one was needed (#4.1). The asymmetry of penalties reflects management's priority to reduce unnecessary RFIs.
- **Lesson:** Before sending any RFI, the investigator must be able to articulate: (1) what specific information gap exists, (2) why available data cannot resolve it, and (3) how a satisfactory response would change the case outcome. If these three questions cannot be answered clearly, the RFI is likely unnecessary and the investigator should make the decision directly.
- **See also:** #14 (universal RFI mitigation test), #20 (three-tier decision framework)
---
### #48 — 2026-02-XX — RFI — Uncooperative vs Unresponsive: Different Block Reasons and Timelines
- **Case Ref:** N/A (RFI & Block/Unblock Training Sessions — Alan, Omer)
- **Scenario:** Training distinguished between two categories of users who fail to satisfy RFI requirements: (1) unresponsive users who do not reply at all after the standard 14-day grace period and 3 reminders, and (2) uncooperative users who reply but provide evasive, insufficient, or irrelevant information despite multiple attempts (initial RFI + two re-triggers).
- **My Decision:** N/A
- **Outcome:** Trainers confirmed these are distinct categories with different procedural handling. Unresponsive users receive WOM under block reason "RFI - SAR Investigation" after 14 days + 3 reminders, with the "Unresponsive User" tag applied. Uncooperative users — those who reply but fail to provide adequate information after three attempts (initial RFI + two re-triggers) — receive WOM under block reason "RFI - Others" with "Uncooperative user" noted in the status. The offboarding consideration timeline also differs: unresponsive users follow the standard 14-day block SLA, while uncooperative users are given approximately 60 days from WOM application before offboarding is considered, reflecting that these users are engaging with the process (just inadequately).
- **What I Learned:** The distinction matters for QC, block classification, and case timeline. Using the wrong block reason or tag creates a QC finding. The uncooperative pathway acknowledges that the user is attempting to engage and provides a longer runway before the offboarding decision, while the unresponsive pathway is more straightforward because the user has chosen not to participate at all.
- **Lesson:** Unresponsive (no reply after 14 days + 3 reminders): WOM under "RFI - SAR Investigation" + "Unresponsive User" tag. Uncooperative (replies but insufficient after 3 attempts): WOM under "RFI - Others" + "Uncooperative user" status. Do not conflate the two. Different block reasons, different tags, different timelines. Before classifying a user as uncooperative, ensure three genuine attempts were made (initial RFI + two re-triggers with progressively more specific questions).
- **See also:** #14 (universal RFI mitigation test), #19 (unresponsive user with multiple red flags — lean toward offboard), #47 (unjustified RFIs)
---
### #49 — 2026-02-XX — Offboarding — Offboarding Reason Must Match Across ICR, User Investigation Tab, and Submission
- **Case Ref:** N/A (Offboarding Training Session / QC Onboarding)
- **Scenario:** Training highlighted a recurring QC finding where the offboarding reason stated in the ICR conclusion (Step 21) did not match the dropdown selection in the User Investigation tab (Step 22), or either did not match the reason submitted in the Binance Admin offboarding request. This three-way mismatch creates confusion for the offboarding team and is a QC-scored item.
- **My Decision:** N/A
- **Outcome:** QC confirmed: the offboarding reason must be identical across all three locations — (1) the ICR conclusion text (Step 21), (2) the User Investigation tab dropdown (Step 22), and (3) the Binance Admin offboarding submission form. Mismatches between any two of these three are a QC finding. The offboarding team may reject submissions where the reason code does not align with the case narrative.
- **What I Learned:** The offboarding reason is a controlled field that drives downstream processing (reporting, analytics, regulatory filings). Inconsistency undermines the integrity of the offboarding record. The most common error is updating the ICR conclusion but forgetting to change the User Investigation tab dropdown, or vice versa.
- **Lesson:** Before submitting any offboarding case, verify all three locations contain the same reason: (1) ICR conclusion paragraph, (2) User Investigation tab dropdown, (3) Binance Admin offboarding submission. A final cross-check before clicking Submit prevents this common QC finding.
- **See also:** #1 (offboarding reason selection — which reason to choose), #46 (WOM requirement for offboarding)
---
### #50 — 2026-02-XX — Offboarding — Offboarding Appeals Must Apply Current Compliance Standards
- **Case Ref:** N/A (Offboarding Appeals Training / QC Guidance)
- **Scenario:** Discussion about how to handle offboarding appeals where the original offboarding decision was made under previous compliance standards or risk appetite thresholds. The question arose whether the appeal should be assessed against the standards that existed at the time of the original decision or against the current standards.
- **My Decision:** N/A
- **Outcome:** The re-evaluation must apply the current compliance standard, not the historical standard at the time of the original offboarding. Compliance policies, risk appetite, and escalation thresholds evolve over time. An offboarding that was correct under previous standards may no longer be warranted under current standards — and vice versa. The appeal is a fresh assessment using today's framework.
- **What I Learned:** Offboarding appeals are not simply a question of "was the original decision correct at the time?" They are a forward-looking assessment: "Based on current compliance standards and available information, should this user remain offboarded?" This means cases offboarded years ago under stricter or more lenient standards may have different outcomes when re-evaluated today.
- **Lesson:** When reviewing an offboarding appeal: (1) apply the current compliance standard and risk appetite, not the historical standard, (2) re-examine the original red flags against current thresholds and decision-matrix.md rules, (3) check whether new information or RFI responses have been provided since the original decision, (4) if the original decision would not be made under current standards, reversal may be appropriate (subject to MLRO approval per the appeals process in icr-steps-post.md Appendix D).
- **See also:** #17 (L3/MLRO safety net — applies to appeal reversals too), #15 (balanced narrative approach)
---
### #51 — 2026-02-XX — Escalation — Dual Escalation: Only Country MLRO Approval Gates Offboarding
- **Case Ref:** N/A (MLRO Escalation Training / Operational Guidance)
- **Scenario:** In dual-escalation jurisdictions (e.g., India, Mexico, Colombia, Brazil, BPay, Bifinity), both ADGM/Country MLRO and fiat-channel MLRO are notified. The question arose which MLRO's approval is required to proceed with offboarding — and whether both must approve before the offboarding request can be submitted.
- **My Decision:** N/A
- **Outcome:** Only the Country MLRO approval is required to proceed with offboarding. The Bifinity or BPay MLRO is escalated for information and potential reporting purposes (they may need to file a SAR/STR for their own regulatory obligations), but their approval is not a gating requirement for the offboarding submission. The investigator should not wait for Bifinity/BPay MLRO response before proceeding with the offboarding once Country MLRO approval is obtained.
- **What I Learned:** Dual escalation serves different purposes for different MLROs. The Country MLRO is the decision-maker for user-level actions (retain/offboard/report). The fiat-channel MLRO (Bifinity/BPay) is informed because the fiat channel creates a separate regulatory nexus that may require independent reporting — but they do not gate the operational decision. Waiting for both approvals creates unnecessary delay.
- **Lesson:** In dual-escalation cases: (1) escalate to both MLROs as required by the matrix, (2) proceed with offboarding upon Country MLRO approval, (3) do not wait for Bifinity/BPay MLRO response to submit the offboarding request. If the fiat-channel MLRO subsequently provides instructions (e.g., additional reporting, specific block requirements), these can be actioned after the offboarding is already in progress.
- **See also:** #3 (Bifinity temporal nexus), #41 (BPay vs Bifinity linkage threshold), #42 (Bifinity entity tag alone insufficient)
---
### #52 — 2026-02-XX — Corporate — Corporate Account with VIP Status: Cumulative Approval Requirements
- **Case Ref:** N/A (Offboarding / VIP Notification Training)
- **Scenario:** Training addressed the scenario where a corporate account also holds VIP status (e.g., a high-volume OTC broker that qualifies for VIP tier based on trading volume). The question was whether corporate approval requirements and VIP notification requirements apply independently or whether one subsumes the other.
- **My Decision:** N/A
- **Outcome:** The two approval pathways are cumulative, not alternative. Corporate accounts require corporate-specific approvals (TL + Manager for corporate entities). VIP accounts require VIP-specific notifications and approvals per the VIP tier (see icr-steps-post.md Step 22 VIP Notification Rules). When an account is both corporate AND VIP, both sets of requirements must be satisfied. The same principle applies to any overlapping account categories (e.g., KOL + VIP, HPI + Corporate).
- **What I Learned:** Account categories are additive for approval purposes. The highest tier of each applicable category determines the approval requirement. A VIP3 corporate account requires corporate approvals AND VIP3-level notification to Jonathan Bracken (if no POC). Missing either pathway is a QC finding.
- **Lesson:** When an account has multiple categories (Corporate + VIP, Merchant + VIP, KOL + Corporate, etc.): (1) identify ALL applicable categories, (2) determine the approval requirements for EACH category independently, (3) satisfy ALL requirements before submitting the offboarding. The approval matrix rows are cumulative — they do not replace each other.
- **See also:** #13 (VIP/corporate offboarding threshold), #46 (WOM requirement)
---
### #53 — 2026-02-XX — Offboarding — Appeal Reversal in Non-Licensed Jurisdiction: Approval Pathway
- **Case Ref:** N/A (Offboarding Appeals Training)
- **Scenario:** Discussion about the approval pathway for reversing an offboarding decision when the user is in a non-licensed jurisdiction (no local MLRO) and the original offboarding did not require MLRO escalation or special approvals beyond the standard L2/L3 process.
- **My Decision:** N/A
- **Outcome:** If the original offboarding followed the standard pathway without additional approvals (no MLRO escalation required, no special VIP/corporate approvals), and the re-evaluation confirms that the user's risk profile is within current FCMI risk appetite, the reversal may proceed without additional approvals beyond the standard process. However, MLRO approval is always required for offboarding reversals — even in non-regulated jurisdictions — per icr-steps-post.md Appendix D. For high-value accounts (VIP, corporate), TL/Manager approval is additionally required regardless of jurisdiction.
- **What I Learned:** The reversal pathway mirrors the original decision pathway but with one addition: MLRO approval is always required for reversals, even when the original offboarding did not require MLRO escalation. This asymmetry exists because reversals carry additional reputational and compliance risk — re-onboarding a previously offboarded user requires a higher level of sign-off than the original offboarding did.
- **Lesson:** For offboarding appeal reversals: (1) MLRO approval is always mandatory regardless of jurisdiction, (2) if the account is VIP or corporate, TL/Manager approval is additionally required, (3) the approval pathway for the reversal is at least as stringent as the original offboarding pathway, never less. Consult the offboarding appeals MLRO matrix on Confluence for the specific regional MLRO.
- **See also:** #50 (apply current standards to appeals), #17 (L3/MLRO safety net)
---
### #54 — 2026-02-XX — General — Binance Internal Clearing Accounts as Counterparties
- **Case Ref:** N/A (Counterparty Analysis Training / Operational Guidance)
- **Scenario:** During counterparty analysis, certain UIDs identified as high-volume counterparties were found to be Binance internal clearing accounts (e.g., crypto_box clearing accounts, P2P clearing/escrow accounts, system operational accounts used for platform-level fund movements). These accounts may show extensive LE ticket history, ICR cases, and block records — but these reflect aggregate platform operations across thousands of users, not the individual counterparty relationship with the subject.
- **My Decision:** N/A
- **Outcome:** Binance internal clearing accounts process transactions for the entire platform user base. Their LE ticket history, ICR count, and alert records reflect the volume and diversity of all users transacting through them — not a risk indicator specific to the subject's relationship with that counterparty. Treating a clearing account's LE history as a risk factor for the subject is analytically incorrect and creates a false mitigation obligation.
- **What I Learned:** Not all counterparties are external third parties. Internal clearing and escrow accounts are platform infrastructure. Their risk profiles reflect platform-level operations and should not be attributed to individual users who transact through them. The investigator should identify these accounts (often recognizable by system-generated email addresses, high transaction counts in the millions, or "Binance" in the account name) and treat them as neutral platform infrastructure.
- **Lesson:** When a counterparty is identified as a Binance internal clearing or escrow account: (1) state this in the counterparty analysis: "UID [X] is a Binance internal clearing account. LE tickets and ICR history on this account reflect aggregate platform operations and are not attributable to the subject's individual transaction relationship," (2) do not deep-dive into the clearing account's individual LE tickets or ICR history, (3) do not include the clearing account's risk profile in the overall counterparty risk assessment for the subject.
- **See also:** #28 (multiple LE tickets may represent single investigation — similar principle of looking beyond surface-level counts)
---
### #55 — 2026-02-XX — General — Proportional Counterparty Review: Low-Volume Offboarded Counterparty May Be Omitted
- **Case Ref:** N/A (QC Guidance / Counterparty Analysis Training)
- **Scenario:** Discussion about whether every offboarded counterparty must receive individual mention in the counterparty analysis, even when the transaction volume with that counterparty is negligible (e.g., less than $5) and higher-risk counterparties with significant volume exist.
- **My Decision:** N/A
- **Outcome:** QC confirmed that proportional review is acceptable. When multiple counterparties are present and the investigator has thoroughly reviewed the highest-risk and highest-volume counterparties, omitting individual mention of an offboarded counterparty with bare minimum transaction volume (e.g., <$5, likely dusting or spam) is not a QC finding — provided the high-risk counterparties have been properly analyzed. The principle is proportionality: investigator time and report space should be allocated to the counterparties that matter most to the risk assessment.
- **What I Learned:** Not every offboarded counterparty is equally significant. A counterparty offboarded for "Suspicious Transaction Activities" with whom the subject transacted $0.50 is materially different from a counterparty offboarded for the same reason with whom the subject transacted $50,000. QC expects thorough review of the significant counterparties — not exhaustive mention of every flagged UID regardless of volume.
- **Lesson:** When reviewing counterparties: (1) always prioritize the highest-risk and highest-volume counterparties for detailed analysis, (2) offboarded counterparties with negligible transaction volume (<$5) may be omitted from individual mention if higher-priority counterparties have been thoroughly reviewed, (3) this proportionality does NOT apply in reverse — omitting a high-volume offboarded counterparty while reviewing only low-risk counterparties is a QC finding. The analytical effort must match the risk significance.
- **See also:** #22 (trivial gambling proportionality — same principle applied to counterparties), #40 (low-value counterparty with post-transaction LE freeze)
---
### #56 — 2026-02-XX — LE — LE Risk Weight Depends on Specificity of Targeting
- **Case Ref:** ICRV20260225-00529
- **Scenario:** Subject had 3 Dutch LE data requests. In each, the subject was one of many targeted UIDs. No freeze, seizure, or confiscation was requested or imposed. No specific transactions were attributed to the subject. The requests were broad-scope data collection across multiple accounts and jurisdictions.
- **My Decision:** Initially assessed the LE profile as unmitigable and contributing to an offboard recommendation.
- **Outcome:** Recalibrated. The LE cases lacked specificity — the subject was not individually named, not the sole target, and no enforcement action was directed at the subject. Broad data requests across many UIDs are standard LE procedure and do not indicate the subject is individually suspected.
- **What I Learned:** LE risk weight is determined by specificity of targeting, not by the existence of LE cases. Mass data sweeps with no freeze, seizure, confiscation, or individual attribution carry no independent risk weight. Only LE cases where the subject is specifically and individually targeted (sole target, freeze/seizure, specific transaction attribution, individually named in connection with criminal activity) carry independent weight toward an offboard or RFI decision.
- **Lesson:** Before assigning risk weight to any LE case, assess specificity using the LE Risk Weight Assessment framework at Step 6. Low-specificity cases are mitigated by stating the lack of individual targeting. High-specificity cases require substantive analysis and carry independent decision weight.
- **See also:** #28 (count distinct investigations — complementary to this rule), #58 (collection of red flags required)
---
### #57 — 2026-02-XX — General — Pass-Through Ratio Does Not Independently Warrant Action
- **Case Ref:** ICRV20260225-00529
- **Scenario:** Account showed a 99.75% outbound-to-inbound ratio with no trading, no fiat, and no earn activity. This was initially treated as a near-automatic offboarding trigger.
- **My Decision:** Initially moved toward offboard based heavily on the pass-through pattern.
- **Outcome:** Recalibrated. Pass-through ratio on its own does not independently support offboarding or RFI. It is an indicator that gains or loses significance depending on what accompanies it. When verified against the UOL and assessed alongside other indicators that were individually mitigated, the pass-through pattern alone was insufficient.
- **What I Learned:** Pass-through is a descriptive metric, not a decision endpoint. Many legitimate use cases produce high pass-through ratios (arbitrage, cross-exchange rebalancing, cross-chain bridging, OTC operations). The ratio must be verified against the UOL to understand what actually occurred, and it only becomes significant when combined with additional unmitigated red flags forming a convergent pattern.
- **Lesson:** Do not treat pass-through as independently actionable. Verify via UOL. Assess in combination with other indicators. If pass-through is the only remaining finding after other risks are mitigated, retain. Full guidance at Step 7.
- **See also:** #58 (collection of red flags required), #26 (API trading mitigates SAWD alerts — related pattern explanation)
---
### #58 — 2026-02-XX — General — No Single Indicator Sufficient — Collection Required
- **Case Ref:** ICRV20260225-00529
- **Scenario:** The case initially presented multiple apparent red flags: 99.75% pass-through, 3 LE cases, rapid fund movement, high-risk Elliptic address (FixedFloat 10/10). Each was assessed as contributing to an offboard recommendation. When each indicator was verified against primary data sources (UOL, Kodex details, Elliptic detail), each was individually mitigated: LE cases were low-specificity mass data sweeps, pass-through was the sole transaction indicator with no corroborating factors, and the FixedFloat address did not appear in the UOL as a direct transaction.
- **My Decision:** Moved from offboard → RFI → retain as each indicator was verified and found individually mitigable.
- **Outcome:** Final recommendation was retain. No collection of unmitigated red flags remained after verification.
- **What I Learned:** The AI was treating each indicator as independently carrying significant weight, stacking them into an apparently strong case for offboarding. In reality, each dissolved upon verification against primary data. The correct approach is: verify each indicator individually against primary sources, then assess whether a collection of verified, unmitigated indicators remains. If not, retain. Identity-based offboarding (Rule #8) and unlicensed gambling (Rule #33) are exceptions — these are categorical determinations, not transactional indicators subject to this verification process.
- **Lesson:** Offboarding requires a convergence of unmitigated red flags — not a stack of individually mitigable indicators. Verify every indicator against primary data before counting it. Operates alongside Rule #10 (pattern assessment) — a coherent behavioral pattern across individually mitigable indicators may itself be unmitigable, but the verification step comes first.
- **See also:** #10 (multiple independent risk factors), #20 (three-tier framework), #14/60 (RFI threshold)
---
### #59 — 2026-02-XX — Elliptic — Verify High-Risk Addresses Against UOL When Data Available
- **Case Ref:** ICRV20260225-00529
- **Scenario:** Elliptic screening returned FixedFloat at 10/10 in the top 10 addresses by value. This was initially treated as a significant unmitigated risk factor. Upon checking the UOL, zero direct transactions with FixedFloat were found — the address appeared in aggregated Elliptic data due to indirect exposure through intermediary wallets.
- **My Decision:** Initially included FixedFloat as a major risk factor supporting offboard recommendation.
- **Outcome:** Recalibrated. The exposure was indirect and not confirmed by direct transaction evidence. Mitigated by stating the distinction between direct and indirect exposure.
- **What I Learned:** Elliptic top 10 by value and exposed addresses are derived from blockchain tracing algorithms that follow fund flows through multiple hops. An entity appearing in these lists does not mean the user directly transacted with that entity. The UOL shows actual direct counterparties. If a high-risk entity does not appear in the UOL, the exposure is indirect and carries significantly less risk weight. Currently, UOL cross-reference data may be provided by the web app — when available, it should be used. When not available, standard Elliptic analysis applies without this additional mitigation layer.
- **Lesson:** When UOL cross-reference data is available, use it to distinguish direct from indirect exposure. Indirect exposure alone is generally mitigable. This is an advisory step, not a mandatory gate — its availability depends on the web app output or manual UOL review. Full procedure at Steps 9/10.
- **See also:** #4 (VASP regulatory risk mitigation — related proportionality principle), #11 (do not report low-risk triggered rules)
---
### #60 — 2026-02-XX — RFI — Strict Four-Part Threshold for Sending RFIs
- **Case Ref:** ICRV20260225-00529
- **Scenario:** After offboarding was ruled out (all indicators individually mitigated), the AI recommended sending an RFI as a middle-ground action. However, no specific unmitigable risk remained that a user response could address — the RFI would have been a procedural step without a clear investigative purpose.
- **My Decision:** Initially considered RFI after ruling out offboard.
- **Outcome:** RFI ruled out. No specific risk existed that the user could mitigate through a response. All risks had been mitigated through available data. Sending an RFI would have created user friction and backlog without changing the outcome.
- **What I Learned:** RFI is not a fallback when offboarding is ruled out. It is a specific tool for a specific situation: when a genuine information gap exists that only the user can fill, and filling it would change the decision. The four conditions must all be satisfied: (1) specific unmitigable risk exists, (2) user response could realistically fully mitigate it, (3) no other way to mitigate, (4) risk would otherwise require offboarding. If any condition fails, the RFI is not justified.
- **Lesson:** Apply the four-part test at Rule #60 before every RFI. Default position is mitigate with available data and retain. Management direction is to minimise RFIs — unjustified RFIs are a severe auto-fail (Rule #47, QC #4.2). This does not override QC #4.1 — genuinely required RFIs must still be sent.
- **See also:** #47 (unjustified RFIs as decision avoidance), #20 (three-tier framework), #14 [SUPERSEDED by #60]
---
### #61 — 2026-02-XX — Corporate — VIP Accounts Receive Enhanced Retention Effort
- **Case Ref:** General operational guidance from senior management discussion.
- **Scenario:** Senior management indicated that VIP-tagged accounts are given greater leeway in practice. The exchange is reluctant to offboard high-value users and risk indicators on VIP accounts tend to be mitigated more robustly than on standard accounts. This is not formally documented in SOPs but is an observed and acknowledged operational reality.
- **My Decision:** N/A — operational guidance received.
- **Outcome:** For VIP accounts, the practical threshold for offboarding is higher than for standard accounts. The investigator is expected to exhaust all available mitigations — primary data verification, proportionality arguments, business profile consistency, and RFI where it meets the Rule #60 threshold — before recommending offboarding. Risk indicators that might support offboarding a standard account may be mitigated for VIP accounts through the combination of business context, transaction volume proportionality, and declared profile consistency.
- **What I Learned:** The exchange has a commercial interest in retaining VIP users and this is reflected in the operational approach to compliance investigations. This does not mean VIP users are immune from offboarding — identity-based cases (Rule #8), unlicensed gambling (Rule #33), and cases where verified unmitigated red flags form an undeniable pattern still result in offboarding regardless of VIP status. What it means is that the investigator should work harder to mitigate risk for VIP accounts before concluding that offboarding is the only option.
- **Lesson:** For VIP-tagged accounts: (1) verify every risk indicator against primary data, (2) apply all proportionality arguments, (3) assess business profile consistency, (4) consider RFI per Rule #60 before offboarding. The enhanced effort is in the mitigation, not in ignoring risk. Rules #8 and #33 are not overridden by VIP status. Strengthens Rule #13 (send RFI first for VIP/corporate). See also OL-6 (offboarding threshold).
- **See also:** #13 (VIP/corporate RFI first), #58 (collection of red flags required), #60 (RFI threshold)
---
### #62 — 2026-03-XX — Fraud — Co-Suspect Counterparty in Same Fraud Referral
- **Case Ref:** ICRV20260210-00987
- **Scenario:** L1 SSO referral identified two suspects in an off-site P2P fraud scheme. Suspect 1 (UID 1164702478) and Suspect 2 (UID 781128002) shared device identifiers and were implicated in coordinated evidence fabrication. The internal counterparty section noted only $4.46 USD in transfers between them and concluded "no significant internal counterparty network identified" and "internal counterparty exposure is minimal" because the scam occurred off-site via Solana. Active blocks were cited as mitigating further risk.
- **QC Finding:** Three errors in the counterparty analysis: (1) UID 781128002 was Suspect 2 per L1 but was treated as a low-risk counterparty due to low dollar volume, (2) the off-site nature of the scam was used to justify "minimal internal exposure" — a faulty causal chain since the internal counterparty relationship exists independently of where the scam transactions occurred, (3) active blocks were used as a counterparty risk mitigation — blocks are operational controls that prevent future activity but do not retroactively reduce the risk significance of an existing co-suspect relationship.
- **Correct Approach:** The counterparty entry for UID 781128002 should have stated: "UID 781128002 is identified as Suspect 2 in the L1 referral, is implicated in the same fraud scheme, and shares device identifiers with the subject. The counterparty relationship is directly connected to the fraudulent activity under investigation and constitutes an aggravating factor supporting offboarding." The dollar volume ($4.46) should have been noted but not used as the basis for risk assessment — the nature of the relationship, not the transaction amount, determines the risk significance.
- **Lesson:** In fraud/scam cases, always cross-reference internal counterparties against UIDs named as suspects in the L1 referral. A co-suspect counterparty is a critical finding regardless of transaction volume. Do not mitigate co-suspect counterparty risk by citing (a) off-site transaction channels, or (b) active account blocks. Both are analytically irrelevant to the counterparty relationship finding.
---
