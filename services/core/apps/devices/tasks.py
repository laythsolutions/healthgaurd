"""Celery tasks for the devices app."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)

# Risk level → device status mapping for automatic status updates
_RISK_TO_STATUS = {
    "critical": "MAINTENANCE",
    "high":     "MAINTENANCE",
}


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def update_device_risk_scores(self):
    """
    Scan all active devices, compute failure risk scores, and update device
    status to MAINTENANCE when risk is critical/high.

    Runs nightly via Celery Beat.

    Returns a summary dict:
        {"scanned": int, "flagged": int, "errors": int}
    """
    from apps.devices.models import Device
    from apps.devices.risk import compute_device_risk

    devices = Device.objects.filter(
        status__in=["ACTIVE", "LOW_BATTERY"]
    ).values_list("pk", flat=True)

    scanned = 0
    flagged = 0
    errors  = 0

    for device_id in devices:
        try:
            result = compute_device_risk(device_id, lookback_days=14)
            scanned += 1

            new_status = _RISK_TO_STATUS.get(result.get("risk_level", ""))
            if new_status:
                Device.objects.filter(pk=device_id).update(status=new_status)
                flagged += 1
                logger.warning(
                    "Device #%d flagged as %s (risk_score=%.1f)",
                    device_id, new_status, result["failure_risk_score"],
                )
        except Exception as exc:
            errors += 1
            logger.error("Risk scoring failed for device #%d: %s", device_id, exc)

    logger.info(
        "Device risk sweep complete: scanned=%d flagged=%d errors=%d",
        scanned, flagged, errors,
    )
    return {"scanned": scanned, "flagged": flagged, "errors": errors}
