"""
AnonymizationService and ConsentManager.

AnonymizationService is stateless and has no Django dependencies — it can be
imported by any service (Django, FastAPI, gateway) that needs to sanitize data
before storage or transmission.

ConsentManager wraps Django ORM calls and should only be used in the backend.
"""

import hashlib
import hmac
import math
import re
import unicodedata
from typing import Optional

from django.conf import settings

# ---------------------------------------------------------------------------
# PII detection patterns
# ---------------------------------------------------------------------------

_PII_PATTERNS = [
    # US phone numbers (various formats)
    (re.compile(r"\b(\+1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"), "[PHONE]"),
    # Email addresses
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL]"),
    # US SSN
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    # Medical record numbers: "MRN", "MR#", "Patient ID" followed by digits
    (re.compile(r"\b(MRN|MR#|Patient\s*ID)[:\s#]*\d+\b", re.IGNORECASE), "[MRN]"),
    # US ZIP+4
    (re.compile(r"\b\d{5}-\d{4}\b"), "[ZIP]"),
    # IPv4 addresses
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP]"),
    # Credit card numbers (loose match — 13–19 digits with optional separators)
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[CC]"),
    # Date of birth patterns: MM/DD/YYYY, YYYY-MM-DD
    (re.compile(r"\b(DOB|Date of Birth)[:\s]*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b", re.IGNORECASE), "[DOB]"),
]

# ---------------------------------------------------------------------------
# Geohash encoding (pure Python, no external dependency)
# ---------------------------------------------------------------------------

_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def _encode_geohash(lat: float, lon: float, precision: int = 6) -> str:
    """Encode lat/lon to geohash string of given precision."""
    min_lat, max_lat = -90.0, 90.0
    min_lon, max_lon = -180.0, 180.0

    bits = [16, 8, 4, 2, 1]
    bit_idx = 0
    char_idx = 0
    even = True
    geohash = []

    while len(geohash) < precision:
        if even:
            mid = (min_lon + max_lon) / 2
            if lon >= mid:
                char_idx |= bits[bit_idx]
                min_lon = mid
            else:
                max_lon = mid
        else:
            mid = (min_lat + max_lat) / 2
            if lat >= mid:
                char_idx |= bits[bit_idx]
                min_lat = mid
            else:
                max_lat = mid

        even = not even
        if bit_idx < 4:
            bit_idx += 1
        else:
            geohash.append(_BASE32[char_idx])
            bit_idx = 0
            char_idx = 0

    return "".join(geohash)


# ---------------------------------------------------------------------------
# AnonymizationService
# ---------------------------------------------------------------------------


