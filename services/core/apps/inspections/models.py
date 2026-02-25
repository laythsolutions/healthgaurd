"""
Health department inspection records.

Separate from the existing `restaurants.ComplianceCheck` (which tracks
internal self-checks by restaurant staff). This app stores official
health department inspections ingested from public data sources.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Inspection(models.Model):
    """An official health department inspection of a food service establishment."""

    class InspectionType(models.TextChoices):
        ROUTINE = "routine", "Routine"
        FOLLOW_UP = "follow_up", "Follow-up"
        COMPLAINT = "complaint", "Complaint-driven"
        PRE_OPENING = "pre_opening", "Pre-opening"
        REINSPECTION = "reinspection", "Re-inspection"
        SPECIAL = "special", "Special"

    class Grade(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        PENDING = "P", "Pending"
        CLOSED = "X", "Closed"

    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="inspections",
    )

    # Inspection identifiers
    external_id = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        help_text="ID from the health department source system",
    )
    source_jurisdiction = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 'LA County', 'NYC DOHMH', 'CA CDPH'",
    )

    # Inspection metadata
    inspection_type = models.CharField(
        max_length=20, choices=InspectionType.choices, default=InspectionType.ROUTINE
    )
    inspected_at = models.DateTimeField()
    inspector_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Anonymized or redacted inspector identifier",
    )

    # Results
    score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    grade = models.CharField(
        max_length=2, choices=Grade.choices, blank=True
    )
    passed = models.BooleanField(null=True, blank=True)

    # Closure
    closed = models.BooleanField(default=False)
    closure_reason = models.TextField(blank=True)
    reopened_at = models.DateTimeField(null=True, blank=True)

    # Document links
    report_url = models.URLField(blank=True)

    # Provenance
    raw_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inspections"
        ordering = ["-inspected_at"]
        indexes = [
            models.Index(fields=["restaurant", "-inspected_at"]),
            models.Index(fields=["grade"]),
            models.Index(fields=["inspected_at"]),
            models.Index(fields=["source_jurisdiction"]),
        ]

    def __str__(self):
        return f"{self.restaurant} | {self.inspection_type} | {self.inspected_at.date()}"


class InspectionViolation(models.Model):
    """A single violation recorded during an inspection."""

    class Severity(models.TextChoices):
        CRITICAL = "critical", "Critical"        # Risk factor — can cause illness
        SERIOUS = "serious", "Serious"            # Significant risk
        MINOR = "minor", "Minor"                  # Good retail practice
        OBSERVATION = "observation", "Observation"

    class Status(models.TextChoices):
        OBSERVED = "observed", "Observed"
        CORRECTED_ON_SITE = "corrected_on_site", "Corrected on site"
        NOT_CORRECTED = "not_corrected", "Not corrected"
        REPEAT = "repeat", "Repeat violation"

    inspection = models.ForeignKey(
        Inspection, on_delete=models.CASCADE, related_name="violations"
    )

    # Violation classification
    code = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.MINOR
    )
    violation_status = models.CharField(
        max_length=25, choices=Status.choices, default=Status.OBSERVED
    )

    # Category grouping for analytics
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "e.g. 'Temperature control', 'Personnel hygiene', "
            "'Food storage', 'Pest control'"
        ),
    )

    # Location within establishment
    location_description = models.CharField(max_length=200, blank=True)

    # Inspector notes
    notes = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)

    points_deducted = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "inspection_violations"
        indexes = [
            models.Index(fields=["inspection", "severity"]),
            models.Index(fields=["code"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.code}: {self.description[:60]}"


class InspectionSchedule(models.Model):
    """A planned future health department inspection."""

    class ScheduleStatus(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        MISSED = "missed", "Missed"

    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="inspection_schedules",
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    inspection_type = models.CharField(
        max_length=20,
        choices=Inspection.InspectionType.choices,
        default=Inspection.InspectionType.ROUTINE,
    )
    assigned_inspector_id = models.CharField(max_length=100, blank=True)
    jurisdiction = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=ScheduleStatus.choices,
        default=ScheduleStatus.SCHEDULED,
    )
    # Linked to resulting inspection once the inspector records it
    completed_inspection = models.OneToOneField(
        Inspection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="schedule",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inspection_schedules"
        ordering = ["scheduled_date"]
        indexes = [
            models.Index(fields=["scheduled_date"]),
            models.Index(fields=["restaurant", "status"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.restaurant} — {self.scheduled_date} ({self.status})"
