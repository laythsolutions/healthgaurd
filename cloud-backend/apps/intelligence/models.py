"""Intelligence models for data insights"""

from django.db import models
from apps.restaurants.models import Restaurant


class PublicInspectionData(models.Model):
    """Public health inspection data harvested from external sources"""

    class DataSource(models.TextChoices):
        STATE_API = 'STATE_API', 'State API'
        CITY_PORTAL = 'CITY_PORTAL', 'City Portal'
        FOIA_REQUEST = 'FOIA', 'FOIA Request'
        BUSINESS_REGISTRY = 'REGISTRY', 'Business Registry'

    # Restaurant identification
    restaurant_name = models.CharField(max_length=255)
    dba_name = models.CharField(max_length=255, blank=True)  # Doing Business As
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    county = models.CharField(max_length=100, blank=True)

    # Link to internal restaurant (if matched)
    matched_restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='public_inspections'
    )

    # Inspection data
    inspection_date = models.DateTimeField()
    inspection_score = models.IntegerField(null=True, blank=True)
    inspection_grade = models.CharField(max_length=10, blank=True)  # A, B, C
    inspection_type = models.CharField(max_length=100, blank=True)

    # Violations
    violations_count = models.IntegerField(default=0)
    critical_violations_count = models.IntegerField(default=0)
    violations_data = models.JSONField(default=list)

    # Risk assessment
    risk_level = models.CharField(max_length=20, blank=True)
    risk_score = models.IntegerField(null=True, blank=True)

    # Data source
    data_source = models.CharField(max_length=20, choices=DataSource.choices)
    source_url = models.URLField(blank=True)
    source_id = models.CharField(max_length=100, blank=True)

    # Processing
    processed = models.BooleanField(default=False)
    matched = models.BooleanField(default=False)

    # Metadata
    harvested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'public_inspection_data'
        indexes = [
            models.Index(fields=['restaurant_name', 'city', 'state']),
            models.Index(fields=['inspection_date']),
            models.Index(fields=['matched_restaurant']),
            models.Index(fields=['processed', 'matched']),
        ]

    def __str__(self):
        return f"{self.restaurant_name} - {self.inspection_date.strftime('%Y-%m-%d')}"


class LeadScore(models.Model):
    """Calculated lead scores for sales targeting"""

    # Restaurant
    restaurant_name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)

    # Link to matched restaurant
    matched_restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lead_scores'
    )

    # Scores
    lead_score = models.IntegerField()  # 0-100
    healthguard_risk_score = models.IntegerField()
    acquisition_probability = models.IntegerField()  # 0-100%

    # Component scores
    size_score = models.IntegerField()
    cuisine_risk_score = models.IntegerField()
    location_density_score = models.IntegerField()
    competitor_gap_score = models.IntegerField()
    tech_readiness_score = models.IntegerField()

    # Recommendations
    optimal_contact_date = models.DateField(null=True, blank=True)
    urgency_level = models.CharField(max_length=20)  # critical, high, medium, low
    recommended_approach = models.CharField(max_length=50)

    # Talking points and outreach
    value_proposition = models.TextField()
    talking_points = models.JSONField(default=list)
    email_template = models.TextField(blank=True)
    call_script = models.TextField(blank=True)

    # Competitor intelligence
    has_competitor = models.BooleanField(default=False)
    detected_competitor = models.CharField(max_length=100, blank=True)

    # Status
    contacted = models.BooleanField(default=False)
    contact_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default='prospect')  # prospect, contacted, demo, closed, lost

    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lead_scores'
        indexes = [
            models.Index(fields=['lead_score']),
            models.Index(fields=['status', 'contacted']),
            models.Index(fields=['optimal_contact_date']),
        ]
        ordering = ['-lead_score']

    def __str__(self):
        return f"{self.restaurant_name} - Lead Score: {self.lead_score}"


class MarketIntelligence(models.Model):
    """Market-level intelligence for sales territories"""

    # Territory
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    # Market stats
    total_restaurants = models.IntegerField(default=0)
    competitor_installations = models.IntegerField(default=0)
    market_penetration_percent = models.DecimalField(max_digits=5, decimal_places=2)

    # Compliance landscape
    avg_inspection_score = models.DecimalField(max_digits=5, decimal_places=2)
    high_risk_restaurants = models.IntegerField(default=0)
    medium_risk_restaurants = models.IntegerField(default=0)
    low_risk_restaurants = models.IntegerField(default=0)

    # Sales opportunities
    total_lead_opportunities = models.IntegerField(default=0)
    high_priority_leads = models.IntegerField(default=0)
    estimated_market_value = models.DecimalField(max_digits=12, decimal_places=2)

    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'market_intelligence'
        verbose_name_plural = 'market intelligence'
        indexes = [
            models.Index(fields=['state', 'city']),
        ]

    def __str__(self):
        return f"{self.city}, {state} - {self.market_penetration_percent}% penetration"
