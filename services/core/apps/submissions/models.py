"""
Models for the jurisdiction submission API.

JurisdictionAccount  — a health department registered to push data
SubmissionBatch      — one push of inspection records from a jurisdiction
"""

from django.db import models
from django.conf import settings


class JurisdictionAccount(models.Model):
    """A health department that has registered to submit inspection data."""

    class JurisdictionType(models.TextChoices):
        COUNTY = "COUNTY", "County"
        CITY   = "CITY",   "City"
        STATE  = "STATE",  "State"
        TRIBAL = "TRIBAL", "Tribal"

    class Status(models.TextChoices):
        PENDING   = "PENDING",   "Pending Review"
        ACTIVE    = "ACTIVE",    "Active"
        SUSPENDED = "SUSPENDED", "Suspended"

    class ScoreSystem(models.TextChoices):
        SCORE_0_100     = "SCORE_0_100",     "Numeric 0–100"
        GRADE_A_F       = "GRADE_A_F",       "Grade A–F"
        PASS_FAIL       = "PASS_FAIL",       "Pass / Fail"
        LETTER_NUMERIC  = "LETTER_NUMERIC",  "Letter + Numeric (hybrid)"

    name              = models.CharField(max_length=200)
    fips_code         = models.CharField(max_length=10, unique=True,
                                         help_text="5-digit FIPS county/state code")
    state             = models.CharField(max_length=2, help_text="2-letter state code")
    contact_email     = models.EmailField()
    jurisdiction_type = models.CharField(max_length=10, choices=JurisdictionType.choices,
                                         default=JurisdictionType.COUNTY)
    website           = models.URLField(blank=True)

    status      = models.CharField(max_length=10, choices=Status.choices,
                                   default=Status.PENDING)
    score_system = models.CharField(max_length=20, choices=ScoreSystem.choices,
                                    default=ScoreSystem.SCORE_0_100)

    # Field-name translation: their keys → canonical keys
    schema_map  = models.JSONField(default=dict, blank=True,
                                   help_text='e.g. {"facility_name": "restaurant_name"}')

    webhook_url = models.URLField(blank=True, help_text="POST callback after batch completes")

    api_key     = models.OneToOneField(
        "accounts.APIKey",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="jurisdiction_account",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="approved_jurisdiction_accounts",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "submission_jurisdiction_accounts"
        indexes  = [models.Index(fields=["state", "status"])]

    def __str__(self):
        return f"{self.name} ({self.fips_code})"


class SubmissionBatch(models.Model):
    """One push of inspection records from a jurisdiction."""

    class Status(models.TextChoices):
        PENDING    = "PENDING",    "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETE   = "COMPLETE",   "Complete"
        FAILED     = "FAILED",     "Failed"

    class SourceFormat(models.TextChoices):
        JSON = "JSON", "JSON"
        CSV  = "CSV",  "CSV"

    jurisdiction   = models.ForeignKey(JurisdictionAccount, on_delete=models.CASCADE,
                                       related_name="batches")
    status         = models.CharField(max_length=12, choices=Status.choices,
                                      default=Status.PENDING)
    source_format  = models.CharField(max_length=4, choices=SourceFormat.choices,
                                      default=SourceFormat.JSON)

    total_rows    = models.IntegerField(default=0)
    created_count = models.IntegerField(default=0)
    skipped_count = models.IntegerField(default=0)
    error_count   = models.IntegerField(default=0)

    # [{"row": 5, "reason": "missing restaurant_name"}]
    row_errors  = models.JSONField(default=list)
    raw_payload = models.JSONField(default=list,
                                   help_text="Original submitted records for reprocessing")

    webhook_delivered    = models.BooleanField(default=False)
    webhook_delivered_at = models.DateTimeField(null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "submission_batches"
        ordering = ["-submitted_at"]
        indexes  = [models.Index(fields=["jurisdiction", "status"])]

    def __str__(self):
        return f"Batch {self.pk} — {self.jurisdiction.name} ({self.status})"
