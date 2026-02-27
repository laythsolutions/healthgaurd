# RFC-003: Sustainability Mechanisms for an Open-Source Food Safety Platform

**Status:** Draft
**Author:** Platform TSC
**Created:** 2026-02-25
**Target milestone:** Year 4

---

## Summary

This RFC defines the economic and governance mechanisms that will allow the food safety
intelligence platform to sustain itself long-term without compromising its open-source
character or creating conflicts of interest with the public health mission it serves.

---

## Problem Statement

Open-source public health infrastructure faces a structural tension: it must be free to
use (maximizing adoption in resource-constrained health departments), yet someone must
pay for ongoing engineering, security patches, and infrastructure.  Without a credible
sustainability model the project risks:

- Contributor burnout when volunteers shoulder production-grade SLAs
- Diverging forks as commercial adopters add proprietary features in private branches
- Abandonment at a critical moment (outbreak response, regulatory deadline)

This RFC proposes a **dual-track** model — open core + optional commercial layer —
deliberately designed so that the commercial track funds the open core rather than
threatening it.

---

## Proposed Sustainability Tracks

### Track 1 — Hosted Analytics (SaaS tier)

A managed cloud offering for health departments that cannot or do not want to self-host.
All data processing still happens under the subscribing health department's data-processing
agreement; the platform operator holds no proprietary claim to outbreak data.

**Tier structure:**

| Tier | Price signal | Included |
|------|-------------|---------|
| **Community** | Free | Self-hosted only; community support; Apache 2.0 |
| **Starter** | ~$200/mo per health dept | Hosted, 1 region, up to 500 monitored restaurants, email support |
| **Professional** | ~$600/mo | Hosted, multi-region, up to 5 000 restaurants, SLA 99.5%, priority support |
| **Enterprise** | Custom | Air-gapped option, HIPAA BAA, dedicated CSM, custom SLA |

All tiers use the identical open-source codebase.  No features are withheld behind a
paywall.  The commercial tiers sell **operations, reliability, and support** — not code.

**Revenue ring-fence commitment:**
≥ 40% of net SaaS revenue is contributed back to an open-source engineering fund
(see Governance section below).

---

### Track 2 — Support Contracts

Health departments and food-industry operators that self-host can purchase time-boxed
support agreements from a TSC-approved list of service providers.

**Support contract tiers:**

| Level | Scope |
|-------|-------|
| **Basic** | Business-hours ticket support, 72h SLA |
| **Standard** | Business-hours + emergency pager, 8h SLA, quarterly reviews |
| **Premium** | 24/7 pager, 4h SLA, dedicated engineer, custom integrations |

Service providers must:
- Be listed in `docs/community/service-providers.md`
- Pass a TSC vendor review (code quality + privacy assessment)
- Contribute back any generic bug-fixes or improvements they develop

The TSC charges a nominal **vendor registration fee** ($1 000 USD/year) to cover
review costs and list maintenance.

---

### Track 3 — Institutional Grants and Public Health Partnerships

Several funding sources are explicitly mission-aligned:

| Source | Instrument |
|--------|-----------|
| CDC / BARDA | Cooperative agreement for outbreak analytics tooling |
| WHO / PAHO  | Technical partnership for international deployment |
| Robert Wood Johnson Foundation | Public health technology grants |
| USDA NIFA   | Food safety research funding |
| EU Horizon  | Digital health research calls |

The TSC will maintain a grants pipeline document and designate a part-time grants
coordinator role (funded from SaaS revenue ring-fence in Year 2 of commercial operations).

---

### Track 4 — Hardware Partner Program

Zigbee/BLE sensor manufacturers and MQTT gateway vendors can be listed as **Certified
Compatible Hardware** after passing an interoperability test suite (see
`gateway/tests/interop/`).

Certification is free.  An optional **Preferred Partner** tier ($3 000/year) provides:
- Logo placement in documentation and the web portal
- Early access to new sensor API drafts
- Co-marketing opportunities

No hardware vendor receives exclusive status or API advantages.

