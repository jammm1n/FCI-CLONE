# Proposal (One-Pager): AI-Assisted Investigation Platform for Level 2 FCI

**Owner:** Tom Turrell / FCI Level 2
**Audience:** James Spaans, Mike Whelan
**Decision Needed:** Approve continued development of the AI-assisted investigation platform with dedicated developer time and a phased pilot timeline for Level 2 FCI.

---

## 1) Problem

Level 2 FCI investigators are expected to handle 10 cases per day. Realistically we're completing around 6, with each case taking anywhere from 20 minutes for a straightforward case handled by an experienced investigator, up to well over an hour for anything more complex or for less experienced team members.

The bottleneck is not the investigation itself. It's everything that has to happen before the investigator can start thinking about the case. Every case requires pulling data from five or six different systems (HauDesk, Binance Admin, C360, Kodex, Elliptic, L1 chat history), reading through all of it, holding the relevant details in your head, and then working through the case template section by section. There is no single view of the case. The investigator has to build that picture themselves, every time.

The pressure to work faster has a predictable side effect. Investigators take shortcuts because they have to. Common ones include copying and pasting narratives from previous cases, reusing boilerplate paragraphs across different risk profiles, and relying on generic wording rather than bespoke analysis. This is completely understandable given the volume expectations, but it creates real risk: copy-paste errors where details from one case bleed into another, generic-sounding investigations that don't reflect the specifics of the case in question, and inconsistency in how SOPs and QC standards are applied from one investigator to the next.

There is also a significant experience dependency. An investigator who has been on the team for a year or two knows exactly which parts of the data to focus on, which risk indicators matter for each case type, and which sections of the template they can move through quickly. They can assess a simple case in 20 minutes. A new starter looking at the same case doesn't have that instinct. They don't know what they can safely skip, so they have to look at everything, and the same case can take them well over an hour. It takes months for new investigators to build up the pattern recognition and system familiarity that experienced team members have. When experienced people leave, the team's throughput drops until their replacements get up to speed, and the cycle repeats.

---

## 2) Objective

Reduce average case completion time to 15 to 20 minutes per case and level out the experience gap across the team by:

- Automating the data gathering and preprocessing so investigators start with a complete, structured case file rather than raw data spread across multiple systems.
- Providing AI-assisted investigation guidance that follows the team's SOPs, decision matrix, and QC standards on every case, every time. A new starter working through the platform gets the benefit of the team's accumulated knowledge and methodology from day one.
- Generating fresh, case-specific analysis from the actual data rather than recycled narratives, eliminating copy-paste risk entirely.
- Giving investigators a single interface for the full workflow: data, analysis, and case form output in one place.
- Keeping the investigator in control throughout. The AI does the heavy lifting on data processing, cross-referencing, and drafting. The human evaluates the risk, applies their experience and judgment, and makes the final decision.

The platform is designed to be template-agnostic. It can produce output in any case file structure and can be adapted as reporting requirements evolve. The investigation engine, the data pipelines, the knowledge base, and the AI methodology all remain the same regardless of what the output format looks like. If the template changes, we update the instructions and output format. The platform itself doesn't need to be rebuilt.

---

## 3) Proposed Change

Replace the current multi-tool workflow with a standalone AI investigation platform built specifically for Level 2 FCI casework.

### A. What Has Been Built (Working Prototype)

A functional prototype is complete and ready for demonstration. It includes:

- A custom investigation dashboard with case data and AI chat side by side, replacing the generic SAFU GPT interface.
- An AI investigation assistant powered by Anthropic Claude, with a knowledge base of 19 documents covering all SOPs, the decision matrix, QC checklist, escalation rules, and step-by-step case form guides.
- Intelligent document retrieval: the AI consults reference documents on demand based on the case context, with a clear record of which documents informed each response.
- Pre-staged case data so investigators open a case and immediately see preprocessed data (counterparty analysis, wallet screening, KYC, prior investigations) without any manual collection.
- Image support: investigators can paste or upload screenshots (KYC documents, Kodex records) directly into the chat for AI analysis.
- Streaming AI responses for a responsive investigation experience.
- PDF transcript export for record-keeping.

### B. Phased Roadmap

