"""Restaurant models for HealthGuard"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Organization(models.Model):
    """Organization (company) that owns multiple restaurants"""

    class Tier(models.TextChoices):
        STARTER = 'STARTER', 'Starter'
        PROFESSIONAL = 'PROFESSIONAL', 'Professional'
        ENTERPRISE = 'ENTERPRISE', 'Enterprise'

    name = models.CharField(max_length=255)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.STARTER)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    logo_url = models.URLField(blank=True)

    # Subscription
    subscription_status = models.CharField(max_length=20, default='active')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=99.00)

    # Health inspection tracking
    last_inspection_date = models.DateField(null=True, blank=True)
    last_inspection_score = models.IntegerField(null=True, blank=True)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['subscription_status']),
        ]

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """Individual restaurant location"""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        CLOSED = 'CLOSED', 'Closed'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)  # e.g., "boston_001"

    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='USA')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Restaurant details
    cuisine_type = models.CharField(max_length=100, blank=True)
    seating_capacity = models.IntegerField(null=True, blank=True)
    square_footage = models.IntegerField(null=True, blank=True)

    # Health inspection
    health_department_id = models.CharField(max_length=100, blank=True)
    last_inspection_date = models.DateField(null=True, blank=True)
    last_inspection_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    compliance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )

    # Gateway info
    gateway_id = models.CharField(max_length=100, unique=True)  # Raspberry Pi ID
    gateway_last_seen = models.DateTimeField(null=True, blank=True)
    gateway_version = models.CharField(max_length=50, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants'
        indexes = [
            models.Index(fields=['organization', 'name']),
            models.Index(fields=['gateway_id']),
            models.Index(fields=['status']),
            models.Index(fields=['city', 'state']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Location(models.Model):
    """Specific location within a restaurant (e.g., Walk-in Cooler #1)"""

    class LocationType(models.TextChoices):
        WALK_IN_COOLER = 'WALK_IN_COOLER', 'Walk-in Cooler'
        WALK_IN_FREEZER = 'WALK_IN_FREEZER', 'Walk-in Freezer'
        REACH_IN_COOLER = 'REACH_IN_COOLER', 'Reach-in Cooler'
        REACH_IN_FREEZER = 'REACH_IN_FREEZER', 'Reach-in Freezer'
        HOT_HOLDING = 'HOT_HOLDING', 'Hot Holding'
        DRY_STORAGE = 'DRY_STORAGE', 'Dry Storage'
        PREP_AREA = 'PREP_AREA', 'Prep Area'
        COOKING_LINE = 'COOKING_LINE', 'Cooking Line'
        DISHWASHING = 'DISHWASHING', 'Dishwashing'
        OTHER = 'OTHER', 'Other'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)  # e.g., "Main Walk-in Cooler"
    location_type = models.CharField(max_length=50, choices=LocationType.choices)

    # Temperature thresholds
    temp_min_f = models.DecimalField(max_digits=5, decimal_places=2)  # Minimum safe temp
    temp_max_f = models.DecimalField(max_digits=5, decimal_places=2)  # Maximum safe temp

    # Additional settings
    description = models.TextField(blank=True)
    position = models.CharField(max_length=100, blank=True)  # e.g., "Back of House"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'locations'
        verbose_name_plural = 'locations'
        indexes = [
            models.Index(fields=['restaurant', 'location_type']),
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"


class ComplianceCheck(models.Model):
    """Manual compliance check logs"""

    class CheckType(models.TextChoices):
        TEMPERATURE_LOG = 'TEMPERATURE_LOG', 'Temperature Log'
        COOLING_LOG = 'COOLING_LOG', 'Cooling Log'
        COOKING_LOG = 'COOKING_LOG', 'Cooking Log'
        HOT_HOLDING = 'HOT_HOLDING', 'Hot Holding'
        COLD_HOLDING = 'COLD_HOLDING', 'Cold Holding'
        DATE_MARKING = 'DATE_MARKING', 'Date Marking'
        SANITIZATION = 'SANITIZATION', 'Sanitization'
        PEST_CONTROL = 'PEST_CONTROL', 'Pest Control'
        OTHER = 'OTHER', 'Other'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='compliance_checks')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    check_type = models.CharField(max_length=50, choices=CheckType.choices)
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    # Check details
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # e.g., temperature
    notes = models.TextField(blank=True)
    passed = models.BooleanField(default=True)
    corrective_action = models.TextField(blank=True)

    # Photo evidence
    photo_url = models.URLField(blank=True)

    # Timestamp
    checked_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance_checks'
        indexes = [
            models.Index(fields=['restaurant', 'checked_at']),
            models.Index(fields=['check_type']),
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.check_type} at {self.checked_at}"
