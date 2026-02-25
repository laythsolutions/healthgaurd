# NSF PESOSE Grant Alignment Document
## Funding Opportunity 26-506 — Pathways to Enable Secure Open-Source Ecosystems
### [PROJECT_NAME] — Open-Source Food Safety Intelligence Platform

> **Prepared for:** U.S. National Science Foundation
> **Program:** Pathways to Enable Secure Open-Source Ecosystems (PESOSE)
> **Opportunity Number:** 26-506
> **Deadline:** September 1, 2026
> **Estimated Total Program Funding:** $40,000,000 (60 awards expected)
> **Assistance Listing:** 47.070 Computer and Information Science and Engineering (primary); 47.074 Biological Sciences; 47.075 Social, Behavioral, and Economic Sciences

---

## 1. Executive Summary

[PROJECT_NAME] is an Apache 2.0–licensed open-source platform that bridges IoT food safety sensors, clinical case reporting, inspection records, and federal recall feeds into a single, privacy-preserving intelligence system for public health. It is purpose-built for the U.S. food safety ecosystem — health departments, restaurants, emergency departments, and consumers — and is designed to interoperate with government data sources (FDA, USDA, CDC) out of the box.

The platform's core is complete and deployed as a working open-source ecosystem (OSE). This document maps every remaining roadmap item to the three PESOSE proposal tracks, explains the technical and socio-technical work required to accomplish each, and frames the full portfolio of remaining work as a coherent NSF funding narrative.

**The project is an ideal PESOSE candidate because it:**

- Is an open-source software ecosystem addressing a documented national challenge (foodborne illness affects 48 million Americans annually, costing $15.6 billion per year — CDC estimate)
- Already has governance documents, CI/CD pipelines, OpenAPI schemas, audit logging, data classification, and role-based access — the OSE foundation is in place
- Requires NSF support specifically to: harden security and supply chain integrity; build a governing community across academia, public health, and industry; and fund pilots that generate the evidence base for national adoption
- Maps cleanly to PESOSE Track 2 ("establish and expand a sustainable OSE") with supplementary activities from Track 3 ("improve safety, security, and privacy")

---

## 2. PESOSE Proposal Track Analysis

The NSF PESOSE solicitation defines three proposal tracks. This project is best positioned for **Track 2** with **Track 3** components.

| Track | Description | This Project's Fit |
|---|---|---|
| **Track 1 — Scope & Plan** | Fund planning activities to assess feasibility of an OSE | Not applicable — the OSE is already operational |
| **Track 2 — Establish & Expand** | Fund establishment of a sustainable OSE governance and community around a promising open-source product | **Primary track.** Platform is built; now needs governance body, pilots, security hardening, and community growth |
| **Track 3 — Safety, Security, Privacy** | Fund improvements to safety, security, and privacy of an existing OSE | **Supplementary.** SBOM, signed images, pen testing, data pipeline security, and privacy-preserving ML features are Track 3 activities |

**Recommended proposal structure:** A combined Track 2 + Track 3 proposal presenting a two-phase plan: (Phase A) security and privacy hardening + formal OSE governance; (Phase B) pilot deployments + community expansion.

---

## 3. Remaining Roadmap Items — Detailed Analysis and Accomplishment Plan

The following items remain on the project roadmap. Each is categorized, explained in technical depth, mapped to PESOSE objectives, and accompanied by a concrete implementation plan suitable for a work plan appendix.

---

### 3.1 Supply Chain Security & Software Integrity

#### 3.1.1 SBOM Generation on Release

**What it is:**
A Software Bill of Materials (SBOM) is a machine-readable inventory of every software component, library, and dependency included in a release artifact. The White House Executive Order 14028 (2021) on Improving the Nation's Cybersecurity mandates SBOMs for software sold to the federal government; NIST SP 800-218 (SSDF) further codifies this expectation.

**Why it is blocked:**
SBOM generation requires agreement on: (a) which SBOM format to use (CycloneDX vs. SPDX), (b) which components to enumerate (Python packages, npm packages, OS layer, compiled Zigbee firmware), and (c) how to publish SBOMs alongside release artifacts. These are community governance decisions that need TSC ratification.

**How to accomplish it:**

1. **Adopt CycloneDX 1.6** as the primary format (JSON). CycloneDX has stronger tool support for Python (cyclonedx-bom), Node.js (@cyclonedx/cyclonedx-npm), and container layers (syft, grype) than SPDX.
2. **Add three SBOM generation steps to the existing GitHub Actions CI pipeline:**
   - Python SBOM: `cyclonedx-bom -r -o sbom-python.json` in the `services/core/` build job
   - Node.js SBOM: `@cyclonedx/cyclonedx-npm --output-format json` in the `web/` build job
   - Container SBOM: `syft packages docker:healthguard/core:$TAG -o cyclonedx-json` after `docker build`
3. **Publish SBOMs as GitHub release assets** attached to every tagged release using `gh release upload`.
4. **Run continuous vulnerability scanning** against the SBOM using `grype sbom:sbom-python.json` in CI; fail the build on CRITICAL CVEs with no fix.
5. **Submit the SBOM schema to the `schemas/` directory** so downstream integrators can validate SBOMs programmatically.

**PESOSE alignment:** Directly addresses "significant vulnerabilities, both technical and socio-technical, to improve the resistance of the ecosystem against threats" (Track 3). NSF reviewers will recognize SBOM compliance as a concrete, measurable security deliverable.

**Estimated effort:** 2–3 weeks of engineering time plus 1 TSC ratification cycle.

---

#### 3.1.2 Signed Container Images

**What it is:**
Cryptographically signed container images allow downstream users (health departments, hospital IT) to verify that a pulled image was built by the project and has not been tampered with in transit or in the registry. Sigstore/cosign is now the CNCF-recommended approach and is free.

