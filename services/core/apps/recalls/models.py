"""Recall records — sourced from FDA/USDA feeds and manual entries."""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Recall(models.Model):
    """A food safety recall event."""

    class Source(models.TextChoices):
        FDA = "fda", "FDA"
        USDA_FSIS = "usda_fsis", "USDA FSIS"
        CDC = "cdc", "CDC"
        MANUAL = "manual", "Manual Entry"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        TERMINATED = "terminated", "Terminated"
        ONGOING = "ongoing", "Ongoing"

    class Classification(models.TextChoices):
        CLASS_I = "I", "Class I — Serious health hazard"
        CLASS_II = "II", "Class II — May cause temporary adverse health consequences"
        CLASS_III = "III", "Class III — Unlikely to cause adverse health consequences"

    # External identifiers
    source = models.CharField(max_length=20, choices=Source.choices)
    external_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="ID from source system (e.g. FDA recall number)",
    )

    # Core recall data
    title = models.CharField(max_length=500)
    reason = models.TextField()
    hazard_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 'Salmonella', 'Listeria', 'Foreign material', 'Undeclared allergen'",
    )
    classification = models.CharField(
        max_length=5, choices=Classification.choices, blank=True
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    # Recalling firm
    recalling_firm = models.CharField(max_length=300)
    firm_city = models.CharField(max_length=100, blank=True)
    firm_state = models.CharField(max_length=50, blank=True)
    firm_country = models.CharField(max_length=50, default="US")

    # Geography affected
    distribution_pattern = models.TextField(
        blank=True, help_text="Narrative description of distribution area"
    )
    affected_states = models.JSONField(
        default=list,
        help_text="List of two-letter state codes",
    )

    # Dates
    recall_initiation_date = models.DateField(null=True, blank=True)
    center_classification_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)

    # Quantities
    voluntary_mandated = models.CharField(max_length=50, blank=True)
    initial_firm_notification = models.CharField(max_length=200, blank=True)
    product_quantity = models.CharField(max_length=200, blank=True)

    # Raw data preserved for reprocessing
    raw_data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "recalls"
        ordering = ["-recall_initiation_date"]
        indexes = [
            models.Index(fields=["source", "external_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["hazard_type"]),
            models.Index(fields=["recall_initiation_date"]),
        ]

    def __str__(self):
        return f"[{self.source.upper()}] {self.title[:80]}"


class RecallProduct(models.Model):
    """A specific product involved in a recall."""

    recall = models.ForeignKey(Recall, on_delete=models.CASCADE, related_name="products")
    product_description = models.TextField()
    brand_name = models.CharField(max_length=200, blank=True)

    # Product identifiers
    upc_codes = models.JSONField(default=list, help_text="List of UPC/GTIN codes")
    lot_numbers = models.JSONField(default=list)
    best_by_dates = models.JSONField(default=list, help_text="List of date strings")

    # Package info
    package_sizes = models.JSONField(
        default=list, help_text="e.g. ['12 oz', '1 lb']"
    )
    code_info = models.TextField(
        blank=True, help_text="Human-readable lot/date code instructions"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recall_products"

    def __str__(self):
        return f"{self.brand_name or 'Unknown brand'} — {self.product_description[:60]}"


class RecallAcknowledgment(models.Model):
    """
    Tracks whether a restaurant/establishment has acknowledged and acted on a recall.
    Used for the remediation workflow.
    """

    class AckStatus(models.TextChoices):
        PENDING = "pending", "Pending review"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        NOT_AFFECTED = "not_affected", "Not affected"
        REMEDIATED = "remediated", "Product removed/returned"
        ESCALATED = "escalated", "Escalated to health dept"

    recall = models.ForeignKey(Recall, on_delete=models.CASCADE, related_name="acknowledgments")
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="recall_acknowledgments",
    )
    status = models.CharField(
        max_length=20, choices=AckStatus.choices, default=AckStatus.PENDING
    )
    acknowledged_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    notes = models.TextField(blank=True)
    remediation_date = models.DateTimeField(null=True, blank=True)
    units_removed = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recall_acknowledgments"
        unique_together = [("recall", "restaurant")]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["recall", "status"]),
        ]

    def __str__(self):
        return f"{self.recall} / {self.restaurant} → {self.status}"