---

## Governance: Open-Source Engineering Fund

The engineering fund is the mechanism that translates commercial revenue into open-source
value.  It operates under the Technical Steering Committee (TSC) with full public
transparency.

### Fund operations

- **Inflows:** SaaS ring-fence (40%+), vendor registration fees, grant overhead
- **Outflows:** Paid maintainer stipends, security audits, infrastructure costs,
  conference representation, bounty program
- **Accounting:** Quarterly treasurer report published in `docs/governance/fund/`
- **Decisions:** Expenditures > $5 000 require TSC vote (simple majority)

### Paid maintainer program

| Role | Hours/week | Stipend |
|------|-----------|---------|
| Core maintainer (2 positions) | 20h | $4 000/mo each |
| Security maintainer (1) | 10h | $2 500/mo |
| Documentation lead (1) | 10h | $2 000/mo |

Maintainer stipends are funded only after the fund reaches a 6-month runway reserve.

### Conflict-of-interest policy

1. TSC members employed by a Preferred Partner or SaaS customer must recuse from votes
   that directly affect that relationship.
2. No single commercial entity may hold more than 2 of 7 TSC seats.
3. The TSC chair may not be employed by a commercial service provider.
4. Fund financial records are published within 30 days of each quarter-end.

---

## Open Core Guarantee

To prevent scope creep into a proprietary model, the following are permanently
in-scope for the Apache 2.0 open-source release:

- All outbreak investigation and cluster detection algorithms
- All IoT sensor ingestion and compliance rule engines
- All data anonymization and privacy tooling
- All API endpoints consumed by health departments and medical institutions
- The full mobile app (Flutter)
- All documentation and schemas

The following **may** be offered exclusively in the hosted tier (not open-sourced):

- Multi-region automated failover orchestration (Helm chart extensions)
- White-label portal theming
- Managed Zigbee gateway provisioning scripts (vendor-specific)

Any addition to the "hosted-only" list requires a TSC vote with a 60% supermajority
and a 30-day public comment period.

---

## Implementation Plan

| Milestone | Deliverable |
|-----------|-------------|
| Q1 Year 4 | Legal entity formation (US 501(c)(6) or fiscal sponsorship via NumFOCUS) |
| Q1 Year 4 | Service provider registry + vendor review checklist |
| Q2 Year 4 | SaaS MVP on a shared k8s cluster (us-east-1, eu-central-1) |
| Q2 Year 4 | First Certified Compatible Hardware listings |
| Q3 Year 4 | Paid maintainer stipend program launch |
| Q4 Year 4 | First quarterly fund transparency report |

---

## Alternatives Considered

### Open Collective only
Relies entirely on voluntary donations.  Historically insufficient for infrastructure
projects of this complexity; does not fund full-time maintainers.

### Dual license (AGPL + commercial)
Stronger copyleft can deter adoption by public health agencies that run on legacy IT
stacks and cannot share internal infrastructure code.  Ruled out in favor of Apache 2.0
which maximises government adoption.

### VC-backed company
Creates misaligned incentives (growth over public health mission, investor exit
pressure).  Explicitly excluded.

---

## Open Questions

1. Should fiscal sponsorship (NumFOCUS / Linux Foundation Public Health) be preferred
   over direct legal entity formation?  Lower overhead but less control over brand.
2. What is the right ring-fence percentage?  40% is a proposal; TSC should set this
   based on Year-1 SaaS revenue projections.
3. HIPAA BAA for Enterprise tier requires a HIPAA-compliant hosting partner.  Who is
   preferred (AWS GovCloud, Azure Government, Google Public Sector)?

---

## References

- Apache 2.0 license — `LICENSE`
- Governance structure — `docs/governance/`
- TSC membership criteria — `docs/governance/TSC.md`
- Vendor registration — `docs/community/service-providers.md`
- OpenSSF Scorecard — planned in `devops/`
- NumFOCUS fiscal sponsorship — https://numfocus.org/sponsored-projects/applying