**Why it is blocked:**
Signing requires a key management decision (keyless Sigstore OIDC-based signing vs. long-lived key pairs), a transparency log strategy (Rekor), and confirmation that the project's container registry (GitHub Container Registry / GHCR) supports cosign attestations.

**How to accomplish it:**

1. **Adopt keyless signing via Sigstore/cosign** — no private keys to manage. The GitHub Actions OIDC token is used as the signing identity, which is tied to the repository's GitHub identity. This is the lowest-overhead path.
2. **Add a `sign-and-attest` job** to the existing `.github/workflows/docker-publish.yml` that runs after the image push:
   ```yaml
   - name: Sign image with cosign
     run: cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}
   - name: Attach SBOM attestation
     run: cosign attest --yes --predicate sbom-python.json --type cyclonedx ghcr.io/${{ github.repository }}:${{ github.sha }}
   ```
3. **Publish a verification guide** in `docs/security/verify-images.md` showing operators how to run `cosign verify` before deploying.
4. **Add signature verification to the Kubernetes reference manifests** using a Kyverno or OPA Gatekeeper policy so that clusters only admit signed images from the project registry.

**PESOSE alignment:** Software supply chain integrity is a top NSF PESOSE concern. This deliverable directly demonstrates "enhancements to the safety, security, and privacy of Open-Source Ecosystems" (Track 3).

**Estimated effort:** 1 week of engineering time.

---

### 3.2 Clinical & Genomic Data Integration

#### 3.2.1 Lab Result Upload with PFGE/WGS Metadata Support `[RFC]`

**What it is:**
Pulsed-Field Gel Electrophoresis (PFGE) and Whole-Genome Sequencing (WGS) are the gold-standard methods used by public health labs (via CDC's PulseNet network) to genetically fingerprint foodborne pathogens and link geographically dispersed cases to a single outbreak source. Currently, [PROJECT_NAME] accepts anonymized clinical case submissions but does not ingest the genetic metadata that links those cases across jurisdictions.

Adding WGS metadata support would allow a health department lab to submit: a pathogen isolate's allele profile (cgMLST), NCBI SRA accession, cluster ID (from CDC's NCBI Pathogen Detection pipeline), and BioSample metadata — enabling the platform to cross-reference locally detected clusters against national genetic clusters.

**Why it is an RFC:**
The data model for genomic metadata is contested. PulseNet uses MLVA, PFGE, and cgMLST depending on pathogen. NCBI Pathogen Detection uses SNP tree distances. Deciding which schema to adopt, how to anonymize submitter-identifying metadata in BioSample records, and whether to store raw reads vs. processed allele profiles requires input from clinical microbiologists, epidemiologists, and biosafety counsel.

**How to accomplish it:**

1. **Draft RFC** proposing a `GenomicIsolate` model linked to `ClinicalCase` with fields: `pathogen`, `serotype`, `sequence_accession` (nullable SRA/BioProject ID), `cluster_id` (PulseNet/NCBI cluster), `cgmlst_allele_hash`, `method` (PFGE/WGS/MLVA), `lab_submitter_id` (hashed), `collection_date`, `specimen_type`.
2. **Engage CDC PulseNet and NCBI Pathogen Detection** teams to confirm schema compatibility. These teams have published open data exchange specifications.
3. **Implement a FASTA/FASTQ-free submission path** — the platform stores only processed metadata (accession numbers, cluster IDs, allele hashes), never raw sequence reads. This sidesteps HIPAA/biosafety concerns around raw genomic data while still enabling cross-cluster linkage.
4. **Add a `genomic_match_score` field** to `OutbreakInvestigation` that reflects NCBI Pathogen Detection cluster overlap with local cases, updated nightly via a Celery task calling the NCBI Pathogen Detection REST API.
5. **Publish the RFC openly** for 30-day comment period in GitHub Discussions before any code is merged.

**PESOSE alignment:** Genomic surveillance of foodborne pathogens is a national security concern under HHS/CDC's One Health framework. Integrating open-source clinical genomics tooling into a food safety OSE directly addresses PESOSE's "national and societal challenges" framing.

**Estimated effort:** 4–6 weeks engineering (post-RFC). RFC process: 6–8 weeks.

---

### 3.3 Retail Supply Chain Integration

#### 3.3.1 Product and Transaction Store (UPC, Brand, Category, De-identified)

**What it is:**
A de-identified product purchase database that stores consumer transaction records — linked to UPC codes, brand, product category, and distribution geography — without storing any personally identifiable information. This enables a new analytical capability: when a recall is issued for a specific lot number, the platform can estimate how many de-identified consumers in a health department's jurisdiction may have purchased the affected product and in what time window, enabling proactive outreach.

**Why it is blocked:**
This requires a data model decision (how to de-identify loyalty card transactions before ingest), a legal review of data use agreements with retail partners, and a community RFC on whether this scope expansion is appropriate for an open-source public health tool vs. a commercial product.

**How to accomplish it:**

1. **Define de-identification standard:** Apply k-anonymity (k≥5) at the ZIP+4 level and temporal binning (week-level, not day-level) before ingest. Use the existing `privacy/anonymization.py` service as the processing pipeline.
2. **Design the `ProductTransaction` model:** `upc`, `brand_name`, `product_category`, `distribution_region` (geohash-6), `purchase_week` (ISO week), `quantity_estimate` (range bin, not exact), `retailer_code` (hashed), `recall_lot_match` (boolean, set by matching engine).
3. **Build a `RetailConnector` abstract base class** in `services/intelligence/` with a concrete `CSVBulkImportConnector` for health departments that receive de-identified data dumps from retail partners, and a stub `LoyaltyAPIConnector` for future live integrations.
4. **Add a matching task** in `recalls/tasks.py` that joins active recall records against `ProductTransaction` by UPC + lot number range + distribution region and sets `recall_lot_match=True`.
5. **Expose a `GET /api/v1/recalls/{id}/exposure-estimate/`** endpoint returning: estimated affected region, week range, product category, and affected-quantity tier — but no individual-level data.

