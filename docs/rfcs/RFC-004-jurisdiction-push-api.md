# RFC-004: Jurisdiction Push API for Inspection Data Submission

**Status:** Accepted — Implemented
**Author(s):** Core maintainers
**Created:** 2026-02-26
**Updated:** 2026-02-26

---

## Summary

Introduce a push API (`apps/submissions`) that allows health departments without
open-data portals to submit inspection records directly to the platform. Jurisdictions
register, receive a scoped API key, and POST batches of up to 500 records per request.
The platform normalises the records using a per-jurisdiction schema map and score system,
then ingests them through the existing `ingest_inspection_record()` pipeline.

---

## Motivation

The current harvester model (scraping public open-data portals) only reaches
jurisdictions that publish structured data online. Approximately **2,000+ US counties
and cities** have no open-data portal. These jurisdictions — disproportionately rural
and under-resourced — are invisible in the platform's inspection dataset, creating
systematic blind spots in outbreak detection.

A lightweight push API with a simple JSON contract lowers the barrier to contribution:
a health department's IT staff needs only an HTTP client and the ability to transform
their existing inspection database exports into a standard JSON format.

---

## Scope

| In scope | Out of scope |
|----------|--------------|
| JSON batch submission (up to 500 records) | CSV file upload (future RFC) |
| Per-jurisdiction schema mapping | Real-time streaming ingest |
| Score/grade normalisation (4 systems) | Full EHR/HL7 integration |
| HMAC-signed webhook callbacks | Bi-directional sync |
| Admin approval workflow | Self-service key rotation UI |
| Idempotent ingest (fingerprint dedup) | Multi-key per jurisdiction |

---

## Detailed Design

### Authentication

Jurisdictions authenticate with a static `X-Submission-Key: hg_live_<...>` header.
Keys are scoped to `submissions:write` and checked by
`SubmissionAPIKeyAuthentication` in `auth.py`:

1. Read `X-Submission-Key` header.
2. SHA-256 hash the raw key.
3. Look up `APIKey` with `key_hash=hash AND scopes__contains='submissions:write' AND is_active=True`.
4. Verify expiry and optional IP allowlist.
5. Stamp `last_used_at`.

Keys are issued only after admin approval; the plaintext key is shown once in the
approval response and never stored in the database (only the SHA-256 hash is persisted).

### Registration Flow

```
Jurisdiction                    Platform                     Admin
    │                               │                           │
    │  POST /submissions/register/  │                           │
    │ ─────────────────────────────>│ JurisdictionAccount       │
    │                               │ status=PENDING            │
    │  201 {id, status=PENDING}     │                           │
    │ <─────────────────────────────│                           │
    │                               │  Notification             │
    │                               │ ─────────────────────────>│
    │                               │  POST /admin/.../review/  │
    │                               │ <─────────────────────────│
    │                               │ Creates APIKey            │
    │                               │ status=ACTIVE             │
    │                               │  200 {api_key: hg_live_}  │
    │                               │ ─────────────────────────>│
    │       Email: api_key          │                           │
    │ <─────────────────────────────────────────────────────────│
```

### Data Format

The submission endpoint accepts:

```json
{
  "records": [
    {
      "restaurant_name": "Taco Palace",
      "address": "123 Main St",
      "city": "Phoenix",
      "inspected_at": "2024-03-15",
      "score": 88,
      "violations": [
        {
          "code": "4-601.11",
          "description": "Food contact surfaces not clean",
          "severity": "minor"
        }
      ]
    }
  ]
}
```

Required per record: `restaurant_name`, `address`, `inspected_at`.

### Schema Mapping

Jurisdictions whose export format uses different field names configure a
`schema_map` JSON dict on their account:

```json
{
  "facility_name":    "restaurant_name",
  "inspection_date":  "inspected_at",
  "street_address":   "address",
  "violation_type":   "severity"
}
```

`apply_schema_map()` renames keys before normalisation. Unmapped keys pass
through unchanged, so jurisdictions can include supplementary data without
breakage.

### Score Normalisation

Four scoring systems are supported, selected per jurisdiction at registration:

| System | Input example | Output score | Output grade |
|--------|--------------|-------------|-------------|
| `SCORE_0_100` | `"88"` | 88 | B |
| `GRADE_A_F` | `"A"` | 95 | A |
| `PASS_FAIL` | `"pass"` | 100 | A |
| `LETTER_NUMERIC` | `"85"` or `"B"` | 85 / 82 | B |

Grade bands for numeric scores: ≥90 → A, ≥80 → B, ≥70 → C, else → X.

### Batch Processing

Batches are processed asynchronously by the `process_submission_batch` Celery
task (max 2 retries, 60 s delay). The pipeline per row:

