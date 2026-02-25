# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` (latest) | Yes |
| Previous releases | Security backports on a best-effort basis |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Because healthgaurd handles sensitive public health data, we take security reports seriously and aim to respond quickly.

### How to report

1. **Email:** Send a description to **security@[project-domain]** with the subject line `[SECURITY] Brief description`.
2. **Include:**
   - Description of the vulnerability and its potential impact
   - Steps to reproduce or a proof-of-concept (without causing harm)
   - Affected component(s) and version(s)
   - Your contact information for follow-up

We use GPG encryption for sensitive reports. Public key available at **security@[project-domain]**.

### What to expect

| Timeline | Action |
|----------|--------|
| Within 48 hours | Acknowledgment of your report |
| Within 7 days | Initial assessment and severity classification |
| Within 30 days | Patch developed and tested (critical/high) |
| Within 90 days | Public disclosure after fix is released |

We will keep you informed throughout the process and credit you in the security advisory unless you prefer to remain anonymous.

## Disclosure Policy

We follow **coordinated disclosure**:

1. You report the vulnerability privately.
2. We validate and develop a fix.
3. We release the fix and publish a GitHub Security Advisory.
4. You may publish your own write-up after the advisory is public.

We ask that you give us a reasonable amount of time to resolve the issue before any public disclosure.

## Scope

**In scope:**
- Authentication and authorization flaws
- Data exposure or leakage (especially health or PII data)
- Injection vulnerabilities (SQL, command, etc.)
- Broken access controls between roles (public, restaurant, health dept, clinical)
- IoT gateway security issues (unauthorized command execution, firmware tampering)
- Cryptographic weaknesses
- Consent bypass or privacy control failures

**Out of scope:**
- Denial-of-service attacks
- Social engineering of maintainers or staff
- Vulnerabilities in third-party dependencies (report to the dependency maintainer directly)
- Issues in infrastructure we don't control

## Security Architecture Overview

Key security controls in place:

- **Auth:** JWT + OIDC, MFA required for health department and clinical roles
- **Data at rest:** Encrypted volumes; database-level encryption for clinical records
- **Data in transit:** TLS 1.2+ enforced on all endpoints
- **Privacy:** PII stripped before storage; geohash encoding for locations; consent tracked per data subject
- **IoT:** RSA-signed firmware updates; mutual TLS on MQTT; gateway auth tokens rotated regularly
- **DevSecOps:** Dependency scanning (Dependabot), static analysis, signed container images, SBOMs on releases

## Bug Bounty

We do not currently operate a paid bug bounty program. We recognize contributors in our security advisories and project credits.
