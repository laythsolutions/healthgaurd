# Contributing to healthgaurd

Thank you for your interest in contributing! healthgaurd is a community-driven open-source project. Every contribution — whether code, documentation, testing, design, or domain expertise — makes the platform more valuable for public health.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Security Vulnerabilities](#security-vulnerabilities)
- [Community](#community)

---

## Code of Conduct

All participants are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

---

## Ways to Contribute

- **Code:** New features, bug fixes, performance improvements.
- **Documentation:** Tutorials, API docs, architecture diagrams, translations.
- **Testing:** Writing tests, testing on different platforms, reporting bugs.
- **Design:** UX/UI improvements, accessibility audits, data visualization.
- **Domain expertise:** Epidemiology, food safety regulation, clinical informatics, IoT.
- **Community:** Answering questions, triaging issues, mentoring new contributors.

---

## Getting Started

### 1. Fork and clone

```bash
git clone https://github.com/laythsolutions/healthgaurd.git
cd healthgaurd
```

### 2. Set up the development environment

```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your local settings

# Start the full stack
docker compose -f docker-compose.dev.yml up -d

# Services will be available at:
# API:           http://localhost:8000
# API Docs:      http://localhost:8000/api/docs
# Web Dashboard: http://localhost:3000
# MQTT Broker:   mqtt://localhost:1883
```

### 3. Find an issue to work on

- Browse [good first issues](https://github.com/laythsolutions/healthgaurd/labels/good%20first%20issue) for newcomers.
- Browse [help wanted](https://github.com/laythsolutions/healthgaurd/labels/help%20wanted) for more complex tasks.
- Comment on the issue to let maintainers know you're working on it.

---

## Development Workflow

```
main ← feature/your-feature-name
```

1. Create a branch from `main`:
   ```bash
   git checkout -b feature/short-description
   ```
2. Make your changes with focused, atomic commits.
3. Run tests locally before pushing (see [Testing Requirements](#testing-requirements)).
4. Push your branch and open a pull request.

---

## Pull Request Process

1. **Fill out the PR template** — describe what changed and why.
2. **Link the related issue** with `Closes #123` or `Fixes #123` in the PR description.
3. **Pass all CI checks** — lint, tests, and build must be green.
4. **Request a review** from at least one maintainer.
5. **Address review feedback** promptly. PRs inactive for 30 days will be closed.
6. A maintainer will merge once approved.

### PR checklist

- [ ] Tests added or updated for new behavior
- [ ] Documentation updated if the interface changed
- [ ] No new secrets or credentials committed
- [ ] Privacy implications considered (does this touch PII or health data?)

---

## Coding Standards

### Python (backend services)

- Style: [Black](https://black.readthedocs.io/) + [isort](https://pycog.readthedocs.io/en/stable/isort.html)
- Linting: [Ruff](https://docs.astral.sh/ruff/)
- Type hints required for all public functions.
- Docstrings for modules and non-trivial functions (Google style).

```bash
# From services/core/
black . && isort . && ruff check .
```

### TypeScript / React (web)

- Style: [Prettier](https://prettier.io/) + [ESLint](https://eslint.org/)
- Strict TypeScript — no `any` without justification.

```bash
# From web/
npm run lint && npm run type-check
```

### Dart / Flutter (mobile)

```bash
# From mobile/
flutter analyze && flutter format .
```

---

## Testing Requirements

All PRs must maintain or improve test coverage.

| Service | Test runner | Minimum coverage |
|---------|-------------|-----------------|
| `services/core` | `pytest` | 80% |
| `services/intelligence` | `pytest` | 70% |
| `web` | `jest` + `playwright` | 70% |
| `mobile` | `flutter test` | 70% |
| `gateway` | `pytest` | 70% |

```bash
# Backend
cd services/core && pytest --cov=. --cov-report=term-missing

# Frontend
cd web && npm test

# Mobile
cd mobile && flutter test
```

---

## Security Vulnerabilities

**Do not open a public GitHub issue for security vulnerabilities.**

Report security issues via the private process described in [SECURITY.md](SECURITY.md). This ensures vulnerabilities are addressed before they are publicly disclosed.

---

## Community

- **GitHub Discussions:** questions, ideas, architecture proposals.
- **Community calls:** held monthly — schedule in `docs/community/`.
- **Mailing list:** announcements and release notes.

We especially welcome contributors with backgrounds in:
- Public health and epidemiology
- Food safety regulation (FDA, USDA, state health departments)
- Clinical informatics and EHR systems
- IoT and embedded systems
- Privacy-preserving computation

---

*By contributing, you agree that your contributions will be licensed under the [Apache 2.0 License](LICENSE).*