**Estimated effort:** 6–8 weeks engineering + legal review.

---

#### 3.3.2 Retail Partner API Connectors (Loyalty/Transaction Ingest) `[RFC]`

**What it is:**
Live API connectors to major grocery/retail chains' loyalty or inventory systems that automatically ingest de-identified purchase data when a new recall is published. This transforms the platform from batch-import (manual CSV from health department) to near-real-time recall impact assessment.

**Why it is an RFC:**
Retail data sharing partnerships involve commercial negotiations, data use agreements, and legal consent frameworks that vary by retailer and state law (CCPA, state privacy laws). The open-source community must decide: should connector code for specific retailers (Kroger, Walmart, Albertsons) be in the main repo, or should it be a governed plugin registry? What data minimization requirements must connectors satisfy before a PR is accepted?

**How to accomplish it:**

1. **Publish RFC:** Propose a `RetailConnector` plugin specification — a Python abstract base class with required methods (`fetch_transactions(recall_id, lot_range, distribution_region)`, `get_connector_metadata()`), a JSON manifest schema for connector capabilities, and a code review checklist that each connector PR must satisfy (de-identification audit, no PII logging, rate limiting).
2. **Create a `connectors/` plugin registry directory** separate from core code, with its own governance: connector PRs require two TSC approvals plus a data privacy review sign-off.
3. **Build a reference connector using a public open dataset** (USDA Economic Research Service food purchase panel data, which is de-identified by design) to demonstrate the interface without requiring a commercial partnership.
4. **Engage USDA Food Safety and Inspection Service (FSIS) and FDA's Coordinated Outbreak Response and Evaluation (CORE)** network as potential government data partners — federal data is not subject to commercial confidentiality constraints.

**PESOSE alignment:** Supply chain data integration is cited in PESOSE's description of "critical fields as varied as... banking, healthcare, research... next-gen manufacturing." Food supply chain traceability is a direct national food safety priority under FSMA Section 204.

---

### 3.4 Security Hardening

#### 3.4.1 Penetration Testing and Remediation

**What it is:**
A formal external security assessment of the platform's attack surface: REST API, WebSocket endpoints, MQTT broker, OTA update pipeline, JWT/MFA authentication, OIDC federation, and the Django admin interface. The assessment should produce a public remediation report consistent with coordinated vulnerability disclosure (CVD) best practices.

**Why it is an external engagement:**
Penetration testing must be performed by an independent third party to be credible to government adopters (health departments, FSIS, FDA). Self-assessment does not satisfy FedRAMP Tailored, NIST SP 800-53, or state health IT security requirements that adopting health departments will face.

**How to accomplish it:**

1. **Issue an RFP** for a CREST- or GIAC-certified penetration testing firm with demonstrated experience in: Django REST APIs, MQTT/IoT protocols, and healthcare data systems (HIPAA-adjacent, clinical case data).
2. **Scope the assessment to cover:**
   - **API security:** OWASP API Security Top 10 (2023 edition) — injection, authentication, authorization, mass assignment, SSRF
   - **MQTT broker:** Authentication bypass, topic ACL enforcement, retained message poisoning, QoS spoofing
   - **OTA pipeline:** Firmware image authentication, rollback attack vectors, update server SSRF
   - **WebSocket:** Authentication token replay, group membership enforcement (restaurant-scoped channels)
   - **Django admin:** Privilege escalation, CSRF, session fixation
   - **Supply chain:** Dependency confusion, typosquatting in `requirements.txt` and `package.json`
3. **Publish the full remediation report** (with CVE assignments where applicable) in `docs/security/pentest-report-YYYY.md`, redacting only zero-day details that have not yet been patched.
4. **Implement a `SECURITY.md` vulnerability disclosure policy** with a 90-day coordinated disclosure window (already exists — ensure it references the pentest report and CVE tracking).
5. **Establish a bug bounty program** on HackerOne or Bugcrowd for ongoing community-driven vulnerability discovery post-pentest.

**PESOSE alignment:** NSF PESOSE explicitly funds "enhancements to the safety, security, and privacy of Open-Source Ecosystems by addressing significant vulnerabilities, both technical and socio-technical." A public pentest report is a landmark Track 3 deliverable.

**Estimated budget:** $40,000–$80,000 for a comprehensive penetration test by a qualified firm.

---

### 3.5 IoT Infrastructure

#### 3.5.1 Zigbee Mesh Topology Support

**What it is:**
Current Zigbee2MQTT deployment treats all sensors as a flat list connected to a single coordinator. Zigbee is a mesh protocol — sensors can route through each other, extending range beyond line-of-sight from the coordinator. Supporting mesh topology means: (a) mapping the mesh graph (which devices are routing through which), (b) surfacing mesh health in the device dashboard, and (c) making the MQTT bridge aware of multi-hop routing so it can detect partial mesh failures (a router device going offline silently takes multiple end-devices with it).

**How to accomplish it:**

1. **Subscribe to `zigbee2mqtt/bridge/devices` and `zigbee2mqtt/bridge/networkmap`** in the MQTT bridge. Zigbee2MQTT publishes a full network topology map (JSON) on demand and on join/leave events.
2. **Add a `ZigbeeMeshNode` model** in `devices/models.py` with fields: `device` (FK), `node_type` (coordinator/router/end-device), `parent_device` (nullable FK to another `ZigbeeMeshNode`), `link_quality` (LQI, 0–255), `last_seen`.
3. **Persist the topology map** by parsing the `networkmap` payload in a new `MeshTopologySync` Celery task triggered on `zigbee2mqtt/bridge/networkmap` MQTT messages.
4. **Implement cascade-offline detection:** When a router device goes offline (no heartbeat for 3× reporting interval), flag all `ZigbeeMeshNode` records whose `parent_device` is that router as `POTENTIALLY_OFFLINE` and generate a `DEVICE_OFFLINE` alert with a note explaining the cascade risk.
5. **Add a mesh topology visualization** to the device dashboard (D3.js force-directed graph or a simple table view showing parent-child relationships and LQI scores).
6. **Update the OTA system** to respect mesh routing: firmware updates should be dispatched to routers before end-devices, and the OTA task should poll `zigbee2mqtt/bridge/devices` to confirm each node's firmware version before proceeding.

