"""
Data access audit logging middleware.

Automatically appends a DataProcessingAuditLog entry for every successful
request (2xx) touching sensitive data endpoints. Runs asynchronously via a
deferred DB write to avoid adding latency to the response path.

Sensitive endpoint prefixes
----------------------------
    /api/v1/clinical/           — anonymized case data
    /api/v1/recalls/            — recall acknowledgment workflow
    /api/v1/inspections/schedule/  — inspection scheduling
    /api/v1/inspections/export/ — bulk export
    /api/v1/devices/risk/       — equipment risk scores

Configuration
-------------
Add to MIDDLEWARE in settings.py (after AuthenticationMiddleware):

    INSTALLED_APPS = [..., 'apps.privacy']

    MIDDLEWARE = [
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'apps.privacy.audit_middleware.DataAccessAuditMiddleware',
        ...
    ]
"""

import logging
import threading
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Map URL prefix → (data_categories, purpose)
_AUDIT_RULES: list[tuple[str, list[str], str]] = [
    ("/api/v1/clinical/",              ["health", "location", "demographics"], "clinical_data_access"),
    ("/api/v1/recalls/acknowledgments", ["recalls", "restaurant_compliance"],   "recall_ack_access"),
    ("/api/v1/inspections/schedule",    ["inspections", "scheduling"],          "inspection_schedule_access"),
    ("/api/v1/inspections/export",      ["inspections", "bulk_export"],         "inspection_export"),
    ("/api/v1/devices/risk",            ["iot_health", "equipment"],            "device_risk_access"),
]

# Only log reads (GET) and writes (POST/PATCH/PUT) — skip HEAD/OPTIONS
_AUDITABLE_METHODS = frozenset({"GET", "POST", "PATCH", "PUT", "DELETE"})


def _match_rule(path: str):
    """Return (data_categories, purpose) for the first matching rule, or None."""
    for prefix, categories, purpose in _AUDIT_RULES:
        if path.startswith(prefix):
            return categories, purpose
    return None


def _write_audit(
    action: str,
    data_categories: list[str],
    purpose: str,
    user,
    endpoint: str,
):
    """Write the audit log entry. Runs in a background thread."""
    try:
        from apps.privacy.services import ConsentManager

        performed_by_user = user if (user and user.is_authenticated) else None
        system_name = "api" if not performed_by_user else f"user:{user.username}"

        ConsentManager.log_access(
            action=action,
            data_categories=data_categories,
            purpose=purpose,
            performed_by_user=performed_by_user,
            performed_by_system=system_name,
            endpoint=endpoint,
        )
    except Exception as exc:
        # Audit logging must never break the application.
        logger.warning("Audit log write failed for %s: %s", endpoint, exc)


class DataAccessAuditMiddleware:
    """
    WSGI middleware that logs data access events to DataProcessingAuditLog.

    Writes are dispatched in a daemon thread so the response is never blocked.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only audit successful responses to auditable methods
        if (
            request.method in _AUDITABLE_METHODS
            and 200 <= response.status_code < 300
        ):
            path = urlparse(request.path).path
            match = _match_rule(path)
            if match:
                data_categories, purpose = match
                action = "read" if request.method == "GET" else "write"
                t = threading.Thread(
                    target=_write_audit,
                    args=(action, data_categories, purpose, request.user, path),
                    daemon=True,
                )
                t.start()

        return response
