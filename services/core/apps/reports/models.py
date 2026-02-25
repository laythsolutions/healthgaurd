"""Compliance report models"""

from django.db import models
from apps.restaurants.models import Restaurant, Organization


class ComplianceReport(models.Model):
    """Generated compliance reports"""

    class ReportType(models.TextChoices):
        DAILY = 'DAILY', 'Daily Summary'
        WEEKLY = 'WEEKLY', 'Weekly Summary'
        MONTHLY = 'MONTHLY', 'Monthly Summary'
        QUARTERLY = 'QUARTERLY', 'Quarterly Summary'
        INSPECTION_PREP = 'INSPECTION_PREP', 'Inspection Preparation'
        SCORECARD = 'SCORECARD', 'Scorecard'
        CUSTOM = 'CUSTOM', 'Custom Report'

    class ReportStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        GENERATING = 'GENERATING', 'Generating'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    # Relationships
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reports')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='org_reports', null=True, blank=True)

    # Report details
    report_type = models.CharField(max_length=30, choices=ReportType.choices)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING)

    # Report period
    period_start = models.DateField()
    period_end = models.DateField()

    # Report data (computed)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    total_readings = models.IntegerField(default=0)
    violation_count = models.IntegerField(default=0)
    critical_alert_count = models.IntegerField(default=0)
    avg_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    # Report file
    report_url = models.URLField(max_length=500, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    file_pages = models.IntegerField(default=0)

    # Email delivery
    email_recipients = models.JSONField(default=list)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    # Generation tracking
    generated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_reports')
    generated_at = models.DateTimeField(null=True, blank=True)

    # Error details (if failed)
    error_message = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'compliance_reports'
        indexes = [
            models.Index(fields=['restaurant', '-created_at']),
            models.Index(fields=['report_type', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['period_start', 'period_end']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.restaurant.name} - {self.report_type} ({self.period_start} to {self.period_end})"


class ReportSchedule(models.Model):
    """Automated report schedules"""

    class Frequency(models.TextChoices):
        DAILY = 'DAILY', 'Daily'
        WEEKLY = 'WEEKLY', 'Weekly'
        BI_WEEKLY = 'BI_WEEKLY', 'Every 2 Weeks'
        MONTHLY = 'MONTHLY', 'Monthly'
        QUARTERLY = 'QUARTERLY', 'Quarterly'

    # Relationships
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='report_schedules')

    # Schedule details
    report_type = models.CharField(max_length=30, choices=ComplianceReport.ReportType.choices)
    frequency = models.CharField(max_length=20, choices=Frequency.choices)

    # Active flag
    is_active = models.BooleanField(default=True)

    # Next run time
    next_run_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)

    # Email recipients
    email_recipients = models.JSONField(default=list)

    # Report parameters
    include_readings = models.BooleanField(default=True)
    include_alerts = models.BooleanField(default=True)
    include_predictions = models.BooleanField(default=False)
    include_recommendations = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'report_schedules'
        verbose_name_plural = 'report schedules'
        indexes = [
            models.Index(fields=['restaurant', 'is_active']),
            models.Index(fields=['next_run_at']),
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.report_type} ({self.frequency})"


class ReportTemplate(models.Model):
    """Custom report templates"""

    class TemplateType(models.TextChoices):
        INSPECTION_SUMMARY = 'INSPECTION_SUMMARY', 'Inspection Summary'
        COMPLIANCE_AUDIT = 'COMPLIANCE_AUDIT', 'Compliance Audit'
        VIOLATION_ANALYSIS = 'VIOLATION_ANALYSIS', 'Violation Analysis'
        TREND_REPORT = 'TREND_REPORT', 'Trend Report'
        CUSTOM = 'CUSTOM', 'Custom Template'

    # Organization
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='report_templates')

    # Template details
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=50, choices=TemplateType.choices)
    description = models.TextField(blank=True)

    # Template structure (JSON)
    template_structure = models.JSONField(default=dict)

    # Sections to include
    include_sections = models.JSONField(default=list)

    # Styling options
    custom_logo_url = models.URLField(blank=True)
    custom_colors = models.JSONField(default=dict)

    # Approval
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_templates')
    approved_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'report_templates'
        verbose_name_plural = 'report templates'
        indexes = [
            models.Index(fields=['organization', 'is_approved']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class ReportDeliveryLog(models.Model):
    """Track report delivery"""

    class DeliveryMethod(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        WEBHOOK = 'WEBHOOK', 'Webhook'
        DOWNLOAD = 'DOWNLOAD', 'Manual Download'

    report = models.ForeignKey(ComplianceReport, on_delete=models.CASCADE, related_name='delivery_logs')
    delivery_method = models.CharField(max_length=20, choices=DeliveryMethod.choices)

    # Recipient
    recipient_email = models.EmailField(null=True, blank=True)
    recipient_phone = models.CharField(max_length=50, blank=True)
    recipient_user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    # Status
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report_delivery_logs'

    def __str__(self):
        return f"{self.report} - {self.delivery_method} to {self.recipient_email or self.recipient_user}"
