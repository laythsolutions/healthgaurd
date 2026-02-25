"""
Utilities for bridging harvested InspectionRecord data into the core Django DB.

The intelligence service (services/intelligence) harvests public health department
data and exposes it via its REST API.  This module converts those dicts into
Inspection + InspectionViolation rows, creating a lightweight "public data"
Restaurant / Organization if one doesn't yet exist.
"""

import hashlib
import logging
from typing import Optional

from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.restaurants.models import Organization, Restaurant
from .models import Inspection, InspectionViolation

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

SYSTEM_ORG_NAME = "HealthGuard Public Data"

GRADE_MAP: dict[str, str] = {
    "a": "A",
    "b": "B",
    "c": "C",
    "p": "P",
    "pending": "P",
    "x": "X",
    "closed": "X",
    "pass": "A",
    "fail": "X",
    "a grade": "A",
    "b grade": "B",
    "c grade": "C",
}

SEVERITY_MAP: dict[str, str] = {
    "critical": "critical",
    "serious": "serious",
    "major": "serious",
    "minor": "minor",
    "low": "minor",
    "observation": "observation",
    "high": "critical",
    "medium": "serious",
    "unknown": "minor",
}


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


def get_or_create_system_org() -> Organization:
    """Return (or lazily create) the system Organization for public data."""
    org, _ = Organization.objects.get_or_create(
        name=SYSTEM_ORG_NAME,
        defaults={
            "tier": Organization.Tier.STARTER,
            "subscription_status": "system",
            "monthly_fee": 0,
        },
    )
    return org


def _fingerprint(state: str, city: str, name: str, address: str) -> str:
    """Stable 16-hex-char fingerprint for a restaurant identity."""
    raw = f"{state}|{city}|{name}|{address}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_or_create_public_restaurant(record: dict) -> Restaurant:
    """
    Find an existing Restaurant for this public record, or create one.

    Public restaurants are keyed on a deterministic fingerprint of
    (state, city, name, address) so repeated ingestion is idempotent.
    They are placed under the system Organisation and have synthetic
    `code` / `gateway_id` values so the required-field constraints are met.
    """
    state = (record.get("state") or "").strip().upper()
    city = (record.get("city") or "").strip()
    name = (record.get("restaurant_name") or "").strip()
    address = (record.get("address") or "").strip()

    fp = _fingerprint(state, city, name, address)
    code = f"pub_{fp}"
    gateway_id = f"pub_{fp}"

    org = get_or_create_system_org()

    restaurant, _ = Restaurant.objects.get_or_create(
        code=code,
        defaults={
            "organization": org,
            "name": name or "Unknown",
            "address": address or "Unknown",
            "city": city,
            "state": state,
            "zip_code": (record.get("zip_code") or "")[:20],
            "gateway_id": gateway_id,
            "status": Restaurant.Status.ACTIVE,
        },
    )
    return restaurant


# ----------------------------------------------------------------------------
# Core ingest
# ----------------------------------------------------------------------------


@transaction.atomic
def ingest_inspection_record(record: dict) -> Optional[Inspection]:
    """
    Convert a harvested InspectionRecord dict into Inspection + InspectionViolation rows.

    Returns the created Inspection, or None when the record is skipped (duplicate
    or missing required data).
    """
    inspected_at_raw = record.get("inspection_date")
    if not inspected_at_raw:
        return None

    inspected_at = (
        parse_datetime(inspected_at_raw)
        if isinstance(inspected_at_raw, str)
        else inspected_at_raw
    )

    if not inspected_at:
        return None

    try:
        restaurant = get_or_create_public_restaurant(record)
    except Exception as exc:
        logger.warning("[ingest] Could not get/create restaurant: %s", exc)
        return None

    jurisdiction = (record.get("state") or "").upper()

    # Deduplication: same restaurant + same date + same jurisdiction
    if Inspection.objects.filter(
        restaurant=restaurant,
        inspected_at__date=inspected_at.date(),
        source_jurisdiction=jurisdiction,
    ).exists():
        return None

    # Grade
    raw_grade = (record.get("grade") or "").strip().lower()
    grade = GRADE_MAP.get(raw_grade, "")

    # Score
    score = record.get("score")
    if score is not None:
        try:
            score = int(float(str(score)))
            if not (0 <= score <= 100):
                score = None
        except (ValueError, TypeError):
            score = None

    inspection = Inspection.objects.create(
        restaurant=restaurant,
        source_jurisdiction=jurisdiction,
        inspection_type=Inspection.InspectionType.ROUTINE,
        inspected_at=inspected_at,
        score=score,
        grade=grade,
        passed=(score >= 70 if score is not None else None),
        raw_data=record.get("raw_data") or {},
    )

    # Violations
    for v in (record.get("violations") or []):
        if not isinstance(v, dict):
            continue
        raw_sev = (v.get("severity") or "minor").strip().lower()
        InspectionViolation.objects.create(
            inspection=inspection,
            code=(v.get("code") or "")[:50],
            description=(v.get("description") or ""),
            severity=SEVERITY_MAP.get(raw_sev, "minor"),
            category=(v.get("category") or "")[:100],
        )

    # Denormalise last inspection fields onto Restaurant
    if (
        restaurant.last_inspection_date is None
        or inspected_at.date() > restaurant.last_inspection_date
    ):
        update_fields = ["last_inspection_date"]
        restaurant.last_inspection_date = inspected_at.date()
        if score is not None:
            restaurant.last_inspection_score = score
            update_fields.append("last_inspection_score")
        restaurant.save(update_fields=update_fields)

    return inspection