**Estimated effort:** 4–5 weeks engineering.

---

### 3.6 Pilot Deployments & Evaluation

These four items are the most strategically important for grant funding. NSF PESOSE reviewers expect evidence that the OSE addresses a real societal need, and pilots generate that evidence.

#### 3.6.1 Pilot with at Least One Local Health Department

**What it is:**
A structured 6–12 month deployment of [PROJECT_NAME] at a county or city health department, covering: inspection data ingestion from the department's existing system, real-time outbreak cluster alerting, recall-to-restaurant matching and acknowledgment workflow, and health department staff training.

**How to accomplish it:**

1. **Identify target jurisdiction:** Prioritize mid-size county health departments (population 100,000–500,000) with existing open APIs for inspection data (e.g., Socrata-based portals used by King County WA, Maricopa County AZ, or NYC DOHMH). These already publish machine-readable data, lowering integration cost.
2. **Execute a Memorandum of Understanding (MOU)** that covers: data use, publication rights for the pilot evaluation report, staff time commitment, and the department's right to terminate without penalty.
3. **Stand up a dedicated instance** using the Kubernetes reference deployment in a cloud region selected by the department (AWS GovCloud or Azure Government for FedRAMP-adjacent compliance).
4. **Deliver a 4-session training curriculum** covering: dashboard navigation, outbreak alert triage, recall acknowledgment workflow, and data export for state reporting.
5. **Collect structured evaluation data** over the pilot period: time-to-alert vs. baseline, number of recalls acknowledged via platform vs. phone/email, staff satisfaction (Likert survey), and any data quality issues discovered.
6. **Publish the evaluation report** openly under CC BY 4.0 on the project website and submit to a peer-reviewed public health informatics journal (e.g., JAMIA, JMIR Public Health).

**PESOSE alignment:** Pilots directly demonstrate "broad user communities across academia, industry, and government" — the core sustainability criterion for Track 2. A government (health department) pilot is the highest-value evidence for federal funders.

**Suggested partners:** NACCHO (National Association of County and City Health Officials) has a technology innovation program that can facilitate introductions to member health departments.

---

#### 3.6.2 Pilot with 10–20 Restaurants (IoT + Compliance)

**What it is:**
Deploy the full IoT stack (Raspberry Pi gateway, Zigbee coordinator, temperature sensors, door sensors, and at least one fryer oil sensor per location) across 10–20 restaurants in a single city, operated through a participating health department or a food service industry association partner.

**How to accomplish it:**

1. **Partner with a regional restaurant association** (e.g., state chapter of the National Restaurant Association, or a local independent restaurant coalition) to recruit 10–20 willing participants. Prioritize diversity: fast food, fast casual, full service, and a food truck if possible.
2. **Provide hardware kits at no cost** to pilot participants (Raspberry Pi 5, Zigbee coordinator, 4× temperature sensors, 2× door sensors, 1× fryer oil sensor per site). Budget: ~$300/site × 20 sites = $6,000 in hardware.
3. **Deploy and configure** each site in a single visit (~3 hours/site with a trained installer). The existing Docker Compose dev stack runs on a Raspberry Pi 5 with 8GB RAM.
4. **Run a 90-day compliance evaluation:** Track: number of temperature violations detected vs. corrected, door-open incidents, fryer oil change intervals, and reduction in manual temperature logging burden (staff time survey).
5. **Compare to a control group** (10 restaurants that remain on paper-based compliance) if the restaurant association can recruit both groups. This creates a quasi-experimental design suitable for publication.
6. **Publish an open dataset** of anonymized, aggregated compliance metrics from the pilot in the `schemas/` directory format.

**PESOSE alignment:** Industry (restaurant) user community + real-world IoT deployment data + open dataset publication. This is the "innovation in critical fields... healthcare" narrative for PESOSE.

---

#### 3.6.3 Pilot with at Least One Healthcare Partner (Clinical Reporting)

**What it is:**
Deploy the Clinical Case API at an emergency department, urgent care network, or regional hospital system, enabling clinicians to submit anonymized foodborne illness case reports directly from their EHR or a web form, and receive real-time cluster alerts when their cases are part of a detected outbreak.

**How to accomplish it:**

1. **Engage a health system's clinical informatics or population health team.** Academic medical centers (e.g., those with NSF-funded research programs) are ideal because they have IRB infrastructure, research staff, and existing relationships with local health departments.
2. **Obtain IRB approval** at both the submitting institution and the project's administering institution for the collection of anonymized case data. The existing consent management microservice and anonymization pipeline were designed specifically to satisfy this requirement — no new PII is stored.
3. **Build an HL7 FHIR R4 bridge** (a single `FHIRCaseAdapter` class) that translates a `Condition` + `Observation` FHIR bundle from an EHR into the platform's `ClinicalCase` submission format. This is a 2–3 week engineering task.
4. **Train clinical staff** (1-hour session) on the voluntary reporting workflow and what triggers a cluster alert back to them.
5. **Measure:** reporting latency vs. existing paper/phone reporting, clinical staff satisfaction, and whether the cluster feedback loop meaningfully changed clinical behavior (e.g., did receiving an alert cause more cases to be reported?).

