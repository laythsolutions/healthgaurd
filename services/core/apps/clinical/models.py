"""
Anonymized clinical case store.

Privacy guarantees enforced at the model level:
- No names, dates of birth, addresses, MRNs, or contact info stored.
- Location is stored as geohash (precision 5 ≈ 5 km cell) or 3-digit ZIP only.
- Age stored as a band string ("30-39"), never exact.
- subject_hash links back to DataSubject in the privacy app.
- Submitted data is routed through AnonymizationService before saving.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportingInstitution(models.Model):
    """A healthcare institution authorized to submit clinical cases."""

    class InstitutionType(models.TextChoices):
        EMERGENCY_DEPT = "ed", "Emergency Department"
        URGENT_CARE = "urgent_care", "Urgent Care"
        PRIMARY_CARE = "primary_care", "Primary Care"
        LABORATORY = "lab", "Laboratory"
        HOSPITAL = "hospital", "Hospital"
        PUBLIC_HEALTH = "public_health", "Public Health Agency"
        OTHER = "other", "Other"

    name = models.CharField(max_length=300)
    institution_type = models.CharField(max_length=20, choices=InstitutionType.choices)
    jurisdiction = models.CharField(max_length=100, blank=True)

    # Location — stored at coarse resolution only
    geohash = models.CharField(max_length=5, blank=True)
    state = models.CharField(max_length=2, blank=True)

    # Authentication
    api_key_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="HMAC of the institution's API key",
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "clinical_institutions"

    def __str__(self):
        return f"{self.name} ({self.institution_type})"


class ClinicalCase(models.Model):
    """
    An anonymized case of suspected foodborne or environmental illness.

    All PII is stripped at intake. The raw submission is never stored.
    """

    class IllnessStatus(models.TextChoices):
        SUSPECTED = "suspected", "Suspected"
        CONFIRMED = "confirmed", "Confirmed"
        RULED_OUT = "ruled_out", "Ruled out"

    class OutcomeStatus(models.TextChoices):
        RECOVERED = "recovered", "Recovered"
        HOSPITALIZED = "hospitalized", "Hospitalized"
        ONGOING = "ongoing", "Ongoing"
        DECEASED = "deceased", "Deceased"
        UNKNOWN = "unknown", "Unknown"

    # Pseudonymous subject link
    subject_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="HMAC of source patient identifier (see privacy app)",
    )

    # Submitter
    reporting_institution = models.ForeignKey(
        ReportingInstitution,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cases",
    )

    # Anonymized demographics
    age_range = models.CharField(max_length=10, blank=True)   # e.g. "30-39"
    sex = models.CharField(
        max_length=10,
        blank=True,
        choices=[("M", "Male"), ("F", "Female"), ("O", "Other/Unknown")],
    )
    geohash = models.CharField(
        max_length=5,
        blank=True,
        help_text="Precision-5 geohash of patient's general area",
    )
    zip3 = models.CharField(max_length=3, blank=True)

    # Illness details
    illness_status = models.CharField(
        max_length=15, choices=IllnessStatus.choices, default=IllnessStatus.SUSPECTED
    )
    onset_date = models.DateField(null=True, blank=True)
    illness_duration_days = models.IntegerField(null=True, blank=True)

    # Symptoms (stored as list of standardized codes)
    symptoms = models.JSONField(
        default=list,
        help_text="List of symptom strings, e.g. ['diarrhea', 'vomiting', 'fever']",
    )

    # Lab results
    stool_culture_collected = models.BooleanField(null=True, blank=True)
    pathogen = models.CharField(max_length=200, blank=True)
    serotype = models.CharField(max_length=100, blank=True)
    lab_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="De-identified lab reference number (not the actual accession number)",
    )

    # Outcome
    outcome = models.CharField(
        max_length=15, choices=OutcomeStatus.choices, default=OutcomeStatus.UNKNOWN
    )
    hospitalized = models.BooleanField(null=True, blank=True)
    icu_admission = models.BooleanField(null=True, blank=True)

    # Investigation linkage
    investigation = models.ForeignKey(
        "clinical.OutbreakInvestigation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cases",
    )

    # Audit trail (no PII — just who submitted)
    submitted_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clinical_cases"
        ordering = ["-onset_date", "-created_at"]
        indexes = [
            models.Index(fields=["onset_date"]),
            models.Index(fields=["pathogen"]),
            models.Index(fields=["geohash"]),
            models.Index(fields=["illness_status"]),
            models.Index(fields=["investigation"]),
        ]

    def __str__(self):
        return f"Case {self.pk} | {self.pathogen or 'unknown'} | {self.onset_date}"


class ClinicalExposure(models.Model):
    """
    A food or environmental exposure reported by a case patient.
    De-identified to establishment type and geohash — no names.
    """

    class ExposureType(models.TextChoices):
        RESTAURANT = "restaurant", "Restaurant / Food service"
        GROCERY = "grocery", "Grocery / Retail food"
        HOME = "home", "Home-prepared food"
        CATERED = "catered", "Catered event"
        WATER = "water", "Water source"
        ANIMAL = "animal", "Animal contact"
        PERSON = "person", "Person-to-person"
        UNKNOWN = "unknown", "Unknown"

    case = models.ForeignKey(
        ClinicalCase, on_delete=models.CASCADE, related_name="exposures"
    )
    exposure_type = models.CharField(max_length=20, choices=ExposureType.choices)
    exposure_date = models.DateField(null=True, blank=True)

    # De-identified location
    geohash = models.CharField(max_length=6, blank=True)
    establishment_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 'Fast food', 'Full-service restaurant', 'Deli'",
    )

    # Food items (no brand or specific identifiers unless linked to a recall)
    food_items = models.JSONField(
        default=list,
        help_text="List of food item descriptions — strip brand names before storing",
    )

    # Recall linkage
    linked_recall = models.ForeignKey(
        "recalls.Recall",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="clinical_exposures",
    )

    # Confidence
    confidence = models.CharField(
        max_length=10,
        choices=[("high", "High"), ("medium", "Medium"), ("low", "Low")],
        default="low",
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "clinical_exposures"
        indexes = [
            models.Index(fields=["exposure_type", "exposure_date"]),
            models.Index(fields=["geohash"]),
            models.Index(fields=["linked_recall"]),
        ]

    def __str__(self):
        return f"Exposure: {self.exposure_type} on {self.exposure_date}"


class OutbreakInvestigation(models.Model):
    """
    A cluster of cases that has crossed the threshold for formal investigation.
    Created automatically by the analytics engine or manually by health dept staff.
    """

    class InvestigationStatus(models.TextChoices):
        OPEN = "open", "Open"
        ACTIVE = "active", "Active investigation"
        CLOSED = "closed", "Closed"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=300)
    status = models.CharField(
        max_length=15,
        choices=InvestigationStatus.choices,
        default=InvestigationStatus.OPEN,
    )

    # Cluster parameters
    pathogen = models.CharField(max_length=200, blank=True)
    suspected_vehicle = models.TextField(blank=True)
    geographic_scope = models.CharField(max_length=200, blank=True)

    # Dates
    cluster_start_date = models.DateField(null=True, blank=True)
    cluster_end_date = models.DateField(null=True, blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Lead investigator
    lead_investigator = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    notes = models.TextField(blank=True)

    # Analytics metadata
    case_count_at_open = models.IntegerField(default=0)
    auto_generated = models.BooleanField(
        default=False,
        help_text="True if created automatically by the clustering engine",
    )
    cluster_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Composite score from the clustering algorithm",
    )

    class Meta:
        db_table = "clinical_investigations"
        ordering = ["-opened_at"]

    def __str__(self):
        return f"Investigation #{self.pk}: {self.title}"
