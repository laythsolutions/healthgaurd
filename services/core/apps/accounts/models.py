"""Account models for HealthGuard"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import secrets


class UserManager(BaseUserManager):
    """Custom user manager"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for HealthGuard"""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        STAFF = 'STAFF', 'Staff'
        INSPECTOR = 'INSPECTOR', 'Inspector'

    username = None  # Remove username field
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True,
        db_index=True
    )
    phone_number = models.CharField(  # Alias for backwards compatibility
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    organization = models.ForeignKey(
        'restaurants.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='members'
    )
    restaurants = models.ManyToManyField(
        'restaurants.Restaurant',
        through='RestaurantAccess',
        through_fields=('user', 'restaurant'),
        related_name='users'
    )
    profile_image = models.URLField(blank=True)
    notification_preferences = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['organization']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class RestaurantAccess(models.Model):
    """Through model for User-Restaurant permissions"""

    class AccessLevel(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        MANAGER = 'MANAGER', 'Manager'
        VIEWER = 'VIEWER', 'Viewer'

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='+')

    class Meta:
        db_table = 'restaurant_access'
        unique_together = ['user', 'restaurant']
        indexes = [
            models.Index(fields=['user', 'restaurant']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.restaurant.name} ({self.access_level})"


class NotificationPreference(models.Model):
    """User notification preferences"""

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='preferences')
    email_alerts = models.BooleanField(default=True)
    sms_alerts = models.BooleanField(default=False)
    push_alerts = models.BooleanField(default=True)
    alert_types = models.JSONField(default=list)  # ['critical', 'warning', 'info']
    email_severities = models.JSONField(default=list)  # ['CRITICAL', 'WARNING', 'INFO']
    sms_severities = models.JSONField(default=list)  # ['CRITICAL']
    push_severities = models.JSONField(default=list)  # ['CRITICAL', 'WARNING', 'INFO']
    quiet_hours_start = models.TimeField(null=True, blank=True)  # e.g., 22:00
    quiet_hours_end = models.TimeField(null=True, blank=True)  # e.g., 08:00
    timezone = models.CharField(max_length=50, default='UTC')

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"


class PushToken(models.Model):
    """FCM push notification tokens for users"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='push_tokens')
    token = models.CharField(max_length=500, unique=True, db_index=True)
    device_id = models.CharField(max_length=255, blank=True)  # For identifying devices
    device_type = models.CharField(max_length=50, blank=True)  # 'ios', 'android', 'web'
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'push_tokens'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.device_type or 'Unknown'}"


class MFASettings(models.Model):
    """Multi-Factor Authentication settings for users"""

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='mfa_settings')
    is_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=255, blank=True)  # TOTP secret key
    verified_at = models.DateTimeField(null=True, blank=True)  # When MFA was set up
    last_verified_at = models.DateTimeField(null=True, blank=True)  # Last successful verification

    class Meta:
        db_table = 'mfa_settings'
        verbose_name_plural = 'MFA settings'

    def __str__(self):
        return f"MFA Settings for {self.user.email}"


class BackupCode(models.Model):
    """Backup codes for MFA recovery"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='backup_codes')
    code_hash = models.CharField(max_length=64)  # SHA256 hash
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'backup_codes'
        indexes = [
            models.Index(fields=['user', 'is_used']),
        ]

    def __str__(self):
        return f"Backup code for {self.user.email}"


class TrustedDevice(models.Model):
    """Trusted devices to skip MFA"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='trusted_devices')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    device_name = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trusted_devices'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"Trusted device for {self.user.email}"


class APIKey(models.Model):
    """API keys for programmatic access"""

    class KeyType(models.TextChoices):
        PERSONAL = 'PERSONAL', 'Personal Access Token'
        SERVICE = 'SERVICE', 'Service Account'
        INTEGRATION = 'INTEGRATION', 'Integration Key'
        WEBHOOK = 'WEBHOOK', 'Webhook Signing Key'

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='api_keys', null=True, blank=True)
    organization = models.ForeignKey('restaurants.Organization', on_delete=models.CASCADE, related_name='api_keys', null=True, blank=True)

    name = models.CharField(max_length=255)  # e.g., "Production API Key", "Testing Script"
    key_type = models.CharField(max_length=20, choices=KeyType.choices, default=KeyType.PERSONAL)
    key_prefix = models.CharField(max_length=10)  # First 8 chars for display
    key_hash = models.CharField(max_length=64, unique=True)  # SHA256 hash
    scopes = models.JSONField(default=list)  # ['read:restaurants', 'write:alerts', etc.]

    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_hour = models.IntegerField(default=1000)

    # IP whitelist (optional)
    allowed_ips = models.JSONField(default=list)  # ['192.168.1.1', '10.0.0.0/8']

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_keys')

    class Meta:
        db_table = 'api_keys'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['key_hash']),
        ]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"

    @classmethod
    def generate_key(cls):
        """Generate a new API key

        Returns:
            Tuple of (full_key, key_hash)
        """
        # Format: hg_live_<random 32 chars>
        random_part = secrets.token_urlsafe(32)
        full_key = f"hg_live_{random_part}"

        # Hash for storage
        import hashlib
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()

        return full_key, key_hash

    def save(self, *args, **kwargs):
        # Generate key if new
        if not self.pk and not self.key_hash:
            full_key, key_hash = self.generate_key()
            self.key_hash = key_hash
            self.key_prefix = full_key[:10]

        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    """Password reset tokens"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'password_reset_tokens'
        indexes = [
            models.Index(fields=['token', 'expires_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    @classmethod
    def generate_token(cls):
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)

    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return (
            not self.used_at and
            self.expires_at > timezone.now()
        )


class Session(models.Model):
    """User session tracking"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=255, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_info = models.JSONField(default=dict)  # Device type, OS, browser

    is_active = models.BooleanField(default=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_key', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Session for {self.user.email}"

    def is_valid(self):
        """Check if session is valid"""
        return self.is_active and self.expires_at > timezone.now()