**PESOSE alignment:** Healthcare is explicitly named in PESOSE's description of target domains. An academic medical center partner satisfies the "academia" component of "broad user communities across academia, industry, and government."

---

#### 3.6.4 Pilot Evaluation Report Published Openly

**What it is:**
A combined, peer-reviewed evaluation report synthesizing findings from all three pilot tracks (health department, restaurant IoT, healthcare partner) into a single public document covering: deployment experience, outcomes data, lessons learned, and recommendations for national scaling.

**How to accomplish it:**

1. **Assign authorship** to include: PI (project lead), co-PIs from the partner health department and healthcare institution, and a social scientist co-author to lead the qualitative analysis (staff interviews, workflow observations).
2. **Submit to JAMIA (Journal of the American Medical Informatics Association), JMIR Public Health, or Food Control** (Elsevier) — all accept open-access publication under CC BY.
3. **Simultaneously publish** a plain-language summary on the project website, a policy brief for NACCHO and ASTHO (Association of State and Territorial Health Officials), and a technical appendix in `docs/pilots/` in the repository.
4. **Use the report as the anchor document** for a national scaling whitepaper submitted to FDA, USDA FSIS, and CDC's Center for Surveillance, Epidemiology, and Laboratory Services (CSELS).

---

### 3.7 Mobile — Consumer Exposure Reporting

#### 3.7.1 Receipt or Menu Photo Upload for Consumer Exposure Reporting `[RFC]`

**What it is:**
Allow consumers to photograph a restaurant receipt or menu item and submit it as exposure evidence during a foodborne illness episode. A computer vision pipeline would extract: restaurant name, menu items purchased, date and time, and optionally a loyalty transaction ID — then link this to any active outbreak investigation or recall record in the platform.

**Why it is an RFC:**
This feature has significant privacy, legal, and ML fairness considerations that require community input before implementation:
- Receipts contain partial credit card numbers, phone numbers, and loyalty IDs — PII that must not be stored
- OCR accuracy varies by receipt format, lighting, and language
- There is a risk of false association (consumer ate at restaurant X but illness was caused by restaurant Y)
- Any ML model trained on receipt images must be evaluated for demographic bias

**How to accomplish it:**

1. **Draft RFC** addressing: data minimization (what fields are extracted and stored, what is immediately discarded), consent UX (explicit opt-in per submission, not app-wide), accuracy thresholds below which a submission is flagged for manual review rather than auto-linked, and model release policy (model weights + training data card published openly).
2. **Build a two-stage ML pipeline:**
   - **Stage 1 — OCR extraction:** Use Tesseract (open-source) or Google Cloud Vision API (paid but accurate) to extract text from the receipt image. Immediately discard the raw image after extraction; never store images.
   - **Stage 2 — Entity recognition:** A fine-tuned NER model (spaCy or Hugging Face) that identifies restaurant name, menu items, and purchase date from the OCR text. Train on a synthetic receipt dataset generated from publicly available menu data to avoid PII in training data.
3. **Implement PII scrubbing** before any structured data is stored: mask partial card numbers (`****1234`), strip phone numbers, hash loyalty IDs (store hash only for deduplication, not the ID itself).
4. **Publish the model card** (training data description, accuracy metrics, bias evaluation across cuisine types and receipt languages) in `schemas/ml/receipt-ocr-model-card.md`.
5. **Rate-limit submissions** to 1 per user per day to prevent adversarial flooding of outbreak investigations.

**PESOSE alignment:** Consumer-facing ML for public health is a direct application of "artificial intelligence (AI)" named in PESOSE's description of open-source tool categories. Publishing the model card and training data openly advances NSF's open science mandate.

---

### 3.8 Open Governance & Community Building

These three items are collectively the most important for PESOSE Track 2 eligibility, which requires evidence of "strong governance, distributed development, and broad user communities."

#### 3.8.1 Public RFC Process Formalized

**What it is:**
A documented, enforceable process for proposing, discussing, and ratifying changes to the platform — modeled on the Rust RFC process, Python PEPs, or IETF RFCs — covering: who can propose an RFC, minimum comment period (30 days), quorum requirements for TSC ratification, and how superseded RFCs are archived.

**How to accomplish it:**

1. **Publish `docs/governance/RFC-process.md`** defining: RFC template (problem statement, proposed solution, alternatives considered, drawbacks, unresolved questions), submission via GitHub Discussions, 30-day minimum public comment period, TSC vote (simple majority with quorum of 3 TSC members), and effective date.
2. **Create a GitHub Discussions category** titled "RFCs" with a pinned index of all open and accepted RFCs.
3. **Retroactively file RFCs** for the three existing `[RFC]`-tagged items (WGS metadata, retail connectors, receipt upload) to demonstrate the process works end-to-end before the grant period begins.
4. **Define RFC lifecycle states:** `draft` → `open-for-comment` → `accepted` / `rejected` / `withdrawn` / `superseded`.
5. **Publish the RFC index at `/rfcs/`** on the project website, auto-generated from a `rfcs/` directory in the repository (similar to the Rust RFC book approach).

**PESOSE alignment:** PESOSE requires "strong governance." A formal RFC process is the most visible governance artifact NSF reviewers look for. Projects like Rust, Python, and Node.js point to their RFC/PEP processes as evidence of OSE maturity.

**Estimated effort:** 1–2 weeks to draft; 30-day community ratification cycle.

---

#### 3.8.2 Contributor Mentorship Program

**What it is:**
A structured program pairing experienced contributors with new contributors — particularly students, early-career developers, and public health professionals who want to contribute code or documentation but lack open-source experience.

**How to accomplish it:**

