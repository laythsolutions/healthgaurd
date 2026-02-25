"""
Celery tasks for the inspections app.

ingest_state_inspections:
    Calls the intelligence service's /api/v1/harvest/records/{state} endpoint,
    then writes each InspectionRecord dict to the core database via ingest_inspection_record().
    Registered in Celery Beat for nightly runs (see settings.CELERY_BEAT_SCHEDULE).
"""

import logging

import httpx
from celery import shared_task
from django.conf import settings

from .utils import ingest_inspection_record

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def ingest_state_inspections(self, state: str, days_back: int = 1) -> dict:
    """
    Fetch harvested inspection records from the intelligence service
    and write them to the core database.

    Args:
        state: Two-letter state code (e.g. 'CA', 'IL') or 'NYC'.
        days_back: How many days of records to fetch.

    Returns:
        dict with keys: state, created, skipped.
    """
    intel_url = getattr(settings, "INTELLIGENCE_SERVICE_URL", "http://intelligence:8001")

    try:
        resp = httpx.get(
            f"{intel_url}/api/v1/harvest/records/{state}",
            params={"days_back": days_back},
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.error(
            "[ingest_state_inspections] Failed to fetch from intelligence for %s: %s",
            state, exc,
        )
        raise self.retry(exc=exc)

    records = data.get("records", [])
    created = 0
    skipped = 0

    for record in records:
        try:
            result = ingest_inspection_record(record)
            if result is not None:
                created += 1
            else:
                skipped += 1
        except Exception as exc:
            logger.warning("[ingest_state_inspections] Failed to ingest record: %s", exc)
            skipped += 1

    logger.info(
        "[ingest_state_inspections] %s: created=%d, skipped=%d",
        state, created, skipped,
    )
    return {"state": state, "created": created, "skipped": skipped}