| Phase | What Gets Delivered | Timeline | Dependencies |
|-------|-------------------|----------|--------------|
| **Phase 1** | Working prototype with pre-staged demo cases. Ready for demonstration. | Complete | SafuAPI Anthropic key needed for deployment inside Binance network |
| **Phase 2** | Data ingestion portal. Investigators upload C360 spreadsheets, LE PDFs, Hexa text dumps, and other case materials into the platform. The backend processes and assembles the case file automatically. Locally deployed. | 2-3 weeks | SafuAPI key, Elliptic API key |
| **Phase 3** | Deploy to shared infrastructure so other investigators can access it. | Depends on IT and infrastructure support | VM provisioning, MongoDB setup, network access |
| **Phase 4** | Controlled pilot with 2-3 investigators on real cases. Measure throughput, QC pass rates, and gather feedback. | 2-4 weeks after deployment | Investigator availability, management oversight |
| **Long term** | Full automation. Most data pipelines feeding into the platform automatically, removing the need for manual data collection altogether. Manual input only for systems without API access (e.g. Kodex). | ~6 month horizon | API access to internal systems |

The C360 spreadsheet processing pipeline and Elliptic API integration code already exist as working software built during the current workflow. Phase 2 is primarily about incorporating these into the platform front end and building the additional ingestion capabilities (LE PDF extraction, Hexa text parsing).

---

## 4) Before vs After (Leadership View)

| Dimension | Current Workflow | With the Platform |
|-----------|-----------------|-------------------|
| **Time per case** | 20 min (experienced, simple case) to 60-90 min (complex or less experienced) | Target: 15-20 minutes consistently across all investigators |
| **Case throughput** | ~6 cases/day per investigator | Target: 10+ cases/day |
| **Data gathering** | Manual, 15-20 min across 5-6 systems per case | Automated. Case data structured and ready when the investigator opens the case |
| **Investigation consistency** | Varies by experience, SOP familiarity, and individual approach | AI follows the same methodology, SOPs, and QC standards on every case |
| **Copy-paste risk** | Common. Recycled narratives, boilerplate paragraphs, details from previous cases left in | Eliminated. Every analysis is generated fresh from the actual case data |
| **Experience dependency** | High. New starters take months to reach full productivity. Throughput drops when experienced investigators leave | Reduced. The platform embeds institutional knowledge. New investigators work at a comparable pace from the start |
| **Training and onboarding** | Weeks of shadowing and learning systems, SOPs, and precedents | Significantly shorter. The AI guides the investigator through the methodology and flags relevant SOPs automatically |
| **Output format** | Tied to current template structure | Template-agnostic. Adapts to any case file format as requirements evolve |

---

## 5) Example Impact

Using a sanitised real case run through the prototype:

**CASE-2026-0451 (Romance Scam):** The AI correctly identified the case as a third-party scam with the subject as a victim, flagged the grooming escalation pattern across counterparty transactions, identified money mule network exposure, and recommended MLRO escalation. All of this came from the pre-staged case data in the initial assessment, before the investigator had asked a single question.

Under the current workflow, an investigator would need to open C360, download and review the transaction spreadsheets, screen wallets in Elliptic, check Kodex for law enforcement cases, review KYC, read any previous investigations, and then hold all of that context in their head while working through the case template. For an experienced investigator, that might take 40 to 60 minutes. For someone newer to the team, it could take considerably longer.

With the platform, the investigator opens the case and finds the data already processed and structured, with an AI assessment ready. Their job is to review the findings, apply their own judgment, challenge anything that doesn't look right, and make the final decision. The target is 15 to 20 minutes, with the investigator's time spent entirely on the work that actually requires a human: evaluating risk and making the call.

---

## 6) Implementation Plan (High-Level)

1. **Demonstrate the prototype** to stakeholders using sanitised case data to validate the approach and confirm the direction.
2. **Build the data ingestion portal** (Phase 2) so investigators can work real cases through the platform. The core processing code for C360 and Elliptic already exists and needs to be integrated into the platform front end. New capabilities for LE PDF extraction and Hexa text parsing will be built.
3. **Deploy to shared infrastructure** (Phase 3) so the pilot group can access it. This requires IT support for VM provisioning, MongoDB, and network configuration.
4. **Run a controlled pilot** (Phase 4) with a small group of investigators on live cases for 2 to 4 weeks. Measure case throughput, QC pass rates, and collect feedback to guide further development.

**What's needed to proceed:**

- Dedicated development time for Ben and colleague with database/data expertise.
- SafuAPI Anthropic key and WAF whitelisting for Binance network deployment.
- Elliptic API key configured for the platform.
- VM or shared infrastructure for deployment beyond local machine.
- Stakeholder time for demo review and pilot oversight.

---

## 7) Approval

| Date | Status | Name | Role |
|------|--------|------|------|
| | | Tom Turrell | Owner |
| | | James Spaans | Stakeholder |
| | | Mike Whelan | Sponsor |
