# healthgaurd

> An open-source food safety intelligence platform — connecting restaurant inspections, IoT sensor monitoring, recall tracking, and clinical outbreak detection into a single, privacy-first system built for public health.

[![CI](https://github.com/laythsolutions/healthgaurd/actions/workflows/ci.yml/badge.svg)](https://github.com/laythsolutions/healthgaurd/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## What this is

healthgaurd is an open-source platform that aggregates data from health department inspections, IoT sensors in food service establishments, FDA/USDA recall feeds, clinical case reports, and retail supply chains — then applies analytics to detect patterns that no single data source can reveal alone.

It is designed to be deployable by local health departments, academic public health programs, and civic technology organizations. All health and personal data is anonymized at ingestion; consent is tracked per data subject; and every component is auditable by the community.

**What it is not:** a commercial product, a replacement for regulatory authority, or a complete epidemiological investigation platform on its own. It is infrastructure and tooling that makes investigation faster and more data-driven.

---

## Key capabilities

| Capability | Description |
|---|---|
| Restaurant intelligence | Registry, inspection history, violation tracking, grade display |
| IoT monitoring | Real-time temperature, door, leak, and fryer oil sensors; predictive failure alerts |
| Recall tracking | FDA/USDA feed ingestion, lot matching, affected-location mapping, remediation workflow |
| Clinical reporting | Anonymized case submission from EDs and labs; cluster threshold alerting |
| Outbreak analytics | Spatial-temporal clustering, odds ratio calculations, supply chain traceback |
| Public transparency | Searchable restaurant grades, anonymized outbreak advisories, public API |
| Privacy by default | PII stripping, geohash encoding, consent management, audit logging |

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                             │
│  Health dept APIs  │  FDA/USDA feeds  │  IoT sensors  │  EHRs  │
└──────────┬──────────────────┬──────────────────┬────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                    services/intelligence                         │
│          Ingestion connectors · Schema validation                │
│          Retry / backoff · Idempotency · Provenance logging      │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                      services/core                               │
│  Privacy & Anonymization  │  Core Data Service  │  Analytics     │
│  (PII strip, geohash,     │  (restaurants,      │  (clustering,  │
│   consent management)     │   sensors, recalls, │   traceback,   │
│                           │   clinical cases)   │   IoT models)  │
│                       ────┤                     │                │
│                Notification & Workflow Service                   │
│          (alerts, recall ACK, remediation tasks)                 │
└───────────┬──────────────────────────────────────────────────────┘
            │
     ┌──────┴──────┐
     ▼             ▼
┌─────────┐  ┌────────────────────────────────────────────────────┐
│ gateway │  │                      web / mobile                  │
│ (edge)  │  │  Public app  │  Restaurant dash  │  Health dept    │
│ Pi+MQTT │  │              │                   │  portal         │
└─────────┘  └────────────────────────────────────────────────────┘
```

---

## Repository structure

```
healthgaurd/
├── services/
│   ├── core/           # Django REST API — auth, restaurants, sensors,
│   │                   #   alerts, analytics, reports, OTA
│   └── intelligence/   # Data harvesters, recall connectors,
│                       #   risk scoring, real-time monitors
├── gateway/            # Raspberry Pi edge software — MQTT bridge,
│                       #   Zigbee/Bluetooth drivers, OTA client
├── web/                # Next.js — public app, restaurant dashboard,
│                       #   health department portal
├── mobile/             # Flutter — QR scan, push alerts, offline cache
├── schemas/            # Shared OpenAPI specs and JSON Schema definitions
├── devops/
│   ├── k8s/            # Kubernetes manifests (Helm charts coming)
│   ├── monitoring/     # Prometheus, Grafana, Alertmanager configs
│   ├── mosquitto/      # MQTT broker configuration
│   └── scripts/        # Deployment and maintenance scripts
└── docs/               # Architecture docs, governance, tutorials
```

---

## Quick start (development)

**Prerequisites:** Docker, Docker Compose, Git.

```bash
git clone https://github.com/laythsolutions/healthgaurd.git
cd healthgaurd

cp .env.example .env
# Edit .env — at minimum set SECRET_KEY, POSTGRES_PASSWORD, TIMESCALEDB_PASSWORD

docker compose -f docker-compose.dev.yml up -d
```

Services:

| Service | URL |
|---|---|
| REST API | http://localhost:8000 |
| Interactive API docs | http://localhost:8000/api/docs |
| Web dashboard | http://localhost:3000 |
| MQTT broker | mqtt://localhost:1883 |

Run backend tests:

```bash
docker compose -f docker-compose.dev.yml exec cloud-api pytest
```

Run frontend tests:

```bash
cd web && npm test
```

See [`docs/development/`](docs/development/) for more detailed setup, including edge gateway emulation and sensor simulation.

---

## Tech stack

| Layer | Technologies |
|---|---|
| Backend API | Django 4.2, Django REST Framework, TimescaleDB, PostgreSQL, Celery, Redis |
| Data services | Python 3.11, FastAPI, Pandas, Scikit-learn, async HTTP |
| Web frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui |
| Mobile | Flutter 3, Dart, Riverpod, SQLite |
| Edge / IoT | Python 3.11, Mosquitto MQTT, Zigbee2MQTT, Docker Compose |
| Infrastructure | Kubernetes, Prometheus, Grafana, GitHub Actions |

---

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the full multi-year plan. High-level milestones:

- **Year 1 (Foundation):** Core backend, inspection ingestion, privacy service, public web app, IoT gateway — [in progress]
- **Year 2 (Integration):** Clinical reporting, recall supply chain, health department portal, security hardening
- **Year 3 (Analytics & Pilots):** Cluster detection, traceback, first real-world pilots, public API
- **Year 4 (Scale):** Internationalization, multi-tenant deployments, sustainability

---

## Contributing

We welcome contributions of all kinds — code, documentation, testing, design, and domain expertise (epidemiology, food safety regulation, clinical informatics, IoT).

Start with [`CONTRIBUTING.md`](CONTRIBUTING.md). Good first issues are tagged [`good first issue`](https://github.com/laythsolutions/healthgaurd/labels/good%20first%20issue).

---

## Governance

healthgaurd is governed by:

- **Technical Steering Committee (TSC)** — roadmap and major decisions
- **Security & Privacy Board** — vulnerability response and data policy
- **Community Council** — voice of end users and domain stakeholders

Governance documents are in [`docs/governance/`](docs/governance/).

---

## Security

Please do not open public issues for security vulnerabilities. See [`SECURITY.md`](SECURITY.md) for the private reporting process and response timelines.

---

## License

[Apache 2.0](LICENSE). Copyright 2026 healthgaurd Contributors.
