"""OTA update models for Django backend"""

from django.db import models
from apps.restaurants.models import Restaurant


class OTAManifest(models.Model):
    """OTA update manifests"""

    class UpdateStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        TESTING = 'TESTING', 'Testing'
        STAGED = 'STAGED', 'Staged'
        ROLLING_OUT = 'ROLLING_OUT', 'Rolling Out'
        COMPLETED = 'COMPLETED', 'Completed'
        ROLLED_BACK = 'ROLLED_BACK', 'Rolled Back'

    version = models.CharField(max_length=50, unique=True)
    release_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    # Docker images for this update
    docker_images = models.JSONField(default=dict)  # {service: image_tag}

    # Configuration changes
    config_changes = models.JSONField(default=list)

    # Migration scripts
    migrations = models.JSONField(default=list)

    # Hooks
    pre_update_hooks = models.JSONField(default=list)
    post_update_hooks = models.JSONField(default=list)

    # Rollback commands
    rollback_commands = models.JSONField(default=list)

    # Version compatibility
    min_gateway_version = models.CharField(max_length=50)
    max_gateway_version = models.CharField(max_length=50)

    # Update properties
    critical = models.BooleanField(default=False)
    rollback_safe = models.BooleanField(default=True)
    requires_reboot = models.BooleanField(default=False)

    # File locations
    manifest_url = models.URLField(blank=True)
    signature_url = models.URLField(blank=True)

    # Rollout status
    status = models.CharField(max_length=20, choices=UpdateStatus.choices, default=UpdateStatus.DRAFT)

    # Rollout configuration
    rollout_percentage = models.IntegerField(default=0)  # 0-100
    auto_approve = models.BooleanField(default=False)

    # Statistics
    total_gateways = models.IntegerField(default=0)
    updated_gateways = models.IntegerField(default=0)
    failed_gateways = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ota_manifests'
        ordering = ['-release_date']
        indexes = [
            models.Index(fields=['version']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Update {self.version} ({self.status})"

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_gateways == 0:
            return 0.0
        return (self.updated_gateways / self.total_gateways) * 100


class GatewayUpdateStatus(models.Model):
    """Track update status for each gateway"""

    class UpdateState(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        DOWNLOADING = 'DOWNLOADING', 'Downloading'
        VERIFYING = 'VERIFYING', 'Verifying'
        BACKING_UP = 'BACKING_UP', 'Backing Up'
        APPLYING = 'APPLYING', 'Applying'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        ROLLED_BACK = 'ROLLED_BACK', 'Rolled Back'

    gateway_id = models.CharField(max_length=100)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    manifest = models.ForeignKey(OTAManifest, on_delete=models.CASCADE, related_name='gateway_statuses')

    # Update state
    state = models.CharField(max_length=20, choices=UpdateState.choices, default=UpdateState.PENDING)

    # Progress tracking
    current_step = models.CharField(max_length=100, blank=True)
    progress_percentage = models.IntegerField(default=0)

    # Error details (if failed)
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)

    # Backup info
    backup_created = models.BooleanField(default=False)
    backup_location = models.CharField(max_length=255, blank=True)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    # Retry tracking
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)

    # Logs
    update_log = models.TextField(blank=True)

    class Meta:
        db_table = 'gateway_update_status'
        unique_together = ['gateway_id', 'manifest']
        indexes = [
            models.Index(fields=['gateway_id', 'state']),
            models.Index(fields=['state']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"{self.gateway_id} - {self.manifest.version} ({self.state})"

    def log(self, message: str):
        """Add log entry"""
        timestamp = timezone.now().isoformat()
        self.update_log = f"{self.update_log}\n[{timestamp}] {message}".strip()
        self.save(update_fields=['update_log'])


class GatewayBackup(models.Model):
    """Gateway backups created before updates"""

    gateway_id = models.CharField(max_length=100)
    manifest = models.ForeignKey(OTAManifest, on_delete=models.CASCADE, related_name='backups')

    # Backup info
    backup_path = models.CharField(max_length=255)
    version = models.CharField(max_length=50)  # Version backed up
    size_bytes = models.BigIntegerField()

    # Backup contents
    includes_database = models.BooleanField(default=True)
    includes_config = models.BooleanField(default=True)
    includes_docker_images = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    # Cleanup
    keep_until = models.DateTimeField(null=True, blank=True)
    is_cleaned_up = models.BooleanField(default=False)

    class Meta:
        db_table = 'gateway_backups'
        indexes = [
            models.Index(fields=['gateway_id', 'created_at']),
            models.Index(fields=['keep_until']),
        ]

    def __str__(self):
        return f"{self.gateway_id} backup {self.created_at}"
