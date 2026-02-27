"""
Celery tasks for the submissions app.

process_submission_batch — normalize + ingest a batch of jurisdiction records
deliver_webhook          — POST result summary to jurisdiction's webhook URL
"""

import hashlib
import hmac
import json
import logging

import httpx
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def process_submission_batch(self, batch_id: int) -> dict:
    """
    Normalize and ingest all rows in a SubmissionBatch.

    Sets batch.status → PROCESSING, then iterates raw_payload rows,
    calling normalize_record() + ingest_inspection_record() for each.
    On completion stamps status → COMPLETE (or FAILED if every row errored)
    and fires deliver_webhook if a webhook_url is configured.
    """
    from apps.submissions.models import SubmissionBatch
    from apps.submissions.normalization import normalize_record
    from apps.inspections.utils import ingest_inspection_record

    try:
        batch = SubmissionBatch.objects.select_related("jurisdiction").get(pk=batch_id)
    except SubmissionBatch.DoesNotExist:
        logger.error("[submissions] Batch %s not found", batch_id)
        return {"error": "batch_not_found"}

    batch.status = SubmissionBatch.Status.PROCESSING
    batch.save(update_fields=["status"])

    jurisdiction = batch.jurisdiction
    rows = batch.raw_payload or []
    created = 0
    skipped = 0
    error_count = 0
    row_errors = []

    for idx, row in enumerate(rows):
        try:
            normalized = normalize_record(row, jurisdiction)
            result = ingest_inspection_record(normalized)
            if result is not None:
                created += 1
            else:
                skipped += 1
        except Exception as exc:
            error_count += 1
            row_errors.append({"row": idx, "reason": str(exc)})
            logger.warning("[submissions] Batch %s row %d error: %s", batch_id, idx, exc)

    total = len(rows)
    if error_count == total and total > 0:
        final_status = SubmissionBatch.Status.FAILED
    else:
        final_status = SubmissionBatch.Status.COMPLETE

    batch.status        = final_status
    batch.created_count = created
    batch.skipped_count = skipped
    batch.error_count   = error_count
    batch.row_errors    = row_errors
    batch.completed_at  = timezone.now()
    batch.save(update_fields=[
        "status", "created_count", "skipped_count",
        "error_count", "row_errors", "completed_at",
    ])

    logger.info(
        "[submissions] Batch %s complete: created=%d skipped=%d errors=%d",
        batch_id, created, skipped, error_count,
    )

    if jurisdiction.webhook_url:
        deliver_webhook.delay(batch_id)

    return {
        "batch_id":     batch_id,
        "status":       final_status,
        "created":      created,
        "skipped":      skipped,
        "error_count":  error_count,
    }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def deliver_webhook(self, batch_id: int) -> dict:
    """
    POST a JSON summary to the jurisdiction's webhook_url.

    Signs the payload with HMAC-SHA256 using SECRET_KEY and sends the
    signature in the X-Submission-Signature header so the recipient can
    verify authenticity.
    """
    from apps.submissions.models import SubmissionBatch

    try:
        batch = SubmissionBatch.objects.select_related("jurisdiction").get(pk=batch_id)
    except SubmissionBatch.DoesNotExist:
        logger.error("[webhook] Batch %s not found", batch_id)
        return {"error": "batch_not_found"}

    webhook_url = batch.jurisdiction.webhook_url
    if not webhook_url:
        return {"skipped": "no webhook_url"}

    payload = {
        "batch_id":      batch.pk,
        "fips_code":     batch.jurisdiction.fips_code,
        "status":        batch.status,
        "total_rows":    batch.total_rows,
        "created_count": batch.created_count,
        "skipped_count": batch.skipped_count,
        "error_count":   batch.error_count,
        "completed_at":  batch.completed_at.isoformat() if batch.completed_at else None,
    }
    body = json.dumps(payload, default=str).encode()

    secret = settings.SECRET_KEY.encode()
    signature = hmac.new(secret, body, hashlib.sha256).hexdigest()

    try:
        resp = httpx.post(
            webhook_url,
            content=body,
            headers={
                "Content-Type":          "application/json",
                "X-Submission-Signature": f"sha256={signature}",
            },
            timeout=10.0,
        )
        resp.raise_for_status()
    except Exception as exc:
        logger.warning("[webhook] Batch %s delivery failed: %s", batch_id, exc)
        raise self.retry(exc=exc)

    from django.utils import timezone as tz
    SubmissionBatch.objects.filter(pk=batch_id).update(
        webhook_delivered=True,
        webhook_delivered_at=tz.now(),
    )
    logger.info("[webhook] Batch %s delivered to %s", batch_id, webhook_url)
    return {"delivered": True}