1. **Define three contributor tracks:**
   - **Code track:** Paired with a TSC member for 8 weeks; assigned 2–3 "good first issue" tickets; goal: first merged PR within 4 weeks
   - **Documentation track:** Paired with a technical writer volunteer; goal: contribute to one user-facing doc page or API reference section
   - **Data/epidemiology track:** Paired with a public health co-PI; goal: contribute a data analysis notebook or a new clustering heuristic
2. **Recruit cohorts twice per year** (January and July) through: NSF REU (Research Experience for Undergraduates) site program, NACCHO's innovation fellowship network, and direct outreach to public health informatics graduate programs (University of Washington, Johns Hopkins BSPH, Emory).
3. **Publish mentor and mentee expectations** in `docs/community/mentorship.md`: weekly 30-minute sync, GitHub activity review, code review participation.
4. **Track cohort outcomes:** merged PRs, new contributors retained (still active 6 months later), and demographic diversity of participants (self-reported, optional). Publish outcomes in the annual project report.

**PESOSE alignment:** "Distributed development and broad user communities" is a Track 2 criterion. A mentorship program is the most direct mechanism to demonstrate intentional community growth, and NSF PESOSE reviewers have explicitly funded mentorship infrastructure in prior OSE grants.

---

#### 3.8.3 University Partnership for Student Projects

**What it is:**
Formal partnerships with 2–4 universities to integrate [PROJECT_NAME] into coursework (capstone projects, practicum courses, research assistantships) so that students contribute meaningfully to the platform while satisfying academic requirements.

**How to accomplish it:**

1. **Target programs:** Public health informatics (MPH/MS), computer science (senior capstone), data science, and epidemiology. Ideal programs already have practicum or community-engaged learning requirements.
2. **Develop a "project in a box" package** for faculty: Docker Compose quickstart, a curated list of 20 open issues tagged `student-project`, a suggested 12-week project timeline, grading rubric suggestions, and a letter of support template for faculty grant applications.
3. **Sign MOUs with partner institutions** specifying: student IP assignment (Apache 2.0, consistent with project license), faculty advisor responsibilities, and project's commitment to reviewing student PRs within 5 business days.
4. **Host a joint student showcase** each spring where student teams present their contributions at a public virtual event, recorded and published on the project YouTube channel.
5. **Track output:** lines of code contributed by students, issues resolved, and documentation pages added. Report in the annual NSF progress report.