1. `apply_schema_map(row, jurisdiction.schema_map)`
2. `normalize_score(raw, jurisdiction.score_system)`
3. `ingest_inspection_record(normalized)` — creates Restaurant + Inspection + Violations, deduplicates by restaurant+date+jurisdiction fingerprint.

Row-level errors are accumulated in `SubmissionBatch.row_errors` and returned
via `GET /submissions/batches/{id}/`. A batch is `FAILED` only if **every** row
errors; partial success counts as `COMPLETE`.

### Webhook Callbacks

If a `webhook_url` is configured, `deliver_webhook` POSTs a JSON summary to the
endpoint after the batch completes:

```json
{
  "batch_id": 42,
  "fips_code": "04013",
  "status": "COMPLETE",
  "total_rows": 150,
  "created_count": 148,
  "skipped_count": 2,
  "error_count": 0,
  "completed_at": "2024-03-15T14:32:00Z"
}
```

The request includes an HMAC-SHA256 signature header:

```
X-Submission-Signature: sha256=<hex-digest>
```

Recipients should verify the signature using the platform's `SECRET_KEY` to
confirm authenticity before processing the payload.

Webhook delivery retries up to 3 times with 60-second delays.

---

## Security Considerations

### Key issuance
- Keys are issued only after manual admin review — no self-service provisioning.
- The plaintext key is returned once in the approval response; subsequent reads of
  the `JurisdictionAccount` never expose it.
- Keys can be invalidated by setting `APIKey.is_active=False` in the admin.

### IP allowlisting
`APIKey.allowed_ips` accepts CIDR ranges. Health departments with static outbound
IPs should configure this to prevent key theft from being exploitable.

### Rate limiting
`submission_bulk: 10/hour` caps the data throughput per key. At 500 rows/request,
a jurisdiction can push up to 5,000 records per hour — sufficient for nightly
batch exports from all but the largest state agencies.

### Webhook validation
Recipients must verify `X-Submission-Signature` before trusting callback payloads.
Reference verification:

```python
import hashlib, hmac
expected = hmac.new(SECRET_KEY.encode(), body, hashlib.sha256).hexdigest()
assert hmac.compare_digest(f"sha256={expected}", request.headers["X-Submission-Signature"])
```

### Data validation
- Records missing `restaurant_name`, `address`, or `inspected_at` are rejected at
  serializer validation (before any DB writes).
- Scores outside 0–100 after normalisation are discarded (row skipped, not errored).
- Ingestion is wrapped in `@transaction.atomic` — a crash mid-row leaves no partial state.

---

## Throttle Rates

| Scope | Rate | Applied to |
|-------|------|-----------|
| `submission_register` | 5 / hour | `POST /submissions/register/` (anon IP) |
| `submission_bulk` | 10 / hour | `POST /submissions/inspections/` (per key) |

---

## Alternatives Considered

### SFTP / file drop
SFTP would accommodate CSV exports without requiring jurisdictions to write HTTP
clients. However it requires infrastructure (SSH keys, shared storage) and is harder
to make idempotent. The `retail_connector.py` SFTPConnector in RFC-002 covers this
pattern for retail partners; a future RFC can add CSV submission.

### Federated scraping
Instead of a push API, we could scrape jurisdiction-specific internal systems.
This requires per-jurisdiction scraper maintenance and raises legal questions around
authorised access. The push model puts control firmly with the jurisdiction.

### Full FHIR/HL7 integration
FHIR R4 `Bundle` resources could standardise the exchange format. The overhead of
FHIR parsing is unnecessary for the simple tabular inspection data being exchanged
here. A FHIR profile can be defined as a future mapping on top of this RFC.

---

## Migration

`submissions.0001_initial` creates:
- `submission_jurisdiction_accounts` — depends on `accounts.0001_initial`
- `submission_batches`

No changes to existing tables.

---

## Future Work

- **CSV upload** — accept multipart `text/csv` and parse server-side before the
  normalization pipeline.
- **Self-service key rotation** — admin UI or `POST /submissions/keys/rotate/`.
- **Per-jurisdiction schema validation UI** — a dry-run endpoint that returns
  normalisation preview without writing to the DB.
- **Webhook retry dashboard** — expose `webhook_delivered` / `webhook_delivered_at`
  in the portal so jurisdictions can see delivery status.
- **State-level bulk onboarding** — a state agency submits on behalf of all its
  counties with a single key; county FIPs disambiguates at the record level.

---

## References

- `services/core/apps/submissions/` — implementation
- `apps/inspections/utils.py` — `ingest_inspection_record()` (reused unchanged)
- `apps/accounts/models.py` — `APIKey` model (reused unchanged)
- RFC-002: Retail Transaction Pipeline — SFTP connector pattern
- RFC-001: Consumer Exposure Reporting — anonymous public endpoint pattern