class AnonymizationService:
    """
    Stateless anonymization utilities.

    All methods are pure functions (or use only the Django settings salt).
    Safe to call from any context — no ORM access.
    """

    # Salt is read from settings to ensure consistent hashing across instances.
    # Must be set as ANONYMIZATION_SALT in Django settings.
    @staticmethod
    def _get_salt() -> bytes:
        salt = getattr(settings, "ANONYMIZATION_SALT", None)
        if not salt:
            raise RuntimeError(
                "ANONYMIZATION_SALT must be set in Django settings. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return salt.encode() if isinstance(salt, str) else salt

    # ------------------------------------------------------------------
    # Location anonymization
    # ------------------------------------------------------------------

    @staticmethod
    def encode_geohash(lat: float, lon: float, precision: int = 6) -> str:
        """
        Convert lat/lon to geohash.

        Precision 6 → ~1.2 km × 0.6 km cell (recommended for public data).
        Precision 5 → ~4.9 km × 4.9 km cell (for high-risk health data).
        """
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"Invalid coordinates: ({lat}, {lon})")
        return _encode_geohash(lat, lon, precision)

    @staticmethod
    def truncate_zip(zip_code: str) -> str:
        """Return first 3 digits of a ZIP code (covers ~30,000 people on average)."""
        digits = re.sub(r"\D", "", zip_code)
        return digits[:3] if len(digits) >= 3 else digits

    # ------------------------------------------------------------------
    # Demographic generalization
    # ------------------------------------------------------------------

    @staticmethod
    def age_to_range(age: int, band_size: int = 10) -> str:
        """
        Convert an exact age to a range string.

        Examples:
            34 → "30-39"
            0  → "0-9"
            85 → "80+"
        """
        if age < 0:
            raise ValueError("Age cannot be negative")
        if age >= 80:
            return "80+"
        lower = (age // band_size) * band_size
        upper = lower + band_size - 1
        return f"{lower}-{upper}"

    # ------------------------------------------------------------------
    # PII stripping
    # ------------------------------------------------------------------

    @staticmethod
    def strip_pii(text: str) -> str:
        """
        Replace known PII patterns in free text with redaction tokens.

        Operates on regex patterns only — does not use NLP/ML.
        Use as a safety net, not a primary de-identification method.
        """
        if not text:
            return text
        for pattern, replacement in _PII_PATTERNS:
            text = pattern.sub(replacement, text)
        return text

    # ------------------------------------------------------------------
    # Deterministic pseudonymization
    # ------------------------------------------------------------------

    @classmethod
    def hash_identifier(cls, value: str, namespace: str = "") -> str:
        """
        Return a 64-character hex HMAC-SHA256 of value + namespace.

        The same input always produces the same hash (deterministic), enabling
        linkage across datasets without storing the original identifier.

        namespace: use to separate hash spaces (e.g. "clinical", "retail").
        """
        salt = cls._get_salt()
        msg = f"{namespace}:{value}".encode("utf-8")
        return hmac.new(salt, msg, hashlib.sha256).hexdigest()

    @classmethod
    def hash_ip(cls, ip: str) -> str:
        return cls.hash_identifier(ip, namespace="ip")

    @classmethod
    def hash_user_agent(cls, ua: str) -> str:
        return cls.hash_identifier(ua, namespace="ua")

    # ------------------------------------------------------------------
    # Full record anonymization
    # ------------------------------------------------------------------

    @classmethod
    def anonymize_clinical_case(cls, raw: dict) -> dict:
        """
        Apply all relevant anonymization rules to a raw clinical case dict.

        Expected raw keys (all optional):
            patient_id, age, date_of_birth, zip_code, latitude, longitude,
            address, notes, symptoms, onset_date, exposures
        """
        result = {}

        # Pseudonymous subject identifier
        if "patient_id" in raw:
            result["subject_hash"] = cls.hash_identifier(
                str(raw["patient_id"]), namespace="clinical"
            )

        # Age → range
        if "age" in raw and raw["age"] is not None:
            result["age_range"] = cls.age_to_range(int(raw["age"]))
        elif "date_of_birth" in raw and raw["date_of_birth"]:
            from datetime import date
            dob = raw["date_of_birth"]
            if not isinstance(dob, date):
                from datetime import datetime
                dob = datetime.fromisoformat(str(dob)).date()
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            result["age_range"] = cls.age_to_range(age)

        # Location: geohash preferred over zip
        if "latitude" in raw and "longitude" in raw and raw["latitude"] and raw["longitude"]:
            result["geohash"] = cls.encode_geohash(
                float(raw["latitude"]), float(raw["longitude"]), precision=5
            )
        elif "zip_code" in raw and raw["zip_code"]:
            result["zip3"] = cls.truncate_zip(str(raw["zip_code"]))

        # Free text: strip PII
        for field in ("notes", "description", "chief_complaint"):
            if field in raw and raw[field]:
                result[field] = cls.strip_pii(str(raw[field]))

        # Pass-through safe fields
        safe_fields = (
            "symptoms", "onset_date", "illness_duration_days",
            "hospitalized", "stool_culture_collected",
            "pathogen", "serotype", "food_exposures",
        )
        for f in safe_fields:
            if f in raw:
                result[f] = raw[f]

        return result


# ---------------------------------------------------------------------------
# ConsentManager
# ---------------------------------------------------------------------------


class ConsentManager:
    """
    Django ORM wrapper for consent operations.

    All mutating operations append a new ConsentRecord — records are never
    modified in place, ensuring a full audit trail.
    """

    @staticmethod
    def get_current_status(subject_hash: str, scope: str) -> Optional[str]:
        """Return the current consent status for a subject+scope, or None if unknown."""
        from apps.privacy.models import DataSubject, ConsentRecord

        try:
            subject = DataSubject.objects.get(subject_hash=subject_hash)
        except DataSubject.DoesNotExist:
            return None

        record = (
            ConsentRecord.objects.filter(subject=subject, scope=scope)
            .order_by("-created_at")
            .first()
        )
        return record.status if record else None

    @staticmethod
    def has_consent(subject_hash: str, scope: str) -> bool:
        """Return True only if the most recent consent record is GRANTED."""
        from apps.privacy.models import ConsentRecord
        status = ConsentManager.get_current_status(subject_hash, scope)
        return status == ConsentRecord.Status.GRANTED

    @staticmethod
    def grant(
        subject_hash: str,
        scope: str,
        source_system: str,
        legal_basis: str = "consent",
        recorded_by_user=None,
        ip: str = "",
        user_agent: str = "",
        notes: str = "",
    ):
        """Record a consent grant event."""
        from apps.privacy.models import DataSubject, ConsentRecord

        subject, _ = DataSubject.objects.get_or_create(
            subject_hash=subject_hash,
            defaults={"source_system": source_system},
        )
        svc = AnonymizationService()
        ConsentRecord.objects.create(
            subject=subject,
            scope=scope,
            status=ConsentRecord.Status.GRANTED,
            recorded_by_system=source_system,
            recorded_by_user=recorded_by_user,
            legal_basis=legal_basis,
            ip_hash=svc.hash_ip(ip) if ip else "",
            user_agent_hash=svc.hash_user_agent(user_agent) if user_agent else "",
            notes=notes,
        )

    @staticmethod
    def revoke(
        subject_hash: str,
        scope: str,
        source_system: str,
        recorded_by_user=None,
        notes: str = "",
    ):
        """Record a consent revocation event."""
        from apps.privacy.models import DataSubject, ConsentRecord

        try:
            subject = DataSubject.objects.get(subject_hash=subject_hash)
        except DataSubject.DoesNotExist:
            return  # Nothing to revoke

        ConsentRecord.objects.create(
            subject=subject,
            scope=scope,
            status=ConsentRecord.Status.REVOKED,
            recorded_by_system=source_system,
            recorded_by_user=recorded_by_user,
            notes=notes,
        )

    @staticmethod
    def log_access(
        action: str,
        data_categories: list,
        purpose: str,
        subject_hash: str = None,
        performed_by_user=None,
        performed_by_system: str = "",
        endpoint: str = "",
        record_type: str = "",
        record_id: str = "",
    ):
        """Write an entry to the data processing audit log."""
        from apps.privacy.models import DataSubject, DataProcessingAuditLog

        subject = None
        if subject_hash:
            subject = DataSubject.objects.filter(subject_hash=subject_hash).first()

        DataProcessingAuditLog.objects.create(
            subject=subject,
            action=action,
            data_categories=data_categories,
            purpose=purpose,
            performed_by_user=performed_by_user,
            performed_by_system=performed_by_system,
            endpoint=endpoint,
            record_type=record_type,
            record_id=str(record_id),
        )
