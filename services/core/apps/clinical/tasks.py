"""Celery tasks for the clinical app."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def run_cluster_detection(self, lookback_days: int = 30):
    """
    Run the spatial-temporal clustering engine against recent clinical cases.

    Scheduled nightly via Celery Beat.  Can also be triggered manually:
        from apps.clinical.tasks import run_cluster_detection
        run_cluster_detection.delay()

    lookback_days controls how far back to scan (default 30 days).
    """
    try:
        from apps.clinical.clustering import detect_clusters
        result = detect_clusters(lookback_days=lookback_days)
        logger.info("Cluster detection result: %s", result)
        return result
    except Exception as exc:
        logger.error("Cluster detection failed: %s", exc)
        raise self.retry(exc=exc)
