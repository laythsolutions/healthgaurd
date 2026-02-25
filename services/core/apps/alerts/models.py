"""Alert models for compliance notifications"""

from django.db import models
from apps.devices.models import Device
from apps.restaurants.models import Restaurant


class Alert(models.Model):
    """Alert generated from sensor readings or compliance violations"""

    class Severity(models.TextChoices):
        CRITICAL = 'CRITICAL', 'Critical'
        WARNING = 'WARNING', 'Warning'
        INFO = 'INFO', 'Info'

    class AlertStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acknowledged'
        RESOLVED = 'RESOLVED', 'Resolved'
        FALSE_POSITIVE = 'FALSE_POSITIVE', 'False Positive'

    class AlertType(models.TextChoices):
        TEMP_VIOLATION = 'TEMP_VIOLATION', 'Temperature Violation'
        HUMIDITY_VIOLATION = 'HUMIDITY_VIOLATION', 'Humidity Violation'
        DOOR_OPEN = 'DOOR_OPEN', 'Door Open Too Long'
        LOW_BATTERY = 'LOW_BATTERY', 'Low Battery'
        DEVICE_OFFLINE = 'DEVICE_OFFLINE', 'Device Offline'
        MANUAL_LOG_REQUIRED = 'MANUAL_LOG', 'Manual Log Required'

    # Alert details
    alert_type = models.CharField(max_length=30, choices=AlertType.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.WARNING)
    status = models.CharField(max_length=30, choices=AlertStatus.choices, default=AlertStatus.ACTIVE)

    # Relationships
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='alerts')
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')

    # Alert data
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Sensor reading that triggered the alert
    temperature = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    threshold_min = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    threshold_max = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Notification tracking
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    notification_methods = models.JSONField(default=list)  # ['email', 'sms', 'push']

    # Acknowledgement
    acknowledged_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledgement_notes = models.TextField(blank=True)

    # Resolution
    resolved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'alerts'
        indexes = [
            models.Index(fields=['restaurant', '-created_at']),
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['alert_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.restaurant.name}"


class AlertRule(models.Model):
    """Rules for automatic alert generation"""

    class RuleType(models.TextChoices):
        TEMPERATURE_THRESHOLD = 'TEMP_THRESHOLD', 'Temperature Threshold'
        HUMIDITY_THRESHOLD = 'HUMIDITY_THRESHOLD', 'Humidity Threshold'
        DOOR_OPEN_DURATION = 'DOOR_DURATION', 'Door Open Duration'
        DEVICE_OFFLINE = 'DEVICE_OFFLINE', 'Device Offline'
        BATTERY_LOW = 'BATTERY_LOW', 'Battery Low'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='alert_rules')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True, related_name='alert_rules')

    rule_type = models.CharField(max_length=30, choices=RuleType.choices)
    severity = models.CharField(max_length=20, choices=Alert.Severity.choices, default=Alert.Severity.WARNING)

    # Rule parameters (JSON for flexibility)
    parameters = models.JSONField(default=dict)  # e.g., {'temp_min': 34, 'temp_max': 41}

    # Notification settings
    enabled = models.BooleanField(default=True)
    notification_methods = models.JSONField(default=list)  # ['email', 'sms', 'push']
    notification_delay_minutes = models.IntegerField(default=0)  # Delay before alerting

    # Escalation
    escalation_enabled = models.BooleanField(default=False)
    escalation_delay_minutes = models.IntegerField(default=30)
    escalation_severity = models.CharField(max_length=20, choices=Alert.Severity.choices, default=Alert.Severity.CRITICAL)

    # Schedule (when rule is active)
    active_all_day = models.BooleanField(default=True)
    active_start_time = models.TimeField(null=True, blank=True)
    active_end_time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'alert_rules'
        verbose_name_plural = 'alert rules'

    def __str__(self):
        return f"{self.restaurant.name} - {self.rule_type}"


class NotificationLog(models.Model):
    """Log of sent notifications"""

    class NotificationType(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        PUSH = 'PUSH', 'Push Notification'
        WEBHOOK = 'WEBHOOK', 'Webhook'

    class DeliveryStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SENT = 'SENT', 'Sent'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED = 'FAILED', 'Failed'

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)

    # Recipient
    recipient = models.CharField(max_length=255)  # Email, phone number, push token, etc.

    # Content
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()

    # Delivery tracking
    status = models.CharField(max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # External IDs
    external_id = models.CharField(max_length=255, blank=True)  # Twilio SID, SendGrid ID, etc.

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_logs'

    def __str__(self):
        return f"{self.notification_type} to {self.recipient}"
