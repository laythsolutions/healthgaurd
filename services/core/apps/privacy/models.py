"""
Privacy, consent, and data subject models.

Design principles:
- No raw PII stored here. `subject_hash` is a salted HMAC-SHA256 of a source
  identifier (e.g., hashed patient ID, hashed loyalty card ID).
- Consent records are append-only via signals; never update in place.
- Audit log is written on every read or write of sensitive data categories.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DataSubject(models.Model):
    """
    A pseudonymous representation of a data subject.

    The `subject_hash` is a deterministic HMAC of the source identifier
    (see AnonymizationService.hash_identifier). It allows cross-system
    linkage without storing the original identifier.
    """

    class SourceSystem(models.TextChoices):
        CLINICAL = "clinical", "Clinical / EHR"
        RETAIL = "retail", "Retail Loyalty"
        CONSUMER = "consumer", "Consumer App"
        RESTAURANT = "restaurant", "Restaurant Staff"

    subject_hash = models.CharField(max_length=64, unique=True, db_index=True)
    source_system = models.CharField(max_length=20, choices=SourceSystem.choices)

    # Anonymized demographic bands — never raw values
    age_range = models.CharField(max_length=10, blank=True)  # e.g. "30-39"
    zip3 = models.CharField(max_length=3, blank=True)        # first 3 digits only
    geohash = models.CharField(max_length=6, blank=True)     # ~1.2 km precision

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "privacy_data_subjects"
        indexes = [
            models.Index(fields=["source_system"]),
        ]

    def __str__(self):
        return f"Subject:{self.subject_hash[:8]}… ({self.source_system})"


class ConsentScope(models.TextChoices):
    INSPECTION_PUBLIC = "inspection_public", "Public inspection data sharing"
    IOT_MONITORING = "iot_monitoring", "IoT sensor monitoring"
    CLINICAL_REPORTING = "clinical_reporting", "Clinical case reporting"
    RECALL_MATCHING = "recall_matching", "Recall and exposure matching"
    ANALYTICS_AGGREGATED = "analytics_aggregated", "Aggregated analytics"
    ANALYTICS_INDIVIDUAL = "analytics_individual", "Individual-level analytics"
    DATA_EXPORT = "data_export", "Data export to third parties"


class ConsentRecord(models.Model):
    """
    Immutable consent event. Never updated — only new records are appended.
    The current consent state for a subject+scope is the most recent record.
    """

    class Status(models.TextChoices):
        GRANTED = "granted", "Granted"
        REVOKED = "revoked", "Revoked"
        PENDING = "pending", "Pending"

    subject = models.ForeignKey(
        DataSubject, on_delete=models.CASCADE, related_name="consent_records"
    )
    scope = models.CharField(max_length=40, choices=ConsentScope.choices)
    status = models.CharField(max_length=10, choices=Status.choices)

    # Who/what recorded this event
    recorded_by_system = models.CharField(max_length=100, blank=True)
    recorded_by_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )

    # The legal basis under which data is processed for this scope
    legal_basis = models.CharField(
        max_length=60,
        blank=True,
        help_text="e.g. 'consent', 'public_interest', 'vital_interests'",
    )

    ip_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="HMAC of IP address, for audit only",
    )
    user_agent_hash = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "privacy_consent_records"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["subject", "scope", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.subject} | {self.scope} → {self.status}"


class DataProcessingAuditLog(models.Model):
    """
    Append-only log of every read, write, delete, or export of sensitive
    data categories. Required for GDPR Article 30 records of processing.
    """

    class Action(models.TextChoices):
        READ = "read", "Read"
        WRITE = "write", "Write"
        DELETE = "delete", "Delete"
        EXPORT = "export", "Export"
        ANONYMIZE = "anonymize", "Anonymize"

    subject = models.ForeignKey(
        DataSubject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=15, choices=Action.choices)
    data_categories = models.JSONField(
        default=list,
        help_text="List of data category labels accessed, e.g. ['health', 'location']",
    )
    purpose = models.CharField(max_length=200)

    # Actor
    performed_by_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    performed_by_system = models.CharField(max_length=100, blank=True)

    # Context
    endpoint = models.CharField(max_length=255, blank=True)
    record_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 'ClinicalCase', 'SensorReading'",
    )
    record_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "privacy_audit_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["subject", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.action} | {self.record_type}:{self.record_id} at {self.created_at}"