**Suggested target universities:** University of Washington (strong BIME + public health), Georgia Tech (strong CS + health informatics), University of Michigan (strong public health + epidemiology), Howard University (HBCU partnership strengthens NSF's equity commitments).

**PESOSE alignment:** University partnerships satisfy the "academia" component of "broad user communities across academia, industry, and government" and demonstrate that the OSE is generating educational value — a secondary PESOSE objective.

---

### 3.9 Platform Scaling & Sustainability (Year 4)

#### 3.9.1 Multi-Tenant Regional Stack for Multiple Health Departments

**What it is:**
Currently, each health department deployment is a fully independent stack (separate database, separate services, separate Kubernetes cluster). A multi-tenant regional stack would allow multiple health departments in the same state or region to share infrastructure while maintaining complete data isolation — reducing per-department deployment cost from ~$800/month to ~$150/month per department on shared infrastructure.

**How to accomplish it:**

1. **Evaluate two multi-tenancy models:**
   - **Schema-per-tenant (PostgreSQL):** Each health department gets its own PostgreSQL schema within a shared database. Django's `django-tenants` library implements this pattern. Pros: strong data isolation, simple backup/restore per tenant. Cons: migrations must run per-tenant; TimescaleDB compatibility requires validation.
   - **Row-level security (RLS):** All tenants share tables; a `tenant_id` column on every model enforces isolation via PostgreSQL RLS policies. Pros: simpler migrations. Cons: a misconfigured query can leak cross-tenant data; requires extensive audit.
   - **Recommendation:** Schema-per-tenant for clinical and IoT data (highest sensitivity); shared schema with RLS for public data (restaurant grades, advisories).
2. **Add a `Tenant` model and middleware** (already scaffolded as `TenantMiddleware` in the codebase) that resolves the active tenant from the request's subdomain or JWT claim.
3. **Deploy a shared Kubernetes namespace** with per-tenant namespace isolation using Kubernetes Network Policies and RBAC to prevent cross-tenant service communication.
4. **Implement per-tenant billing metering** (if sustainability contracts are adopted): a `TenantUsageRecord` model tracking API calls, sensor readings ingested, and storage consumed per billing cycle.
5. **Publish a multi-tenant deployment guide** in `docs/deployment/multi-tenant.md` and add a Helm chart for the regional stack.

**Estimated effort:** 8–12 weeks engineering (the most complex remaining item).

---

#### 3.9.2 Offline-First Mobile Refinements for Low-Connectivity and Rural Deployments

**What it is:**
The current PWA service worker (`web/public/sw.js`) provides basic offline caching for restaurant pages and recall data. Full offline-first for rural health department inspectors means: the inspection form works completely offline, photos can be taken and queued, form submissions are replicated when connectivity returns, and the inspector's assigned restaurant list is pre-loaded at the start of the day.

**How to accomplish it:**

1. **Adopt IndexedDB as the offline data store** (via the `idb` library or Dexie.js) for: the inspector's assigned restaurant list, partially-completed inspection forms, queued form submissions, and cached recall/advisory data.
2. **Implement a background sync queue** using the Background Sync Web API (supported in Chrome/Edge; requires a service worker): when a form submission fails due to no connectivity, it is added to a sync queue and replayed automatically when connection is restored.
3. **Add a conflict resolution strategy** for the case where the inspector submits a form offline and the restaurant record was updated server-side while offline: last-write-wins for inspection form fields; alert the inspector if server-side record changed.
4. **Build a "pre-load for the day" feature:** when the inspector opens the app on Wi-Fi in the morning, the service worker pre-fetches all restaurants on today's inspection schedule, their recent violation history, and any active recalls or advisories for their district.
5. **Test specifically on low-end Android devices** (the most common device type in low-resource health department field staff) using Chrome DevTools' network throttling and the Lighthouse PWA audit.

**PESOSE alignment:** Rural and low-connectivity deployment is an equity consideration that NSF PESOSE reviewers respond well to — it expands the user community beyond urban, well-resourced health departments.

---

#### 3.9.3 Sustainability Mechanisms (Support Contracts, Hosted Analytics) `[RFC]`

**What it is:**
Long-term OSE sustainability requires revenue mechanisms that do not compromise the open-source nature of the core platform. Potential mechanisms include: paid support contracts for health departments, a hosted analytics tier (compute-intensive WGS cluster matching or supply chain traceback run on managed infrastructure), and training/certification programs for health department staff.

**Why it is an RFC:**
Revenue-generating activities by an open-source project require community governance decisions about: which activities are "open core" vs. commercial, how revenue is allocated (back to development? to fiscal sponsor? to maintainer stipends?), and what entity structure governs the commercial activities (fiscal sponsor like Linux Foundation or Apache Software Foundation vs. a separate LLC).

**How to accomplish it:**

1. **Select a fiscal sponsor:** Apply to the Linux Foundation, Apache Software Foundation, or a public health–specific fiscal sponsor (e.g., a university-based center). The fiscal sponsor provides: legal entity, 501(c)(3) status for donations, HR/payroll for stipended maintainers, and contracting infrastructure for support agreements.
2. **Define the open-core boundary in the RFC:** The following are always free and open-source: core platform, all data models, all APIs, all ML models, all governance documents. The following are potentially commercial: managed hosting (SaaS), professional services (deployment, training), and premium SLA support contracts.
3. **Draft a model support contract** for health departments: includes deployment assistance, security patch SLA (patches released within 72 hours of critical CVE), and a dedicated support channel.
4. **Apply for fiscal sponsorship** from the Center for Civic Technology or a public health research center at a partner university to formalize the grant-receiving capacity independent of a single institution.
5. **Establish a project sustainability fund** — a transparent, publicly reported reserve fund (minimum 6 months of core maintainer stipends) as a condition of long-term OSE health.

**PESOSE alignment:** PESOSE explicitly requires OSE sustainability as a Track 2 deliverable. Demonstrating a credible sustainability plan — including a fiscal sponsor, a support contract model, and a reserve fund policy — is a grant requirement, not a bonus.

---

#### 3.9.4 Formal Partnerships with National or International Public Health Agencies

**What it is:**
Memoranda of Understanding or data sharing agreements with: CDC (Center for Surveillance, Epidemiology, and Laboratory Services), FDA (Center for Food Safety and Applied Nutrition), USDA FSIS, WHO (Global Foodborne Infections Network — GFN), or EFSA (European Food Safety Authority) — establishing the platform as a recognized node in the global food safety intelligence ecosystem.

**How to accomplish it:**

1. **Engage CDC CSELS** through the NSF–CDC joint public health informatics initiative. CDC has an existing open-data program (CDC Open Technology) that actively seeks open-source tools for food safety surveillance.
2. **Submit a technology brief to FDA's CORE Network** describing how the platform's recall-acknowledgment workflow can complement FDA's existing RFR (Recall Follow-Up Report) system — specifically as a last-mile communication channel to restaurants that currently receive recall notices by mail.
3. **Present at ISAFP (International Association for Food Protection) annual symposium** and engage WHO's FoodNet Global network as a potential international data exchange partner.
4. **File a formal comment** on USDA FSIS's open rulemaking on FSMA Section 204 (food traceability) citing [PROJECT_NAME]'s open-source supply chain traceback capability as a reference implementation.
5. **Apply to participate in CDC's Data Modernization Initiative (DMI)** — a $1.7B initiative to modernize public health data infrastructure — as a complementary open-source tool.

**PESOSE alignment:** Government agency partnerships are the highest-value evidence of "broad user communities across... government" for PESOSE Track 2. Even a letter of support from CDC or FDA dramatically strengthens a PESOSE proposal.

---

## 4. Grant Work Plan Summary

The following table organizes all remaining items into a two-phase grant work plan suitable for a PESOSE proposal covering a 24-month award period.

| Phase | Month | Deliverable | PESOSE Track | Budget Estimate |
|---|---|---|---|---|
| **A** | 1–3 | Formal RFC process published; 3 retroactive RFCs filed | Track 2 | $15,000 (staff) |
| **A** | 1–3 | SBOM generation in CI pipeline | Track 3 | $10,000 (staff) |
| **A** | 1–3 | Signed container images (cosign/Sigstore) | Track 3 | $5,000 (staff) |
| **A** | 2–5 | External penetration test + public remediation report | Track 3 | $60,000 (contractor) |
| **A** | 2–6 | WGS/PFGE metadata RFC + model design | Track 2 | $20,000 (staff + RFC process) |
| **A** | 3–6 | Zigbee mesh topology support | Track 2 | $25,000 (staff) |
| **A** | 3–8 | Contributor mentorship program (Cohort 1) | Track 2 | $30,000 (stipends + coordination) |
| **A** | 4–8 | University partnership MOUs (2–4 partners) | Track 2 | $15,000 (staff + travel) |
| **B** | 6–18 | Health department pilot (1 jurisdiction, 12 months) | Track 2 | $120,000 (staff + infra + training) |
| **B** | 6–12 | Restaurant IoT pilot (10–20 sites, 90 days) | Track 2 | $40,000 (hardware + staff) |
| **B** | 8–18 | Healthcare partner pilot (IRB + FHIR bridge + deployment) | Track 2 | $80,000 (staff + IRB costs) |
| **B** | 10–18 | WGS metadata feature implementation (post-RFC) | Track 2 | $35,000 (staff) |
| **B** | 10–20 | Receipt photo upload ML pipeline (post-RFC + IRB) | Track 2/3 | $45,000 (staff + compute) |
| **B** | 12–20 | Multi-tenant regional stack | Track 2 | $60,000 (staff) |
| **B** | 14–22 | Offline-first mobile refinements | Track 2 | $30,000 (staff) |
| **B** | 18–24 | Pilot evaluation report (peer-reviewed publication) | Track 2 | $20,000 (staff + OA fees) |
| **B** | 18–24 | Sustainability plan + fiscal sponsorship application | Track 2 | $15,000 (legal + staff) |
| **B** | 20–24 | Contributor mentorship program (Cohort 2) | Track 2 | $30,000 (stipends + coordination) |
| | | **Total (24 months)** | | **~$655,000** |

*Note: Figures are illustrative estimates. A certified budget will require detailed institutional rate agreements (F&A/indirect costs), fringe benefit rates, and subcontract budgets from partner institutions.*

---

## 5. Societal Impact Narrative

This section provides language suitable for use directly in a PESOSE Broader Impacts statement.

### 5.1 Scale of the Problem

Foodborne illness affects **48 million Americans annually**, causing 128,000 hospitalizations and 3,000 deaths (CDC, 2024). Economic burden: **$15.6 billion per year** in direct costs and lost productivity (USDA ERS). The 2024 E. coli O157:H7 outbreak linked to McDonald's onions affected 104 people across 14 states before traceback was complete — a 19-day investigation that would have been accelerated by integrated supply chain and genomic data of the type [PROJECT_NAME] is designed to provide.

### 5.2 Gap This Project Fills

Current food safety surveillance is fragmented across: state health departments (inspection records), CDC (clinical case surveillance via FoodNet), FDA (recall records), USDA FSIS (meat and poultry inspections), and hospital systems (emergency department admissions). No open-source tool integrates these streams. Existing commercial solutions are cost-prohibitive for small and rural health departments. [PROJECT_NAME] is designed to be deployable on a $50/month cloud instance or on-premises on a Raspberry Pi.

### 5.3 Equity Considerations

- **Rural health departments** with 2–5 full-time staff and no IT department are the primary underserved users. The platform's offline-first design, Docker Compose single-server deployment, and free license are specifically designed to make adoption possible without a dedicated IT infrastructure team.
- **Non-English speaking restaurant workers** are disproportionately affected by foodborne illness compliance violations driven by language barriers. The platform's internationalization framework (English, Spanish, Vietnamese, Korean, Chinese, Tagalog) directly addresses this population.
- **University partnerships** prioritize HBCUs and HSIs (Hispanic-Serving Institutions) to ensure that the contributor community reflects the diversity of the food service workforce.

### 5.4 National Security Dimension

Food safety is a component of national biosecurity. The 2001 anthrax attacks and subsequent bioterrorism planning have established that food and water supply systems are critical infrastructure (Presidential Policy Directive 21). An open-source, auditable food safety intelligence platform with published security practices (SBOM, signed images, penetration test reports) is more trustworthy infrastructure for this role than proprietary alternatives.

---

## 6. Alignment with NSF Strategic Priorities

| NSF Priority | Project Evidence |
|---|---|
| **Artificial Intelligence** | ML-powered spatial-temporal clustering, supply chain traceback graph, receipt OCR pipeline, equipment failure risk scoring |
| **Cybersecurity** | SBOM, signed images, penetration testing, audit logging, data classification, OIDC federation |
| **Open Science** | Apache 2.0 license, all datasets published openly, model cards for ML models, peer-reviewed pilot evaluation report |
| **Equity and Inclusion** | Rural deployment design, i18n (6 languages), HBCU/HSI university partnerships, mentorship program |
| **Public Health** | Direct integration with FDA, USDA, CDC data; clinical case reporting; outbreak cluster detection |
| **Workforce Development** | Contributor mentorship program, university partnerships, student project coursework integration |

---

## 7. Recommended Next Steps Before Application

In order of priority before the September 1, 2026 deadline:

1. **Identify an institutional home (PI eligibility).** The PI must be employed by the submitting organization. Options: a university research center (submit as IHE), a nonprofit (submit as non-profit non-academic), or a state/local government health department (submit as government). A university-affiliated Open-Source Program Office (OSPO) is ideal — several universities now have OSPOs that can serve as institutional homes for open-source projects seeking grants.

2. **Obtain a letter of support from at least one health department.** Even a brief letter ("we are interested in piloting this platform and support the project's NSF application") substantially strengthens a PESOSE Track 2 proposal.

3. **File the first RFC publicly.** The WGS metadata RFC or the RFC process formalization RFC should be filed and open for comment before the proposal is submitted — this demonstrates that the governance process exists and is active.

4. **Register on Research.gov and Grants.gov.** NSF requires institutional registration (SAM.gov UEI, Research.gov organizational account) before an application can be submitted. This process takes 4–8 weeks. Begin immediately.

5. **Engage NSF Program Officers.** PESOSE program officers hold office hours (listed on the NSF website). A 15-minute conversation with a program officer before submission dramatically improves proposal quality and fit. Submit a 1-page summary to `pesose@nsf.gov` (check current contact in the solicitation) requesting a call.

6. **Draft the Project Description** (15 pages maximum for Track 2). Structure: (1) OSE description and current state, (2) societal/national need, (3) governance plan, (4) community building plan, (5) safety/security/privacy plan, (6) sustainability plan, (7) evaluation plan.

---

*This document was prepared to support [PROJECT_NAME]'s NSF PESOSE 26-506 grant application. It should be reviewed by the PI, co-PIs, institutional grants office, and legal counsel before submission. All budget figures are illustrative and must be developed with institutional sponsored research office input.*

*Last updated: February 2026*
