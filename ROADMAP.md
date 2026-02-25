# Roadmap

This document describes the planned development trajectory for [PROJECT_NAME]. The roadmap is maintained by the Technical Steering Committee (TSC) and updated after each community review cycle.

Items marked **[RFC]** require a public Request for Comments before implementation begins. Community members are encouraged to comment on open RFCs in GitHub Discussions.

---

## Year 1 — Foundation

**Goal:** A working, deployable platform covering the core data pipeline and minimal viable interfaces.

### Backend & Data

- [x] Restaurant registry and inspection record store
- [x] IoT sensor time-series ingestion (MQTT/HTTP)
- [x] Alert rules and multi-channel notification delivery (email, SMS, push, webhook)
- [x] JWT + MFA authentication with role-based access control
- [x] OTA firmware update system with rollback
- [x] **Privacy & Anonymization Service** — PII stripping, geohash encoding, ZIP truncation, age-to-range conversion
- [x] **Consent Management Microservice** — status, scopes, revocation, audit log
- [x] **FDA/USDA Recall Feed Connector** — ingest and link recall records to products and establishments
- [x] **Inspection Record Ingestion** — connectors for state health department APIs and bulk import
- [x] Recall records data model and API
- [x] Shared data schemas in `schemas/` (OpenAPI + JSON Schema)

### Interfaces

- [x] Restaurant owner/staff dashboard (IoT status, compliance timeline)
- [x] **Public web app** — restaurant search, grade display, inspection history, accessibility (WCAG 2.1 AA)
- [x] Basic outbreak advisory map (anonymized, aggregated only)

### Infrastructure

- [x] Docker Compose development stack
- [x] Kubernetes reference deployment (single-tenant)
- [x] Prometheus + Grafana monitoring
- [x] CI pipeline: lint, test, build, container publish (GitHub Actions)
- [ ] SBOM generation on release
- [ ] Signed container images
- [x] Governance documents (LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY)

---

## Year 2 — Integration

**Goal:** Connect clinical data sources and retail supply chain; harden security; expand IoT capabilities.

### Clinical Reporting

- [x] **Clinical Case API** — anonymized case submission endpoint for EDs, urgent care, labs
- [x] Clinical case store with exposure linkage
- [ ] Lab result upload with PFGE/WGS metadata support **[RFC]**
- [x] **Medical Institution Interface** — case entry UI, local cluster alerts, pathogen guidance

### Recall & Supply Chain

- [ ] Product and transaction store (UPC, brand, category, de-identified)
- [ ] Retail partner API connectors (loyalty/transaction ingest) **[RFC]**
- [x] Recall-to-product matching logic (lot numbers, distribution geography)
- [x] Recall acknowledgment and remediation workflow

### Health Department Portal

- [x] Inspection scheduling and digital forms
- [x] Cluster detection dashboard with drill-down
- [x] Recall management and compliance tracking
- [x] Data export tools (CSV/API) for state and federal integration

### Security Hardening

- [x] Audit logging for all data access (who accessed what, when)
- [x] Data classification tagging with access-control enforcement
- [ ] Penetration testing and remediation (external engagement)
- [x] OIDC federation for health department SSO

### IoT Expansion

- [x] Additional sensor types: fryer oil degradation, door open/close, water leak
- [x] Sensor calibration and health check (battery, connectivity reporting)
- [ ] Zigbee mesh topology support

---

## Year 3 — Analytics & Pilots

**Goal:** Multi-source cluster detection, traceback, and first real-world deployments.

### Analytics Engine

- [x] **Spatial-temporal clustering** — group cases by time, place, and exposure **[RFC]**
- [x] Odds ratio and confidence interval calculation for exposure associations
- [x] **Supply chain traceback graph builder** — link cases to lots and distribution
- [x] IoT predictive models — equipment failure risk scores
- [x] Streaming analytics mode (near-real-time alerts alongside nightly batch jobs)

### Pilots

- [ ] Pilot deployment with at least one local health department
- [ ] Pilot with 10–20 restaurants (IoT + compliance)
- [ ] Pilot with at least one healthcare partner (clinical reporting)
- [ ] Pilot evaluation report published openly

### Public API

- [x] Aggregated public data API (restaurant grades, recall summaries, anonymized outbreak regions)
- [x] Rate-limited access tiers for researchers and civic technologists
- [x] API versioning and deprecation policy

### Mobile

- [x] QR code scan to view restaurant grade
- [x] Push alerts for recalls and outbreak advisories in user's area
- [x] Offline cache for low-connectivity areas
- [ ] Receipt or menu photo upload for consumer exposure reporting **[RFC]**

### Community

- [ ] Contributor mentorship program launched
- [ ] University partnership for student projects
- [ ] Public RFC process formalized

---

## Year 4 — Scaling & Sustainability

**Goal:** Expand reach, support international use, and establish long-term sustainability.

- [x] Internationalization (i18n) and localization framework
- [ ] Multi-tenant regional stack for multiple health departments sharing infrastructure
- [ ] Offline-first mobile refinements for low-connectivity and rural deployments
- [ ] Expanded sensor library and third-party integrations
- [ ] Sustainability mechanisms (support contracts, hosted analytics) — open governance required **[RFC]**
- [ ] Formal partnerships with national or international public health agencies

---

## How to Influence the Roadmap

- **Open an issue** tagged `roadmap` to propose a new item.
- **Comment on open RFCs** in GitHub Discussions.
- **Attend community calls** (schedule in `docs/community/`).
- **Join the TSC** — see `docs/governance/TSC.md` for membership criteria.

The TSC reviews the roadmap quarterly. Items can be reprioritized based on community needs, pilot feedback, and available contributors.
