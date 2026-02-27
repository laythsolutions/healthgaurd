# RFC-001: Consumer Exposure Reporting via Receipt/Photo Upload

**Status:** Accepted — Implemented
**Author(s):** Core maintainers
**Created:** 2026-02-25
**Updated:** 2026-02-25

---

## Summary

Add an anonymous public endpoint that accepts a photo (restaurant receipt or menu) and brief symptom report from a consumer. Extracted exposure data feeds into the clinical clustering pipeline as low-confidence signals, improving outbreak detection speed without requiring clinical reporting.

## Motivation

Most foodborne illness cases are never reported to health departments. Consumers who experience symptoms after eating at a restaurant have no lightweight way to contribute that information. Even noisy, unverified signals — aggregated across many reports — can accelerate cluster detection by days compared to waiting for clinical submissions alone.

## Detailed Design

### Endpoint

```
POST /api/v1/public/exposure-reports/
Content-Type: multipart/form-data
```

**Fields:**
- `photo` (optional, file) — JPEG/PNG/HEIC receipt or menu image, max 10 MB
- `restaurant_name` (string, optional if photo provided)
- `restaurant_address` (string, optional)
- `visit_date` (date, ISO 8601)
- `symptoms` (array of strings, from controlled vocabulary)
- `onset_date` (date, optional)
- `severity` (enum: mild | moderate | severe)

No account required. No IP address stored.

**Response:** `201 Created` with an anonymous report ID (UUID). No personal data echoed back.

### Privacy Controls

- EXIF metadata stripped from all uploaded images before storage (using `Pillow`)
- Photo stored in a separate, restricted-access bucket; not exposed via any API
- OCR runs server-side for restaurant name extraction only; raw image deleted after 24 hours
- `restaurant_name` and `restaurant_address` are fuzzy-matched to the establishment registry — only the matched `restaurant_id` is stored, not the raw text
- No cookies, no session, no user agent stored
- Rate limited: 3 reports per IP per hour (IP checked in Redis, not stored in DB)

### Data Model

New model `ConsumerExposureReport`:

```python
class ConsumerExposureReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    restaurant = models.ForeignKey(Restaurant, null=True, on_delete=models.SET_NULL)
    visit_date = models.DateField()
    onset_date = models.DateField(null=True)
    symptoms = ArrayField(models.CharField(max_length=64))
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES)
    location_geohash = models.CharField(max_length=8, null=True)  # from restaurant, not reporter
    confidence = models.CharField(default='consumer', max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    # No user FK, no IP, no photo path after 24h purge
```

Data classification: **internal** (not PHI — no individual is identified).

### Clustering Integration

`ConsumerExposureReport` records feed into `detect_clusters()` in `clinical/clustering.py` as exposure signals with `confidence='consumer'` weight 0.3 (vs. 1.0 for clinically confirmed cases). A cluster that would not meet the `MIN_CASES=3` threshold from clinical reports alone may be elevated to an investigation if consumer reports corroborate the pattern.

### Photo Storage

- S3-compatible object store (MinIO for self-hosted, configurable for AWS S3 / GCS)
- Bucket policy: private, no public access
- Server-side encryption at rest
- 24-hour lifecycle rule deletes originals after OCR extraction

## Alternatives Considered

**Require account registration** — Rejected. Friction eliminates most consumer reports. Anonymous submission is the only realistic path to volume.

**No photo, text-only** — Acceptable fallback. Photo upload is optional; the endpoint works without it. OCR is a nice-to-have for reducing manual restaurant matching.

**Store reports as clinical cases** — Rejected. Consumer reports are unverified. Mixing them with clinical data degrades analytical quality. Separate model with explicit confidence level is the right approach.

## Drawbacks

- Spam and false reports are a real risk. Mitigation: rate limiting + restaurant fuzzy-match means random noise won't cluster on a real location.
- OCR adds a dependency (Tesseract or cloud Vision API). Self-hosted deployments must install Tesseract; cloud Vision API requires configuration.
- Photo storage adds infrastructure complexity for self-hosted deployments.

## Privacy & Security Impact

- No new personal data collected (no name, no email, no IP stored).
- Photo is the most sensitive element — EXIF stripping and 24-hour deletion are mandatory, not optional.
- Restaurant match via fuzzy search means a misspelled name results in `restaurant=NULL`, which is stored but doesn't link to a real establishment — acceptable.
- Requires Security & Privacy Board review before TSC vote.

## Open Questions

1. Should OCR be required (hard dependency on Tesseract) or optional with a fallback to manual name entry only?
2. What is the right weight for consumer reports in the clustering algorithm? 0.3 is a starting estimate.
3. Should reports be surfaced to health departments via the portal? If so, under what aggregation threshold?
4. 24-hour photo deletion — should this be configurable for jurisdictions that want a longer audit trail?

## References

- Related issues: (open one at https://github.com/[org]/[repo]/issues)
- Clustering engine: `services/core/apps/clinical/clustering.py`
- Privacy classification: `services/core/apps/privacy/classification.py`
